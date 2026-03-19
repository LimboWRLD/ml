#  AerialWaste - Detekcija Divljih Deponija (MVP)

Ovaj repozitorijum dokumentuje pipeline za detekciju i lokalizaciju divljih deponija u Srbiji koristeći Sentinel-2 satelitske snimke i modele trenirane na AerialWaste datasetu.

---

## 1. Setup i Instalacija

Instaliraj potrebne biblioteke:

```bash
# Osnovne biblioteke
pip install numpy opencv-python rasterio geemap ee scikit-learn tqdm pandas torch torchvision
```

## 2. Struktura Projekta
```bash
TIAC_LANDFILLS/
├── checkpoints/                        # Model weights (preuzeti sa Drive-a)
├── checkpoints_classifier_backup/      # Backup model weights (preuzeti sa Drive-a)
├── satelitski_snimci_srbija/          # Preuzeti Sentinel-2 TIFF fajlovi
├── svi_isečci_srbija/                 # Tile-ovani isečci za pipeline
├── downloader.py                       # Preuzimanje snimaka
├── tile_cutter.py                      # Seckanje TIFF fajlova
├── predict_classifier.py               # Klasifikacija isečaka
├── predict_segmentation.py             # Segmentacija i maske
├── calculate_areas.py                  # Izračunavanje površina
├── get_coordinates.py                  # GPS centar isečka
└── README.md
```
## 3. Preuzimanje Modela i Foldera
Modeli su preveliki za GitHub. Preuzmi ih sa Google Drive-a:

[checkpoints i checkpoints_classifier_backup](https://drive.google.com/drive/folders/1imgklhCv8QGOhUMq0iNG3NP3k65_dfAA?usp=sharing)

Nakon preuzimanja, postavi oba foldera u root repozitorijuma.
```bash
TIAC_LANDFILLS/
├── checkpoints/
└── checkpoints_classifier_backup/
```

## 4. Pipeline Koraci

FAZA 0: Preuzimanje Sentinel-2 Snimaka
```bash
python downloader.py
```

FAZA 1: Seckanje snimaka
```bash
python tile_cutter.py --input-dir ./satelitski_snimci_srbija/ --output-dir ./svi_isečci_srbija/ --tile-size 1000
```

FAZA 2: Klasifikacija
```bash
python predict_classifier.py --image-dir ./svi_isečci_srbija/ --model-path ./checkpoints_classifier_backup/best_model.pth --output-dir ./pipeline_step1 --threshold 0.1
```

FAZA 3: Segmentacija
```bash
python predict_segmentation.py --all-tiles-dir ./svi_isečci_srbija/ --classifier-results ./pipeline_step1/classifier_results.txt --model-path ./checkpoints/best_model.pth --output-dir ./pipeline_step2_results
```

FAZA 4: Izveštavanje i Lokalizacija
```bash
python calculate_areas.py
python get_coordinates.py
```
Površine i GPS koordinata se izračunavaju, a ručna provera je korišćena za hibridnu validaciju.

## 5. MVP Rešenje: Hibridna Validacija
AI klasifikator locira moguće deponije.

Najbolji kandidati se ručno proveravaju u Google Earth Pro.

Ručno se izmerava stvarna površina, utvrđuje tačan Lat/Lon i Početna Godina.

Na osnovu toga se izračunavaju prateći parametri: zapremina, masa, emisije.

## 6. Video Demonstracija
[Video demo](https://drive.google.com/file/d/1XD7XIM7W_8MjDe9h48S1J7G9VQiMAOB0/view?usp=sharing)
