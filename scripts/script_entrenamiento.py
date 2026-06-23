

import pipeline.entrenamiento as entrenamiento


check = entrenamiento.entrenar_modelo_regression()
if check:
    print("Modelo de regresión entrenado.")