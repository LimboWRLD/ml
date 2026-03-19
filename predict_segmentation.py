import torch
import torch.nn as nn
from torchvision import transforms
from PIL import Image
import os
import argparse
from tqdm import tqdm
import numpy as np
import cv2 
from torchvision.models.segmentation import deeplabv3_resnet50, DeepLabV3_ResNet50_Weights

def get_segmentation_model(num_classes, model_path, device):
    
    # Inicijalizujemo DeepLabV3 sa pre-treniranim ResNet50 backbone-om.
    weights = DeepLabV3_ResNet50_Weights.DEFAULT
    
    # Inicijalizujemo model, DeepLabV3 ce automatski ucitati ResNet50 tezine
    model = deeplabv3_resnet50(weights=weights) 
    
    # DeepLabV3 klasifikator se sastoji od vise slojeva, poslednji je Conv2d
    in_channels = model.classifier[4].in_channels
    model.classifier[4] = nn.Conv2d(in_channels, num_classes, kernel_size=(1, 1), stride=(1, 1))
    
    print(f"Loading segmentation model from: {model_path}")
    checkpoint = torch.load(model_path, map_location=device)
    
    # Ponekad se kljucevi u checkpointu zovu 'model_state_dict' ili 'state_dict'
    state_dict = checkpoint.get('state_dict', checkpoint) 

    model.load_state_dict(state_dict, strict=False) 
    
    model = model.to(device)
    model.eval()
    return model


def main(args):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    

    NUM_CLASSES = 1 
    model = get_segmentation_model(NUM_CLASSES, args.model_path, device)


    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    try:
        with open(args.classifier_results, 'r') as f:
            relative_image_paths = [line.strip() for line in f if line.strip()] 
    except FileNotFoundError:
        print(f"ERROR: Fajl sa rezultatima klasifikatora nije pronađen na: {args.classifier_results}")
        return
    
    os.makedirs(os.path.join(args.output_dir, "binary_masks"), exist_ok=True)
    os.makedirs(os.path.join(args.output_dir, "heatmaps"), exist_ok=True) 


    with torch.no_grad():
        for relative_path in tqdm(relative_image_paths, desc="Segmentation (Step 2)"):
            
            # Formiranje pune putanje
            full_img_path = os.path.join(args.all_tiles_dir, relative_path)
            
            # Ime fajla bez ekstenzije (za snimanje)
            base_name = os.path.basename(relative_path).replace('.png', '')
            
            try:
                # Ucitavanje slike i cuvanje originalne velicine
                image = Image.open(full_img_path).convert('RGB')
                original_size = image.size # (width, height)
                
                # Transformacija i predviđanje
                tensor = transform(image).unsqueeze(0).to(device)
                output = model(tensor)['out'] # DeepLabV3 izlaz je dictionary, pa ['out']
                
                # Post-obrada maske
                # Skaliramo na originalnu velicinu (1000x1000)
                output_mask = nn.functional.interpolate(
                    output, 
                    size=original_size[::-1], # (height, width)
                    mode='bilinear', 
                    align_corners=False
                )
                
                mask_tensor = torch.sigmoid(output_mask).squeeze()
                
                # Postavi piksele iznad praga (npr. 0.5) na 255 (Belo), ostalo na 0 (Crno)
                binary_mask = (mask_tensor > 0.5).cpu().numpy().astype(np.uint8) * 255 
                
                
                # Snimanje Binarne Maske (KalkulaciJA povrsine)
                mask_filename = f"{base_name}_mask.png"
                mask_filepath = os.path.join(args.output_dir, "binary_masks", mask_filename)
                
                # Koristimo OpenCV jer PIL nekada ima problema sa formatima boja
                cv2.imwrite(mask_filepath, binary_mask)

            except Exception as e:
                print(f"Skipping {relative_path}. Error during prediction: {e}")
                continue

    print(f"\nSegmentation finished. Binary masks saved to: {os.path.join(args.output_dir, 'binary_masks')}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Segmentation Prediction Runner')
    parser.add_argument('--all-tiles-dir', type=str, required=True, help='Root folder sa SVIM iseccima (npr. ./svi_isecci_srbija/).')
    parser.add_argument('--classifier-results', type=str, required=True, help='Putanja do classifier_results.txt (npr. ./pipeline_step1/classifier_results.txt).')
    parser.add_argument('--model-path', type=str, required=True, help='Putanja do tvog SEGMENTACIONOG modela (npr. ./checkpoints/best_model.pth).')
    parser.add_argument('--output-dir', type=str, default='./pipeline_step2_results', help='Folder za cuvanje maski.')
    
    args = parser.parse_args()
    main(args)