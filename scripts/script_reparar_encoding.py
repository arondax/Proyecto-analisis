"""
Script de un solo uso: repara amigos_recurrentes.json después del bug de
encoding (ensure_ascii=False escribiendo bytes UTF-8 "sueltos" que
limpieza_datos.py no podía leer en Windows). Lee el fichero en UTF-8
(que es como está guardado de verdad) y lo vuelve a guardar con
ensure_ascii=True, igual que el resto del proyecto — mismo contenido,
formato seguro para cualquier lector.

No hace falta correrlo más de una vez ni meterlo en ningún workflow.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import config

RUTA_AMIGOS = os.path.join(config.JSON_INFO_DIR, 'amigos_recurrentes.json')

with open(RUTA_AMIGOS, 'r', encoding='utf-8') as f:
    datos = json.load(f)

with open(RUTA_AMIGOS, 'w', encoding='utf-8') as f:
    json.dump(datos, f, indent=4)

print(f"amigos_recurrentes.json reparado: {len(datos.get('amigos', []))} amigo(s), formato ASCII-safe.")