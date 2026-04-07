import pandas as pd
from sklearn.preprocessing import OrdinalEncoder, OneHotEncoder
from sklearn.compose import ColumnTransformer
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns



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
    return None

"""
The function delete the duplicate row based only in the match id.
"""
def quitar_duplicados(df):
    print("Numero de duplicados: ", df.duplicated().sum())
    #Borramos duplciados en base al id de la partida. 
    df_limpio = df.drop_duplicates(subset=[df.columns[0]])
    
    return df_limpio

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
    df['es_main'] = (df['personaje'] == df['personaje_main_del_bloque']).astype(int)
    
    df.drop(columns=['bloque_10', 'personaje_main_del_bloque', 'personaje'], inplace=True)
    
    return df

def borrar_no_competitivo(df):
    df_limpio= df[df['modo'].str.contains('Competitive')]
    return df_limpio


prueba = limpieza_jugador("angelutrix")
