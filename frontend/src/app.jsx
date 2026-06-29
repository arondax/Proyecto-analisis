import { useState } from "react";
import { createRoot } from "react-dom/client";
import Estadisticas from "./estadisticas";

const API_BASE = "https://valorantpredicter.onrender.com";

const MAPAS = [
  "Abyss", "Ascent", "Bind", "Breeze", "Corrode",
  "Fracture", "Haven", "Icebox", "Lotus", "Pearl", "Split", "Sunset", "Summit"
];

const REGIONES = [
  { value: "eu",    label: "EU — Europa" },
  { value: "na",    label: "NA — Norteamérica" },
  { value: "ap",    label: "AP — Asia Pacífico" },
  { value: "kr",    label: "KR — Corea" },
  { value: "latam", label: "LATAM — Latinoamérica" },
  { value: "br",    label: "BR — Brasil" },
];

const MODELOS = [
  { value: "randomforest",    label: "Random Forest" },
  { value: "arboldeDecision", label: "Árbol de Decisión" },
  { value: "RegresionLineal", label: "Regresión Lineal" },
];

const labelStyle = {
  display: "block",
  fontFamily: "'Space Mono', monospace",
  fontSize: 11,
  letterSpacing: "0.12em",
  color: "var(--c-text-muted)",
  textTransform: "uppercase",
  marginBottom: 10,
};

function MapCard({ mapa, selected, onClick }) {
  return (
    <button
      type="button"
      onClick={() => onClick(mapa)}
      style={{
        background: selected ? "var(--c-accent)" : "var(--c-surface)",
        border: selected ? "1px solid var(--c-accent-border)" : "1px solid var(--c-border)",
        borderRadius: 6,
        padding: "8px 10px",
        cursor: "pointer",
        color: selected ? "#fff" : "var(--c-text-muted)",
        fontSize: 13,
        fontFamily: "'Space Mono', monospace",
        letterSpacing: "0.03em",
        transition: "all 0.15s ease",
        textAlign: "left",
        width: "100%",
      }}
    >
      {mapa}
    </button>
  );
}

function ResultCard({ data, onReset }) {
  const isVictoria = data.resultado === "Victoria";
  return (
    <div style={{ animation: "fadeSlide 0.4s ease forwards" }}>
      <div style={{
        background: "var(--c-surface)",
        border: `1px solid ${isVictoria ? "#22c55e55" : "#ef444455"}`,
        borderRadius: 12,
        padding: "2rem",
        textAlign: "center",
        marginBottom: "1.5rem",
      }}>
        <p style={{
          fontFamily: "'Space Mono', monospace",
          fontSize: 11,
          letterSpacing: "0.15em",
          color: "var(--c-text-muted)",
          textTransform: "uppercase",
          margin: "0 0 0.5rem",
        }}>
          {data.nombre} · {data.mapa}
        </p>

        <p style={{
          fontFamily: "'Rajdhani', sans-serif",
          fontSize: 52,
          fontWeight: 700,
          margin: "0.25rem 0",
          color: isVictoria ? "#22c55e" : "#ef4444",
          lineHeight: 1,
          letterSpacing: "-0.02em",
        }}>
          {data.resultado.toUpperCase()}
        </p>

        <div style={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          gap: "1.5rem",
          marginTop: "1.5rem",
        }}>
          {[
            { label: "rondas ganadas",  val: data.rondas_ganadas,  color: "#22c55e" },
            { label: "rondas perdidas", val: data.rondas_perdidas, color: "#ef4444" },
          ].map(({ label, val, color }) => (
            <div key={label} style={{ textAlign: "center" }}>
              <p style={{
                fontFamily: "'Rajdhani', sans-serif",
                fontSize: 36,
                fontWeight: 600,
                color,
                margin: 0,
                lineHeight: 1,
              }}>
                {val.toFixed(1)}
              </p>
              <p style={{
                fontFamily: "'Space Mono', monospace",
                fontSize: 10,
                letterSpacing: "0.1em",
                color: "var(--c-text-muted)",
                textTransform: "uppercase",
                margin: "4px 0 0",
              }}>
                {label}
              </p>
            </div>
          ))}
        </div>
      </div>

      <button
        onClick={onReset}
        style={{
          width: "100%",
          padding: "12px",
          background: "transparent",
          border: "1px solid var(--c-border)",
          borderRadius: 8,
          color: "var(--c-text-muted)",
          fontFamily: "'Space Mono', monospace",
          fontSize: 12,
          letterSpacing: "0.1em",
          cursor: "pointer",
          textTransform: "uppercase",
        }}
      >
        Nueva predicción
      </button>
    </div>
  );
}

function App() {
  // ── navegación ──────────────────────────────────────────────
  const [vista, setVista] = useState("prediccion");

  // ── predicción ───────────────────────────────────────────────
  const [nombre,    setNombre]    = useState("");
  const [tag,       setTag]       = useState("");
  const [region,    setRegion]    = useState("eu");
  const [mapa,      setMapa]      = useState("");
  const [esMain,    setEsMain]    = useState(true);
  const [numAmigos, setNumAmigos] = useState(2);
  const [modelo,    setModelo]    = useState("randomforest");
  const [loading,   setLoading]   = useState(false);
  const [result,    setResult]    = useState(null);
  const [error,     setError]     = useState("");

  async function handleSubmit(e) {
    e.preventDefault();
    if (!nombre.trim()) { setError("Introduce tu nombre de jugador."); return; }
    if (!tag.trim())    { setError("Introduce tu tag (sin #)."); return; }
    if (!mapa)          { setError("Selecciona un mapa antes de continuar."); return; }
    setError("");
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/predecir`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          nombre:     nombre.trim(),
          tag:        tag.trim(),
          region,
          mapa,
          es_main:    esMain ? 1.0 : 0.0,
          num_amigos: numAmigos,
          modelo,
        }),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Error del servidor");
      }
      setResult(await res.json());
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Space+Mono:wght@400;700&display=swap');

        :root {
          --c-bg:            #0d0f11;
          --c-surface:       #13161a;
          --c-surface-2:     #1a1e24;
          --c-border:        rgba(255,255,255,0.08);
          --c-accent:        #ff4655;
          --c-accent-border: #ff4655aa;
          --c-text:          #e8eaec;
          --c-text-muted:    #6b7280;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
          background: var(--c-bg);
          color: var(--c-text);
          min-height: 100vh;
          display: flex;
          align-items: flex-start;
          justify-content: center;
          padding: 2rem 1rem;
        }

        select, input[type=range], input[type=text] {
          background: var(--c-surface-2);
          border: 1px solid var(--c-border);
          border-radius: 6px;
          color: var(--c-text);
          padding: 8px 12px;
          font-family: 'Space Mono', monospace;
          font-size: 13px;
          width: 100%;
          outline: none;
          appearance: none;
          -webkit-appearance: none;
        }

        input[type=text]::placeholder { color: var(--c-text-muted); }
        input[type=text]:focus, select:focus { border-color: var(--c-accent); }

        input[type=range] {
          padding: 0;
          height: 4px;
          cursor: pointer;
          accent-color: var(--c-accent);
        }

        @keyframes fadeSlide {
          from { opacity: 0; transform: translateY(12px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        @keyframes spin {
          from { transform: rotate(0deg); }
          to   { transform: rotate(360deg); }
        }
      `}</style>

      <div style={{ width: "100%", maxWidth: 460 }}>

        {/* ── Header ── */}
        <div style={{ marginBottom: "1.5rem" }}>
          <p style={{
            fontFamily: "'Space Mono', monospace",
            fontSize: 10,
            letterSpacing: "0.2em",
            color: "var(--c-accent)",
            textTransform: "uppercase",
            marginBottom: "0.35rem",
          }}>
            Astralis Analytics
          </p>
          <h1 style={{
            fontFamily: "'Rajdhani', sans-serif",
            fontSize: 32,
            fontWeight: 700,
            color: "var(--c-text)",
            letterSpacing: "-0.01em",
            lineHeight: 1.1,
          }}>
            {vista === "prediccion" ? "Predicción de partida" : "Estadísticas"}
          </h1>
          <p style={{
            fontFamily: "'Space Mono', monospace",
            fontSize: 12,
            color: "var(--c-text-muted)",
            marginTop: "0.5rem",
          }}>
            {vista === "prediccion"
              ? "Basada en tu historial de los últimos 5 partidos"
              : "Resumen de rendimiento por jugador"}
          </p>
        </div>

        {/* ── Nav ── */}
        <div style={{ display: "flex", gap: 8, marginBottom: "1.5rem" }}>
          {["prediccion", "estadisticas"].map(v => (
            <button
              key={v}
              type="button"
              onClick={() => setVista(v)}
              style={{
                background: vista === v ? "var(--c-accent)" : "var(--c-surface)",
                border: `1px solid ${vista === v ? "var(--c-accent-border)" : "var(--c-border)"}`,
                borderRadius: 6,
                padding: "7px 16px",
                color: vista === v ? "#fff" : "var(--c-text-muted)",
                fontFamily: "'Space Mono', monospace",
                fontSize: 11,
                letterSpacing: "0.1em",
                textTransform: "uppercase",
                cursor: "pointer",
              }}
            >
              {v === "prediccion" ? "Predicción" : "Estadísticas"}
            </button>
          ))}
        </div>

        {/* ── Contenido según vista ── */}
        {vista === "estadisticas" ? (
          <Estadisticas />
        ) : (
          result ? (
            <ResultCard data={result} onReset={() => setResult(null)} />
          ) : (
            <form onSubmit={handleSubmit}>

              <div style={{ display: "grid", gridTemplateColumns: "1fr auto", gap: 8, marginBottom: "1.5rem" }}>
                <div>
                  <label style={labelStyle}>Nombre de jugador</label>
                  <input
                    type="text"
                    value={nombre}
                    onChange={e => setNombre(e.target.value)}
                    placeholder="rondax"
                    autoComplete="off"
                    spellCheck={false}
                  />
                </div>
                <div style={{ width: 100 }}>
                  <label style={labelStyle}>Tag</label>
                  <div style={{ position: "relative", display: "flex", alignItems: "center" }}>
                    <span style={{
                      position: "absolute",
                      left: 10,
                      color: "var(--c-text-muted)",
                      fontFamily: "'Space Mono', monospace",
                      fontSize: 13,
                      pointerEvents: "none",
                      userSelect: "none",
                    }}>#</span>
                    <input
                      type="text"
                      value={tag}
                      onChange={e => setTag(e.target.value)}
                      placeholder="EUW"
                      autoComplete="off"
                      spellCheck={false}
                      style={{ paddingLeft: 22 }}
                    />
                  </div>
                </div>
              </div>

              <div style={{ marginBottom: "1.5rem" }}>
                <label style={labelStyle}>Región</label>
                <select value={region} onChange={e => setRegion(e.target.value)}>
                  {REGIONES.map(r => (
                    <option key={r.value} value={r.value}>{r.label}</option>
                  ))}
                </select>
              </div>

              <div style={{ marginBottom: "1.5rem" }}>
                <label style={labelStyle}>
                  Mapa
                  {!mapa && (
                    <span style={{ color: "var(--c-accent)", marginLeft: 6, fontSize: 11 }}>
                      requerido
                    </span>
                  )}
                </label>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 6 }}>
                  {MAPAS.map(m => (
                    <MapCard key={m} mapa={m} selected={mapa === m} onClick={setMapa} />
                  ))}
                </div>
              </div>

              <div style={{ marginBottom: "1.5rem" }}>
                <label style={labelStyle}>¿Juegas tu main?</label>
                <div style={{ display: "flex", gap: 8 }}>
                  {[true, false].map(v => (
                    <button
                      key={String(v)}
                      type="button"
                      onClick={() => setEsMain(v)}
                      style={{
                        flex: 1,
                        padding: "9px",
                        background: esMain === v ? "var(--c-accent)" : "var(--c-surface-2)",
                        border: `1px solid ${esMain === v ? "var(--c-accent)" : "var(--c-border)"}`,
                        borderRadius: 6,
                        color: esMain === v ? "#fff" : "var(--c-text-muted)",
                        fontFamily: "'Space Mono', monospace",
                        fontSize: 12,
                        cursor: "pointer",
                        letterSpacing: "0.05em",
                        transition: "all 0.15s ease",
                      }}
                    >
                      {v ? "Sí" : "No"}
                    </button>
                  ))}
                </div>
              </div>

              <div style={{ marginBottom: "1.5rem" }}>
                <label style={{ ...labelStyle, display: "flex", justifyContent: "space-between" }}>
                  <span>Amigos en el equipo</span>
                  <span style={{
                    fontFamily: "'Rajdhani', sans-serif",
                    fontSize: 20,
                    fontWeight: 700,
                    color: "var(--c-text)",
                  }}>
                    {numAmigos} <span style={{ color: "var(--c-text-muted)", fontSize: 13, fontFamily: "'Space Mono'" }}>/ 4</span>
                  </span>
                </label>
                <input
                  type="range"
                  min={0} max={4} step={1}
                  value={numAmigos}
                  onChange={e => setNumAmigos(Number(e.target.value))}
                />
                <div style={{
                  display: "flex",
                  justifyContent: "space-between",
                  fontFamily: "'Space Mono', monospace",
                  fontSize: 10,
                  color: "var(--c-text-muted)",
                  marginTop: 6,
                }}>
                  {[0, 1, 2, 3, 4].map(n => <span key={n}>{n}</span>)}
                </div>
              </div>

              <div style={{ marginBottom: "2rem" }}>
                <label style={labelStyle}>Modelo</label>
                <select value={modelo} onChange={e => setModelo(e.target.value)}>
                  {MODELOS.map(m => (
                    <option key={m.value} value={m.value}>{m.label}</option>
                  ))}
                </select>
              </div>

              {error && (
                <div style={{
                  background: "#ef444415",
                  border: "1px solid #ef444440",
                  borderRadius: 6,
                  padding: "10px 14px",
                  fontFamily: "'Space Mono', monospace",
                  fontSize: 12,
                  color: "#ef4444",
                  marginBottom: "1rem",
                }}>
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                style={{
                  width: "100%",
                  padding: "14px",
                  background: loading ? "var(--c-surface-2)" : "var(--c-accent)",
                  border: "none",
                  borderRadius: 8,
                  color: loading ? "var(--c-text-muted)" : "#fff",
                  fontFamily: "'Rajdhani', sans-serif",
                  fontSize: 17,
                  fontWeight: 700,
                  letterSpacing: "0.08em",
                  textTransform: "uppercase",
                  cursor: loading ? "not-allowed" : "pointer",
                  transition: "all 0.15s ease",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: 10,
                }}
              >
                {loading ? (
                  <>
                    <span style={{
                      display: "inline-block",
                      width: 14,
                      height: 14,
                      border: "2px solid var(--c-text-muted)",
                      borderTopColor: "transparent",
                      borderRadius: "50%",
                      animation: "spin 0.7s linear infinite",
                    }} />
                    Calculando...
                  </>
                ) : "Predecir partida →"}
              </button>

            </form>
          )
        )}

      </div>
    </>
  );
}

const container = document.getElementById("root");
const root = createRoot(container);
root.render(<App />);