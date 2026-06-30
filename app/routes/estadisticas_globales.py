import os
import glob
import numpy as np
import pandas as pd
import config

from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas import CorrelacionItem, StatsGrupo, StatsMapa, EstadisticasGlobalesResponse, RangoJugadores, CeldaHeatmap


router = APIRouter()

#Helpers.

def _ultimo_csv_entrenamiento() -> str:
    
    patron= os.path.join(config.DATASET_ENTRENAMIENTO_DIR, "dataset_ingest_entrenamiento_*.csv")
    
    archivos = sorted(glob.glob(patron))
    
    if not archivos:
        raise HTTPException(status_code=404, detail= "No hay datasets disponibles")

    return archivos[-1] #Devolvemos el ultimo ya que es el mas reciente

def _agrupar (df: pd.DataFrame, columna: str) -> List[StatsGrupo]:
    grupos = []
    
    for valor, grupo in df.groupby(columna):
        grupos.append(StatsGrupo(
            categoria= str(valor),
            partidas=len(grupo),
            winrate=round(grupo["victoria"].mean()*100, 1),
            media_acs=round(grupo["acs"].mean(), 2),
            media_kills=round(grupo["kills"].mean(), 2),
            media_muertes=round(grupo["muertes"].mean(), 2),
        ))
    grupos.sort(key=lambda g:g.partidas, reverse=True)
    return grupos

def _jugadores_por_rango_actual() -> List[RangoJugadores]:
    patron = os.path.join(config.DATASET_INGEST_DIR, "dataset_*.csv")
    archivos = glob.glob(patron)

    conteo = {}
    for ruta in archivos:
        try:
            df_jugador = pd.read_csv(ruta)
            if df_jugador.empty or "rango" not in df_jugador.columns:
                continue
            rango_actual = df_jugador.iloc[-1]["rango"]
            if pd.isna(rango_actual):
                continue
            rango_actual = str(rango_actual)
            conteo[rango_actual] = conteo.get(rango_actual, 0) + 1
        except Exception:
            continue

    resultado = [RangoJugadores(rango=r, jugadores=n) for r, n in conteo.items()]
    resultado.sort(key=lambda x: x.jugadores, reverse=True)
    return resultado


def _heatmap_rango_mapa(df: pd.DataFrame) -> List[CeldaHeatmap]:
    celdas = []
    for (rango, mapa), grupo in df.groupby(["rango", "mapa"]):
        if len(grupo) < 3:  # evita celdas con 1-2 partidas que distorsionan el winrate
            continue
        celdas.append(CeldaHeatmap(
            rango=str(rango),
            mapa=str(mapa),
            partidas=len(grupo),
            winrate=round(grupo["victoria"].mean() * 100, 1),
        ))
    return celdas
#Endpoints

@router.get("/estadisticas-globales", response_model=EstadisticasGlobalesResponse)
def estadisticas_globales():
    ruta = _ultimo_csv_entrenamiento()
    df = pd.read_csv(ruta)
    
    columnas_requeridas = ["rondas_ganadas", "rondas_perdidas", "mapa", "rango", "kills", "muertes", "acs", "num_amigos", "es_main"]
    
    faltantes = [c for c in columnas_requeridas if c not in df.columns]
    
    if faltantes:
        raise HTTPException(status_code=500, detail=f"Columasn faltantes en el dataset: {faltantes}")
    
    df["victoria"] = df ["rondas_ganadas"]> df["rondas_perdidas"]
    df["acs"] = pd.to_numeric(df["acs"], errors="coerce")
    df["kills"] = pd.to_numeric(df["kills"], errors="coerce")
    df["muertes"] = pd.to_numeric(df["muertes"], errors="coerce")
    
    total = len(df)
    
    por_mapa=_agrupar(df, "mapa")
    por_rango= _agrupar(df, "rango")
    por_num_amigos = _agrupar(df, "num_amigos")
    
    df["main_label"] = df["es_main"].apply(lambda x: "Main" if x== 1 or x==1.0 else "No main")
    
    main_vs_no_main =_agrupar(df, "main_label")
    
    #Correlacion
    columnas_num = ["kills", "muertes", "acs", "headshots", "num_amigos", "es_main"]
    columnas_num = [c for c in columnas_num if c in df.columns]
    df_num = df[columnas_num + ["rondas_ganadas"]].apply(pd.to_numeric, errors="coerce")
    
    correlaciones=[]
    
    corr_matrix= df_num.corr()["rondas_ganadas"].drop("rondas_ganadas")
    for feature, valor in corr_matrix.items():
        if pd.isna(valor):
            continue
        correlaciones.append(CorrelacionItem(feature=feature, correlacion=round(float(valor),3)))
    correlaciones.sort(key = lambda c: abs(c.correlacion), reverse = True) 
    
    jugadores_por_rango = _jugadores_por_rango_actual()
    heatmap_rango_mapa = _heatmap_rango_mapa(df)
    return EstadisticasGlobalesResponse(
        total_partidas=total,
        por_mapa=por_mapa,
        por_rango=por_rango,
        por_num_amigos=por_num_amigos,
        main_vs_no_main=main_vs_no_main,
        correlacion=correlaciones,
        jugadores_por_rango=jugadores_por_rango,
        heatmap_rango_mapa=heatmap_rango_mapa,
    )   