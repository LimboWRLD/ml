import ee
import geemap
import os
from datetime import datetime, timedelta
import numpy as np


try:
    ee.Initialize()
    print("EE inicijalizovan.")
except Exception:
    print("Pokretanje autentifikacije...")
    ee.Authenticate()
    ee.Initialize(project='tiaclandfills')


class SerbiaSatelliteDownloader:
    def __init__(self, output_dir="./satelitski_snimci_srbija"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    def get_individual_urban_areas_serbia(self):
        # Glavni gradovi i veci gradovi u Srbiji
        cities = [
            [20.46513, 44.80401, 'Beograd'],
            [21.89546, 43.32472, 'Nis'],
            [19.83355, 45.25167, 'Novi_Sad'],
            [20.97639, 44.02543, 'Kragujevac'],
            [21.94433, 44.65454, 'Zrenjanin'],
            [19.63625, 45.11843, 'Subotica'],
            [21.35889, 43.85833, 'Leskovac'],
            [22.01194, 44.26417, 'Smederevo'],
            [20.04111, 44.65417, 'Valjevo'],
            [19.61278, 44.87194, 'Sombor'],
        ]
        
        areas = []
        for lon, lat, name in cities:
            point = ee.Geometry.Point([lon, lat])
            buffer = point.buffer(20000)  # 20km
            areas.append({'name': name, 'geometry': buffer}) # Vracamo geometriju i ime
        
        return areas
    
    def download_sentinel2_images(self, start_date='2023-06-01', end_date='2023-09-01', cloud_filter=20, max_images=20):
        
        print("Preuzimanje Sentinel-2 snimaka za Srbiju (razbijeno po gradovima)...")
        
        # Dobijamo listu malih regiona (bufera)
        city_regions = self.get_individual_urban_areas_serbia()
        
        # Kreiramo region za filtriranje (UNION svih bufera)
        filtering_region = ee.Geometry.MultiPolygon([d['geometry'] for d in city_regions])
        
        # Filtriranje slika
        collection = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
                      .filterBounds(filtering_region)
                      .filterDate(start_date, end_date)
                      .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', cloud_filter))
                      .sort('CLOUDY_PIXEL_PERCENTAGE'))
        
        count = collection.size().getInfo()
        print(f"Pronađeno {count} snimaka")
        
        if count == 0:
            print("Nema dostupnih snimaka za navedene kriterijume")
            return []
        
        image_list = collection.toList(max_images)
        downloaded_files = []
        
        file_counter = 0

        for i in range(min(max_images, count)):
            image = ee.Image(image_list.get(i))
            date = image.date().format('YYYY-MM-dd').getInfo()
            tile = image.get('MGRS_TILE').getInfo()
            
            for j, city_data in enumerate(city_regions):
                city_name = city_data['name']
                city_geom = city_data['geometry']
                
                #  Uzimamo presek (Intersection) slike i bufera grada
                export_region = image.geometry().intersection(city_geom, ee.ErrorMargin(10)) 
                
                try:
                    file_counter += 1
                    filename = f"s2_{date}_{tile}_{city_name}.tif"
                    filepath = os.path.join(self.output_dir, filename)

                    print(f"Preuzimanje {file_counter}: {filename}...")
                    
                    geemap.ee_export_image(
                        image.select(['B4', 'B3', 'B2']), # RGB kanali
                        filename=filepath,
                        scale=10,  # 10m rezolucija
                        region=export_region, 
                        file_per_band=False
                    )

                    downloaded_files.append(filepath)
                    print(f" Preuzeto: {filename}")
                
                except Exception as e:
                    # Preskacemo preuzimanja gde se tile i bufer ne preklapaju (ili su greske)
                    error_message = str(e)
                    if "A geometry has too many vertices" in error_message or "Export failed" in error_message:
                        print(f"Preskacem snimak: {filename}")
                    else:
                        print(f"Greska pri preuzimanju snimka {filename}: {e}")
                    continue
        
        return downloaded_files

def download_serbia_satellite_images():
    downloader = SerbiaSatelliteDownloader()
    
    # Preuzmi Sentinel-2 snimke
    sentinel_files = downloader.download_sentinel2_images(
        start_date='2023-06-01',
        end_date='2023-09-01',
        cloud_filter=20,
        max_images=20 # 20 snimaka * 10 gradova = 200 pokusaja preuzimanja
    )
    
    print(f"Preuzeto ukupno {len(sentinel_files)} TIFF fajlova.")
    return sentinel_files

if __name__ == "__main__":
    downloaded_files = download_serbia_satellite_images()
