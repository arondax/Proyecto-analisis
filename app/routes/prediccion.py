# Clase ruta prediccion
import os

import joblib
import config
import pipeline.predictor as predictor
import pipeline.api as api
import pipeline.procesador as procesador
import pipeline.limpieza_datos as limpieza_datos
import pipeline.entrenamiento as entrenamiento
import pandas as pd


from app.schemas import PrediccionRequest, PrediccionResponse
from fastapi import APIRouter
from dotenv import load_dotenv
from fastapi import HTTPException



load_dotenv()
api_key = os.getenv("VALORANT_API_KEY")

router = APIRouter()

if not api_key:
    raise ValueError(
        "¡Error! No se encontró la VALORANT_API_KEY. Revisa tu archivo .env"
    )


#Helpers


def cargar_modelo(modelo_nombre: str):
    """_summary_ Carga el modelo de machine learning especificado por el usuario.

    Args:
        modelo_nombre (str): _description_ El nombre del modelo a cargar (ej. "randomforest", "arboldeDecision", "RegresionLineal").

    Raises:
        HTTPException: _description_  Si el modelo especificado no se encuentra en la carpeta de modelos, se lanza una excepción HTTP con un mensaje de error.

    Returns:
        _type_: _description_ Devuelve el modelo cargado desde el archivo correspondiente en la carpeta de modelos.
    """
    ruta_modelo = os.path.join(config.MODELOS_DIR, f"{modelo_nombre}.pkl")
    if not os.path.exists(ruta_modelo):
        raise HTTPException(status_code=400, detail=f"Modelo '{modelo_nombre}' no encontrado.")
    return joblib.load(ruta_modelo)

def cargar_artefactos():
    preprocessor = cargar_modelo('preprocessor')
    scaler = cargar_modelo('scaler')
    nombres_columnas = cargar_modelo('feature_names')
    return preprocessor, scaler, nombres_columnas

def cargar_df_jugador(nombre: str, tag:str, region: str) -> pd.DataFrame:
    ruta_jugador = os.path.join(config.DATASET_INGEST_DIR, f"dataset_ingest_{nombre}.csv")
    if not os.path.exists(ruta_jugador):
        print("[DEBUG] No se encontró el CSV del jugador. Intentando extraer datos...")
        try:
            entrenamiento.procesado_jugador(nombre, tag, region, api_key)
        except ValueError as e:
            print(f" ! Error crítico: {e}")
            raise HTTPException(status_code=404, detail=f"Jugador '{nombre}' no encontrado.")
    return pd.read_csv(ruta_jugador)

@router.post("/predecir", response_model=PrediccionResponse)
def predecir(request: PrediccionRequest):
    
    print(f"[PREDECIR] Iniciando para {request.nombre}#{request.tag}")
    resultado_api = api.getData(request.nombre.strip(), request.tag.strip(), request.region, api_key)
    print(f"[PREDECIR] resultado_api: {resultado_api is not None}")
    
    if not resultado_api:
        raise HTTPException(status_code=404, detail="No se encontraron datos del jugador")

    df_raw = procesador.extraccion_datos(request.nombre.strip(), request.tag.strip())
    print(f"[PREDECIR] df_raw shape: {df_raw.shape if df_raw is not None else None}")
    if df_raw is None or df_raw.empty:
        raise HTTPException(status_code=422, detail=f"El jugador {request.nombre} no tiene partidas válidas")

    df = limpieza_datos.limpieza_jugador(request.nombre.strip())

    if df is None or df.empty:
        # Fallback: usar el dataset de ingest existente
        ruta_ingest = os.path.join(config.DATASET_INGEST_DIR, f'dataset_ingest_{request.nombre.strip()}.csv')
        if os.path.exists(ruta_ingest):
            df = pd.read_csv(ruta_ingest)
            print(f"[PREDECIR] Usando dataset ingest existente para {request.nombre}")
        else:
            raise HTTPException(status_code=422, detail=f"No hay partidas válidas para {request.nombre}")

    modelo = cargar_modelo(request.modelo)
    preprocessor, scaler, nombres_columnas = cargar_artefactos()
    desconocidos = 5 - request.num_amigos

 
    resultado = predictor.predecir_jugador(
    modelo, preprocessor, scaler, nombres_columnas ,df, request.mapa,
    float(request.es_main), request.num_amigos,
    desconocidos, request.nombre
    )

    return PrediccionResponse(
        nombre=request.nombre,
        mapa=request.mapa,
        rondas_ganadas=resultado["rondas_ganadas"],
        rondas_perdidas=resultado["rondas_perdidas"],
        resultado=resultado["resultado"],
    )

