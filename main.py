import api, procesador

jugador = "Chiste sad002"
tag = "EUW"
region = "eu"

print("Inicio programa: ")
print(" \n Introduce tu nombre de Valorant: ")
#jugador = input("rondax")
print("\n Introduce tu region (na, eu, ap, kr): ")
#region= input("eu")
print("\n Introduce el tag sin #: ")
#tag = input("EUW")


resultado = api.getData(jugador,tag,region)
#api.obtener_mapeo_roles()

if resultado:
    print("Funciona correcatamente")
    print("Procesado de la partida")
    procesador.extraccion_datos(jugador, tag)
    
#TODO, que haya 1 solo csv con el dataset. Los archivos json de consulta eliminarlos despues. JSON donde se agregen los amigos. Recabar mas datos. Filtrar aquellos que sean COMPETITIVO.