import os


BASE_DIR= os.path.dirname(os.path.abspath(__file__))

DATASET_DIR = os.path.join(BASE_DIR, 'data','raw')

DATASET_INGEST_DIR = os.path.join(BASE_DIR, 'data','procesado')

DATASET_ENTRENAMIENTO_DIR = os.path.join(BASE_DIR, 'data','entrenamiento')

MODELOS_DIR = os.path.join(BASE_DIR, 'ml', 'modelos')

JSON_INFO_DIR = os.path.join(BASE_DIR, 'data','info')

PARTIDAS_DIR = os.path.join(BASE_DIR, 'data','partidas')

LOGS_DIR = os.path.join(BASE_DIR, 'ml', 'modelos', 'logs')

DIST_DIR = os.path.join(BASE_DIR, 'frontend','dist')