import json

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import pandas as pd
import joblib
import os
import entrenamiento
# Carga las variables del archivo .env en el sistema
load_dotenv()

# Accede a la API Key de forma segura
api_key = os.getenv("VALORANT_API_KEY")

if not api_key:
    raise ValueError(
        "¡Error! No se encontró la VALORANT_API_KEY. Revisa tu archivo .env"
    )

app = FastAPI(title="Valorant Predicter", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, restringe esto a tu dominio específico
    allow_methods=['*'],
    allow_headers=['*'],
    allow_credentials=False,
)

#configuramos las rutas

BASE_DIR= os.path.dirname(os.path.abspath(__file__))

ROOT_DIR = os.path.dirname(BASE_DIR)

JUGADORES_DIR = os.path.join(ROOT_DIR, 'dataset_ingest')

MODELOS_DIR = os.path.join(ROOT_DIR, 'modelos')

MAPAS_DIR = os.path.join(ROOT_DIR, 'json')

#Modelos Pydantic

class PrediccionRequest(BaseModel):
    nombre: str = Field(..., example="PlayerName")
    tag: str = Field(..., example="1234")
    region: str = Field(..., example="NA")
    mapa: str = Field(..., example="Ascent")
    es_main: bool = Field(..., example=True)
    num_amigos: int = Field(..., example=5) 
    modelo: Optional[str] = Field("randomforest", description="Modelo a usar: randomforest, arboldeDecision, RegresionLineal")


class PrediccionResponse(BaseModel):
    nombre: str
    mapa: str
    rondas_ganadas: float
    rondas_perdidas: float
    resultado: str
    confianza: Optional[str] = None
    
    
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
    ruta_modelo = os.path.join(MODELOS_DIR, f"{modelo_nombre}.pkl")
    if not os.path.exists(ruta_modelo):
        raise HTTPException(status_code=400, detail=f"Modelo '{modelo_nombre}' no encontrado.")
    return joblib.load(ruta_modelo)

def cargar_mapas():
    
    with open(os.path.join(MAPAS_DIR, 'info_valorant.json'), 'r') as f:
        info = json.load(f)
        mapas = info['mapas']['ranked']
        
    return mapas

def cargar_df_jugador(nombre: str, tag:str, region: str) -> pd.DataFrame:
    ruta_jugador = os.path.join(JUGADORES_DIR, f"dataset_ingest_{nombre}.csv")
    if not os.path.exists(ruta_jugador):
        print("[DEBUG] No se encontró el CSV del jugador. Intentando extraer datos...")
        try:
            entrenamiento.procesado_jugador(nombre, tag, region, api_key)
        except FileNotFoundError:
            print(f" ! Error crítico: El archivo matches_{nombre}.json no pudo ser creado o descargado.")
            raise HTTPException(status_code=404, detail=f"Jugador '{nombre}' no encontrado. ruta: {ruta_jugador}, {MAPAS_DIR}, {MODELOS_DIR}")
    return pd.read_csv(ruta_jugador)

def construir_input(df: pd.DataFrame, mapa:str, es_main: float, num_amigos:int) ->pd.DataFrame:
    columnas_a_excluir = ["id_partida", "rondas_ganadas", "rondas_perdidas"]
    columnas_modelo = [col for col in df.columns if col not in columnas_a_excluir]
 
    columnas_numericas = ["kills", "asistencias", "muertes", "headshots", "acs", "fb", "fd"]
    columnas_mapa = [col for col in df.columns if col.startswith("mapa_")]
 
    ultima = df.iloc[-1]
    medias = df[columnas_numericas].mean()
 
    partida = {}
    partida["rango"]        = ultima["rango"]
    partida["subrango"]     = ultima["subrango"]
    partida["racha"]        = ultima["racha"]
    partida["es_main"]      = es_main
    partida["num_amigos"]   = float(num_amigos)
    partida["desconocidos"] = float(4 - num_amigos)
    partida.update(medias.to_dict())
 
    for col in columnas_mapa:
        partida[col] = 0.0
 
    mapa_col = f"mapa_{mapa}"
    if mapa_col not in columnas_mapa:
        raise HTTPException(
            status_code=400,
            detail=f"Mapa '{mapa}' no reconocido. Disponibles: {MAPAS}"
        )
    partida[mapa_col] = 1.0
 
    return pd.DataFrame([partida])[columnas_modelo]

#Endpoints

@app.get("/")
def root():
    return {"message": "Bienvenido al Valorant Predicter API. Usa el endpoint /predecir para obtener predicciones de tus partidas."}

@app.get("/jugadores")
def get_jugadores():
    """Devuelve la lista de jugadores disponibles."""
    return {"jugadores": [j["nombre"] for j in JUGADORES]}
 
 
@app.get("/mapas")
def get_mapas():
    """Devuelve el pool de mapas disponibles."""
    mapas= cargar_mapas()
    return {"mapas": mapas}
 
 
@app.get("/modelos")
def get_modelos():
    """Devuelve los modelos disponibles en /modelos/."""
    if not os.path.exists(MODELOS_DIR):
        return {"modelos": []}
    archivos = [f.replace(".pkl", "") for f in os.listdir(MODELOS_DIR) if f.endswith(".pkl")]
    return {"modelos": archivos}

@app.post("/predecir", response_model=PrediccionResponse)
def predecir(request: PrediccionRequest):
    """
    Realiza una predicción de rondas ganadas/perdidas para un jugador
    en un mapa determinado, usando su historial de partidas.
    """
    try:
        df     = cargar_df_jugador(request.nombre, request.tag, request.region)
    except HTTPException as e:
        raise e
    
    try:
        modelo = cargar_modelo(request.modelo)
    except HTTPException as e:
        raise e

    X      = construir_input(df, request.mapa, request.es_main, request.num_amigos)
 
    pred       = modelo.predict(X)[0]
    rondas_g   = round(float(pred[0]), 1)
    rondas_p   = round(float(pred[1]), 1)
    resultado  = "Victoria" if rondas_g > rondas_p else "Derrota"
 
    return PrediccionResponse(
        nombre          = request.nombre,
        mapa            = request.mapa,
        rondas_ganadas  = rondas_g,
        rondas_perdidas = rondas_p,
        resultado       = resultado,
    )