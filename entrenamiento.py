#Imports
import json ,api, procesador, limpieza_datos, glob, os, modelos
import pandas as pd
from datetime import datetime

#Clase
def obtencion_lista():
    """_summary_
    La función va a recorrer toda la lista (jugadores para entrenamiento) y creará sus datasets. 
    Returns:
        _type_: _description_ devuelve un valor booleano para indicar si la obtención de los datos se ha hecho de manera satisfactoria
    """
    #Leemos el json de con los datos de los jugadores:
    try:                                                            
        with open(f'./jugadores_entrenamiento.json','r', encoding='utf-8') as archivo:
            datos = json.load(archivo)
    except FileNotFoundError:
        print(f"No se encontró el archivo jugadores_entrenamiento.json")
    
    return True, datos

def procesado_jugadores(datos, api_key):
    """_summary_

    Args:
        datos (_type_): _description_

    Returns:
        _type_: _description_
    """
#Recorremos la lista de amigos, y aplicamos para crear dataset y csv
    nombre_jugador =""
    tag=""
    for jugador in datos.get("jugadores"):
        nombre_jugador= jugador.get("nombre")
        tag= jugador.get("tag")
        
        resultado= api.getData(nombre_jugador, tag, "eu", api_key)
        if resultado:
            print(f"Datos optenidos de: ", nombre_jugador,"#",tag)
            print("Procesado de la partida")
            procesador.extraccion_datos(nombre_jugador, tag)
            df = limpieza_datos.limpieza_jugador(nombre_jugador)
            limpieza_datos.guardar_dataset(nombre_jugador, df)
            print("DATOS LIMPIOS Y PREPARADOS PARA INGESTA")
    
    return True

def entrenar_modelo_regression():
    """_summary_

    Returns:
        _type_: _description_
    """
    dia=datetime.today()
    dia_texto= dia.strftime('%Y%m%d')
    identificador = (f'entrenamiento_{dia_texto}')

    direccion_archivo=f"dataset_ingest/dataset_ingest_{identificador}.csv"
    existe_archivo= os.path.exists(direccion_archivo)
    
    if not existe_archivo:
        ruta_csv=f'./dataset_ingest/'
        patron = os.path.join(ruta_csv, '*.csv')
        archivos_csv = glob.glob(patron)
        df_unido = pd.concat((pd.read_csv(f) for f in archivos_csv), ignore_index=True)
     
        if df_unido.to_csv(f'dataset_ingest/dataset_ingest_{identificador}.csv', index=False):
            print("CSV general creado")
    
    
    #Leemos el CSV
    df=modelos.lectura_csv(identificador)
    print("======INFO DATASET=======")
    print(df.info())
    print("=========================")
    print(df.shape)
    print("=========================")
    print(df.describe())
    print("=========================")
    
    modelos.entrenamiento_regresion(df, identificador)
        
    
    return True, 



