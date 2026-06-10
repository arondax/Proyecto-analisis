# 🎯 Valorant Predicter (En progreso)

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
├── test_predicciones.py            # Tests con datos simulados (mock)
│
├── info_valorant.json              # Pool de mapas y jerarquía de rangos
├── agentes_config.json             # Mapeo de agente → rol
├── amigos_recurrentes.json         # Lista de jugadores del grupo de amigos
├── jugadores_entrenamiento.json    # Jugadores incluidos en el entrenamiento
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
└── modelos/                        # Modelos entrenados serializados
    ├── regresionlineal.pkl
    ├── arboldedesicion.pkl
    └── randomforest.pkl
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

## 🤖 Automatización con GitHub Actions

El entrenamiento se ejecuta automáticamente cada lunes a las 8:00 (hora local, UTC+2) mediante un workflow programado. También puede lanzarse manualmente desde la pestaña **Actions** del repositorio con `workflow_dispatch`.

---

## 📌 Decisiones de diseño

- **Regresión sobre clasificación**: predecir el marcador exacto (rondas ganadas/perdidas) aporta más información que un simple win/loss.
- **Modelo generalista**: el campo `jugador` se excluye del entrenamiento para que el modelo sea válido para cualquier jugador del grupo.
- **`mapa_Abyss` con valores cero**: se conserva intencionalmente para mantener compatibilidad futura con la rotación de mapas.
- **Duplicados de `id_partida` entre jugadores**: son correctos por diseño, cada fila representa el rendimiento individual de un jugador en esa partida.
- **Orden de columnas**: se usa `modelo.feature_names_in_` para alinear el input de predicción con el orden exacto del entrenamiento.

---

## 🗺️ Roadmap

- [ ] Ampliar el dataset con más jugadores y partidas
- [ ] Despliegue en producción (Render + persistencia de datos)
- [ ] Interfaz web accesible vía FastAPI + HTML/CSS/JS
- [ ] Red neuronal que incorpore todos los jugadores de una partida simultáneamente
- [ ] Fine-tuning por jugador individual usando `warm_start`
