"""
pipeline/pool_entrenamiento.py

Mecanismo B del auto-discovery: quién entra (y quién sale) del pool de
ingesta individual, jugadores_entrenamiento.json.

A diferencia del mecanismo A (candidatos.py, que acumula apariciones a
lo largo de TODAS las partidas procesadas), este mecanismo solo mira la
partida MÁS RECIENTE de cada jugador ya activo en el pool, y de ahí
muestrea un porcentaje pequeño y aleatorio. No lleva contador propio ni
fichero de candidatos: es deliberadamente más simple y más "ruidoso" —
prioriza diversidad para el modelo generalista, sobre precisión — y por
eso necesita el tope duro y la criba de actividad para no degradar el
pool con jugadores fantasma.

Cada entrada de jugadores_entrenamiento.json pasa a tener un campo
`activo` (true/false). Si es false, no se le pide más historial durante
la ingesta normal, pero su CSV no se borra y su entrada se conserva.

Tres funciones públicas, cada una con su propio disparador:

    - registrar_ultima_partida(pares, region) + procesar_muestreo()
      La primera se llama una vez por jugador activo procesado durante
      la ingesta, acumulando en memoria a sus compañeros de la última
      partida. La segunda se llama UNA vez al final de la ejecución
      (script_datos.py) y consume/vacía lo acumulado.

    - revisar_actividad_semanal()
      Se llama una vez por semana (p.ej. junto al reentrenamiento). Pone
      activo=false a quien no cumpla el mínimo de partidas ranked
      recientes, liberando hueco en el pool.

    - revisar_inactivos_mensual(api_key)
      Se llama una vez al mes. A diferencia de las otras dos, SÍ hace
      llamadas a la API (una por cada jugador en activo=false), porque
      es la única forma de saber si alguien pausado ha vuelto a jugar.
      Reactiva a quien vuelva a cumplir la condición, si hay hueco.
"""
import os
from datetime import date, datetime

import pandas as pd

import config

RUTA_ENTRENAMIENTO = os.path.join(config.JSON_INFO_DIR, 'jugadores_entrenamiento.json')

# --- Parámetros ajustables ---
PORCENTAJE_MUESTREO_MIN = 0.10
PORCENTAJE_MUESTREO_MAX = 0.20
MAX_JUGADORES_ENTRENAMIENTO = 100

MIN_PARTIDAS_RANKED = 5       # partidas ranked necesarias para poder evaluar actividad
VENTANA_DIAS_ACTIVIDAD = 7    # la 5ª partida más reciente no puede ser más vieja que esto


def _clave(nombre, tag):
    return f"{(nombre or '').strip().lower()}#{(tag or '').strip().lower()}"


def _cargar_entrenamiento():
    if not os.path.exists(RUTA_ENTRENAMIENTO):
        return {'jugadores': []}
    import json
    with open(RUTA_ENTRENAMIENTO, 'r', encoding='utf-8') as f:
        datos = json.load(f)
    datos.setdefault('jugadores', [])
    return datos


def _guardar_entrenamiento(datos):
    import json
    os.makedirs(os.path.dirname(RUTA_ENTRENAMIENTO), exist_ok=True)
    with open(RUTA_ENTRENAMIENTO, 'w', encoding='utf-8') as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)


def _es_activo(jugador):
    # Los jugadores ya existentes en el json antes de este cambio no
    # tienen el campo `activo` todavía: se tratan como activos por
    # defecto (ya se les estaba ingiriendo con normalidad).
    return jugador.get('activo', True)


def _contar_activos(datos):
    return sum(1 for j in datos['jugadores'] if _es_activo(j))


# ---------------------------------------------------------------------
# 1. Muestreo (cada ejecución de ingesta)
# ---------------------------------------------------------------------

# Lista temporal en memoria: se va rellenando durante la ejecución (una
# llamada a registrar_ultima_partida por cada jugador activo procesado)
# y se consume y vacía al llamar a procesar_muestreo() al final del run.
# No es un fichero porque solo tiene sentido dentro de una misma
# ejecución de script_datos.py — no hace falta persistirlo entre runs.
_pendientes = {}


def registrar_ultima_partida(nombres_tags, region):
    """
    Se llama una vez por jugador activo, con los pares (nombre, tag) de
    sus compañeros de equipo en la partida MÁS RECIENTE (no todas las
    partidas, a diferencia de candidatos.registrar_compañeros). Solo
    acumula en memoria, no toca ningún fichero — eso lo hace
    procesar_muestreo() al final.
    """
    for nombre, tag in nombres_tags:
        if not nombre or not tag or nombre == 'Desconocido':
            continue
        clave = _clave(nombre, tag)
        _pendientes.setdefault(clave, (nombre, tag, region))


def procesar_muestreo():
    """
    Consume lo acumulado por registrar_ultima_partida() durante esta
    ejecución. Excluye a quien ya tenga activo=true, elige un porcentaje
    aleatorio entre PORCENTAJE_MUESTREO_MIN y MAX sobre el resto, y
    añade/reactiva respetando MAX_JUGADORES_ENTRENAMIENTO. Vacía la
    lista temporal al terminar, pase lo que pase.
    """
    import random

    try:
        datos = _cargar_entrenamiento()
        indice_completo = {_clave(j['nombre'], j['tag']): j for j in datos['jugadores']}
        claves_activas = {c for c, j in indice_completo.items() if _es_activo(j)}

        hueco = MAX_JUGADORES_ENTRENAMIENTO - len(claves_activas)
        if hueco <= 0:
            print(f"[pool_entrenamiento] Pool lleno ({len(claves_activas)}/{MAX_JUGADORES_ENTRENAMIENTO}), "
                  f"no se muestrea nada este run.")
            return

        # Deduplicar candidatos válidos, excluyendo a quien ya esté activo
        candidatos_unicos = {}
        for clave, (nombre, tag, region) in _pendientes.items():
            if clave in claves_activas:
                continue
            candidatos_unicos.setdefault(clave, (nombre, tag, region))

        if not candidatos_unicos:
            print("[pool_entrenamiento] Sin candidatos nuevos en esta ejecución.")
            return

        porcentaje = random.uniform(PORCENTAJE_MUESTREO_MIN, PORCENTAJE_MUESTREO_MAX)
        tamaño_muestra = round(len(candidatos_unicos) * porcentaje)
        tamaño_muestra = min(tamaño_muestra, hueco, len(candidatos_unicos))

        if tamaño_muestra <= 0:
            print(f"[pool_entrenamiento] {len(candidatos_unicos)} candidato(s) nuevo(s) vistos, "
                  f"pero el muestreo ({porcentaje:.0%}) no selecciona a nadie este run.")
            return

        elegidos = random.sample(list(candidatos_unicos.values()), k=tamaño_muestra)

        hoy = date.today().isoformat()
        nuevos, reactivados = 0, 0

        for nombre, tag, region in elegidos:
            clave = _clave(nombre, tag)
            if clave in indice_completo:
                # Ya existía (estaba en activo=false): se reactiva, no se duplica
                indice_completo[clave]['activo'] = True
                indice_completo[clave]['reactivado_el'] = hoy
                reactivados += 1
            else:
                nueva_entrada = {
                    'nombre': nombre,
                    'tag': tag,
                    'region': region,
                    'activo': True,
                    'desde': hoy,
                }
                datos['jugadores'].append(nueva_entrada)
                indice_completo[clave] = nueva_entrada
                nuevos += 1

        _guardar_entrenamiento(datos)
        ocupado = len(claves_activas) + nuevos + reactivados
        print(f"[pool_entrenamiento] Muestreo {porcentaje:.0%} sobre {len(candidatos_unicos)} candidato(s): "
              f"{nuevos} nuevo(s), {reactivados} reactivado(s). Pool: {ocupado}/{MAX_JUGADORES_ENTRENAMIENTO}.")
    finally:
        _pendientes.clear()


# ---------------------------------------------------------------------
# 2. Criba semanal (activo -> inactivo)
# ---------------------------------------------------------------------

def _quinta_partida_reciente(nombre):
    """
    Lee el CSV ya procesado (ranked filtrado) de un jugador y devuelve la
    fecha de su 5ª partida más reciente, o None si tiene menos de
    MIN_PARTIDAS_RANKED partidas registradas (no se puede evaluar aún:
    recién promocionado o reactivado, se le da margen).
    """
    ruta_csv = os.path.join(config.DATASET_INGEST_DIR, f'dataset_ingest_{nombre}.csv')
    if not os.path.exists(ruta_csv):
        return None

    df = pd.read_csv(ruta_csv)
    if 'fecha' not in df.columns or len(df) < MIN_PARTIDAS_RANKED:
        return None

    fechas = pd.to_datetime(df['fecha'], errors='coerce').dropna().sort_values(ascending=False)
    if len(fechas) < MIN_PARTIDAS_RANKED:
        return None

    return fechas.iloc[MIN_PARTIDAS_RANKED - 1]


def revisar_actividad_semanal():
    """
    Para cada jugador con activo=true, mira su 5ª partida ranked más
    reciente. Si es de hace más de VENTANA_DIAS_ACTIVIDAD días, se marca
    activo=false. Si aún no tiene MIN_PARTIDAS_RANKED partidas, se le
    deja como está (margen de gracia implícito: sin datos suficientes,
    no se evalúa todavía).
    """
    datos = _cargar_entrenamiento()
    hoy = pd.Timestamp(datetime.now().date())
    desactivados = 0

    for j in datos['jugadores']:
        # Normalizamos el campo `activo` en todas las entradas, exista o no antes
        j['activo'] = _es_activo(j)
        if not j['activo']:
            continue

        fecha_5a = _quinta_partida_reciente(j['nombre'])
        if fecha_5a is None:
            continue  # sin datos suficientes todavía, se le da margen

        dias_inactividad = (hoy - fecha_5a).days
        if dias_inactividad > VENTANA_DIAS_ACTIVIDAD:
            j['activo'] = False
            j['desactivado_el'] = date.today().isoformat()
            desactivados += 1

    _guardar_entrenamiento(datos)
    activos = _contar_activos(datos)
    print(f"[pool_entrenamiento] Criba semanal: {desactivados} jugador(es) desactivado(s). "
          f"Pool activo: {activos}/{MAX_JUGADORES_ENTRENAMIENTO}.")


# ---------------------------------------------------------------------
# 3. Revisión mensual (inactivo -> activo, si vuelve a cumplir)
# ---------------------------------------------------------------------

def revisar_inactivos_mensual(api_key):
    """
    Para cada jugador con activo=false, vuelve a pedirle su historial a
    la API (única forma de saber si ha vuelto a jugar, ya que a los
    inactivos no se les consulta en la ingesta normal) y reevalúa la
    misma condición que la criba semanal. Reactiva si hay hueco,
    priorizando a quien tenga la partida más reciente entre los que
    cumplen. Es la única de las tres funciones que consume presupuesto
    de API, y solo una vez al mes.

    Import de pipeline.entrenamiento hecho aquí dentro (no arriba del
    módulo) para evitar import circular: entrenamiento.py llama a
    procesar_muestreo() de este módulo, y este módulo llama a
    entrenamiento.procesado_jugador() para refrescar a los inactivos.
    """
    import pipeline.entrenamiento as entrenamiento

    datos = _cargar_entrenamiento()
    inactivos = [j for j in datos['jugadores'] if not _es_activo(j)]

    if not inactivos:
        print("[pool_entrenamiento] Revisión mensual: no hay jugadores inactivos que revisar.")
        return

    candidatos_reactivacion = []  # (jugador_dict, fecha_5a_partida)

    for j in inactivos:
        try:
            entrenamiento.procesado_jugador(j['nombre'], j['tag'], j['region'], api_key)
        except ValueError:
            continue  # sin datos válidos en la API, se queda inactivo

        fecha_5a = _quinta_partida_reciente(j['nombre'])
        if fecha_5a is None:
            continue

        hoy = pd.Timestamp(datetime.now().date())
        if (hoy - fecha_5a).days <= VENTANA_DIAS_ACTIVIDAD:
            candidatos_reactivacion.append((j, fecha_5a))

    if not candidatos_reactivacion:
        print("[pool_entrenamiento] Revisión mensual: ningún inactivo cumple la condición para reactivarse.")
        return

    # Prioriza a quien tenga la partida más reciente si hay más candidatos que hueco
    candidatos_reactivacion.sort(key=lambda par: par[1], reverse=True)

    activos_actuales = _contar_activos(datos)
    hueco = MAX_JUGADORES_ENTRENAMIENTO - activos_actuales
    reactivados = 0

    for j, _fecha in candidatos_reactivacion:
        if hueco <= 0:
            break
        j['activo'] = True
        j['reactivado_el'] = date.today().isoformat()
        hueco -= 1
        reactivados += 1

    _guardar_entrenamiento(datos)
    print(f"[pool_entrenamiento] Revisión mensual: {reactivados}/{len(candidatos_reactivacion)} "
          f"inactivo(s) elegible(s) reactivado(s) (limitado por hueco disponible).")