import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pipeline.entrenamiento as entrenamiento
import pipeline.pool_entrenamiento as pool_entrenamiento
import pipeline.candidatos as candidatos


check = entrenamiento.entrenar_modelo_regression()
if check:
    print("Modelo de regresión entrenado.")
    pool_entrenamiento.revisar_actividad_semanal()
    candidatos.vaciar_candidatos()