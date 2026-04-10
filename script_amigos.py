#Imports
import json ,api, procesador, limpieza_datos


def procesar_amigos():
    #Leemos el json de con los datos de los jugadores:
    try:                                                            
        with open(f'./amigos_recurrentes.json','r', encoding='utf-8') as archivo:
            datos = json.load(archivo)
    except FileNotFoundError:
        print(f"❌ No se encontró el archivo amigos_recurrentes.json")
    #Recorremos la lista de amigos, y aplicamos para crear dataset y csv
    nombre_jugador =""
    tag=""
    for jugador in datos.get("jugadores"):
        nombre_jugador= jugador.get("nombre")
        tag= jugador.get("tag")
        
        resultado= api.getData(nombre_jugador, tag, "eu")
        if resultado:
            print(f"Datos optenidos de: ", nombre_jugador,"#",tag)
            print("Procesado de la partida")
            procesador.extraccion_datos(nombre_jugador, tag)
            limpieza_datos.limpieza_jugador(nombre_jugador)
    return True,datos
        

    
