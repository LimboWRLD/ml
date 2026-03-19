import glob
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import os
import argparse
from tqdm import tqdm

def main(args):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    model = models.resnet50(weights=None) 
    num_ftrs = model.fc.in_features

    model.fc = nn.Linear(num_ftrs, 22) 
    
    print(f"Loading classifier model from: {args.model_path}")
    checkpoint = torch.load(args.model_path, map_location=device)
    model.load_state_dict(checkpoint['state_dict'])
    model = model.to(device)
    model.eval() 

    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224), # ResNet je treniran na 224x224
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    results = []
    # Pronadji sve PNG fajlove u folderu
    image_files = glob.glob(os.path.join(args.image_dir, '**', '*.png'), recursive=True)
    
    if not image_files:
        print(f"ERROR: Nije pronadjena nijedna slika u {args.image_dir} ili njegovim podfolderima.")
        return 

    with torch.no_grad():
        for img_path in tqdm(image_files, desc="Classifier filtering (Step 1)"): # Iteriramo kroz pune putanje
            filename = os.path.basename(img_path) # Treba nam samo ime fajla za rezultat
            try:
                image = Image.open(img_path).convert('RGB')
                tensor = transform(image).unsqueeze(0).to(device)
                output = model(tensor)
                
                # Uzimamo verovatnocu (za visestruke klase, uzimamo maksimalnu)
                prob = torch.sigmoid(output).max().item()
                
                # Ako je model sumnjicav, sacuvaj fajl
                if prob > args.threshold:
                    relative_path = os.path.relpath(img_path, args.image_dir)
                    results.append({'file': relative_path, 'confidence': prob}) 
            except Exception as e:
                print(f"Skipping {filename} at {img_path}: {e}")

    results.sort(key=lambda x: x['confidence'], reverse=True)
    
    output_file = os.path.join(args.output_dir, "classifier_results.txt")
    os.makedirs(args.output_dir, exist_ok=True)
    
    with open(output_file, 'w') as f:
        for res in results:
            f.write(f"{res['file']}\n")
            
    print(f"\nClassifier finished. Found {len(results)} suspicious tiles.")
    print(f"List of suspicious tiles saved to: {output_file}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Classifier Prediction Runner')
    parser.add_argument('--image-dir', type=str, required=True, help='Folder sa SVIM iseccima (npr. ./tiles_srem).')
    parser.add_argument('--model-path', type=str, required=True, help='Putanja do tvog KLASIFIKACIONOG modela (npr. ./checkpoints_classifier_backup/best_model.pth).')
    parser.add_argument('--output-dir', type=str, default='./pipeline_step1', help='Folder gde ce se sacuvati classifier_results.txt.')
    parser.add_argument('--threshold', type=float, default=0.5, help='Prag "sumnjivosti" (0.0 - 1.0).')
    
    args = parser.parse_args()
    main(args)