import api, procesador, script_amigos, limpieza_datos

all_users = True

if all_users:
    script, datos= script_amigos.procesar_amigos()
    if script:
        print("Script ejecutado sin problemas")
        
    
else:
    nombre_jugador = "rondax"
    tag = "EUW"
    region = "eu"

    print("Inicio programa: ")
    print(" \n Introduce tu nombre de Valorant: ")
    #nombre_jugador = input("rondax")
    print("\n Introduce tu region (na, eu, ap, kr): ")
    #region= input("eu")
    print("\n Introduce el tag sin #: ")
    #tag = input("EUW")
    resultado = api.getData(nombre_jugador,tag,region)
    #api.obtener_mapeo_roles()

    if resultado:
        print("Funciona correcatamente")
        print("Procesado de la partida")
        procesador.extraccion_datos(nombre_jugador, tag)
        limpieza_datos.limpieza_jugador(nombre_jugador)
        print("DATOS LIMPIOS Y PREPARADOS PARA INGESTA")



#TODO, que haya 1 solo csv con el dataset. Los archivos json de consulta eliminarlos despues. JSON donde se agregen los amigos. Recabar mas datos. Filtrar aquellos que sean COMPETITIVO.