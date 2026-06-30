import { useState } from "react";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

const label = {
  display: "block",
  fontFamily: "'Space Mono', monospace",
  fontSize: 11,
  letterSpacing: "0.12em",
  color: "var(--c-text-muted)",
  textTransform: "uppercase",
  marginBottom: 8,
};

function StatBox({ titulo, valor, sub }) {
  return (
    <div style={{
      background: "var(--c-surface)",
      border: "1px solid var(--c-border)",
      borderRadius: 10,
      padding: "1rem 1.25rem",
    }}>
      <p style={{ ...label, marginBottom: 4 }}>{titulo}</p>
      <p style={{
        fontFamily: "'Rajdhani', sans-serif",
        fontSize: 28,
        fontWeight: 700,
        color: "var(--c-text)",
        margin: 0,
      }}>{valor}</p>
      {sub && <p style={{ ...label, marginTop: 4, marginBottom: 0 }}>{sub}</p>}
    </div>
  );
}

function MapaRow({ s }) {
  const color = s.winrate >= 50 ? "#22c55e" : "#ef4444";
  return (
    <div style={{
      display: "grid",
      gridTemplateColumns: "1fr 60px 70px 80px",
      gap: 8,
      padding: "10px 0",
      borderBottom: "1px solid var(--c-border)",
      alignItems: "center",
    }}>
      <span style={{ fontFamily: "'Rajdhani', sans-serif", fontSize: 15, fontWeight: 600, color: "var(--c-text)" }}>
        {s.mapa}
      </span>
      <span style={{ fontFamily: "'Space Mono', monospace", fontSize: 11, color: "var(--c-text-muted)", textAlign: "right" }}>
        {s.partidas}p
      </span>
      <span style={{ fontFamily: "'Space Mono', monospace", fontSize: 11, color, textAlign: "right" }}>
        {s.winrate}%
      </span>
      <span style={{ fontFamily: "'Space Mono', monospace", fontSize: 11, color: "var(--c-text-muted)", textAlign: "right" }}>
        {s.media_acs} ACS
      </span>
    </div>
  );
}

export default function Estadisticas() {
  const [nombre, setNombre] = useState("");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function buscar() {
    if (!nombre.trim()) return;
    setLoading(true);
    setError(null);
    setData(null);
    try {
      const res = await fetch(`${API_BASE}/estadisticas/${nombre.trim().toLowerCase()}`);
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Error al obtener estadísticas");
      }
      setData(await res.json());
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      {/* Buscador */}
      <div style={{ marginBottom: "1.5rem" }}>
        <label style={label}>Nombre del jugador</label>
        <div style={{ display: "flex", gap: 10 }}>
          <input
            value={nombre}
            onChange={e => setNombre(e.target.value)}
            onKeyDown={e => e.key === "Enter" && buscar()}
            placeholder="rondax"
            style={{
              flex: 1,
              background: "var(--c-surface)",
              border: "1px solid var(--c-border)",
              borderRadius: 8,
              padding: "10px 14px",
              color: "var(--c-text)",
              fontFamily: "'Space Mono', monospace",
              fontSize: 13,
              outline: "none",
            }}
          />
          <button
            onClick={buscar}
            disabled={loading}
            style={{
              background: loading ? "var(--c-surface-2)" : "var(--c-accent)",
              border: "none",
              borderRadius: 8,
              padding: "10px 20px",
              color: "#fff",
              fontFamily: "'Rajdhani', sans-serif",
              fontSize: 15,
              fontWeight: 700,
              letterSpacing: "0.08em",
              textTransform: "uppercase",
              cursor: loading ? "not-allowed" : "pointer",
            }}
          >
            {loading ? "Cargando..." : "Ver →"}
          </button>
        </div>
      </div>

      {error && (
        <p style={{ color: "#ef4444", fontFamily: "'Space Mono', monospace", fontSize: 12 }}>
          {error}
        </p>
      )}

      {data && (
        <div>
          {/* Header jugador */}
          <p style={{
            fontFamily: "'Rajdhani', sans-serif",
            fontSize: 22,
            fontWeight: 700,
            color: "var(--c-text)",
            marginBottom: "1rem",
          }}>
            {data.nombre}
            <span style={{ color: "var(--c-text-muted)", fontSize: 14, fontWeight: 400, marginLeft: 10, fontFamily: "'Space Mono', monospace" }}>
              {data.total_partidas} partidas
            </span>
          </p>

          {/* Stats grid */}
          <div style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(140px, 1fr))",
            gap: 10,
            marginBottom: "1.5rem",
          }}>
            <StatBox titulo="Winrate" valor={`${data.winrate}%`} />
            <StatBox titulo="Media Kills" valor={data.media_kills} />
            <StatBox titulo="Media ACS" valor={data.media_acs} />
            <StatBox titulo="Media HS%" valor={`${(data.media_headshots * 100).toFixed(1)}%`} />
            <StatBox titulo="Agente" valor={data.agente_mas_jugado} />
            <StatBox titulo="Mejor mapa" valor={data.mejor_mapa ?? "—"} />
            <StatBox titulo="Peor mapa" valor={data.peor_mapa ?? "—"} />
          </div>

          {/* Tabla por mapa */}
          <div>
            <div style={{
              display: "grid",
              gridTemplateColumns: "1fr 60px 70px 80px",
              gap: 8,
              padding: "6px 0",
              borderBottom: "1px solid var(--c-border)",
              marginBottom: 4,
            }}>
              {["Mapa", "Partidas", "Winrate", "ACS"].map(h => (
                <span key={h} style={{ ...label, marginBottom: 0, textAlign: h === "Mapa" ? "left" : "right" }}>{h}</span>
              ))}
            </div>
            {data.stats_por_mapa.map(s => <MapaRow key={s.mapa} s={s} />)}
          </div>
        </div>
      )}
    </div>
  );
}