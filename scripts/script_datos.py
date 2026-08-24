import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pipeline.entrenamiento as entrenamiento
import pipeline.api as api
import pipeline.procesador as procesador
import pipeline.limpieza_datos as limpieza_datos
import pipeline.candidatos as candidatos
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

# Ya puedes usar tu api_key para las peticiones REST
print(f"API Key cargada correctamente: {api_key[:9]}...")

check, datos= entrenamiento.obtencion_lista()
if check:
    print("Datos obtenidos")
    check = entrenamiento.procesado_jugadores(datos, api_key)
    if check:
            print("Datos procesados")
            # Auto-discovery: se evalúa UNA vez al final de la ingesta, no por jugador.
            # Mecanismo A: candidato -> amigo recurrente (sin coste de API)
            candidatos.evaluar_promocion_amigos()
            candidatos.guardar_partidas_vistas()
            # Mecanismo B: muestreo 10-20% sobre la última partida -> jugador de entrenamiento
            pool_entrenamiento.procesar_muestreo()