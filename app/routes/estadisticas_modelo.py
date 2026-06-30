import os
import re
import glob
from typing import List
import joblib
import config

from fastapi import APIRouter, HTTPException
from app.schemas import MetricasObjetivo, MetricasModelo, FeatureImportance, EstadisticasModeloResponse

router =APIRouter()

#helpers

def _ultimo_log()-> str:
    patron= os.path.join(config.LOGS_DIR, "log_20*.txt")
    archivos = sorted(glob.glob(patron))
    
    if not archivos:
        raise HTTPException (status_code=404, detail="no hya logs disponibles")
    return archivos[-1]

def _leer_log(ruta: str) -> str:
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        with open(ruta, "r", encoding="latin-1") as f:
            return f.read()

def _parsear_log(contenido: str):
    identificador_match = re.search(r"Log de entrenamiento - (.+)", contenido)
    identificador = identificador_match.group(1).strip() if identificador_match else "desconocido"
 
    tamanyo_match = re.search(r"Tama.o:\s*(\d+)", contenido)
    tamanyo_dataset = int(tamanyo_match.group(1)) if tamanyo_match else None
 
    # Separa el contenido antes del bloque "Feature Importances" para no mezclarlo con los modelos
    partes = re.split(r"\n\s*Feature Importances?:", contenido, maxsplit=1)
    cuerpo_modelos = partes[0]
    cuerpo_importancia = partes[1] if len(partes) > 1 else ""
 
    bloques = re.split(r"={5,}\n\s*(.+?)\n={5,}", cuerpo_modelos)
 
    modelos = []
    for i in range(1, len(bloques) - 1, 2):
        nombre = bloques[i].strip()
        cuerpo = bloques[i + 1]
 
        metricas = []
        for objetivo in ("rondas_ganadas", "rondas_perdidas"):
            mae_match = re.search(rf"\[{objetivo}\] MAE:\s*([\d.]+)", cuerpo)
            rmse_match = re.search(rf"\[{objetivo}\] RMSE:\s*([\d.]+)", cuerpo)
            r2_match = re.search(rf"\[{objetivo}\] R.:\s*([\d.\-]+)", cuerpo)
            if mae_match and rmse_match and r2_match:
                metricas.append(MetricasObjetivo(
                    objetivo=objetivo,
                    mae=float(mae_match.group(1)),
                    rmse=float(rmse_match.group(1)),
                    r2=float(r2_match.group(1)),
                ))
 
        cv_match = re.search(r"CV R. \(5-fold\):\s*([\d.\-]+)\s*.\s*([\d.\-]+)", cuerpo)
        cv_mean = float(cv_match.group(1)) if cv_match else None
        cv_std = float(cv_match.group(2)) if cv_match else None
 
        if metricas:
            modelos.append(MetricasModelo(
                nombre=nombre,
                metricas=metricas,
                cv_r2_mean=cv_mean,
                cv_r2_std=cv_std,
            ))
 
    feature_importance = []
    for linea in cuerpo_importancia.strip().splitlines():
        m = re.match(r"\s*([\w_]+):\s*([\d.]+)%", linea)
        if m:
            feature_importance.append(FeatureImportance(
                feature=m.group(1),
                importancia=float(m.group(2)),
            ))
 
    return identificador, tamanyo_dataset, modelos, feature_importance



@router.get("/estadisticas-modelo", response_model=EstadisticasModeloResponse)
def estadisticas_modelo():
    ruta_log = _ultimo_log()
    contenido = _leer_log(ruta_log)
    identificador, tamanyo_dataset, modelos, feature_importance = _parsear_log(contenido)
    
    if not modelos:
        raise HTTPException(status_code=500, detail="No se pudieron extraer métricas del log")
    
    return EstadisticasModeloResponse(
        identificador=identificador,
        tamanyo_dataset=tamanyo_dataset,
        modelos=modelos,
        feature_importance=feature_importance,
    )