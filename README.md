# 🎯 Astralis Analytics — Valorant Predicter

Sistema de predicción de rendimiento individual en Valorant. Recopila partidas reales vía API, entrena modelos de machine learning y sirve predicciones a través de una interfaz web con estética dark tactical.

**Demo en producción:** https://valorantpredicter.onrender.com

---

## 📁 Estructura del proyecto

```
valorant-predicter/
│
├── config.py                          # Rutas centralizadas (única fuente de verdad)
│
├── pipeline/                          # Lógica de negocio desacoplada del servidor
│   ├── api.py                         # Obtención de datos desde Henrik Dev API
│   ├── procesador.py                  # Extracción y estructuración de datos por partida
│   ├── limpieza_datos.py              # Limpieza, transformación y encoding de features
│   ├── modelos.py                     # Entrenamiento, guardado y carga de modelos ML
│   ├── predictor.py                   # Construcción de input y lógica de predicción
│   └── entrenamiento.py              # Orquestación del pipeline completo
│
├── app/                               # Backend FastAPI
│   ├── app.py                         # Punto de entrada, registro de routers, CORS
│   ├── schemas.py                     # Modelos Pydantic (request/response)
│   └── routes/
│       ├── prediccion.py              # POST /predecir
│       ├── mapas.py                   # GET /mapas
│       ├── modelos.py                 # GET /modelos
│       └── jugadores.py              # GET /jugadores
│
├── frontend/                          # Frontend React (Vite)
│   ├── src/
│   │   └── App.jsx                    # Componente principal — Astralis Analytics
│   ├── dist/                          # Build de producción (servido por FastAPI)
│   └── package.json
│
├── scripts/                           # Scripts invocados por GitHub Actions
│   ├── script_datos.py                # Recopilación de datos (ingesta)
│   └── script_entrenamiento.py        # Entrenamiento semanal
│
├── data/
│   ├── raw/                           # Datasets en bruto por jugador (pre-limpieza)
│   │   └── dataset_<jugador>.csv
│   ├── procesado/                     # Datasets listos para entrenamiento (post-limpieza)
│   │   └── dataset_ingest_<jugador>.csv
│   ├── entrenamiento/                 # Dataset consolidado para entrenar
│   │   └── dataset_ingest_entrenamiento_<fecha>.csv
│   ├── partidas/                      # JSONs brutos de la API (efímeros en Render)
│   │   └── matches_<jugador>.json
│   └── info/
│       ├── info_valorant.json         # Pool de mapas y jerarquía de rangos
│       ├── agentes_config.json        # Mapeo agente → rol
│       ├── amigos_recurrentes.json    # Pool de jugadores del grupo
│       └── jugadores_entrenamiento.json
│
├── ml/
│   └── modelos/
│       ├── regresionlineal.pkl
│       ├── arboldedesicion.pkl
│       ├── randomforest.pkl
│       └── logs/                      # Métricas de evaluación por ejecución
│
├── .github/
│   └── workflows/
│       ├── script_github.yml          # Ingesta 3x/día (8, 16, 23 UTC)
│       └── scrip_entrenamiento.yml    # Reentrenamiento semanal (lunes 8 UTC)
│
└── requirements.txt
```

---

## ⚙️ Requisitos

Python 3.10+

```bash
pip install pandas scikit-learn joblib python-dotenv requests fastapi uvicorn
```

Node 20+ para el frontend:

```bash
cd frontend && npm install && npm run build
```

---

## 🔐 Configuración

Crea un archivo `.env` en la raíz del proyecto:

```env
VALORANT_API_KEY=HDEV-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

En producción (Render), añadir la variable `VALORANT_API_KEY` en el dashboard.

---

## 🚀 Arrancar en local

```bash
# Backend
python -m uvicorn app.app:app --reload

# Frontend (desarrollo)
cd frontend && npm run dev

# Frontend (producción — build servido por FastAPI en /app)
cd frontend && npm run build
```

---

## 🌐 API REST

El servidor escucha en `http://localhost:8000` por defecto.

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET`  | `/`  | Redirige a `/app` |
| `GET`  | `/app` | Sirve el frontend (build de React) |
| `GET`  | `/mapas` | Pool de mapas ranked desde `info_valorant.json` |
| `GET`  | `/modelos` | Modelos `.pkl` disponibles |
| `GET`  | `/jugadores` | Jugadores con CSV de ingest disponible |
| `POST` | `/predecir` | Realiza una predicción completa |

### `POST /predecir`

**Body:**
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

`modelo` acepta: `randomforest`, `arboldeDecision`, `RegresionLineal`. Por defecto: `randomforest`.

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

Si el jugador no tiene CSV previo, el backend ejecuta automáticamente el pipeline completo (API → procesado → limpieza) antes de predecir. Si no hay partidas competitivas válidas devuelve `422`.

---

## 🧠 Pipeline de Machine Learning

### Features de entrada

| Feature | Descripción |
|---------|-------------|
| `rango` | Rango codificado ordinalmente (Iron=0 … Radiant=8) |
| `subrango` | Subrango numérico |
| `mapa_*` | One-Hot Encoding del mapa (12 columnas, pool fijo) |
| `kills`, `asistencias`, `muertes`, `headshots` | Media histórica del jugador |
| `acs` | Average Combat Score — media histórica |
| `fb`, `fd` | First bloods / First deaths — media histórica |
| `es_main` | 1 si el agente es el main del jugador, 0 si no |
| `num_amigos` | Amigos conocidos en el equipo |
| `desconocidos` | Compañeros desconocidos (= 4 - num_amigos) |

> `racha` fue eliminada: actuaba como proxy del resultado (importancia ~60%) en lugar de ser un predictor genuino. Su eliminación bajó R² de ~0.85 a ~0.46–0.62, rendimiento más honesto.

### Targets

- `rondas_ganadas`
- `rondas_perdidas`

El resultado (Victoria / Derrota) se infiere comparando ambas predicciones.

### Evaluación

- Métrica principal: **R²** y **MAE** con `cross_val_score` (preferido sobre split único dado el tamaño del dataset)
- Logs por modelo en `ml/modelos/logs/` tras cada reentrenamiento

---

## 🗂️ Pipeline de limpieza (`pipeline/limpieza_datos.py`)

1. Eliminación de duplicados por `id_partida`
2. Filtrado de modos: solo Competitive y Premier
3. Detección de main: agente más usado en bloques de 10 partidas → columna `es_main`
4. Detección de amigos: cruce con `amigos_recurrentes.json` → columnas `num_amigos` y `desconocidos`
5. Transformación numérica: `rango` → OrdinalEncoder, `mapa` → OneHotEncoder (pool fijo)

---

## 🤖 GitHub Actions

### `script_github.yml` — Ingesta de datos

Ejecuta `scripts/script_datos.py` tres veces al día: **8:00, 16:00 y 23:00 UTC** (10:00, 18:00 y 01:00 hora Madrid en verano). Descarga partidas recientes de todos los jugadores configurados y hace commit automático.

Puede lanzarse manualmente con `workflow_dispatch`.

### `scrip_entrenamiento.yml` — Reentrenamiento semanal

Ejecuta `scripts/script_entrenamiento.py` cada **lunes a las 8:00 UTC**. Pipeline completo: recopilación → procesado → limpieza → entrenamiento de los 3 modelos → commit de los `.pkl` actualizados.

Puede lanzarse manualmente con `workflow_dispatch`.

Ambos workflows corren en `windows-latest`, Python 3.11, e inyectan la API key desde los Secrets del repositorio (`VALORANT_API_KEY`).

---

## 🗄️ Supabase

Actualmente en uso para logging de predicciones (tabla `consultas`). Migración completa de CSVs a PostgreSQL planificada como siguiente fase.

---

## 📌 Decisiones de diseño

- **Regresión sobre clasificación:** predecir el marcador exacto aporta más información que un win/loss binario.
- **Modelo generalista:** el campo `jugador` se excluye del entrenamiento para que el modelo sea válido para cualquier jugador del pool.
- **`mapa_Abyss` con valores cero:** mantenido intencionalmente para compatibilidad futura con la rotación de mapas.
- **Duplicados de `id_partida` entre jugadores:** correctos por diseño — cada fila representa el rendimiento individual de un jugador en esa partida.
- **`os.makedirs(..., exist_ok=True)`** obligatorio en cualquier ruta de escritura nueva — el filesystem de Render es efímero.
- **`config.py` como única fuente de verdad** para todas las rutas del proyecto.

---

## 🗺️ Roadmap

- [x] Pipeline de ingesta automatizado con GitHub Actions
- [x] Backend FastAPI con arquitectura por capas (`pipeline/` + `app/routes/`)
- [x] Frontend React — Astralis Analytics (build servido por FastAPI)
- [x] Despliegue en producción (Render)
- [x] Logging de predicciones en Supabase
- [x] Sección de estadísticas por jugador (endpoint + charts con Recharts)
- [x] StandardScaler dentro de sklearn Pipeline
- [x] Añadir los amigos al json de los jugadores. 
- [x] Auto-discovery de jugadores nuevos encontrados en partidas
- [ ] Migración completa de datasets a Supabase (fase 2)
- [ ] Split temporal train/test (cuando el dataset tenga suficiente histórico fechado)
- [ ] Fine-tuning por jugador con `warm_start`
- [ ] Red neuronal incorporando todos los jugadores de una partida