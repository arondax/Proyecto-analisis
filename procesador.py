import json
import pandas as pd
import os
import csv

def extraccion_datos(nombre, tag):
    filas_finales = []
    agentes= cargar_config_personajes()
    #Leemos el archivo
    try:                                                            
        with open(f'./partidas/matches_{nombre}.json','r', encoding='utf-8') as archivo:
            datos = json.load(archivo)
    except FileNotFoundError:
        print(f"❌ No se encontró el archivo matches_{nombre}.json")
        return None
    
    racha = 0
    
    #Revisamos si el archivo existe
    direccion_archivo = f"./datasets/dataset_{nombre}.csv"
    existe_archivo= os.path.exists(direccion_archivo)
    
    for partida in datos['data']:
        MODOS_SIN_EQUIPOS = {'skirmish', 'deathmatch'}

        modo = partida.get('metadata').get('mode')
        if not modo or modo.lower() in MODOS_SIN_EQUIPOS:
            continue
        
        lista_estadisticas = buscar_personaje(partida, nombre, tag)
        
        if not lista_estadisticas:
            continue # Si no encuentra al jugador en esta partida, salta a la siguiente
        
        id_partida= partida.get('metadata').get('matchid')
        mapa_actual = partida.get('metadata').get('map')
        personaje = lista_estadisticas['personaje']
        rol = agentes.get(personaje, "Desconocido")
        rango = lista_estadisticas['rango']
        subrango = lista_estadisticas['subrango']
        headshot = lista_estadisticas['headshot']
        equipo = lista_estadisticas['equipo']
        modo = partida.get('metadata').get('mode')
        
        puntuacion_total = lista_estadisticas['score']
        #print("puntuacion: ",puntuacion_total)
        puntuacion_total = int(puntuacion_total)
        n_rondas = partida.get('metadata').get('rounds_played')
        #print("numero rondas: ",n_rondas)
        n_rondas = int(n_rondas)
        acs= puntuacion_total/n_rondas
        acs = "{:.3f}".format(acs)
        
        teammates = buscar_teammates(partida, equipo , nombre, tag)
        composicion = obtener_composicion(partida, equipo, nombre, tag)
        rondas_win_lose = obtener_rondas(partida, equipo)
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
            'rondas_perdidas': rondas_l
        }
        # 3. Añadimos la "fila" a nuestra lista
        filas_finales.append(nueva_fila)
        
       # 4. Convertimos toda la lista en el DataFrame final
    df = pd.DataFrame(filas_finales)
    pd.set_option('display.max_columns', None)
    print("\n--- Vista previa del DataFrame ---")
    #print(df.columns.values)
    print(df.head())
    
    if existe_archivo:
        df.to_csv(direccion_archivo, mode='a', header=False, index=False)
    else:
        df.to_csv(direccion_archivo, index=False)    
        
    return df
    """
    Funcion que busca dentro del archivo los valores del agente jugado, las kills, las asistencias, muertes y devuelve una lista clave valor con ellas
    """
def buscar_personaje(partida, nombre_jugador, tag_jugador):
    for jugador in partida['players']['all_players']:
        if jugador['name']==nombre_jugador and jugador['tag'] == tag_jugador :
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
    """
    Funcion que carga el json con los personajes y sus roles
    """
def cargar_config_personajes():
    try:
        with open('agentes_config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("⚠️ Error: No se encontró 'agentes_config.json'. Usando diccionario vacío.")
        return {}
    
def buscar_teammates(partida_jugador, equipo_jugador, nombre_jugador, tag_jugador):
    teammates = []
    for partida in partida_jugador.get('players', {}).get('all_players', []):
        if partida.get('team') == equipo_jugador:
            #Buscamos que no sea yo mismo, mismo tag y mismo nombre
            es_el_jugador = (partida.get('name')== nombre_jugador and partida.get('tag') == tag_jugador)
            if not es_el_jugador:
                teammates.append(partida.get('name','Desconocido'))
        
    return teammates


def obtener_composicion(partida_jugador, equipo_jugador, nombre_jugador, tag_jugador):
    composicion = []
    for partida in partida_jugador.get('players', {}).get('all_players', []):
        if partida.get('team') == equipo_jugador:
            composicion.append(partida.get('character',{}))
        
    return composicion

def obtener_rondas(datos_partida, equipo_jugador):

    equipo_jugador = equipo_jugador.lower()
    rondas_w = datos_partida.get('teams').get(equipo_jugador).get('rounds_won')
    rondas_l = datos_partida.get('teams').get(equipo_jugador).get('rounds_lost')
    rondas_w_l = [rondas_w, rondas_l]
    
    return rondas_w_l


def calcular_impacto_ronda(partida, mi_nombre, mi_tag):
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

