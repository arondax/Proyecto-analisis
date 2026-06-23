import random
import pandas as pd
import numpy as np

# Importamos tu función modificada (asegúrate de que el archivo se llame prediccion.py)
import pipeline.predictor as predictor

# ==========================================
# 1. CONFIGURACIÓN DE DATOS DE PRUEBA
# ==========================================
datos_jugadores = {
    "jugadores": [
        {"nombre": "rondax", "tag": "EUW"},
        {"nombre": "angelutrix", "tag": "EUW"},
        {"nombre": "Chiste sad002", "tag": "EUW"},
        {"nombre": "Aaronnn17", "tag": "1704"},
        {"nombre": "mamipito", "tag": "4860"},
        {"nombre": "papa pito", "tag": "4284"},
    ]
}

pool_mapas = [
    "Abyss",
    "Ascent",
    "Bind",
    "Breeze",
    "Corrode",
    "Fracture",
    "Haven",
    "Icebox",
    "Lotus",
    "Pearl",
    "Split",
    "Sunset",
]


# ==========================================
# 2. MOCK DE MODELO Y DATAFRAME HISTÓRICO
# ==========================================
# Creamos un simulador del modelo para no obligarte a cargar el .pkl real en el test
class MockModelo:

    def predict(self, X):
        # Devuelve un array simulando [rondas_ganadas, rondas_perdidas]
        # Por ejemplo, una victoria ajustada 13-10 o una derrota
        g = float(random.randint(5, 13))
        p = 13.0 if g < 13 else float(random.randint(0, 11))
        return np.array([[g, p]])


# Construimos un DataFrame 'df' artificial con la misma estructura exacta que usas
def generar_df_historico_falso():
    columnas_mapa = [f"mapa_{m}" for m in pool_mapas]
    columnas_resto = [
        "rango",
        "id_partida",
        "kills",
        "asistencias",
        "muertes",
        "headshots",
        "subrango",
        "acs",
        "fb",
        "fd",
        "racha",
        "rondas_ganadas",
        "rondas_perdidas",
        "es_main",
        "num_amigos",
        "desconocidos",
    ]

    # Juntamos todo manteniendo el esquema que me mostraste en consola
    todas_las_columnas = (
        ["rango"]
        + columnas_mapa
        + [
            "id_partida",
            "kills",
            "asistencias",
            "muertes",
            "headshots",
            "subrango",
            "acs",
            "fb",
            "fd",
            "racha",
            "rondas_ganadas",
            "rondas_perdidas",
            "es_main",
            "num_amigos",
            "desconocidos",
        ]
    )

    # Añadimos unas filas de datos dummy para que la función pueda calcular .mean() e .iloc[-1]
    datos_dummy = []
    for i in range(5):
        fila = {col: 0.0 for col in todas_las_columnas}
        fila["rango"] = 3.0  # Plata/Oro por ejemplo
        fila["subrango"] = 2.0
        fila["kills"] = 15.0 + i
        fila["asistencias"] = 5.0
        fila["muertes"] = 12.0
        fila["headshots"] = 6.0
        fila["acs"] = 210.5
        fila["racha"] = 1.0 if i % 2 == 0 else 0.0
        # Activar un mapa dummy por fila
        mapa_random = f"mapa_{random.choice(pool_mapas)}"
        fila[mapa_random] = 1.0
        datos_dummy.append(fila)

    return pd.DataFrame(datos_dummy)


# ==========================================
# 3. EJECUCIÓN DE LA PRUEBA EN BUCLE
# ==========================================
if __name__ == "__main__":
    print("[TEST] Iniciando entorno de pruebas para predicciones...")

    # Inicializamos el dataframe dummy y el modelo falso
    df_prueba = generar_df_historico_falso()
    modelo_prueba = MockModelo()

    print(f"[TEST] Estructura de columnas simulada correctamente.")
    print(f"[TEST] Lanzando predicciones para los {len(datos_jugadores['jugadores'])} jugadores...\n")

    for jugador in datos_jugadores["jugadores"]:
        nombre_completo = f"{jugador['nombre']}#{jugador['tag']}"

        # Parámetros aleatorios de simulación para la partida
        mapa_partida = random.choice(pool_mapas)
        es_main_char = random.choice([0.0, 1.0])
        amigos = float(random.randint(0, 4))
        desconocidos = 4.0 - amigos

        # Ejecutamos tu lógica
        try:
            predictor.predecir_jugador(
                modelo=modelo_prueba,
                df=df_prueba,
                mapa=mapa_partida,
                es_main=es_main_char,
                num_amigos=amigos,
                desconocidos=desconocidos,
                nombre_jugador=nombre_completo,
            )
        except Exception as e:
            print(f"[ERROR] Falló la predicción para {nombre_completo}: {e}")

    print("\n" + "=" * 40)
    print("[TEST COMPLETO] Revisa si se ha generado o actualizado 'predicciones.txt'.")
    print("=" * 40)