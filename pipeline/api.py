import requests
import json
import time
import os
import config


class CuentaNoEncontrada(ValueError):
    """
    La cuenta de Riot no existe (código 22 de Henrik Dev): nombre#tag con
    error de escritura, cambiado, o cuenta borrada. A diferencia de un
    429 o un error transitorio, no tiene sentido reintentar ni volver a
    consultarla en el futuro.

    Hereda de ValueError a propósito: procesado_jugador() en
    entrenamiento.py ya convierte un fallo de la API en ValueError para
    el endpoint /predecir, así que cualquier `except ValueError` que ya
    exista en el código (como en app/routes/prediccion.py) la sigue
    capturando sin tener que tocar nada ahí. Solo donde de verdad
    importa la diferencia (el bucle de ingesta y la revisión mensual) se
    captura específicamente `except CuentaNoEncontrada`.
    """
    pass


##Funcion para conseguir los datos en bruto
def getData(nombre, tag, region, api_key):
    URL = f"https://api.henrikdev.xyz/valorant/v3/matches/{region}/{nombre}/{tag}"
    print(f"Buscando datos de {nombre}#{tag}...")
    headers = {"Authorization": api_key, "Accept": "*/*"}

    #print(f"[DEBUG] API Key primeros 10 chars: '{api_key[:10]}'")
    for intento in range(3):
        response = requests.get(URL, headers=headers)

        if response.status_code == 200:
            print('Solicitud existosa')
            data = response.json()
            nombre_archivo = f"matches_{nombre}.json"
            os.makedirs(config.PARTIDAS_DIR, exist_ok=True)
            direccion_archivo = os.path.join(config.PARTIDAS_DIR, nombre_archivo)
            with open(direccion_archivo, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            print(f"Archivo '{nombre_archivo}' creado con éxito.")
            return data

        elif response.status_code == 429:
            espera = 30 * (2 ** intento)  # 30s, 60s, 120s
            print(f"Rate limit, esperando {espera}s antes de reintentar...")
            time.sleep(espera)

        elif response.status_code == 404:
            codigo_error = None
            try:
                codigo_error = response.json().get('errors', [{}])[0].get('code')
            except (ValueError, IndexError, KeyError):
                pass

            if codigo_error == 22:
                raise CuentaNoEncontrada(f"{nombre}#{tag} ({region}): cuenta no encontrada en Riot.")

            # Otro tipo de 404 (p.ej. sin partidas todavía): se trata como antes
            print(f'Error en la solicitud, detalles: {response.status_code} ', response.text)
            return None

        else:
            print(f'Error en la solicitud, detalles: {response.status_code} ', response.text)
            return None

    print(f"Rate limit persistente para {nombre}#{tag}, saltando...")
    return None
""""
def obtener_mapeo_roles():
    url = "https://api.henrikdev.xyz/valorant/v1/content"
    # ... (tus headers con la API KEY)
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        content = response.json()
        mapeo = {}
        # Recorremos los personajes (characters) en el contenido
        for personaje in content['data']['characters']:
            nombre = personaje['name']
            rol = personaje['role'] # Ejemplo: "Duelist"
            mapeo[nombre] = rol

        nombre_archivo=f"personajes.json"
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            json.dump(mapeo, f, indent=4)
        print(f"Archivo '{nombre_archivo}' creado con éxito.")

        return mapeo
    return {}
"""