import { useState, useEffect } from "react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell,
} from "recharts";
import { PieChart, Pie, Cell as PieCell, Legend } from "recharts";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

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

const COLORES_RANGO = [
  "#ff4655", "#ff6b58", "#ffa45c", "#ffd166", "#9be564",
  "#5ed6a0", "#5ec8d6", "#7a9cff", "#a07aff", "#c77aff",
];

function winrateAColor(winrate) {
  // 0% -> rojo, 50% -> gris neutro, 100% -> verde
  if (winrate >= 50) {
    const t = Math.min((winrate - 50) / 50, 1); // 0..1
    const r = Math.round(107 + (34 - 107) * t);
    const g = Math.round(114 + (197 - 114) * t);
    const b = Math.round(128 + (94 - 128) * t);
    return `rgb(${r},${g},${b})`;
  } else {
    const t = Math.min((50 - winrate) / 50, 1); // 0..1
    const r = Math.round(107 + (239 - 107) * t);
    const g = Math.round(114 + (68 - 114) * t);
    const b = Math.round(128 + (68 - 128) * t);
    return `rgb(${r},${g},${b})`;
  }
}

function HeatmapRangoMapa({ data }) {
  if (!data || data.length === 0) return null;

  const rangos = [...new Set(data.map(d => d.rango))];
  const mapas = [...new Set(data.map(d => d.mapa))].sort();

  const lookup = {};
  data.forEach(d => { lookup[`${d.rango}__${d.mapa}`] = d; });

  return (
    <div style={{ overflowX: "auto" }}>
      <table style={{ borderCollapse: "collapse", width: "100%", minWidth: mapas.length * 70 + 90 }}>
        <thead>
          <tr>
            <th style={{
              padding: "6px 8px",
              fontFamily: "'Space Mono', monospace",
              fontSize: 10,
              color: "var(--c-text-muted)",
              textAlign: "left",
              position: "sticky",
              left: 0,
              background: "var(--c-surface)",
            }} />
            {mapas.map(mapa => (
              <th key={mapa} style={{
                padding: "6px 4px",
                fontFamily: "'Space Mono', monospace",
                fontSize: 10,
                letterSpacing: "0.05em",
                color: "var(--c-text-muted)",
                textTransform: "uppercase",
                textAlign: "center",
                whiteSpace: "nowrap",
              }}>
                {mapa}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rangos.map(rango => (
            <tr key={rango}>
              <td style={{
                padding: "6px 8px",
                fontFamily: "'Rajdhani', sans-serif",
                fontSize: 13,
                fontWeight: 600,
                color: "var(--c-text)",
                whiteSpace: "nowrap",
                position: "sticky",
                left: 0,
                background: "var(--c-surface)",
              }}>
                {rango}
              </td>
              {mapas.map(mapa => {
                const celda = lookup[`${rango}__${mapa}`];
                if (!celda) {
                  return (
                    <td key={mapa} style={{
                      padding: 4,
                      textAlign: "center",
                    }}>
                      <div style={{
                        width: "100%",
                        height: 36,
                        borderRadius: 4,
                        background: "var(--c-surface-2)",
                      }} />
                    </td>
                  );
                }
                return (
                  <td key={mapa} style={{ padding: 4, textAlign: "center" }} title={`${celda.partidas} partidas`}>
                    <div style={{
                      width: "100%",
                      height: 36,
                      borderRadius: 4,
                      background: winrateAColor(celda.winrate),
                      display: "flex",
                      flexDirection: "column",
                      alignItems: "center",
                      justifyContent: "center",
                    }}>
                      <span style={{
                        fontFamily: "'Space Mono', monospace",
                        fontSize: 11,
                        fontWeight: 700,
                        color: "#fff",
                        textShadow: "0 1px 2px rgba(0,0,0,0.4)",
                      }}>
                        {celda.winrate}%
                      </span>
                    </div>
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
      <p style={{
        fontFamily: "'Space Mono', monospace",
        fontSize: 10,
        color: "var(--c-text-muted)",
        marginTop: 10,
      }}>
        Celdas con menos de 3 partidas no se muestran. Pasa el cursor sobre una celda para ver el nº de partidas.
      </p>
    </div>
  );
}

function GraficaJugadoresPorRango({ data }) {
  const total = data.reduce((acc, d) => acc + d.jugadores, 0);
  return (
    <div>
      <div style={{ display: "flex", height: 28, borderRadius: 6, overflow: "hidden", marginBottom: 14 }}>
        {data.map((d, i) => (
          <div
            key={d.rango}
            title={`${d.rango}: ${d.jugadores} jugadores`}
            style={{
              flex: d.jugadores,
              background: COLORES_RANGO[i % COLORES_RANGO.length],
            }}
          />
        ))}
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(110px, 1fr))", gap: 8 }}>
        {data.map((d, i) => (
          <div key={d.rango} style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span style={{
              width: 10, height: 10, borderRadius: 2,
              background: COLORES_RANGO[i % COLORES_RANGO.length],
              flexShrink: 0,
            }} />
            <span style={{ fontFamily: "'Space Mono', monospace", fontSize: 11, color: "var(--c-text)" }}>
              {d.rango}
            </span>
            <span style={{ fontFamily: "'Space Mono', monospace", fontSize: 11, color: "var(--c-text-muted)", marginLeft: "auto" }}>
              {d.jugadores}
            </span>
          </div>
        ))}
      </div>
      <p style={{
        fontFamily: "'Space Mono', monospace",
        fontSize: 10,
        color: "var(--c-text-muted)",
        marginTop: 10,
      }}>
        {total} jugadores en seguimiento, agrupados por su rango más reciente
      </p>
    </div>
  );
}


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
      <Seccion titulo="Jugadores por rango actual">
        <GraficaJugadoresPorRango data={data.jugadores_por_rango} />
      </Seccion>

      <Seccion titulo="Winrate por mapa">
        <GraficaWinrate data={data.por_mapa} />
        <TablaDetalle data={data.por_mapa} />
      </Seccion>

      <Seccion titulo="Winrate por rango">
        <GraficaWinrate data={data.por_rango} />
        <TablaDetalle data={data.por_rango} />
      </Seccion>

      <Seccion titulo="Winrate por rango y mapa">
        <HeatmapRangoMapa data={data.heatmap_rango_mapa} />
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