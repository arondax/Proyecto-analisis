import requests
import json


key= "HDEV-0fe75a76-4407-4ac7-b11a-9fe5baedcbc7"

headers = {
    "Authorization": key,
    "Accept": "*/*"
}
##Funcion para conseguir los datos en bruto
def getData(nombre, tag, region):
    URL=f"https://api.henrikdev.xyz/valorant/v3/matches/{region}/{nombre}/{tag}"
    print(f"Buscando datos de {nombre}#{tag}...")
    
    #Peticion
    response = requests.get(URL, headers=headers)
    
    if response.status_code == 200:
        print('Solicitud existosa')
        data = response.json()
        #Creamos un archivo json
        nombre_archivo=f"matches_{nombre}.json"
        
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print(f"✅ Archivo '{nombre_archivo}' creado con éxito.")
        return data   
    else:
        print(f'Error en la solicitud, detalles: {response.status_code} ', response.text)    
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
        print(f"✅ Archivo '{nombre_archivo}' creado con éxito.")   
        
        return mapeo
    return {}
"""


