#Clase ruta mapas

import os
import config
import json
from fastapi import APIRouter

router = APIRouter()

@router.get("/mapas")
def get_mapas():
    """Devuelve el pool de mapas disponibles."""
    mapas= cargar_mapas()
    return {"mapas": mapas}
 
 
def cargar_mapas():
    
    with open(os.path.join(config.JSON_INFO_DIR, 'info_valorant.json'), 'r') as f:
        info = json.load(f)
        mapas = info['mapas']['ranked']
        
    return mapas