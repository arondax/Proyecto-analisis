import api, procesador, entrenamiento, limpieza_datos, modelos
import prediccion
from dotenv import load_dotenv #para proteger la clave api
import os

# Carga las variables del archivo .env en el sistema
load_dotenv()

# Accede a la API Key de forma segura
api_key = os.getenv("VALORANT_API_KEY")

if not api_key:
    raise ValueError(
        "¡Error! No se encontró la VALORANT_API_KEY. Revisa tu archivo .env"
    )

# Ya puedes usar tu api_key para las peticiones REST
print(f"API Key cargada correctamente: {api_key[:9]}...")

check, datos= entrenamiento.obtencion_lista()
if check:
    print("Datos obtenidos")
    check = entrenamiento.procesado_jugadores(datos, api_key)
    if check:
            print("Datos procesados")