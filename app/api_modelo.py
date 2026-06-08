from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
import joblib
import prediccion
import api
import procesador
import limpieza_datos
import os, json
from fastapi.middleware.cors import CORSMiddleware




load_dotenv()
api_key = os.getenv("VALORANT_API_KEY")
if not api_key:
    raise ValueError("¡Error! No se encontró la VALORANT_API_KEY.")

modelo = joblib.load('modelos/randomforest.pkl')

app = FastAPI(title="Valorant Predicter")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción puedes restringirlo a tu dominio
    allow_methods=["POST"],
    allow_headers=["*"],
)
class DatosEntrada(BaseModel):
    nombre: str
    tag: str
    region: str
    mapa: str
    es_main: bool
    num_amigos: int

app.mount("/static", StaticFiles(directory="static"), name="static")
@app.get("/app")

def frontend():
    """Funcion que define el frontend

    Returns:
        _type_: _description_ Devuelve el archivo HTML del frontend para que el usuario pueda interactuar con la aplicación.
    """
    return FileResponse("static/valorant_predictor_frontend.html")

@app.get("/")
def health_check():
    """_summary_ Revisa el estado de la web

    Returns:
        _type_: _description_ Devuelve un mensaje de estado para confirmar que la API está funcionando correctamente.
    """
    return {"status": "ok"}

@app.get("/mapas")
def get_mapas():
    """_summary_ Devuelve la lista de mapas disponibles para la predicción, obtenida desde un archivo de configuración JSON.
    Returns:
        _type_: _description_ Un diccionario con la lista de mapas disponibles para la predicción, que el frontend puede usar para mostrar opciones al usuario.
    """
    with open("./json/info_valorant.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    return {"mapas": config["mapas"]["ranked"]}




@app.post("/predecir")
def predecir(datos: DatosEntrada):
    """ _summary_ Realiza una predicción sobre el resultado de una partida de Valorant.

    Args:
        datos (DatosEntrada): _description_ Un objeto que contiene los datos de entrada necesarios para realizar la predicción, incluyendo el nombre del jugador, su tag, región, mapa seleccionado, si es main o no, y el número de amigos en el equipo.

    Raises:
        HTTPException: _description_ HTTPException con código 404 si no se encuentran datos del jugador, o con código 422 si no hay partidas competitivas para ese jugador. Estas excepciones se lanzan para informar al cliente sobre problemas específicos relacionados con los datos de entrada o la disponibilidad de información necesaria para realizar la predicción.
        HTTPException: _description_ HTTPException con código 500 para cualquier otro error inesperado durante el proceso de predicción, proporcionando un mensaje de error genérico para indicar que ocurrió un problema interno en el servidor.

    Returns:
        _type_: _description_ Un diccionario con los resultados de la predicción, incluyendo las rondas ganadas y perdidas predichas, así como el resultado final (Victoria o Derrota). Este diccionario se devuelve al cliente para que pueda mostrar los resultados de la predicción al usuario.
    """
    # Pipeline completo igual que en main.py
    resultado_api = api.getData(datos.nombre, datos.tag, datos.region, api_key)
    if not resultado_api:
        raise HTTPException(status_code=404, detail="No se encontraron datos del jugador")
    
    df_raw = procesador.extraccion_datos(datos.nombre, datos.tag)

    if df_raw is None or df_raw.empty:
        raise HTTPException(
            status_code=422,
            detail=f"El jugador {datos.nombre} no tiene partidas válidas (solo Deathmatch/Skirmish)"
        )

    df = limpieza_datos.limpieza_jugador(datos.nombre)
    
    if df is None or df.empty:
        raise HTTPException(status_code=422, detail="No hay partidas competitivas para este jugador")
    
    desconocidos = 5 - datos.num_amigos
    resultado = prediccion.predecir_jugador(
        modelo, df, datos.mapa,
        float(datos.es_main), datos.num_amigos,
        desconocidos, datos.nombre
    )
    return resultado


