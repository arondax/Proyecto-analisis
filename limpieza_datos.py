import pandas as pd
from sklearn.preprocessing import OrdinalEncoder, OneHotEncoder
from sklearn.compose import ColumnTransformer
import matplotlib.pyplot as plt
import numpy as np
import ast
import json
import string
"""
Archivo que realiza unalimpieza inicial de los datos.
1. Elimina entradas duplciadas en base al id de la partida
2. Elimina las entradas que no sean de partidas competitivas
3. Crea la columna es_main y la define en 0-1 en base al personaje más jugado en grupos de 10 partidas
4. Crea las columnas n_amigos y n_desconocidos
5. Borra la columna de id, jugador, modo, composicion y rol
"""


def limpieza_jugador(nombre_jugador):
    ruta_csv=f"./datasets/dataset_{nombre_jugador}.csv"
    
    df = pd.read_csv(ruta_csv)
    
    print("Dimensiones: ", df.shape)
    print("-------------------------")
    print(df.info())
    
    #Borramos primero duplicados antes de borrar la columna de id de la partida
    df= quitar_duplicados(df)
    print("-------------------------")
    print(df.info())
    
    #Borramos las entradas donde el modo no sea competitivo
    print(df['modo'].unique())
    df = borrar_no_competitivo(df)
    print(df['modo'].unique())
    
    #Obtenemos el main
    df= obtener_main(df)
    
    print("-------------------------")
    print(df.info())
    
    ruta_json = "amigos_recurrentes.json"
    df= obtener_amigos(df, ruta_json)
    print("-------------------------")
    print(df.info())
    
    #Con los datos limpios borramos las columnas id_partida, jugador, modo
    columnas_a_eliminar = ['id_partida', 'jugador', 'modo', 'composición', 'rol']

    for col in columnas_a_eliminar:
        if col in df.columns:
            df = df.drop(columns=[col])
            print(f"Columna '{col}' borrada.")
        else:
            print(f"La columna '{col}' no existía o ya fue borrada.")   
    
    print("-------------------------")
    print(df.info())
    pd.set_option('display.max_columns', None)
    print(df.head(5))
    return None

"""
Elimina duplicados en base al id.
"""
def quitar_duplicados(df):
    print("Numero de duplicados: ", df.duplicated().sum())
    #Borramos duplciados en base al id de la partida. 
    df_limpio = df.drop_duplicates(subset=[df.columns[0]])
    
    return df_limpio
"""_summary_
Obtiene el personaje mas jugado en grupos de 10 partidas, y lo asigna a la columna es_main,
como valor binario.
"""
def obtener_main(df):
    #suponemos que el orden es cornológico
    df['bloque_10'] = np.arange(len(df)) // 10
    
    #Personaje mas usado por bloque:
    main_bloque = df.groupby('bloque_10')['personaje'].apply(
        lambda x: x.value_counts().idxmax()
    )
    #Resultado y mapeo
    df['personaje_main_del_bloque'] = df['bloque_10'].map(main_bloque)
    
    #Añadimos a la columna binaria
    df['es_main'] = (df['personaje'].str.strip().str.capitalize() == df['personaje_main_del_bloque'].str.strip().str.capitalize()).astype(int)
    
    df.drop(columns=['bloque_10', 'personaje_main_del_bloque', 'personaje'], inplace=True)
    
    return df
"""_summary_
La función revisa el json de los amigos y busca aquellos individuos con los que hayas jugado mas de 3 veces
y luego los compara con los compañeros para sacer el numero de amigos y el numero de desconocidos
"""
def obtener_amigos(df, ruta_json):
    #abrimos el json de amigos recurrentes
    with open(ruta_json, 'r') as f:
            datos = json.load(f)
    
    amigos_json = set()
    for jugador in datos.get("jugadores"):
        nombre= jugador.get("nombre")   
        amigos_json.add(nombre) 
        
    #Revisamos si el contenido de esta columna es de tipo str
    if isinstance(df['compañeros'].iloc[0], str):
        df['compañeros'] = df['compañeros'].apply(ast.literal_eval)
    
    #Contamos apariciones de cada jugador 
    conteo= df['compañeros'].explode().value_counts()
    amigos_frecuentes = set (conteo[conteo > 3].index)
    
    set_total_amigos = amigos_json.union(amigos_frecuentes)
    def calcular_cantidad(lista_partida):
        #Convertimos los jugadores de la partida en un set
        jugadores_partida = set(lista_partida)
        #Hacemos una interseccion para comparar los nombres
        amigos_detectados = jugadores_partida & set_total_amigos
    
        return len(amigos_detectados)
    
    df['num_amigos']= df['compañeros'].apply(calcular_cantidad)
    df=df.drop(columns = ['compañeros'])
    df['desconocidos']= 4 - df['num_amigos']
    return df



"""_summary_
Filtra por las columnas que tienen el valor competitivo
"""
def borrar_no_competitivo(df):
    df_limpio= df[df['modo'].str.contains('Competitive', case=False)] #reforzamos que lea competitive independientemente si es mayusculas o no
    return df_limpio


prueba = limpieza_jugador("angelutrix")
