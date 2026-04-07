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
    
    
    
    return None

"""
The function delete the duplicate row based only in the match id.
"""
def quitar_duplicados(df):
    print("Numero de duplicados: ", df.duplicated().sum())
    #Borramos duplciados en base al id de la partida. 
    df_limpio = df.drop_duplicates(subset=[df.columns[0]])
    
    return df_limpio





prueba = limpieza_jugador("angelutrix")
