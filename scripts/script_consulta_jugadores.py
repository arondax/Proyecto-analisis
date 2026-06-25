import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pipeline.entrenamiento as entrenamiento
import pipeline.api as api
import pipeline.procesador as procesador
import pipeline.limpieza_datos as limpieza_datos
from dotenv import load_dotenv #para proteger la clave api


load_dotenv()

# Accede a la API Key de forma segura
api_key = os.getenv("VALORANT_API_KEY")

jugador="mamipito"
tag="4860"
region="eu"

api.getData(jugador, tag, region, api_key)

df= procesador.extraccion_datos(jugador, tag)

print (df.head())