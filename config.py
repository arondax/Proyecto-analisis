import os


BASE_DIR= os.path.dirname(os.path.abspath(__file__))

DATASET_DIR = os.path.join(BASE_DIR, 'datasets')

DATASET_INGEST_DIR = os.path.join(BASE_DIR, 'dataset_ingest')

DATASET_ENTRENAMIENTO_DIR = os.path.join(BASE_DIR, 'dataset_entrenamiento')

MODELOS_DIR = os.path.join(BASE_DIR, 'modelos')

JSON_INFO_DIR = os.path.join(BASE_DIR, 'json')

PARTIDAS_DIR = os.path.join(BASE_DIR, 'partidas')

LOGS_DIR = os.path.join(BASE_DIR, 'modelos', 'logs')