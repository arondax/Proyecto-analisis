import { useState, useEffect } from "react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell,
} from "recharts";

const API_BASE = "https://valorantpredicter.onrender.com";

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

function GraficaWinrate({ data }) {
  return (
    <ResponsiveContainer width="100%" height={Math.max(180, data.length * 32)}>
      <BarChart data={data} layout="vertical" margin={{ top: 0, right: 20, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--c-border)" horizontal={false} />
        <XAxis type="number" domain={[0, 100]} tick={{ fill: "var(--c-text-muted)", fontSize: 11 }} />
        <YAxis
          type="category"
          dataKey="categoria"
          width={90}
          tick={{ fill: "var(--c-text)", fontSize: 12, fontFamily: "'Space Mono', monospace" }}
        />
        <Tooltip
          contentStyle={tooltipStyle}
          formatter={(value, name, props) => [`${value}%`, `Winrate (${props.payload.partidas} partidas)`]}
        />
        <Bar dataKey="winrate" radius={[0, 4, 4, 0]}>
          {data.map((d, i) => (
            <Cell key={i} fill={d.winrate >= 50 ? "#22c55e" : "#ef4444"} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

function GraficaCorrelacion({ data }) {
  return (
    <ResponsiveContainer width="100%" height={Math.max(180, data.length * 32)}>
      <BarChart data={data} layout="vertical" margin={{ top: 0, right: 20, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--c-border)" horizontal={false} />
        <XAxis type="number" domain={[-1, 1]} tick={{ fill: "var(--c-text-muted)", fontSize: 11 }} />
        <YAxis
          type="category"
          dataKey="feature"
          width={90}
          tick={{ fill: "var(--c-text)", fontSize: 12, fontFamily: "'Space Mono', monospace" }}
        />
        <Tooltip contentStyle={tooltipStyle} formatter={(value) => [value, "Correlación"]} />
        <Bar dataKey="correlacion" radius={[0, 4, 4, 0]}>
          {data.map((d, i) => (
            <Cell key={i} fill={d.correlacion >= 0 ? "#ff4655" : "#6b7280"} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

function TablaDetalle({ data }) {
  return (
    <div style={{ marginTop: 12 }}>
      <div style={{
        display: "grid",
        gridTemplateColumns: "1fr 70px 70px 70px 70px",
        gap: 8,
        padding: "6px 0",
        borderBottom: "1px solid var(--c-border)",
        marginBottom: 4,
      }}>
        {["Categoría", "Partidas", "ACS", "Kills", "Muertes"].map(h => (
          <span key={h} style={{
            fontFamily: "'Space Mono', monospace",
            fontSize: 10,
            letterSpacing: "0.08em",
            color: "var(--c-text-muted)",
            textTransform: "uppercase",
            textAlign: h === "Categoría" ? "left" : "right",
          }}>{h}</span>
        ))}
      </div>
      {data.map(d => (
        <div key={d.categoria} style={{
          display: "grid",
          gridTemplateColumns: "1fr 70px 70px 70px 70px",
          gap: 8,
          padding: "6px 0",
          borderBottom: "1px solid var(--c-border)",
        }}>
          <span style={{ fontFamily: "'Rajdhani', sans-serif", fontSize: 13, fontWeight: 600, color: "var(--c-text)" }}>
            {d.categoria}
          </span>
          <span style={{ fontFamily: "'Space Mono', monospace", fontSize: 11, color: "var(--c-text-muted)", textAlign: "right" }}>
            {d.partidas}
          </span>
          <span style={{ fontFamily: "'Space Mono', monospace", fontSize: 11, color: "var(--c-text-muted)", textAlign: "right" }}>
            {d.media_acs}
          </span>
          <span style={{ fontFamily: "'Space Mono', monospace", fontSize: 11, color: "var(--c-text-muted)", textAlign: "right" }}>
            {d.media_kills}
          </span>
          <span style={{ fontFamily: "'Space Mono', monospace", fontSize: 11, color: "var(--c-text-muted)", textAlign: "right" }}>
            {d.media_muertes}
          </span>
        </div>
      ))}
    </div>
  );
}

export default function EstadisticasGlobales() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let activo = true;
    setLoading(true);
    setError(null);
    fetch(`${API_BASE}/estadisticas-globales`)
      .then(res => {
        if (!res.ok) throw new Error("Error al obtener estadísticas globales");
        return res.json();
      })
      .then(json => { if (activo) setData(json); })
      .catch(e => { if (activo) setError(e.message); })
      .finally(() => { if (activo) setLoading(false); });
    return () => { activo = false; };
  }, []);

  if (loading) {
    return (
      <p style={{ fontFamily: "'Space Mono', monospace", fontSize: 12, color: "var(--c-text-muted)" }}>
        Cargando estadísticas globales...
      </p>
    );
  }

  if (error) {
    return (
      <p style={{ fontFamily: "'Space Mono', monospace", fontSize: 12, color: "#ef4444" }}>
        {error}
      </p>
    );
  }

  return (
    <div>
      <p style={{
        fontFamily: "'Space Mono', monospace",
        fontSize: 12,
        color: "var(--c-text-muted)",
        marginBottom: "1.5rem",
      }}>
        Basado en {data.total_partidas} partidas del dataset de entrenamiento
      </p>

      <Seccion titulo="Winrate por mapa">
        <GraficaWinrate data={data.por_mapa} />
        <TablaDetalle data={data.por_mapa} />
      </Seccion>

      <Seccion titulo="Winrate por rango">
        <GraficaWinrate data={data.por_rango} />
        <TablaDetalle data={data.por_rango} />
      </Seccion>

      <Seccion titulo="Winrate por número de amigos">
        <GraficaWinrate data={data.por_num_amigos} />
        <TablaDetalle data={data.por_num_amigos} />
      </Seccion>

      <Seccion titulo="Main vs no main">
        <GraficaWinrate data={data.main_vs_no_main} />
        <TablaDetalle data={data.main_vs_no_main} />
      </Seccion>

      <Seccion titulo="Correlación con rondas ganadas">
        <GraficaCorrelacion data={data.correlacion} />
      </Seccion>
    </div>
  );
}