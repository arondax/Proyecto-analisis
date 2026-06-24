
from importlib.metadata import metadata
from pipeline import api, limpieza_datos

import json
import pandas as pd
import config
import os


def extraccion_datos(nombre, tag):
    """_summary_ Función que se encarga de extraer los datos relevantes de las partidas del jugador, a partir del archivo JSON obtenido de la API, y luego guarda estos datos en un archivo CSV específico para cada jugador. La función procesa cada partida del jugador, extrae información como el agente jugado, las kills, asistencias, muertes, compañeros de equipo, rango, composición del equipo, acs, entre otros datos relevantes para el análisis y entrenamiento del modelo. Luego, organiza estos datos en un DataFrame de pandas y lo guarda en un archivo CSV dentro de la carpeta designada para datasets, utilizando el nombre del jugador para nombrar el archivo. Además, la función también añade el jugador a un JSON de amigos recurrentes para su posterior uso en el entrenamiento del modelo.

    Args:
        nombre (_type_): _description_ El nombre del jugador del cual se van a extraer los datos de las partidas. Este nombre se utiliza para localizar el archivo JSON específico que contiene los datos de las partidas del jugador, y también se utiliza para nombrar el archivo CSV donde se guardarán los datos extraídos. El nombre del jugador debe coincidir con el formato utilizado en el archivo JSON para que la función pueda localizar correctamente los datos correspondientes a ese jugador.
        tag (_type_): _description_ El tag del jugador del cual se van a extraer los datos de las partidas. Este tag se utiliza junto con el nombre del jugador para localizar el archivo JSON específico que contiene los datos de las partidas del jugador, y también se utiliza para identificar al jugador dentro de las partidas al extraer los datos relevantes. El tag del jugador debe coincidir con el formato utilizado en el archivo JSON para que la función pueda localizar correctamente los datos correspondientes a ese jugador.

    Returns:
        _type_: _description_   Devuelve un DataFrame de pandas que contiene los datos extraídos de las partidas del jugador, organizados en columnas relevantes para el análisis y entrenamiento del modelo. Este DataFrame se puede utilizar posteriormente para realizar análisis exploratorios, limpieza de datos, y entrenamiento del modelo de machine learning. Además, la función también guarda estos datos en un archivo CSV específico para el jugador, dentro de la carpeta designada para datasets, utilizando el nombre del jugador para nombrar el archivo.
    """
    
    #print(f"[DEBUG] Directorio de trabajo actual: {os.getcwd()}")
    #print(f"[DEBUG] Buscando JSON en: {os.path.abspath(f'./partidas/matches_{nombre}.json')}")
    #print(f"[DEBUG] CSV destino: {os.path.abspath(f'./datasets/dataset_{nombre}.csv')}")
    
    filas_finales = []
    agentes= cargar_config_personajes()
    #Leemos el archivo
    try:              
        ruta_partidas = os.path.join(config.PARTIDAS_DIR, f'matches_{nombre}.json')                                              
        with open(ruta_partidas,'r', encoding='utf-8') as archivo:
            datos = json.load(archivo)
    except FileNotFoundError:
        print(f"No se encontró el archivo matches_{nombre}.json")
        return None
    
    racha = 0
    
    #Revisamos si el archivo existe
    direccion_archivo = os.path.join(config.DATASET_DIR,f'dataset_{nombre}.csv')
    existe_archivo= os.path.exists(direccion_archivo)
    
    for partida in datos['data']:
        MODOS_SIN_EQUIPOS = {'Deathmatch', 'Team Deathmatch', 'Custom Game', 'Spike Rush', 'Escalation'}
        metadata = partida.get('metadata')
        if metadata is None:
            print(f"[DEBUG] Partida sin metadata, saltando")
            continue
        modo = partida.get('metadata').get('mode')
        if not modo or modo.lower() in MODOS_SIN_EQUIPOS:
            print(f"[DEBUG] Filtrada por modo: {modo}")
            continue
        
        lista_estadisticas = buscar_personaje(partida, nombre, tag)
        
        if not lista_estadisticas:
            print(f"[DEBUG] Jugador no encontrado en partida {partida.get('metadata').get('matchid')}")
            continue # Si no encuentra al jugador en esta partida, salta a la siguiente
        
        id_partida= partida.get('metadata').get('matchid')
        mapa_actual = partida.get('metadata').get('map')
        print(f"[DEBUG] Partida encontrada - Modo: {modo} | Mapa: {mapa_actual}")
        personaje = lista_estadisticas['personaje']
        rol = agentes.get(personaje, "Desconocido")
        rango = lista_estadisticas['rango']
        subrango = lista_estadisticas['subrango']
        headshot = lista_estadisticas['headshot']
        equipo = lista_estadisticas['equipo']
        modo = partida.get('metadata').get('mode')
        fecha = partida.get('metadata',{}).get('game_start')
        fecha_legible = partida.get('metadata',{}).get('game_start_patched')
        region = partida.get('metadata').get('region')
        
        puntuacion_total = lista_estadisticas['score']
        #print("puntuacion: ",puntuacion_total)
        puntuacion_total = int(puntuacion_total)
        n_rondas = partida.get('metadata').get('rounds_played')
        #print("numero rondas: ",n_rondas)
        n_rondas = int(n_rondas)
        acs= puntuacion_total/n_rondas
        acs = "{:.3f}".format(acs)
        
        teammates = buscar_teammates(partida, equipo , nombre, tag)
        composicion = obtener_composicion(partida, equipo)
        rondas_win_lose = obtener_rondas(partida, equipo)
        if rondas_win_lose is None or rondas_win_lose == (None, None):
            print(f"[DEBUG] Partida sin datos de rondas, saltando")
            continue

        rondas_w = rondas_win_lose[0]
        rondas_l = rondas_win_lose[1]
        
        fb, fd = calcular_impacto_ronda(partida, nombre, tag)
        
        #Calculamos la racha
        if rondas_w > rondas_l:
            racha+=1
        elif rondas_w < rondas_l:
            racha = 0
                
        #victoria = victoria_jugador(datos, equipo)
        #print(f"Mapa: {mapa_actual} | Agente: {personaje} | Rol: {rol} ")
        
        nueva_fila = {
            'id_partida': id_partida,
            'jugador': nombre,
            'mapa': mapa_actual,
            'modo': modo,
            'personaje': personaje, # Dato a extraer de players
            'rol': rol,       # Dato a extraer de players
            'kills': lista_estadisticas['kills'],
            'asistencias': lista_estadisticas['asistencias'], 
            'muertes': lista_estadisticas['muertes'],
            'headshots': headshot,
            'compañeros': teammates,
            'rango': rango,
            'subrango':subrango,
            'composición': composicion,
            'acs': acs,
            'fb': fb,
            'fd': fd,
            'racha': racha,
            'rondas_ganadas': rondas_w,
            'rondas_perdidas': rondas_l,
            'fecha': fecha,
            'fecha_legible': fecha_legible
        }
        # 3. Añadimos la "fila" a nuestra lista
        filas_finales.append(nueva_fila)
        
       # 4. Convertimos toda la lista en el DataFrame final
    df = pd.DataFrame(filas_finales)
    
    if df.empty:  
        print(f"! No hay partidas válidas para {nombre}. No se crea CSV.")
        return None
    
    pd.set_option('display.max_columns', None)
    #print("\n--- Vista previa del DataFrame ---")
    #print(df.columns.values)
    #print(df.head())
    
    if existe_archivo:
        df.to_csv(direccion_archivo, mode='a', header=False, index=False)
    else:
        df.to_csv(direccion_archivo, index=False)    
        
    #Añadir el jugador a la json de amigos recurrentes para luego cargarlo en el csv general de entrenamiento
    añadir_jugador_json(nombre, tag, region)
        
    #TODO Añadir el nombre del jugador a la json de entrenamiento y amigos para luego cargarlo en el csv general de entrenamiento
    return df

def añadir_jugador_json(nombre, tag, region):
    """_summary_ Función que se encarga de añadir un jugador a los JSON de amigos recurrentes y jugadores recurrentes para su posterior uso en el entrenamiento del modelo.

    Args:
        nombre (_type_): _description_ El nombre del jugador que se va a añadir a los JSON de amigos recurrentes y jugadores recurrentes. Este nombre se utiliza para identificar al jugador dentro de los JSON, y se asegura de que el jugador se añada correctamente a ambas listas para su posterior uso en el entrenamiento del modelo.
        tag (_type_): _description_ El tag del jugador que se va a añadir a los JSON de amigos recurrentes y jugadores recurrentes. Este tag se utiliza junto con el nombre del jugador para identificar al jugador dentro de los JSON, y se asegura de que el jugador se añada correctamente a ambas listas para su posterior uso en el entrenamiento del modelo.
        region (_type_): _description_ La región a la que pertenece el jugador. Esta información es necesaria para identificar al jugador dentro de los JSON y asegurar que se añada correctamente a ambas listas para su posterior uso en el entrenamiento del modelo.

    Returns:
        _type_: _description_ Devuelve None después de completar el proceso de añadir el jugador a los JSON de amigos recurrentes y jugadores recurrentes. La función no devuelve un valor específico, pero se encarga de actualizar ambos JSON con la información del nuevo jugador, asegurándose de que el jugador se añada correctamente a ambas listas para su posterior uso en el entrenamiento del modelo.
    """
    
    #Guardamos el jugador en los dos json de amigos recurrentes y jugadores recurrentes para luego cargarlo en el csv general de entrenamiento
    ruta_amigos = os.path.join(config.JSON_INFO_DIR, 'amigos_recurrentes.json')
    with open(ruta_amigos, 'r+', encoding='utf-8') as f:
        datos_amigos = json.load(f)
        nuevo_amigo = {
            "nombre": nombre,
            "tag": tag,
            "region": region
        }
        if nuevo_amigo not in datos_amigos.get("amigos", []):
            datos_amigos["amigos"].append(nuevo_amigo)
            f.seek(0)
            json.dump(datos_amigos, f, indent=4)
            f.truncate()
    
    ruta_jugadores_entrenamiento = os.path.join(config.JSON_INFO_DIR, 'jugadores_entrenamiento.json')        
    with open(ruta_jugadores_entrenamiento, 'r+', encoding='utf-8') as f:
        datos_amigos = json.load(f)
        nuevo_amigo = {
            "nombre": nombre,
            "tag": tag,
            "region": region
        }
        if nuevo_amigo not in datos_amigos.get("jugadores", []):
            datos_amigos["jugadores"].append(nuevo_amigo)
            f.seek(0)
            json.dump(datos_amigos, f, indent=4)
            f.truncate()

    
def buscar_personaje(partida, nombre_jugador, tag_jugador):
    """_summary_ Función que se encarga de buscar al jugador dentro de una partida específica, y extraer las estadísticas relevantes del jugador para esa partida. La función recorre la lista de jugadores en la partida, identifica al jugador utilizando su nombre y tag, y luego extrae información como el agente jugado, las kills, asistencias, muertes, equipo, rango, puntuación, entre otros datos relevantes para el análisis y entrenamiento del modelo. Si el jugador es encontrado en la partida, la función devuelve un diccionario con las estadísticas extraídas; si el jugador no es encontrado, devuelve None.
    """

    for jugador in partida['players']['all_players']:
        
        if jugador['name'].lower() == nombre_jugador.lower() and jugador['tag'].lower() == tag_jugador.lower():
            print(f"[DEBUG] Jugador en JSON: nombre='{jugador['name']}' tag='{jugador['tag']}'")
            personaje = jugador.get('character')
            kills = jugador['stats']['kills']
            asistencias =  jugador['stats']['assists']
            muertes = jugador.get('stats',{}).get('deaths')
            equipo = jugador.get('team')
            puntuacion = jugador.get('stats', {}).get('score')
            headshot = jugador.get('stats',{}).get('headshots')
            
            rango_completo = jugador.get('currenttier_patched')
            if rango_completo:
                partes = rango_completo.split()
                rango = partes[0]
                
                # Verificamos si existe el subrango antes de asignarlo
                subrango = partes[1] if len(partes) > 1 else ""
            else:
                rango = rango = partes[0]
                subrango = ""
            lista_estadisticas= {'personaje': personaje, 'kills':kills, 'asistencias' :asistencias,'muertes': muertes, 'equipo': equipo, 'rango': rango, 'subrango': subrango, 'score': puntuacion, 'headshot': headshot}
            return lista_estadisticas
    return None

def cargar_config_personajes():
    """_summary_ Función que se encarga de cargar la configuración de personajes desde un archivo JSON específico, y devuelve un diccionario que mapea cada personaje con su rol correspondiente. La función intenta leer el archivo JSON que contiene la configuración de personajes, y si el archivo es encontrado, carga los datos en un diccionario y lo devuelve. Si el archivo no es encontrado, la función maneja la excepción y devuelve un diccionario vacío, asegurándose de que el programa pueda continuar ejecutándose sin interrupciones incluso si el archivo de configuración no está disponible.

    Returns:
        _type_: _description_ Devuelve un diccionario que mapea cada personaje con su rol correspondiente, cargado desde un archivo JSON específico. Este diccionario se utiliza para identificar el rol de cada personaje durante el proceso de extracción de datos de las partidas, y es esencial para organizar los datos de manera adecuada para el análisis y entrenamiento del modelo. Si el archivo JSON no es encontrado, la función devuelve un diccionario vacío, lo que permite que el programa continúe ejecutándose sin interrupciones incluso si la configuración de personajes no está disponible.
    """
    ruta_agentes = os.path.join(config.JSON_INFO_DIR, 'agentes_config.json')
    try:
        with open(ruta_agentes, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: No se encontró 'agentes_config.json'. Usando diccionario vacío.")
        return {}
    
def buscar_teammates(partida_jugador, equipo_jugador, nombre_jugador, tag_jugador):
    """_summary_ Función que se encarga de buscar los compañeros de equipo del jugador dentro de una partida específica. La función recorre la lista de jugadores en la partida, identifica a los jugadores que pertenecen al mismo equipo que el jugador objetivo, y luego extrae sus nombres para crear una lista de compañeros de equipo. La función también se asegura de no incluir al jugador objetivo en la lista de compañeros, utilizando su nombre y tag para identificarlo correctamente. Si el jugador es encontrado en la partida, la función devuelve una lista con los nombres de sus compañeros de equipo; si el jugador no es encontrado, devuelve una lista vacía.

    Args:
        partida_jugador (_type_): _description_ El diccionario que contiene los datos de la partida específica en la que se va a buscar a los compañeros de equipo del jugador. Este diccionario debe contener una estructura que incluya una lista de jugadores con sus respectivos equipos, para que la función pueda identificar correctamente a los compañeros de equipo del jugador objetivo.
        equipo_jugador (_type_): _description_ El equipo al que pertenece el jugador objetivo dentro de la partida. Este valor se utiliza para identificar a los jugadores que pertenecen al mismo equipo que el jugador objetivo, y así extraer sus nombres para crear la lista de compañeros de equipo. El valor del equipo debe coincidir con el formato utilizado en el diccionario de la partida para que la función pueda identificar correctamente a los compañeros de equipo del jugador objetivo.
        nombre_jugador (_type_): _description_ El nombre del jugador objetivo del cual se van a buscar los compañeros de equipo. Este nombre se utiliza junto con el tag del jugador para identificarlo correctamente dentro de la lista de jugadores en la partida, y asegurarse de que el jugador objetivo no sea incluido en la lista de compañeros de equipo. El nombre del jugador debe coincidir con el formato utilizado en el diccionario de la partida para que la función pueda identificar correctamente al jugador objetivo y sus compañeros de equipo.
        tag_jugador (_type_): _description_ El tag del jugador objetivo del cual se van a buscar los compañeros de equipo. Este tag se utiliza junto con el nombre del jugador para identificarlo correctamente dentro de la lista de jugadores en la partida, y asegurarse de que el jugador objetivo no sea incluido en la lista de compañeros de equipo. El tag del jugador debe coincidir con el formato utilizado en el diccionario de la partida para que la función pueda identificar correctamente al jugador objetivo y sus compañeros de equipo.

    Returns:
        _type_: _description_ Devuelve una lista con los nombres de los compañeros de equipo del jugador objetivo dentro de la partida específica. Esta lista se crea al identificar a los jugadores que pertenecen al mismo equipo que el jugador objetivo, y se asegura de no incluir al jugador objetivo en la lista utilizando su nombre y tag para identificarlo correctamente. Si el jugador objetivo es encontrado en la partida, la función devuelve una lista con los nombres de sus compañeros de equipo; si el jugador no es encontrado, devuelve una lista vacía.
    """
    teammates = []
    for partida in partida_jugador.get('players', {}).get('all_players', []):
        if partida.get('team') == equipo_jugador:
            #Buscamos que no sea yo mismo, mismo tag y mismo nombre
            es_el_jugador = (partida.get('name')== nombre_jugador and partida.get('tag') == tag_jugador)
            if not es_el_jugador:
                teammates.append(partida.get('name','Desconocido'))
        
    return teammates


def obtener_composicion(partida_jugador, equipo_jugador):
    """_summary_ Función que se encarga de obtener la composición del equipo del jugador dentro de una partida específica. La función recorre la lista de jugadores en la partida, identifica a los jugadores que pertenecen al mismo equipo que el jugador objetivo, y luego extrae los personajes que están jugando para crear una lista de composición del equipo. La función también se asegura de no incluir al jugador objetivo en la lista de composición, utilizando su nombre y tag para identificarlo correctamente. Si el jugador es encontrado en la partida, la función devuelve una lista con los personajes de sus compañeros de equipo; si el jugador no es encontrado, devuelve una lista vacía.

    Args:
        partida_jugador (_type_): _description_ El diccionario que contiene los datos de la partida específica en la que se va a buscar la composición del equipo del jugador. Este diccionario debe contener una estructura que incluya una lista de jugadores con sus respectivos equipos y personajes, para que la función pueda identificar correctamente a los compañeros de equipo del jugador objetivo y extraer los personajes que están jugando para crear la lista de composición del equipo.
        equipo_jugador (_type_): _description_ Lista de los agentes

    Returns:
        _type_: _description_ Devuelve la composicion del equipo
    """
    composicion = []
    for partida in partida_jugador.get('players', {}).get('all_players', []):
        if partida.get('team') == equipo_jugador:
            composicion.append(partida.get('character',{}))
        
    return composicion

def obtener_rondas(datos_partida, equipo_jugador):
    equipo_jugador = equipo_jugador.lower()
    
    teams = datos_partida.get('teams')
    if teams is None:
        return None, None
    
    equipo_data = teams.get(equipo_jugador)
    if equipo_data is None:
        return None, None
    
    rondas_w = equipo_data.get('rounds_won')
    rondas_l = equipo_data.get('rounds_lost')
    
    return [rondas_w, rondas_l]


def calcular_impacto_ronda(partida, mi_nombre, mi_tag):
    """_summary_ Función que analiza el impacto que ha tenido el jugador en cada ronda

    Args:
        partida (_type_): _description_ El diccionario de la partida especifica
        mi_nombre (_type_): _description_ Nombre del jugador
        mi_tag (_type_): _description_ El tag del jugador

    Returns:
        _type_: _description_ las variables de las primeras sangres y muertes
    """
    first_bloods = 0
    first_deaths = 0
    
    # Creamos un diccionario para guardar la primera muerte de cada ronda
    # Clave: número de ronda, Valor: el objeto de la primera muerte encontrada
    primeras_muertes_por_ronda = {}

    # 1. Recorremos todas las bajas de la partida
    for kill in partida.get('kills', []):
        n_ronda = kill.get('round')
        tiempo = kill.get('kill_time_in_round')

        # Si no tenemos ninguna muerte registrada para esta ronda o esta es más temprana
        if n_ronda not in primeras_muertes_por_ronda:
            primeras_muertes_por_ronda[n_ronda] = kill
        else:
            if tiempo < primeras_muertes_por_ronda[n_ronda]['kill_time_in_round']:
                primeras_muertes_por_ronda[n_ronda] = kill

    # 2. Ahora que tenemos la lista de las "primeras de cada ronda", chequeamos quién eres tú
    mi_id_completo = f"{mi_nombre}#{mi_tag}"
    
    for kill in primeras_muertes_por_ronda.values():
        if kill.get('killer_display_name') == mi_id_completo:
            first_bloods += 1
        if kill.get('victim_display_name') == mi_id_completo:
            first_deaths += 1
            
    return first_bloods, first_deaths

