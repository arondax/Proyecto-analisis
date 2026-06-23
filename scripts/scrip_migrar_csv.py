import pandas as pd
import glob
import os

ruta_csv = './datasets/'
patron = os.path.join(ruta_csv, '*.csv')
archivos = glob.glob(patron)

for archivo in archivos:
    df = pd.read_csv(archivo)
    
    if 'fecha' not in df.columns:
        df['fecha'] = None
    if 'fecha_legible' not in df.columns:
        df['fecha_legible'] = None
        
    df.to_csv(archivo, index=False)
    print(f"Migrado: {archivo}")