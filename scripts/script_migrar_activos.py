"""
Script de migración, de un solo uso: añade los campos `activo` y `desde`
a las entradas de jugadores_entrenamiento.json que se crearon antes de
meter el mecanismo de auto-discovery (y que por tanto no los tienen).

No hace falta para que el código funcione (todo el pipeline ya trata la
ausencia de `activo` como True por defecto), es solo para dejar el JSON
explícito y evitar sorpresas si en algún momento inspeccionas el fichero
a mano o escribes otra herramienta que sí espere el campo.

Se ejecuta una vez y ya está; no forma parte de ningún workflow.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from datetime import date

import config

RUTA_ENTRENAMIENTO = os.path.join(config.JSON_INFO_DIR, 'jugadores_entrenamiento.json')

with open(RUTA_ENTRENAMIENTO, 'r', encoding='utf-8') as f:
    datos = json.load(f)

hoy = date.today().isoformat()
actualizados = 0

for jugador in datos.get('jugadores', []):
    cambiado = False

    if 'activo' not in jugador:
        jugador['activo'] = True
        cambiado = True

    if 'desde' not in jugador:
        jugador['desde'] = hoy
        cambiado = True

    if cambiado:
        actualizados += 1

with open(RUTA_ENTRENAMIENTO, 'w', encoding='utf-8') as f:
    json.dump(datos, f, indent=4, ensure_ascii=False)

print(f"Migración completada: {actualizados} jugador(es) actualizado(s) con 'activo' y 'desde'.")