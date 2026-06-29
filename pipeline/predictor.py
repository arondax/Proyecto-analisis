import pandas as pd
import os
from datetime import datetime


def predecir_jugador(modelo, preprocessor, scaler, nombre_columnas, df, mapa, es_main, num_amigos, nombre_jugador):
    """_summary_ Función que se encarga de predecir el resultado de una partida para un jugador específico utilizando un modelo de machine learning entrenado. La función toma como entrada el modelo, un DataFrame con los datos históricos del jugador, el mapa en el que se va a jugar la partida, si el jugador es main o no, el número de amigos que jugarán la partida, el número de desconocidos que jugarán la partida, y el nombre del jugador. La función procesa estos datos para construir un nuevo DataFrame con las características necesarias para la predicción, asegurando que las columnas estén en el mismo orden que durante el entrenamiento del modelo. Luego, utiliza el modelo para predecir las rondas ganadas y perdidas, determina el resultado final (victoria o derrota), muestra la predicción en consola, y guarda la predicción en un archivo de texto específico para mantener un historial de predicciones realizadas.

    Args:
        modelo (_type_): _description_ El modelo de machine learning entrenado que se utilizará para realizar la predicción de la partida. Este modelo debe haber sido entrenado previamente con un dataset que incluya las características relevantes para la predicción, y debe estar cargado en memoria para ser utilizado en esta función. El modelo se utiliza para predecir las rondas ganadas y perdidas basándose en las características del jugador y la partida, y se espera que devuelva una predicción que se pueda interpretar para determinar el resultado de la partida (victoria o derrota).
        df (_type_): _description_ Un DataFrame que contiene los datos históricos del jugador, incluyendo las características relevantes para la predicción de la partida. Este DataFrame debe estar limpio y preparado, con las mismas columnas que se utilizaron durante el entrenamiento del modelo, y debe incluir las características necesarias para construir el nuevo DataFrame de entrada para la predicción. El DataFrame se utiliza para calcular las medias de las características numéricas del jugador, que se incluyen en el nuevo DataFrame de entrada para la predicción, junto con otras características como el mapa, si el jugador es main o no, el número de amigos y desconocidos.
        mapa (_type_): _description_ El mapa en el que se va a jugar la partida para la cual se desea realizar la predicción. Este valor se utiliza para activar la columna correspondiente al mapa en el nuevo DataFrame de entrada para la predicción, asegurando que el modelo tenga la información correcta sobre el mapa en el que se jugará la partida. El mapa debe ser uno de los mapas reconocidos por el modelo, y se espera que el DataFrame de entrada para la predicción tenga columnas específicas para cada mapa, con valores binarios (0 o 1) para indicar si el mapa es el actual o no.
        es_main (_type_): _description_ Un valor binario (0 o 1) que indica si el jugador es main o no. Este valor se incluye como una característica en el nuevo DataFrame de entrada para la predicción, y se utiliza por el modelo para tener en cuenta si el jugador es main o no al realizar la predicción de las rondas ganadas y perdidas. El valor de es_main puede influir en la predicción, ya que los jugadores main pueden tener un rendimiento diferente en las partidas en comparación con los jugadores que no son main.
        num_amigos (_type_): _description_ El número de amigos que jugarán la partida junto con el jugador para el cual se desea realizar la predicción. Este valor se incluye como una característica en el nuevo DataFrame de entrada para la predicción, y se utiliza por el modelo para tener en cuenta la influencia que puede tener jugar con amigos en el rendimiento del jugador durante la partida. El número de amigos puede afectar la dinámica de la partida y, por lo tanto, puede ser un factor relevante para la predicción de las rondas ganadas y perdidas.
        desconocidos (_type_): _description_ El número de desconocidos que jugarán la partida junto con el jugador para el cual se desea realizar la predicción. Este valor se incluye como una característica en el nuevo DataFrame de entrada para la predicción, y se utiliza por el modelo para tener en cuenta la influencia que puede tener jugar con desconocidos en el rendimiento del jugador durante la partida. El número de desconocidos puede afectar la dinámica de la partida y, por lo tanto, puede ser un factor relevante para la predicción de las rondas ganadas y perdidas.
        nombre_jugador (_type_): _description_ El nombre del jugador para el cual se desea realizar la predicción de la partida. Este valor se utiliza para mostrar la predicción en consola de manera personalizada, indicando el nombre del jugador junto con la información de la predicción, como el mapa, las rondas ganadas y perdidas predichas, y el resultado final (victoria o derrota). El nombre del jugador también se utiliza para guardar la predicción en un archivo de texto específico, permitiendo mantener un historial de predicciones realizadas para cada jugador.

    Raises:
        ValueError: _description_ Si el mapa proporcionado no es reconocido por el modelo, se lanza un error indicando que el mapa no es válido y mostrando los mapas disponibles. Este error se produce cuando la función intenta activar la columna correspondiente al mapa en el nuevo DataFrame de entrada para la predicción, pero no encuentra una columna que corresponda al mapa proporcionado, lo que puede deberse a un error en el nombre del mapa o a que el mapa no está incluido en las características utilizadas durante el entrenamiento del modelo. Es importante asegurarse de que el mapa proporcionado sea uno de los mapas reconocidos por el modelo para evitar este error y garantizar que la predicción se realice correctamente.

    Returns:
        _type_: _description_ Devuelve un diccionario con las rondas ganadas y perdidas predichas, así como el resultado final (victoria o derrota) de la partida para el jugador específico. El diccionario tiene la siguiente estructura:
    """


    # CREAR EL DATAFRAME ASEGURANDO EL ORDEN ORIGINAL
    X = construir_input(df, mapa, es_main, num_amigos)
    X = preprocessor.transform(X)
    X = pd.DataFrame(X, columns=nombre_columnas)
    X = scaler.transform(X)
    # 6. Hacer la predicción
    prediccion = modelo.predict(X)[0]
    rondas_g = prediccion[0]
    rondas_p = prediccion[1]
    resultado = "Victoria" if rondas_g > rondas_p else "Derrota"

    # Mostrar en consola (Tu diseño original)
    print(f"{'='*40}")
    print(f"   Predicción de partida - {nombre_jugador}")
    print(f"   Mapa: {mapa}")
    print(f"{'='*40}")
    print(f"Rondas ganadas predichas:  {rondas_g:.1f}")
    print(f"Rondas perdidas predichas: {rondas_p:.1f}")
    print(f"Resultado predicho: {resultado}")

    # LLAMADA A LA FUNCIÓN DE GUARDADO
    #guardar_prediccion_txt(nombre_jugador, mapa, rondas_g, rondas_p, resultado)
    return {
        "rondas_ganadas": round(rondas_g, 1),
        "rondas_perdidas": round(rondas_p, 1),
        "resultado": resultado
    }

def construir_input(df, mapa, es_main, num_amigos):
    columnas_numericas = ["kills", "asistencias", "muertes", "headshots", "acs", "fb", "fd"]
    
    ultima = df.iloc[-1]
    medias = df[columnas_numericas].mean()
    
    partida = {}
    partida["rango"]        = ultima["rango"]
    partida["mapa"]         = mapa
    partida["subrango"]     = ultima["subrango"]
    partida["es_main"]      = es_main
    partida["num_amigos"]   = float(num_amigos)
    partida["desconocidos"] = float(4 - num_amigos)
    partida.update(medias.to_dict())
    
    return pd.DataFrame([partida])


def guardar_prediccion_txt(
    nombre_jugador, mapa, rondas_ganadas, rondas_perdidas, resultado
):
    """_summary_ Función que se encarga de guardar la predicción de una partida para un jugador específico en un archivo de texto llamado "predicciones.txt". La función verifica si el archivo ya existe, y si no existe, lo crea con un encabezado. Luego, obtiene la fecha y hora actual para registrar cuándo se realizó la predicción, y estructura un bloque de texto con la información del jugador, el mapa, las rondas ganadas y perdidas predichas, y el resultado final (victoria o derrota). Finalmente, escribe este bloque de texto en el archivo "predicciones.txt", manteniendo un historial de todas las predicciones realizadas para diferentes jugadores.

    Args:
        nombre_jugador (_type_): _description_ El nombre del jugador para el cual se desea guardar la predicción de la partida. Este valor se utiliza para identificar al jugador en el bloque de texto que se guarda en el archivo "predicciones.txt", permitiendo mantener un historial de predicciones realizadas para cada jugador específico. El nombre del jugador se muestra en el bloque de texto junto con la información de la predicción, como el mapa, las rondas ganadas y perdidas predichas, y el resultado final (victoria o derrota).
        mapa (_type_): _description_ El mapa en el que se va a jugar la partida para la cual se desea guardar la predicción. Este valor se incluye en el bloque de texto que se guarda en el archivo "predicciones.txt", proporcionando información adicional sobre la partida para la cual se realizó la predicción. El mapa se muestra junto con el nombre del jugador, las rondas ganadas y perdidas predichas, y el resultado final (victoria o derrota) en el bloque de texto registrado en el archivo.
        rondas_ganadas (_type_): _description_ El número de rondas ganadas predichas por el modelo para la partida del jugador específico. Este valor se incluye en el bloque de texto que se guarda en el archivo "predicciones.txt", proporcionando información sobre la cantidad de rondas ganadas que se espera que el jugador obtenga en la partida según la predicción del modelo. Las rondas ganadas predichas se muestran junto con el nombre del jugador, el mapa, las rondas perdidas predichas, y el resultado final (victoria o derrota) en el bloque de texto registrado en el archivo.
        rondas_perdidas (_type_): _description_ El número de rondas perdidas predichas por el modelo para la partida del jugador específico. Este valor se incluye en el bloque de texto que se guarda en el archivo "predicciones.txt", proporcionando información sobre la cantidad de rondas perdidas que se espera que el jugador obtenga en la partida según la predicción del modelo. Las rondas perdidas predichas se muestran junto con el nombre del jugador, el mapa, las rondas ganadas predichas, y el resultado final (victoria o derrota) en el bloque de texto registrado en el archivo.
        resultado (_type_): _description_ El resultado final de la partida predicho por el modelo, que puede ser "Victoria" o "Derrota". Este valor se incluye en el bloque de texto que se guarda en el archivo "predicciones.txt", proporcionando una interpretación clara de la predicción realizada por el modelo en términos de si se espera que el jugador gane o pierda la partida. El resultado se muestra junto con el nombre del jugador, el mapa, las rondas ganadas y perdidas predichas en el bloque de texto registrado en el archivo.
    """
    #TODO Arreglar esta direccion relativa
    archivo = "predicciones.txt"

    # Comprobar si el archivo existe; si no, crearlo con un encabezado
    if not os.path.exists(archivo):
        with open(archivo, "w", encoding="utf-8") as f:
            f.write("=" * 60 + "\n")
            f.write("ASTRALIS ANALYTICS - HISTORIAL DE PREDICCIONES\n")
            f.write("=" * 60 + "\n\n")
        print(f"[INFO] El archivo '{archivo}' no existía y ha sido creado.")

    # Obtener la fecha y hora actual para el registro
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Estructurar el bloque de texto para el jugador
    texto_registro = (
        f"Fecha/Hora: {fecha_actual}\n"
        f"Jugador:    {nombre_jugador}\n"
        f"Mapa:       {mapa}\n"
        f"Predicción: {rondas_ganadas:.1f} G - {rondas_perdidas:.1f} P\n"
        f"Resultado:  {resultado}\n"
        f"{'-'*40}\n"
    )

    # Escribir (añadir) los datos en el bloc de notas
    with open(archivo, "a", encoding="utf-8") as f:
        f.write(texto_registro)

    print(f"[OK] Predicción de {nombre_jugador} guardada en '{archivo}'.")