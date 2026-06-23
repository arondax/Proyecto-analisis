import pandas as pd
import joblib
import entrenamiento
import pipeline.api as api
import pipeline.procesador as procesador
import pipeline.limpieza_datos as limpieza_datos
import json
import pipeline.predictor as predictor
import os

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional

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

DIST_DIR = os.path.join(ROOT_DIR, "dist")

if os.path.exists(DIST_DIR):
    app.mount("/assets", StaticFiles(directory=os.path.join(DIST_DIR, "assets")), name="assets")


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
        except ValueError as e:
            print(f" ! Error crítico: {e}")
            raise HTTPException(status_code=404, detail=f"Jugador '{nombre}' no encontrado.")
    return pd.read_csv(ruta_jugador)


#Endpoints


@app.get("/app")
def frontend():
    return FileResponse(os.path.join(DIST_DIR, "index.html"))

@app.get("/")
def root():
    return RedirectResponse(url="/app")

 
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
    resultado_api = api.getData(request.nombre, request.tag, request.region, api_key)
    if not resultado_api:
        raise HTTPException(status_code=404, detail="No se encontraron datos del jugador")

    df_raw = procesador.extraccion_datos(request.nombre, request.tag)
    if df_raw is None or df_raw.empty:
        raise HTTPException(status_code=422, detail=f"El jugador {request.nombre} no tiene partidas válidas")

    df = limpieza_datos.limpieza_jugador(request.nombre)
    if df is None or df.empty:
        raise HTTPException(status_code=422, detail="No hay partidas competitivas para este jugador")

    modelo = cargar_modelo(request.modelo)
    desconocidos = 5 - request.num_amigos

 
    resultado = predictor.predecir_jugador(
    modelo, df, request.mapa,
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


