import pandas as pd
import glob
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

ruta_csv = config.DATASET_INGEST_DIR
patron = os.path.join(ruta_csv, '*.csv')
archivos = glob.glob(patron)

for archivo in archivos:
    df = pd.read_csv(archivo)
    
    if 'rango' in df.columns:
        df['rango'] = df['rango'] + 1
        df.to_csv(archivo, index=False)
        print(f"Migrado: {os.path.basename(archivo)}")
    else:
        print(f"Sin columna rango: {os.path.basename(archivo)}")