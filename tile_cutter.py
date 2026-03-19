import rasterio
from rasterio.windows import Window
from PIL import Image
import os
from tqdm import tqdm
import numpy as np
import argparse

def tile_geotiff(input_tif, output_dir, tile_size=1000):
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with rasterio.open(input_tif) as src:
        width = src.width
        height = src.height
        bands_to_read = [1, 2, 3] # RGB

        print(f"Seckanje slike {input_tif} ({width}x{height}) na {tile_size}x{tile_size} plocice...")

        for y in tqdm(range(0, height, tile_size), desc="Tiling"):
            for x in range(0, width, tile_size):
                
                window = Window(x, y, tile_size, tile_size)
                
                try:
                    tile_data = src.read(bands_to_read, window=window)
                    tile_data_rgb = np.transpose(tile_data, (1, 2, 0))
                    
                    # Normalizacija za Sentinel-2. Vrednosti idu do ~3000-4000.
                    # Rastežemo ih na 0-255 za PNG.
                    # Ovo je bolja normalizacija (clipping) nego min-max.
                    clip_max = 3500
                    tile_data_rgb = np.clip(tile_data_rgb / clip_max * 255, 0, 255).astype(np.uint8)

                    img = Image.fromarray(tile_data_rgb)

                    if img.getbbox() is None: # Preskoci crne (prazne) plocice
                        continue
                    
                    # Ime fajla sadrzi koordinate
                    output_filename = f"tile_y{y}_x{x}.png" 
                    img.save(os.path.join(output_dir, output_filename))

                except Exception as e:
                    print(f"Greska na plocici {y}, {x}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Tile GeoTIFF into PNGs')
    parser.add_argument('--input-dir', type=str, required=True, help='Folder sa .tif fajlovima.')
    parser.add_argument('--output-dir', type=str, required=True, help='Glavni folder za isecke.')
    parser.add_argument('--tile-size', type=int, default=1000, help='Velicina plocice.')
    
    args = parser.parse_args()

    for tif_file in os.listdir(args.input_dir):
        if tif_file.endswith('.tif'):
            input_path = os.path.join(args.input_dir, tif_file)
            # Napravi poseban podfolder za isecke svake velike slike
            output_subfolder = os.path.join(args.output_dir, os.path.splitext(tif_file)[0])
            tile_geotiff(input_path, output_subfolder, args.tile_size)