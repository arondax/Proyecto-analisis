# 🎯 Valorant Predicter

Sistema de predicción de rendimiento individual y resultado de partidas de Valorant, construido con Python, scikit-learn y FastAPI. Recopila datos reales vía API, entrena modelos de machine learning y sirve predicciones a través de una interfaz web.

---

## 📁 Estructura del proyecto

```
valorant-predicter/
├── main.py                         # Punto de entrada principal
├── api.py                          # Obtención de datos desde la API de Valorant
├── procesador.py                   # Extracción y estructuración de datos por partida
├── limpieza_datos.py               # Limpieza, transformación y codificación de features
├── modelos.py                      # Entrenamiento, guardado y carga de modelos ML
├── prediccion.py                   # Lógica de predicción e historial en .txt
├── entrenamiento.py                # Orquestación del pipeline completo de entrenamiento
├── script_entrenamiento.py         # Script invocado por el workflow de entrenamiento
├── script_datos.py                 # Script invocado por el workflow de recopilación
├── test_predicciones.py            # Tests con datos simulados (mock)
│
├── app/                            # Backend FastAPI
│   ├── __init__.py
│   └── app.py                      # Endpoints REST + lógica de predicción vía API
│
├── static/                         # Frontend
│   ├── valorant_predictor_frontend.html  # Versión HTML standalone
│   └── src/
│       └── App.jsx                 # Frontend React (Astralis Analytics)
│
├── .github/
│   └── workflows/
│       ├── script_github.yml       # Recopilación de datos (3 veces al día)
│       └── scrip_entrenamiento.yml # Entrenamiento semanal (lunes 8:00 UTC)
│
├── json/
│   ├── info_valorant.json          # Pool de mapas y jerarquía de rangos
│   ├── agentes_config.json         # Mapeo de agente → rol
│   ├── amigos_recurrentes.json     # Lista de jugadores del grupo de amigos
│   └── jugadores_entrenamiento.json
│
├── datasets/                       # Datos en bruto por jugador (pre-limpieza)
│   └── dataset_<jugador>.csv
│
├── dataset_ingest/                 # Datos listos para entrenamiento (post-limpieza)
│   ├── dataset_ingest_<jugador>.csv
│   └── dataset_ingest_entrenamiento_<fecha>.csv
│
├── partidas/                       # JSON brutos devueltos por la API
│   └── matches_<jugador>.json
│
├── modelos/                        # Modelos entrenados serializados
│   ├── regresionlineal.pkl
│   ├── arboldedesicion.pkl
│   ├── randomforest.pkl
│   └── logs/                       # Métricas de entrenamiento por modelo
│
└── predicciones.txt                # Historial de predicciones realizadas
```

---

## ⚙️ Requisitos

- Python 3.10+
- Dependencias principales:

```bash
pip install pandas scikit-learn joblib python-dotenv requests fastapi uvicorn
```

---

## 🔐 Configuración

Crea un archivo `.env` en la raíz del proyecto con tu clave de la [HenrikDev API](https://docs.henrikdev.xyz/):

```env
VALORANT_API_KEY=tu_clave_aqui
```

---

## 🚀 Uso

### Ejecución principal

```bash
python main.py
```

Configura las variables al inicio de `main.py` para elegir qué operaciones ejecutar:

```python
entrenar_modelo_v = False   # True para ejecutar el pipeline de entrenamiento
obtener_datos     = False   # True para llamar a la API y obtener partidas nuevas
entrenar          = False   # True para entrenar y guardar los modelos
```

### Pipeline de entrenamiento completo

```python
# entrenamiento.py — orquesta las siguientes fases:
obtencion_lista()           # Lee jugadores_entrenamiento.json
procesado_jugadores()       # Llama a la API → procesa → limpia → guarda CSV por jugador
entrenar_modelo_regression()# Une todos los CSVs → entrena los 3 modelos → guarda .pkl
```

### Predicción individual

```python
from modelos import cargar_modelo, lectura_csv
from prediccion import predecir_jugador

df     = lectura_csv("mamipito")
modelo = cargar_modelo("randomforest")

predecir_jugador(
    modelo        = modelo,
    df            = df,
    mapa          = "Breeze",
    es_main       = 1.0,
    num_amigos    = 3,
    desconocidos  = 1,
    nombre_jugador= "mamipito"
)
```

El resultado se imprime en consola y se registra en `predicciones.txt`.

---

## 🧠 Pipeline de Machine Learning

### Features de entrada

| Feature | Descripción |
|---|---|
| `rango` | Rango codificado ordinalmente (Iron=0 … Radiant=8) |
| `mapa_*` | One-Hot Encoding del mapa (12 columnas) |
| `kills`, `asistencias`, `muertes`, `headshots` | Estadísticas de combate (media histórica) |
| `acs` | Average Combat Score (media histórica) |
| `fb`, `fd` | First bloods / First deaths (media histórica) |
| `subrango` | Subrango numérico |
| `racha` | Racha de victorias consecutivas |
| `es_main` | 1 si el agente es el main del jugador, 0 si no |
| `num_amigos` | Número de amigos conocidos en el equipo |
| `desconocidos` | Número de compañeros desconocidos |

### Targets (regresión)

- `rondas_ganadas`
- `rondas_perdidas`

El resultado de la partida (Victoria / Derrota) se infiere comparando ambas predicciones.

### Modelos entrenados

| Modelo | Archivo |
|---|---|
| Regresión Lineal | `regresionlineal.pkl` |
| Árbol de Decisión | `arboldedesicion.pkl` |
| Random Forest | `randomforest.pkl` |

---

## 🗂️ Limpieza de datos (`limpieza_datos.py`)

1. **Eliminación de duplicados** por `id_partida`
2. **Filtrado de modos**: solo partidas Competitive (y Premier para el entrenamiento grupal)
3. **Detección de main**: personaje más usado en bloques de 10 partidas → columna `es_main`
4. **Detección de amigos**: cruce con `amigos_recurrentes.json` + frecuencia de aparición → columnas `num_amigos` y `desconocidos`
5. **Transformación numérica**:
   - `rango` → OrdinalEncoder
   - `mapa` → OneHotEncoder (pool fijo desde `info_valorant.json`)

---

## 🌐 API REST (`app/app.py`)

Levanta el servidor con:

```bash
uvicorn app.app:app --reload
```

El servidor escucha en `http://localhost:8000` por defecto.

### Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/` | Health check |
| `GET` | `/mapas` | Lista de mapas disponibles (desde `info_valorant.json`) |
| `GET` | `/modelos` | Modelos `.pkl` disponibles en `/modelos/` |
| `GET` | `/jugadores` | Jugadores con CSV de ingest disponible |
| `POST` | `/predecir` | Realiza una predicción completa |

### `POST /predecir`

**Body (JSON):**

```json
{
  "nombre":     "rondax",
  "tag":        "EUW",
  "region":     "eu",
  "mapa":       "Ascent",
  "es_main":    true,
  "num_amigos": 2,
  "modelo":     "randomforest"
}
```

Los valores válidos de `modelo` son `randomforest`, `arboldeDecision` y `RegresionLineal`. Si se omite, se usa `randomforest` por defecto.

**Respuesta:**

```json
{
  "nombre":          "rondax",
  "mapa":            "Ascent",
  "rondas_ganadas":  13.2,
  "rondas_perdidas": 9.8,
  "resultado":       "Victoria"
}
```

Si el jugador no tiene CSV previo, el backend ejecuta automáticamente el pipeline completo (API → procesado → limpieza) antes de predecir. Si no existen partidas competitivas válidas, devuelve `422`.

---

## 🖥️ Frontend

El proyecto tiene dos implementaciones del frontend:

### React (`static/src/App.jsx`)

Interfaz principal con estética dark tactical (Astralis Analytics). Para ejecutarla:

```bash
cd static
npm install
npm run dev
```

Características: selección de mapa por grid de botones, selector de región, slider de amigos, selector de modelo, toggle de main agente. Consume el backend en `http://localhost:8000`.

### HTML standalone (`static/valorant_predictor_frontend.html`)

Versión ligera servida directamente por FastAPI en la ruta `/app`:

```
GET http://localhost:8000/app
```

Útil para uso rápido sin necesidad de levantar Node. La `API_URL` está configurada como variable en la cabecera del script.

---

## 🤖 GitHub Actions — Workflows

### `script_github.yml` — Recopilación de datos

Ejecuta `script_datos.py` tres veces al día: 8:00, 16:00 y 23:00 UTC (10:00, 18:00 y 01:00 hora Madrid en verano). Llama a la API de Valorant, descarga las partidas recientes de todos los jugadores configurados y hace commit automático de los cambios al repositorio.

También puede lanzarse manualmente desde la pestaña **Actions** con `workflow_dispatch`.

### `scrip_entrenamiento.yml` — Entrenamiento semanal

Ejecuta `script_entrenamiento.py` cada lunes a las 8:00 UTC. Realiza el pipeline completo de entrenamiento: recopilación → procesado → limpieza → entrenamiento de los 3 modelos → guardado de `.pkl`. Hace commit automático de los modelos actualizados.

También puede lanzarse manualmente con `workflow_dispatch`.

Ambos workflows corren sobre `windows-latest`, usan Python 3.11 e inyectan la API key desde los **Secrets** del repositorio (`VALORANT_API_KEY`).

---

## 📊 Logs de modelos (`modelos/logs/`)

Cada ejecución de entrenamiento genera un log por modelo con las métricas de evaluación (MAE, RMSE, R²) sobre el conjunto de validación. Los logs permiten comparar el rendimiento entre ejecuciones y detectar degradación del modelo conforme crece el dataset.

---

## 📌 Decisiones de diseño

- **Regresión sobre clasificación**: predecir el marcador exacto (rondas ganadas/perdidas) aporta más información que un simple win/loss.
- **Modelo generalista**: el campo `jugador` se excluye del entrenamiento para que el modelo sea válido para cualquier jugador del grupo.
- **`mapa_Abyss` con valores cero**: se conserva intencionalmente para mantener compatibilidad futura con la rotación de mapas.
- **Duplicados de `id_partida` entre jugadores**: son correctos por diseño, cada fila representa el rendimiento individual de un jugador en esa partida.
- **Orden de columnas**: se usa `modelo.feature_names_in_` para alinear el input de predicción con el orden exacto del entrenamiento.

---

## 🗺️ Roadmap

- [x] Pipeline de entrenamiento automatizado con GitHub Actions
- [x] Backend FastAPI con endpoints REST
- [x] Frontend React (Astralis Analytics) + versión HTML standalone
- [ ] Despliegue en producción (Render + persistencia de datos)
- [ ] Ampliar el dataset con más jugadores y partidas
- [ ] Fine-tuning por jugador individual usando `warm_start`
- [ ] Red neuronal que incorpore todos los jugadores de una partida simultáneamente