import { useState, useEffect } from "react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell,
} from "recharts";

const API_BASE = "http://localhost:8000";

const MODELOS = [
  { value: "randomforest",   label: "Random Forest" },
  { value: "arboldedesicion", label: "Árbol de Decisión" },
  { value: "regresionlineal", label: "Regresión Lineal" },
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

const tooltipStyle = {
  background: "var(--c-surface-2)",
  border: "1px solid var(--c-border)",
  borderRadius: 6,
  fontFamily: "'Space Mono', monospace",
  fontSize: 12,
  color: "var(--c-text)",
};

function Seccion({ titulo, children }) {
  return (
    <div style={{ marginBottom: "2rem" }}>
      <label style={labelStyle}>{titulo}</label>
      <div style={{
        background: "var(--c-surface)",
        border: "1px solid var(--c-border)",
        borderRadius: 10,
        padding: "1rem",
      }}>
        {children}
      </div>
    </div>
  );
}

function StatBox({ titulo, valor }) {
  return (
    <div style={{
      background: "var(--c-surface-2)",
      border: "1px solid var(--c-border)",
      borderRadius: 8,
      padding: "0.75rem 1rem",
      textAlign: "center",
    }}>
      <p style={{ ...labelStyle, marginBottom: 4, fontSize: 9 }}>{titulo}</p>
      <p style={{
        fontFamily: "'Rajdhani', sans-serif",
        fontSize: 22,
        fontWeight: 700,
        color: "var(--c-text)",
        margin: 0,
      }}>{valor}</p>
    </div>
  );
}

function TablaModelo({ modelo }) {
  return (
    <div style={{ marginBottom: "1rem" }}>
      <p style={{
        fontFamily: "'Rajdhani', sans-serif",
        fontSize: 17,
        fontWeight: 700,
        color: "var(--c-text)",
        marginBottom: 10,
      }}>
        {modelo.nombre}
      </p>

      {modelo.cv_r2_mean != null && (
        <p style={{
          fontFamily: "'Space Mono', monospace",
          fontSize: 11,
          color: "var(--c-text-muted)",
          marginBottom: 10,
        }}>
          CV R² (5-fold): {modelo.cv_r2_mean.toFixed(4)} ± {modelo.cv_r2_std.toFixed(4)}
        </p>
      )}

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
        {modelo.metricas.map(m => (
          <div key={m.objetivo} style={{
            background: "var(--c-surface-2)",
            border: "1px solid var(--c-border)",
            borderRadius: 8,
            padding: "0.75rem",
          }}>
            <p style={{ ...labelStyle, marginBottom: 8, fontSize: 9 }}>
              {m.objetivo.replace("_", " ")}
            </p>
            <div style={{ display: "flex", justifyContent: "space-between", fontFamily: "'Space Mono', monospace", fontSize: 11 }}>
              <span style={{ color: "var(--c-text-muted)" }}>MAE</span>
              <span style={{ color: "var(--c-text)" }}>{m.mae.toFixed(2)}</span>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", fontFamily: "'Space Mono', monospace", fontSize: 11 }}>
              <span style={{ color: "var(--c-text-muted)" }}>RMSE</span>
              <span style={{ color: "var(--c-text)" }}>{m.rmse.toFixed(2)}</span>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", fontFamily: "'Space Mono', monospace", fontSize: 11 }}>
              <span style={{ color: "var(--c-text-muted)" }}>R²</span>
              <span style={{ color: m.r2 >= 0.5 ? "#22c55e" : "#ef4444" }}>{m.r2.toFixed(4)}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function GraficaFeatureImportance({ data }) {
  return (
    <ResponsiveContainer width="100%" height={Math.max(220, data.length * 28)}>
      <BarChart data={data} layout="vertical" margin={{ top: 0, right: 20, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--c-border)" horizontal={false} />
        <XAxis type="number" tick={{ fill: "var(--c-text-muted)", fontSize: 11 }} />
        <YAxis
          type="category"
          dataKey="feature"
          width={110}
          tick={{ fill: "var(--c-text)", fontSize: 11, fontFamily: "'Space Mono', monospace" }}
        />
        <Tooltip contentStyle={tooltipStyle} formatter={(value) => [value, "Importancia"]} />
        <Bar dataKey="importancia" radius={[0, 4, 4, 0]} fill="#ff4655" />
      </BarChart>
    </ResponsiveContainer>
  );
}
function formatearFecha(identificador) {
  if (!/^\d{8}$/.test(identificador)) return identificador;
  const anio = identificador.slice(0, 4);
  const mes = identificador.slice(4, 6);
  const dia = identificador.slice(6, 8);
  return `${dia}/${mes}/${anio}`;
}

export default function EstadisticasModelo() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let activo = true;
    setLoading(true);
    setError(null);
    fetch(`${API_BASE}/estadisticas-modelo/`)
      .then(res => {
        if (!res.ok) throw new Error("Error al obtener estadísticas del modelo");
        return res.json();
      })
      .then(json => { if (activo) setData(json); })
      .catch(e => { if (activo) setError(e.message); })
      .finally(() => { if (activo) setLoading(false); });
    return () => { activo = false; };
  },[]);

  return (
    <div>
      <div style={{ marginBottom: "1.5rem" }}>
        <label style={labelStyle}>Estadsiticas de los modelos Randomforest, Regresion lineal y arbol de decisiones</label>
      </div>

      {loading && (
        <p style={{ fontFamily: "'Space Mono', monospace", fontSize: 12, color: "var(--c-text-muted)" }}>
          Cargando estadísticas del modelo...
        </p>
      )}

      {error && (
        <p style={{ fontFamily: "'Space Mono', monospace", fontSize: 12, color: "#ef4444" }}>
          {error}
        </p>
      )}

      {data && !loading && !error && (
        <>
          <div style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: 10,
            marginBottom: "1.5rem",
          }}>
            <StatBox titulo="Dataset" valor={formatearFecha(data.identificador)} />
            <StatBox titulo="Tamaño" valor={data.tamanyo_dataset ?? "—"} />
          </div>

          <Seccion titulo="Métricas por modelo">
            {data.modelos.map(m => <TablaModelo key={m.nombre} modelo={m} />)}
          </Seccion>

          {data.feature_importance.length > 0 && (
            <Seccion titulo={`Feature importance — Modelos`}>
              <GraficaFeatureImportance data={data.feature_importance} />
            </Seccion>
          )}
        </>
      )}
    </div>
  );
}