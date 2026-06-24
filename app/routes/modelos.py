#Clase ruta modelos
import os
import config

from fastapi import APIRouter

router = APIRouter()

@router.get("/modelos")
def get_modelos():
    """Devuelve los modelos disponibles en /modelos/."""
    if not os.path.exists(config.MODELOS_DIR):
        return {"modelos": []}
    archivos = [f.replace(".pkl", "") for f in os.listdir(config.MODELOS_DIR) if f.endswith(".pkl")]
    return {"modelos": archivos}