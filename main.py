import api, procesador, script_amigos, limpieza_datos, modelo

all_users = False

if all_users:
    script, datos= script_amigos.procesar_amigos()
    if script:
        print("Script ejecutado sin problemas")
        
    
else:
    nombre_jugador = "Aaronnn17"
    tag = "1704"
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
        print("------------------------------------")
        print("-----Entrenamiento------------")
        df = modelo.lectura_csv(nombre_jugador)
        if not df.empty:
            modelo.entrenamiento(df)

#TODO repasar los modelos y los datos que entran porque los modelos creo que no estan entrando todos los datos de csv
#TODO, que haya 1 solo csv con el dataset. Los archivos json de consulta eliminarlos despues. JSON donde se agregen los amigos. Recabar mas datos. Filtrar aquellos que sean COMPETITIVO.