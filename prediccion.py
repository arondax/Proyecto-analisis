import pandas as pd
import os
from datetime import datetime


def predecir_jugador(modelo, df, mapa, es_main, num_amigos, desconocidos, nombre_jugador):
    # 1. Identificar las columnas exactas con las que se entrenó el modelo.
    # Excluimos el ID y los targets (rondas ganadas/perdidas) manteniendo el orden exacto del df.
    columnas_a_excluir = ["id_partida", "rondas_ganadas", "rondas_perdidas"]
    columnas_modelo = [col for col in df.columns if col not in columnas_a_excluir]

    # 2. Definir cuáles son las numéricas para sacar las medias
    columnas_numericas = [
        "kills",
        "asistencias",
        "muertes",
        "headshots",
        "acs",
        "fb",
        "fd",
    ]
    columnas_mapa = [col for col in df.columns if col.startswith("mapa_")]

    # 3. Extraer datos históricos
    ultima = df.iloc[-1]
    medias = df[columnas_numericas].mean()

    # 4. Construir el diccionario de la nueva partida
    partida = {}
    partida["rango"] = ultima["rango"]
    partida["subrango"] = ultima["subrango"]
    partida["racha"] = ultima["racha"]
    partida["es_main"] = es_main
    partida["num_amigos"] = num_amigos
    partida["desconocidos"] = desconocidos

    # Añadir las medias calculadas
    partida.update(medias.to_dict())

    # Inicializar los mapas en 0.0
    for col in columnas_mapa:
        partida[col] = 0.0

    # Activar el mapa actual
    mapa_col = f"mapa_{mapa}"
    if mapa_col not in columnas_mapa:
        mapas_disponibles = [m.replace("mapa_", "") for m in columnas_mapa]
        raise ValueError(
            f"Mapa no reconocido: {mapa}. Disponibles: {mapas_disponibles}"
        )
    partida[mapa_col] = 1.0

    # 5. CREAR EL DATAFRAME ASEGURANDO EL ORDEN ORIGINAL
    X = pd.DataFrame([partida])[columnas_modelo]

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
    guardar_prediccion_txt(nombre_jugador, mapa, rondas_g, rondas_p, resultado)
    return {
        "rondas_ganadas": round(rondas_g, 1),
        "rondas_perdidas": round(rondas_p, 1),
        "resultado": resultado
    }



def guardar_prediccion_txt(
    nombre_jugador, mapa, rondas_ganadas, rondas_perdidas, resultado
):
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