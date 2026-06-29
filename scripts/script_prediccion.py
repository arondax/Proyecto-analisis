import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline import predictor, limpieza_datos
from pipeline.modelos import cargar_modelo

nombre = "rondax"
tag= "EUW"
mapa = "Ascent"
es_main = 1.0
num_amigos = 2

df = limpieza_datos.limpieza_jugador(nombre)

modelo = cargar_modelo("randomforest")
preprocessor = cargar_modelo("preprocessor")
scaler = cargar_modelo("scaler")
nombre_columnas = cargar_modelo("feature_names")

resultado = predictor.predecir_jugador(
    modelo=modelo,
    preprocessor=preprocessor,
    scaler=scaler,
    nombre_columnas=nombre_columnas,
    df=df,
    mapa=mapa,
    es_main=es_main,
    num_amigos=num_amigos,
    nombre_jugador=nombre
)

print(resultado)