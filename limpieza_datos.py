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
    print("Cabecera: \n", df.columns.tolist())
    
    return None

prueba = limpieza_jugador("angelutrix")