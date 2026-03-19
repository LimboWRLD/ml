import rasterio
import json
from rasterio.plot import show
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import os
from pyproj import Transformer

def analyze_tif_location(tif_path):
    
    print(f"Analiziram: {tif_path}")
    
    with rasterio.open(tif_path) as src:
        # Osnovni metapodaci
        print("\n METAPODACI:")
        print(f"   Format: {src.driver}")
        print(f"   Dimenzije: {src.width} x {src.height} piksela")
        print(f"   Broj kanala: {src.count}")
        print(f"   Rezolucija: {src.res}")
        print(f"   CRS (koordinatni sistem): {src.crs}")
        
        # Geografski bound (granice)
        bounds = src.bounds
        print(f"\n UTM KOORDINATE:")
        print(f"   Levo: {bounds.left:.1f} m")
        print(f"   Desno: {bounds.right:.1f} m") 
        print(f"   Dole: {bounds.bottom:.1f} m")
        print(f"   Gore: {bounds.top:.1f} m")
        
        # Centar slike u UTM
        center_x = (bounds.left + bounds.right) / 2
        center_y = (bounds.bottom + bounds.top) / 2
        print(f"   Centar UTM: {center_x:.1f} m E, {center_y:.1f} m N")
        
        # Konvertuj UTM u geografske koordinate (latitude/longitude)
        transformer = Transformer.from_crs(src.crs, "EPSG:4326", always_xy=True)
        
        # Konvertuj granice
        left_lon, bottom_lat = transformer.transform(bounds.left, bounds.bottom)
        right_lon, top_lat = transformer.transform(bounds.right, bounds.top)
        center_lon, center_lat = transformer.transform(center_x, center_y)
        
        print(f"\n GEOGRAFSKE KOORDINATE (WGS84):")
        print(f"   Levo (zapad): {left_lon:.6f}°")
        print(f"   Desno (istok): {right_lon:.6f}°")
        print(f"   Dole (jug): {bottom_lat:.6f}°")
        print(f"   Gore (sever): {top_lat:.6f}°")
        print(f"   Centar: {center_lon:.6f}°E, {center_lat:.6f}°N")
        
        # Povrsina u km2
        width_km = (bounds.right - bounds.left) / 1000  # m to km
        height_km = (bounds.top - bounds.bottom) / 1000
        area_km2 = width_km * height_km
        print(f"Povrsina: {area_km2:.2f} km2")
        
        return {
            'utm_bounds': {
                'left': bounds.left,
                'right': bounds.right, 
                'bottom': bounds.bottom,
                'top': bounds.top
            },
            'geo_bounds': {
                'west': left_lon,
                'east': right_lon,
                'south': bottom_lat, 
                'north': top_lat
            },
            'center_utm': [center_x, center_y],
            'center_geo': [center_lon, center_lat],
            'crs': str(src.crs),
            'dimensions': [src.width, src.height],
            'area_km2': area_km2
        }

def create_geojson_from_tif(tif_path, output_geojson_path):
    
    with rasterio.open(tif_path) as src:
        # Konvertuj UTM u geografske koordinate
        transformer = Transformer.from_crs(src.crs, "EPSG:4326", always_xy=True)
        bounds = src.bounds
        
        left_lon, bottom_lat = transformer.transform(bounds.left, bounds.bottom)
        right_lon, top_lat = transformer.transform(bounds.right, bounds.top)
        
        # Kreiraj GeoJSON feature sa bounding box-om
        feature = {
            "type": "Feature",
            "properties": {
                "filename": os.path.basename(tif_path),
                "date": "2023-07-15",
                "satellite": "Sentinel-2",
                "location": "Subotica, Srbija",
                "mgrs_tile": "34TDR",
                "crs": str(src.crs),
                "area_km2": round(((bounds.right - bounds.left) / 1000) * ((bounds.top - bounds.bottom) / 1000), 2)
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [left_lon, bottom_lat],
                    [right_lon, bottom_lat],
                    [right_lon, top_lat],
                    [left_lon, top_lat],
                    [left_lon, bottom_lat]
                ]]
            }
        }
        
        geojson = {
            "type": "FeatureCollection",
            "features": [feature]
        }
        
        # Sacuvaj GeoJSON
        with open(output_geojson_path, 'w') as f:
            json.dump(geojson, f, indent=2)
        
        print(f" GeoJSON sacuvan: {output_geojson_path}")
        return geojson

def preview_tif_image(tif_path, output_image_path):
    # Kreiraj pregled slike sa oznacenom lokacijom
    
    with rasterio.open(tif_path) as src:
        # citaj sve kanale
        image_data = src.read()
        
        print(f"Oblik podataka: {image_data.shape}")
        
        # Proveri broj kanala i prilagodi
        if image_data.shape[0] >= 3:
            # Uzmi prva 3 kanala za RGB
            red = image_data[0]
            green = image_data[1] 
            blue = image_data[2]
        else:
            # Ako ima manje kanala, koristi grayscale
            red = green = blue = image_data[0]
        
        # Normalizuj za prikaz
        def normalize(band):
            band_min, band_max = band.min(), band.max()
            if band_max == band_min:
                return np.zeros_like(band, dtype=np.uint8)
            return ((band - band_min) / (band_max - band_min) * 255).astype(np.uint8)
        
        red_norm = normalize(red)
        green_norm = normalize(green)
        blue_norm = normalize(blue)
        
        # Kombinuj u RGB
        rgb = np.stack([red_norm, green_norm, blue_norm], axis=-1)
        
        print(f"Oblik RGB: {rgb.shape}")
        
        # Kreiraj plot
        fig, ax = plt.subplots(1, 1, figsize=(12, 10))
        
        # Prikazi sliku
        ax.imshow(rgb)
        
        # Konvertuj centar u geografske koordinate za prikaz
        transformer = Transformer.from_crs(src.crs, "EPSG:4326", always_xy=True)
        bounds = src.bounds
        center_x = (bounds.left + bounds.right) / 2
        center_y = (bounds.bottom + bounds.top) / 2
        center_lon, center_lat = transformer.transform(center_x, center_y)
        
        # Dodaj informacije
        ax.set_title(f"Sentinel-2 Snimak: Subotica, Srbija\n15. Jul 2023 * MGRS: 34TDR", 
                    fontsize=14, fontweight='bold')
        ax.text(0.02, 0.98, f"Lokacija: {center_lon:.4f}°E, {center_lat:.4f}°N\n"
                          f"Dimenzije: {src.width}×{src.height} px\n"
                          f"Povrsina: {((bounds.right-bounds.left)/1000*(bounds.top-bounds.bottom)/1000):.1f} km²", 
                transform=ax.transAxes, fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle="round", facecolor="white", alpha=0.8))
        
        # Ukloni osne oznake
        ax.set_xticks([])
        ax.set_yticks([])
        
        plt.tight_layout()
        plt.savefig(output_image_path, dpi=150, bbox_inches='tight')
        print(f" Slika sacuvana: {output_image_path}")
        plt.close()  # Zatvori plot da ne bi blokirao izvrsavanje

def get_google_maps_link(center_lon, center_lat):
    # Generisi Google Maps link za lokaciju
    maps_link = f"https://www.google.com/maps/@{center_lat:.6f},{center_lon:.6f},12z"
    return maps_link

def get_openstreetmap_link(bounds):
    # Generisi OpenStreetMap link za bounding box
    osm_link = f"https://www.openstreetmap.org/?minlon={bounds['west']}&minlat={bounds['south']}&maxlon={bounds['east']}&maxlat={bounds['north']}&box=yes"
    return osm_link

def get_bbox_center(bounds):
    # Izracunaj centar bounding box-a
    center_lon = (bounds['west'] + bounds['east']) / 2
    center_lat = (bounds['south'] + bounds['north']) / 2
    return center_lon, center_lat


def main(tif_path):
    
    # 1. Analiziraj lokaciju
    location_data = analyze_tif_location(tif_path)
    
    # 2. Kreiraj GeoJSON
    geojson_path = os.path.splitext(tif_path)[0] + "_location.geojson"
    
    # 3. Kreiraj pregled slike
    preview_path = os.path.splitext(tif_path)[0] + "_preview.png"
    preview_tif_image(tif_path, preview_path)

    
    return location_data

if __name__ == "__main__":
    tif_file = "./satelitski_snimci_srbija/s2_2023-07-15_34TDR_Subotica.tif"
    
    if os.path.exists(tif_file):
        result = main(tif_file)
        
    else:
        print(f"Fajl {tif_file} ne postoji!")