import os
import config

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import estadisticas_modelo, modelos, mapas, prediccion, estadisticas, estadisticas_globales



app = FastAPI(title="Valorant Predicter", version="1.0")
app.include_router(modelos.router)
app.include_router(mapas.router)
app.include_router(prediccion.router)
app.include_router(estadisticas.router)
app.include_router(estadisticas_globales.router)
app.include_router(estadisticas_modelo.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, restringe esto a tu dominio específico
    allow_methods=['*'],
    allow_headers=['*'],
    allow_credentials=False,
)

if os.path.exists(config.DIST_DIR):
    app.mount("/assets", StaticFiles(directory=os.path.join(config.DIST_DIR, "assets")), name="assets")


#Endpoints

@app.get("/app")
def frontend():
    return FileResponse(os.path.join(config.DIST_DIR, "index.html"))

@app.get("/")
def root():
    return RedirectResponse(url="/app")



