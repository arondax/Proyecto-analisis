import api, procesador, entrenar_modelo, limpieza_datos, modelos

entrenar_modelo_v = True

#Obtendremos todos los datos de la lista de jugadores (los amigos) y crearemos sus 
if entrenar_modelo_v:
    skip_datos= True
    if not skip_datos:
        script, datos= entrenar_modelo.obtencion_lista()
        if script:
            print("Datos obtenidos")
    
    script = entrenar_modelo.entrenar_modelo_regression()
    if script:
        print("Modelo de regresión entrenado.")
        
    
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
        df = modelos.lectura_csv(nombre_jugador)
        if not df.empty:
            modelos.entrenamiento(df)

#TODO repasar los modelos y los datos que entran porque los modelos creo que no estan entrando todos los datos de csv
#TODO, que haya 1 solo csv con el dataset. Los archivos json de consulta eliminarlos despues. JSON donde se agregen los amigos. Recabar mas datos. Filtrar aquellos que sean COMPETITIVO.