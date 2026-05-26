import api, procesador, entrenamiento, limpieza_datos, modelos
import prediccion

entrenar_modelo_v = False

#Obtendremos todos los datos de la lista de jugadores (los amigos) y crearemos sus 
if entrenar_modelo_v:
    
    obtener_datos= False
    if obtener_datos:
        check, datos= entrenamiento.obtencion_lista()
        if check:
            print("Datos obtenidos")
        check = entrenamiento.procesado_jugadores(datos)
        if check:
            print("Datos procesados")
            
    entrenar = False
    if entrenar:
        check = entrenamiento.entrenar_modelo_regression()
        if check:
            print("Modelo de regresión entrenado.")
    
    prueba_prediccion =True
    if prueba_prediccion:
        df = modelos.lectura_csv(identificador="mamipito")
        modelo = modelos.cargar_modelo('randomforest')
        modelos.predecir_partida(modelo,df)
        
        
    
else:
    nombre_jugador = "rondax"
    tag = "EUW"
    region = "eu"
    mapa = "Corrode"
    es_main = 1.0
    num_amigos:int = 4
    desconocidos:int = 5- num_amigos

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
        df = limpieza_datos.limpieza_jugador(nombre_jugador)
        modelo = modelos.cargar_modelo('randomforest')
        print("Pasamos a prediccion")
        if not df.empty:
            prediccion.predecir_jugador(modelo,df, mapa, es_main, num_amigos, desconocidos, nombre_jugador)
            
            

#TODO repasar los modelos y los datos que entran porque los modelos creo que no estan entrando todos los datos de csv
#TODO, que haya 1 solo csv con el dataset. Los archivos json de consulta eliminarlos despues. JSON donde se agregen los amigos. Recabar mas datos. Filtrar aquellos que sean COMPETITIVO.