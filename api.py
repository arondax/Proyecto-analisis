import requests
import json
import time

##Funcion para conseguir los datos en bruto
def getData(nombre, tag, region, api_key):
    URL = f"https://api.henrikdev.xyz/valorant/v3/matches/{region}/{nombre}/{tag}"
    print(f"Buscando datos de {nombre}#{tag}...")
    headers = {"Authorization": api_key, "Accept": "*/*"}
    
    for intento in range(3):
        response = requests.get(URL, headers=headers)
        
        if response.status_code == 200:
            print('Solicitud existosa')
            data = response.json()
            nombre_archivo = f"matches_{nombre}.json"
            direccion_archivo = f"./partidas/{nombre_archivo}"
            with open(direccion_archivo, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            print(f"Archivo '{nombre_archivo}' creado con éxito.")
            return data
        
        elif response.status_code == 429:
            espera = 30 * (2 ** intento)  # 30s, 60s, 120s
            print(f"Rate limit, esperando {espera}s antes de reintentar...")
            time.sleep(espera)
        
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


