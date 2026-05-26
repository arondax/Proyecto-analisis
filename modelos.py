import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestRegressor
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.metrics import (accuracy_score, precision_score, 
                             recall_score, f1_score, confusion_matrix,
                             ConfusionMatrixDisplay)

def lectura_csv(nombre_jugador):
    ruta_csv=f"./dataset_ingest/dataset_ingest_{nombre_jugador}.csv"
    df= pd.read_csv(ruta_csv)
    return df
#TODO Añadir validación cruzada tambión si quiero quitar el train_test, lo que se va a hacer es hacer un datset grupal y entrenar el modelo.
def entrenamiento(df):
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
       
       print(f"\n{'='*40}")
       print(f"  {nombre}")
       print(f"{'='*40}")
       for i, col in enumerate(['rondas_ganadas', 'rondas_perdidas']):
            mae  = mean_absolute_error(y_test.iloc[:, i], y_pred[:, i])
            rmse = np.sqrt(mean_squared_error(y_test.iloc[:, i], y_pred[:, i]))
            r2   = r2_score(y_test.iloc[:, i], y_pred[:, i])
            print(f"  [{col}] MAE: {mae:.2f} | RMSE: {rmse:.2f} | R²: {r2:.4f}")
    return None