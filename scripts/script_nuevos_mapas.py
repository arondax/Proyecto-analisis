import pandas as pd
import glob
import os
import json
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# Cargamos el pool de mapas desde el JSON
with open(os.path.join(config.JSON_INFO_DIR, 'info_valorant.json'), 'r', encoding='utf-8') as f:
    info = json.load(f)

mapas = info['mapas']['ranked']
columnas_mapa = [f'mapa_{m}' for m in mapas]

ruta_csv = config.DATASET_INGEST_DIR
patron = os.path.join(ruta_csv, '*.csv')
archivos = glob.glob(patron)

for archivo in archivos:
    df = pd.read_csv(archivo)
    modificado = False

    for columna in columnas_mapa:
        if columna not in df.columns:
            # Buscamos la última columna mapa_ existente para insertar después
            cols_mapa_existentes = [c for c in df.columns if c.startswith('mapa_')]
            if cols_mapa_existentes:
                idx = df.columns.get_loc(cols_mapa_existentes[-1]) + 1
            else:
                idx = len(df.columns)
            df.insert(idx, columna, 0)
            print(f"  + {columna} añadida en {os.path.basename(archivo)}")
            modificado = True

    if modificado:
        df.to_csv(archivo, index=False)
        print(f"Migrado: {os.path.basename(archivo)}")
    else:
        print(f"Sin cambios: {os.path.basename(archivo)}")