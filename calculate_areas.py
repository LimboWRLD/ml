import os
import cv2
import numpy as np
import csv
from tqdm import tqdm

POVRSINA_PO_PIKSELU_M2 = 100 

MASK_DIR = './pipeline_step2_results/binary_masks/'
OUTPUT_CSV = 'FINAL_RESULTS.csv'

results = []

print("Racunanje povrsina iz binarnih maski")
for mask_file in tqdm(os.listdir(MASK_DIR)):
    if mask_file.endswith('_mask.png'):
        mask_path = os.path.join(MASK_DIR, mask_file)
        
        # Ucitaj masku
        mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
        
        if mask is not None:
            # Broji bele piksele (gde je vrednost > 0)
            broj_belih_piksela = np.count_nonzero(mask)
            
            # Izracunaj povrsinu
            povrsina_m2 = broj_belih_piksela * POVRSINA_PO_PIKSELU_M2
            
            if povrsina_m2 > 0:
                # Izvuci koordinate iz imena fajla
                original_filename = mask_file.replace('_mask.png', '.png')
                results.append([original_filename, povrsina_m2])

with open(OUTPUT_CSV, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['ime_fajla', 'povrsina_m2'])
    writer.writerows(results)
