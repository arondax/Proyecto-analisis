import pandas as pd
import numpy as np
import unicodedata, os, joblib
import config
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

#FUNCIONES GENERICAS
def lectura_csv(identificador):
    """_summary_ Función que se encarga de leer un archivo CSV específico del dataset de entrenamiento, utilizando un identificador para localizar el archivo correcto. El identificador se utiliza para construir la ruta del archivo CSV, que se encuentra en la carpeta de entrenamiento, y luego se carga el contenido del CSV en un DataFrame de pandas, que se devuelve para su uso en el proceso de entrenamiento del modelo.

    Args:
        identificador (_type_): _description_ Un identificador que se utiliza para localizar el archivo CSV específico del dataset de entrenamiento. Este identificador se incluye en el nombre del archivo CSV, que se encuentra en la carpeta de entrenamiento, y permite cargar el contenido del CSV en un DataFrame de pandas para su uso en el proceso de entrenamiento del modelo.

    Returns:
        _type_: _description_ Devuelve un DataFrame de pandas que contiene los datos cargados desde el archivo CSV específico del dataset de entrenamiento, identificado por el parámetro de entrada. Este DataFrame se utiliza posteriormente en el proceso de entrenamiento del modelo de machine learning.
    """
    ruta_csv= os.path.join(config.DATASET_ENTRENAMIENTO_DIR , f"dataset_ingest_entrenamiento_{identificador}.csv")
    df= pd.read_csv(ruta_csv)
    return df

def guardar_modelo (modelo, nombre:str, ruta:str=os.path.join(config.MODELOS_DIR)):
    """_summary_ Función que se encarga de guardar un modelo de machine learning entrenado en un archivo específico dentro de una carpeta designada para modelos. La función utiliza la biblioteca joblib para serializar el modelo y guardarlo en un archivo con un nombre basado en el parámetro de entrada, dentro de la ruta especificada. Si la carpeta no existe, se crea automáticamente antes de guardar el modelo.

    Args:
        modelo (_type_): _description_ El modelo de machine learning entrenado que se desea guardar. Este modelo se serializa utilizando joblib y se guarda en un archivo específico dentro de la carpeta designada para modelos, con un nombre basado en el parámetro de entrada.
        nombre (str): _description_ El nombre que se utilizará para el archivo donde se guardará el modelo. Este nombre se incluye en el nombre del archivo, que se encuentra dentro de la carpeta designada para modelos, y permite identificar fácilmente el modelo guardado.
        ruta (str, optional): _description_. Defaults to './modelos/'. La ruta donde se guardará el modelo. Si no se especifica, se utiliza la ruta predeterminada './modelos/', que es la carpeta designada para almacenar los modelos de machine learning entrenados.
    """
    os.makedirs(ruta, exist_ok=True)
    ruta_completa = os.path.join(ruta, f'{nombre}.pkl')
    joblib.dump(modelo, ruta_completa)
    print(f"Modelo guardado en {ruta_completa}")
    
def cargar_modelo(nombre: str, ruta: str = os.path.join(config.MODELOS_DIR)):
    """_summary_ Función que se encarga de cargar un modelo de machine learning previamente guardado desde un archivo específico dentro de una carpeta designada para modelos. La función utiliza la biblioteca joblib para deserializar el modelo desde el archivo, utilizando el nombre del modelo y la ruta especificada para localizar el archivo correcto. Si el archivo no existe, se lanza un error indicando que no se encontró el modelo.

    Args:
        nombre (str): _description_ El nombre del modelo que se desea cargar. Este nombre se utiliza para construir el nombre del archivo desde el cual se cargará el modelo, que se encuentra dentro de la carpeta designada para modelos, y permite identificar fácilmente el modelo que se desea cargar.
        ruta (str, optional): _description_. Defaults to './modelos/'. La ruta donde se encuentra el modelo que se desea cargar. Si no se especifica, se utiliza la ruta predeterminada './modelos/', que es la carpeta designada para almacenar los modelos de machine learning entrenados. La función busca el archivo del modelo en esta ruta utilizando el nombre proporcionado, y si lo encuentra, lo carga y devuelve el modelo deserializado. Si el archivo no existe, se lanza un error indicando que no se encontró el modelo.

    Raises:
        FileNotFoundError: _description_ Si el archivo del modelo que se desea cargar no existe en la ruta especificada, se lanza un error indicando que no se encontró el modelo. Este error se produce cuando la función intenta localizar el archivo del modelo utilizando el nombre proporcionado y no lo encuentra en la carpeta designada para modelos, lo que puede deberse a que el modelo no ha sido guardado previamente o a un error en el nombre o la ruta proporcionados.

    Returns:
        _type_: _description_ Devuelve el modelo de machine learning deserializado que se ha cargado desde el archivo específico dentro de la carpeta designada para modelos, utilizando el nombre del modelo y la ruta especificada para localizar el archivo correcto. Este modelo se puede utilizar posteriormente para realizar predicciones o evaluaciones en nuevos datos.
    """
    ruta_completa = os.path.join(ruta, f'{nombre}.pkl')
    if not os.path.exists(ruta_completa):
        raise FileNotFoundError(f"No existe el modelo: {ruta_completa}")
    return joblib.load(ruta_completa)


#FUNCIONES REGRESION
#TODO Añadir validación cruzada tambión si quiero quitar el train_test, lo que se va a hacer es hacer un datset grupal y entrenar el modelo.

def entrenamiento_regresion(df, identificador):
    """_summary_ Función que se encarga de entrenar un modelo de regresión utilizando un DataFrame de entrenamiento específico, y luego evalúa el rendimiento del modelo utilizando métricas como MAE, RMSE y R². La función divide el DataFrame en conjuntos de entrenamiento y prueba, entrena varios modelos de regresión (Regresión Lineal, Árbol de Decisión y Random Forest), realiza predicciones en el conjunto de prueba, y luego calcula y guarda las métricas de evaluación para cada modelo en un archivo de log específico para el entrenamiento.

    Args:
        df (_type_): _description_ El DataFrame de entrenamiento que contiene los datos que se utilizarán para entrenar el modelo de regresión. Este DataFrame debe estar limpio y preparado, con las características relevantes para el entrenamiento del modelo, y debe incluir las columnas de salida (rondas_ganadas y rondas_perdidas) que se utilizarán como variables objetivo para la regresión.

    Returns:
        _type_: _description_ Devuelve None después de completar el proceso de entrenamiento y evaluación del modelo de regresión. La función no devuelve un valor específico, pero guarda los modelos entrenados en archivos específicos dentro de la carpeta designada para modelos, y también guarda las métricas de evaluación en un archivo de log específico para el entrenamiento, utilizando el identificador proporcionado para nombrar los archivos correspondientes.
    """
    df= df.copy()
    
    #df_sorted = df.sort_values('fecha', na_position='first')  # los sin fecha van primero (datos viejos)

    # Aquí haces el split
    #split = int(len(df_sorted) * 0.8)
    #df_train = df_sorted.iloc[:split]
    #df_test  = df_sorted.iloc[split:]

    # Ahora sí dropeas fecha antes de pasarlo al modelo
    #columnas_drop = ['jugador', 'modo', 'id_partida', 'fecha', 'fecha_legible']
    #df_train = df_train.drop(columns=columnas_drop, errors='ignore')
    #df_test  = df_test.drop(columns=columnas_drop, errors='ignore')
        
    scaler= StandardScaler()
    y = df[['rondas_ganadas', 'rondas_perdidas']] 
    X= df.drop(columns=['id_partida', 'rondas_ganadas','rondas_perdidas','racha'])

    x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    x_train = scaler.fit_transform(x_train)
    x_test = scaler.transform(x_test)
    algoritmos = {
    "Regresión Lineal": LinearRegression(),
    "Árbol de Decisión": DecisionTreeRegressor(random_state=42, max_depth=4),
    "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42, max_depth=4)
    }
    
    archivo=crear_log(identificador)
    tamanyo= len(df)
    archivo.write(f"Dataset: {identificador} | Tamaño: {tamanyo}\n")
    for nombre, modelo  in algoritmos.items():
        
    
       modelo.fit(x_train, y_train)
       y_pred = modelo.predict(x_test) 
       #Limpiamos los nombres
       limpiar = lambda texto: "".join(c for c in unicodedata.normalize('NFKD', texto) if unicodedata.category(c) != 'Mn').replace(" ", "")
       guardar_modelo(modelo, limpiar(nombre).lower().replace(' ', '_'))
       
       print(f"\n{'='*40}")
       archivo.write(f"\n{'='*40}\n")
       print(f"  {nombre}")
       archivo.write(f"  {nombre}\n")
       print(f"{'='*40}")
       archivo.write(f"{'='*40}\n")
       for i, col in enumerate(['rondas_ganadas', 'rondas_perdidas']):
            mae  = mean_absolute_error(y_test.iloc[:, i], y_pred[:, i])
            archivo.write(f"  [{col}] MAE: {mae:.2f}\n")
            rmse = np.sqrt(mean_squared_error(y_test.iloc[:, i], y_pred[:, i]))
            archivo.write(f"  [{col}] RMSE: {rmse:.2f}\n")
            r2   = r2_score(y_test.iloc[:, i], y_pred[:, i])
            archivo.write(f"  [{col}] R²: {r2:.4f}\n")
            print(f"  [{col}] MAE: {mae:.2f} | RMSE: {rmse:.2f} | R²: {r2:.4f}")
            
            scores = cross_val_score(modelo, X, y, cv=5, scoring='r2')
            archivo.write(f"  CV R² (5-fold): {scores.mean():.4f} ± {scores.std():.4f}\n")
            archivo.write(f"Muestras totales: {len(df)} | Train: {len(x_train)} | Test: {len(x_test)}\n")
            archivo.write(f"Split: random (sin fecha disponible)\n")
            
            archivo.flush()  # Asegura que se escriba en el archivo después de cada modelo
    return None

def crear_log (identificador):
    """_summary_ Función que se encarga de crear un archivo de log específico para el entrenamiento del modelo de regresión, utilizando un identificador para nombrar el archivo. La función verifica si el archivo de log ya existe en la carpeta designada para logs, y si no existe, lo crea y escribe un encabezado con el identificador. Si el archivo ya existe, simplemente lo abre en modo de adición para agregar nuevas entradas al log. El archivo de log se utiliza para guardar las métricas de evaluación del modelo de regresión durante el proceso de entrenamiento.

    Args:
        identificador (_type_): _description_ Un identificador que se utiliza para nombrar el archivo de log específico para el entrenamiento del modelo de regresión. Este identificador se incluye en el nombre del archivo de log, que se encuentra dentro de la carpeta designada para logs, y permite identificar fácilmente el log correspondiente al entrenamiento del modelo. La función verifica si el archivo de log ya existe, y si no existe, lo crea y escribe un encabezado con el identificador. Si el archivo ya existe, simplemente lo abre en modo de adición para agregar nuevas entradas al log durante el proceso de entrenamiento.

    Returns:
        _type_: _description_ Devuelve un objeto de archivo abierto en modo de escritura o adición, que se utiliza para escribir las métricas de evaluación del modelo de regresión durante el proceso de entrenamiento. Este objeto de archivo se puede utilizar posteriormente para escribir nuevas entradas al log a medida que se evalúan los modelos durante el entrenamiento, y se asegura de que las métricas se guarden correctamente en el archivo de log correspondiente al entrenamiento del modelo.
    """
    
    ruta_logs = os.path.join(config.MODELOS_DIR, 'logs')
    os.makedirs(ruta_logs, exist_ok=True)
    
    ruta_logs_identificdos = os.path.join(ruta_logs, f'log_{identificador}.txt')
    archivo_existe = os.path.exists(ruta_logs_identificdos)
    
    archivo = open(ruta_logs_identificdos, 'a' if archivo_existe else 'w')
    
    if not archivo_existe:
        archivo.write(f"Log de entrenamiento - {identificador}\n")
        archivo.write(f"{'='*50}\n")
    return archivo
