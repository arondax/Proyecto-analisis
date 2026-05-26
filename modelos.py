import pandas as pd
import numpy as np
import unicodedata
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from sklearn.ensemble import RandomForestRegressor

#FUNCIONES GENERICAS
def lectura_csv(identificador):
    """_summary_

    Args:
        identificador (_type_): _description_

    Returns:
        _type_: _description_
    """
    ruta_csv=f"./dataset_ingest/dataset_ingest_{identificador}.csv"
    df= pd.read_csv(ruta_csv)
    return df

def guardar_modelo (modelo, nombre:str, ruta:str='./modelos/'):
    """_summary_

    Args:
        modelo (_type_): _description_
        nombre (str): _description_
        ruta (str, optional): _description_. Defaults to './modelos/'.
    """
    os.makedirs(ruta, exist_ok=True)
    ruta_completa = os.path.join(ruta, f'{nombre}.pkl')
    joblib.dump(modelo, ruta_completa)
    print(f"Modelo guardado en {ruta_completa}")
    
def cargar_modelo(nombre: str, ruta: str = './modelos/'):
    """_summary_

    Args:
        nombre (str): _description_
        ruta (str, optional): _description_. Defaults to './modelos/'.

    Raises:
        FileNotFoundError: _description_

    Returns:
        _type_: _description_
    """
    ruta_completa = os.path.join(ruta, f'{nombre}.pkl')
    if not os.path.exists(ruta_completa):
        raise FileNotFoundError(f"No existe el modelo: {ruta_completa}")
    return joblib.load(ruta_completa)


#FUNCIONES REGRESION
#TODO Añadir validación cruzada tambión si quiero quitar el train_test, lo que se va a hacer es hacer un datset grupal y entrenar el modelo.

def entrenamiento_regresion(df):
    """_summary_

    Args:
        df (_type_): _description_

    Returns:
        _type_: _description_
    """
    df= df.copy()
    y = df[['rondas_ganadas', 'rondas_perdidas']] 
    X= df.drop(columns=['id_partida', 'rondas_ganadas','rondas_perdidas'])
    x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    
    algoritmos = {
    "Regresión Lineal": LinearRegression(),
    "Árbol de Decisión": DecisionTreeRegressor(random_state=42, max_depth=4),
    "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42, max_depth=4)
    }

    for nombre, modelo  in algoritmos.items():
       modelo.fit(x_train, y_train)
       y_pred = modelo.predict(x_test) 
       #Limpiamos los nombres
       limpiar = lambda texto: "".join(c for c in unicodedata.normalize('NFKD', texto) if unicodedata.category(c) != 'Mn').replace(" ", "")
       guardar_modelo(modelo, limpiar(nombre).lower().replace(' ', '_'))
       
       print(f"\n{'='*40}")
       print(f"  {nombre}")
       print(f"{'='*40}")
       for i, col in enumerate(['rondas_ganadas', 'rondas_perdidas']):
            mae  = mean_absolute_error(y_test.iloc[:, i], y_pred[:, i])
            rmse = np.sqrt(mean_squared_error(y_test.iloc[:, i], y_pred[:, i]))
            r2   = r2_score(y_test.iloc[:, i], y_pred[:, i])
            print(f"  [{col}] MAE: {mae:.2f} | RMSE: {rmse:.2f} | R²: {r2:.4f}")
    return None
