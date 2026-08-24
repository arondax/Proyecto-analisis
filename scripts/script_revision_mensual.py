import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pipeline.pool_entrenamiento as pool_entrenamiento
from dotenv import load_dotenv #para proteger la clave api


# Carga las variables del archivo .env en el sistema
load_dotenv()

# Accede a la API Key de forma segura
api_key = os.getenv("VALORANT_API_KEY")

if not api_key:
    raise ValueError(
        "¡Error! No se encontró la VALORANT_API_KEY. Revisa tu archivo .env"
    )

print(f"API Key cargada correctamente: {api_key[:9]}...")

pool_entrenamiento.revisar_inactivos_mensual(api_key)