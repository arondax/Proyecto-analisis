#Imports
import json
import api
import procesador

def procesar_amigos():
    #Leemos el json de con los datos de los jugadores:
    try:                                                            
        with open(f'./amigos_recurrentes.json','r', encoding='utf-8') as archivo:
            datos = json.load(archivo)
    except FileNotFoundError:
        print(f"❌ No se encontró el archivo amigos_recurrentes.json")
    #Recorremos la lista de amigos, y aplicamos para crear dataset y csv
    nombre =""
    tag=""
    for jugador in datos.get("jugadores"):
        nombre= jugador.get("nombre")
        tag= jugador.get("tag")
        
        resultado= api.getData(nombre, tag, "eu")
        if resultado:
            print(f"Datos optenidos de: ", nombre,"#",tag)
            print("Procesado de la partida")
            procesador.extraccion_datos(nombre, tag)
    return True
        

    
