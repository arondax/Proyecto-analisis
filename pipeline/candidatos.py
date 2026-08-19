
"""
pipeline/candidatos.py
 
Mecanismo A del auto-discovery: candidato -> amigo_recurrente.
 
- candidato: alguien visto como compañero de equipo en CUALQUIER partida
  procesada de un jugador ya trackeado (no solo la última). Registrarlo
  NO cuesta ninguna llamada a la API, solo se anota en
  candidatos_jugadores.json.
 
- amigo_recurrente: candidato que ha aparecido >= UMBRAL_CANDIDATO
  veces. Se promociona a amigos_recurrentes.json. Sigue sin costar API:
  solo mejora los features num_amigos/desconocidos en limpieza_datos.py.
  Aunque ya sea amigo, se le sigue sumando apariciones (por si en algún
  momento se usa esa cifra para priorizar el mecanismo B).
 
Este módulo NO decide quién entra en jugadores_entrenamiento.json — esa
es una responsabilidad aparte (mecanismo B, muestreo del 10-20% sobre la
última partida + criba de actividad + revisión mensual), que vive en
pipeline/pool_entrenamiento.py. Aquí solo se excluye a quien YA esté en
jugadores_entrenamiento.json (da igual si activo o no), porque ese
jugador ya pasó de tier y no tiene sentido seguir contándole apariciones
como candidato.
 
Uso típico:
 
    - Dentro del bucle de extracción de partidas (procesador.py), por
      cada partida procesada:
          pares = buscar_teammates_con_tag(partida, equipo, nombre, tag)
          candidatos.registrar_compañeros(pares, region)
 
    - Una vez al final de la ingesta (script_datos.py), tras procesar a
      todos los jugadores del pool:
          candidatos.evaluar_promocion_amigos()
"""

import json
import os
from datetime import date

import config


RUTA_CANDIDATOS = os.path.join(config.JSON_INFO_DIR, 'candidatos_jugadores.json')
RUTA_AMIGOS = os.path.join(config.JSON_INFO_DIR, 'amigos_recurrentes.json')
RUTA_ENTRENAMIENTO = os.path.join(config.JSON_INFO_DIR, 'jugadores_entrenamiento.json')


# -- Umbrales para determinar si un jugador es candidato a entrenamiento
UMBRAL_CANDIDATO = 3 #Numero de apariciones


def _clave(nombre, tag):
        """Normaliza nombre#tag para comparar sin problemas de mayúsculas/espacios."""
        return f"{(nombre or '').strip().lower()}#{(tag or '').strip().lower()}"

def _cargar(ruta, clave_lista):
    if not os.path.exists(ruta):
        return {clave_lista: []}
    with open (ruta, 'r', encoding='utf-8') as f:
        return json.load(f)
    
def _guardar(ruta, datos):
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, 'w', encoding='utf-8') as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)
        
def registrar_compañeros(nombres_tags, region):
    """
    nombres_tags: lista de tuplas (nombre, tag) vistas como compañeras de
    equipo en una partida.
 
    - Si ya está en jugadores_entrenamiento.json (activo o no): se ignora,
      ya pasó de tier.
    - Si ya es amigo recurrente: se le suma una aparición en
      amigos_recurrentes.json.
    - Si no es ninguna de las dos cosas: se registra/incrementa en
      candidatos_jugadores.json.
 
    Entradas sin tag se ignoran (no se puede consultar la API sin tag).
    Devuelve True si hubo cambios que guardar.
    """
    amigos = _cargar(RUTA_AMIGOS,'amigos')
    entrenamiento = _cargar (RUTA_ENTRENAMIENTO, 'jugadores')
    candidatos = _cargar (RUTA_CANDIDATOS, 'candidatos')
    
    amigos.setdefault('amigos', [])
    entrenamiento.setdefault('jugadores',[])
    
    claves_entrenamiento = {_clave(j['nombre'], j['tag']) for j in entrenamiento['jugadores']}
    indice_amigos = {_clave(a['nombre'], a['tag']): a for a in amigos['amigos']}
    indice_candidatos = {_clave(c['nombre'], c['tag']): c for c in candidatos.get('candidatos', [])}
    
    hoy = date.today().isoformat()
    cambios_candidatos = False
    cambios_amigos = False
    
    for nombre, tag in nombres_tags:
        if not nombre or not tag or nombre == 'Desconocido':
            continue
        
        clave = _clave(nombre, tag)
        if clave in claves_entrenamiento:
            continue  # ya está en entrenamiento, no hacer nada
        
        if clave in indice_amigos:
            indice_amigos[clave]['apariciones'] = indice_amigos[clave].get('apariciones', 0) + 1
            indice_amigos[clave]['ultima_vez'] = hoy
            cambios_amigos = True
            continue
        
        if clave in indice_candidatos:
            indice_candidatos[clave]['apariciones'] += 1
            indice_candidatos[clave]['ultima_vez'] = hoy
        else:
            indice_candidatos[clave] = {
                'nombre': nombre,
                'tag': tag,
                'region': region,
                'apariciones': 1,
                'primera_vez': hoy,
                'ultima_vez': hoy,
            }
        cambios_candidatos = True
 
    if cambios_candidatos:
        candidatos['candidatos'] = list(indice_candidatos.values())
        _guardar(RUTA_CANDIDATOS, candidatos)
    if cambios_amigos:
        amigos['amigos'] = list(indice_amigos.values())
        _guardar(RUTA_AMIGOS, amigos)
 
    return cambios_candidatos or cambios_amigos


def evaluar_promocion_amigos():
    """
    Promociona a amigos_recurrentes.json a todo candidato que haya
    alcanzado UMBRAL_CANDIDATO apariciones. Pensado para
    llamarse UNA vez al final de cada ingesta, no por partida.
    """
    candidatos = _cargar(RUTA_CANDIDATOS, 'candidatos')
    amigos = _cargar(RUTA_AMIGOS, 'amigos')
    amigos.setdefault('amigos', [])
 
    restantes = []
    promovidos = 0
 
    for c in candidatos.get('candidatos', []):
        if c['apariciones'] >= UMBRAL_CANDIDATO:
            amigos['amigos'].append({
                'nombre': c['nombre'],
                'tag': c['tag'],
                'region': c['region'],
                'apariciones': c['apariciones'],
                'amigo_desde': date.today().isoformat(),
            })
            promovidos += 1
        else:
            restantes.append(c)
 
    if promovidos:
        candidatos['candidatos'] = restantes
        _guardar(RUTA_CANDIDATOS, candidatos)
        _guardar(RUTA_AMIGOS, amigos)
        print(f"[candidatos] {promovidos} candidato(s) promovido(s) a amigo recurrente.")