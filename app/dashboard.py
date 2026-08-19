import sqlite3
from pathlib import Path
from math import radians, sin, cos, sqrt, atan2

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from streamlit_autorefresh import st_autorefresh


# =========================================================
# CONFIGURAÇÃO
# =========================================================

st.set_page_config(
    page_title="TelemetryPulse AI",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st_autorefresh(
    interval=2000,
    limit=None,
    key="telemetry_refresh",
)

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "database" / "telemetry.db"


# =========================================================
# CSS — OPERATIONAL COMMAND CENTER
# =========================================================

st.markdown(
    """
<style>
:root{
    --bg:#02070d;--panel:#07131e;--panel2:#091824;--line:#143047;
    --cyan:#16d9ff;--blue:#3b82f6;--purple:#8b5cf6;
    --green:#24e58b;--red:#ff4d5d;--amber:#f6b73c;
    --text:#f5fbff;--muted:#6f8799;
}

html,body,[data-testid="stAppViewContainer"]{
    background:
        radial-gradient(circle at 78% -8%,rgba(22,217,255,.10),transparent 28%),
        radial-gradient(circle at 0% 30%,rgba(59,130,246,.08),transparent 25%),
        linear-gradient(180deg,#02070d 0%,#030912 100%);
    color:var(--text);
}

[data-testid="stHeader"]{
    background:rgba(2,7,13,.95);
    border-bottom:1px solid rgba(20,48,71,.78);
    backdrop-filter:blur(12px);
}

#MainMenu,footer{visibility:hidden}
.block-container{max-width:1900px;padding-top:1.2rem;padding-bottom:1rem}

@keyframes opsPulse{
    0%,100%{box-shadow:0 0 0 0 rgba(36,229,139,.18)}
    50%{box-shadow:0 0 0 7px rgba(36,229,139,0)}
}
@keyframes fadeUp{
    from{opacity:0;transform:translateY(8px)}
    to{opacity:1;transform:translateY(0)}
}

.ops-header{
    display:grid;
    grid-template-columns:1.65fr .78fr .78fr;
    gap:10px;
    margin-bottom:10px;
}

.ops-hero,.ops-mini{
    border:1px solid rgba(20,48,71,.88);
    border-radius:17px;
    background:
        radial-gradient(circle at 88% 5%,rgba(22,217,255,.09),transparent 31%),
        linear-gradient(145deg,#071722,#04101a);
}

.ops-hero{
    min-height:92px;
    padding:16px 18px;
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:14px;
}

.ops-mini{padding:14px 15px;min-height:92px}
.ops-title{font-size:30px;font-weight:950;letter-spacing:-.055em;line-height:1}
.ops-title span{color:var(--cyan)}
.ops-kicker{margin-top:7px;color:#6d8598;font-size:9px;font-weight:800;letter-spacing:1.45px}

.ops-pill{
    display:flex;
    align-items:center;
    gap:8px;
    padding:7px 11px;
    border:1px solid rgba(20,48,71,.9);
    border-radius:999px;
    background:#06131e;
    color:#b4c7d5;
    font-size:9px;
    font-weight:900;
    white-space:nowrap;
}

.ops-dot{
    width:8px;height:8px;border-radius:50%;
    animation:opsPulse 1.8s infinite;
}

.ops-mini-label{font-size:8px;color:#668094;font-weight:900;letter-spacing:1px}
.ops-mini-value{font-size:17px;color:#f6fbff;font-weight:950;margin-top:8px;line-height:1.15;overflow-wrap:anywhere}
.ops-mini-sub{font-size:8px;color:#6b8497;margin-top:6px}

.kpi-grid{
    display:grid;
    grid-template-columns:repeat(6,minmax(0,1fr));
    gap:10px;
    margin-bottom:10px;
}

.kpi{
    position:relative;
    min-height:112px;
    padding:14px 15px;
    border-radius:16px;
    border:1px solid rgba(20,48,71,.88);
    background:
        radial-gradient(circle at 100% 0%,rgba(22,217,255,.08),transparent 34%),
        linear-gradient(145deg,#071722,#04101a);
    overflow:hidden;
    animation:fadeUp .35s ease both;
}

.kpi:after{
    content:"";
    position:absolute;
    left:0;right:0;top:0;height:2px;
    background:linear-gradient(90deg,transparent,var(--cyan),transparent);
    opacity:.42;
}

.kpi-label{color:#738ca0;font-size:8px;font-weight:900;letter-spacing:1px}
.kpi-value{color:#f8fbff;font-size:24px;font-weight:950;margin-top:10px;line-height:1}
.kpi-sub{color:#4fca8d;font-size:8px;margin-top:9px}

.section-title{font-size:11px;font-weight:950;color:#f5fbff;letter-spacing:.8px;margin:2px 0}
.section-subtitle{color:#6d8598;font-size:8px;margin-bottom:8px}

.device-card{
    border:1px solid rgba(20,48,71,.85);
    background:linear-gradient(145deg,#07141f,#05101a);
    border-radius:14px;
    padding:12px 13px;
    margin-bottom:8px;
}

.device-label{font-size:8px;color:#6e8799;font-weight:900;letter-spacing:.9px}
.device-value{font-size:17px;font-weight:950;margin-top:6px;color:#f7fbff;overflow-wrap:anywhere}
.device-small{font-size:8px;color:#667f92;margin-top:4px}

.ops-strip{
    display:grid;
    grid-template-columns:repeat(4,1fr);
    gap:8px;
    margin:0 0 10px 0;
}

.ops-strip-card{
    border:1px solid rgba(20,48,71,.78);
    background:#06131e;
    border-radius:12px;
    padding:9px 11px;
    min-height:56px;
}

.ops-strip-card .lbl{color:#607b8f;font-size:7px;font-weight:900;letter-spacing:.8px}
.ops-strip-card .val{color:#eaf7ff;font-size:12px;font-weight:900;margin-top:5px}

div[data-testid="stPlotlyChart"]{
    border:1px solid rgba(20,48,71,.88);
    border-radius:16px;
    overflow:hidden;
    background:#06131e;
    box-shadow:0 14px 38px rgba(0,0,0,.16);
}

div[data-testid="stDataFrame"]{
    border:1px solid rgba(20,48,71,.85);
    border-radius:16px;
    overflow:hidden;
}

.footer-status{
    margin-top:10px;
    border:1px solid rgba(20,48,71,.85);
    border-radius:14px;
    background:#06131e;
    padding:10px 13px;
    display:flex;
    justify-content:space-between;
    flex-wrap:wrap;
    gap:10px 18px;
    font-size:8px;
    color:#6f8799;
}
.footer-status strong{color:#eef8ff}

@media(max-width:1300px){
    .ops-header{grid-template-columns:1fr 1fr}
    .ops-hero{grid-column:1/-1}
    .kpi-grid{grid-template-columns:repeat(3,1fr)}
}

@media(max-width:760px){
    .ops-header{grid-template-columns:1fr}
    .kpi-grid{grid-template-columns:repeat(2,1fr)}
    .ops-strip{grid-template-columns:repeat(2,1fr)}
    .ops-title{font-size:25px}
}
</style>
""",
    unsafe_allow_html=True,
)


# =========================================================
# FUNÇÕES
# =========================================================

@st.cache_data(ttl=1)
def load_data():
    if not DB.exists():
        return pd.DataFrame()

    with sqlite3.connect(DB) as conn:
        return pd.read_sql_query(
            "SELECT * FROM telemetry ORDER BY id ASC",
            conn,
        )


def haversine(lat1, lon1, lat2, lon2):
    radius_km = 6371.0
    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)
    delta_lat = radians(lat2 - lat1)
    delta_lon = radians(lon2 - lon1)

    a = (
        sin(delta_lat / 2) ** 2
        + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon / 2) ** 2
    )

    return 2 * radius_km * atan2(sqrt(a), sqrt(1 - a))


def calculate_distance(dataframe):
    if len(dataframe) < 2:
        return 0.0

    total = 0.0
    for i in range(1, len(dataframe)):
        total += haversine(
            float(dataframe.iloc[i - 1]["latitude"]),
            float(dataframe.iloc[i - 1]["longitude"]),
            float(dataframe.iloc[i]["latitude"]),
            float(dataframe.iloc[i]["longitude"]),
        )
    return total


def calculate_status(latest_row):
    try:
        received = pd.to_datetime(
            latest_row["received_at"],
            utc=True,
            errors="coerce",
        )

        if pd.isna(received):
            return False, None

        seconds = (
            pd.Timestamp.now(tz="UTC") - received
        ).total_seconds()

        online = 0 <= seconds <= 30

        return online, max(seconds, 0)

    except Exception:
        return False, None


def safe_number(value, default=0.0):
    try:
        if pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def section(title, subtitle):
    # HTML propositalmente em UMA linha para o Markdown não exibir tags como código.
    st.markdown(
        f'<div class="section-title">{title}</div><div class="section-subtitle">{subtitle}</div>',
        unsafe_allow_html=True,
    )


def device_card(label, value, small=""):
    small_html = f'<div class="device-small">{small}</div>' if small else ""
    st.markdown(
        f'<div class="device-card"><div class="device-label">{label}</div><div class="device-value">{value}</div>{small_html}</div>',
        unsafe_allow_html=True,
    )


# =========================================================
# DADOS
# =========================================================

df = load_data()

if df.empty:
    st.markdown(
        '<div class="tp-header"><div><div class="tp-title">TelemetryPulse <span>AI</span></div><div class="tp-subtitle">REAL-TIME MOBILE TELEMETRY · FLEET INTELLIGENCE COMMAND CENTER</div></div><div class="live-offline">● AGUARDANDO GPS</div></div>',
        unsafe_allow_html=True,
    )
    st.info("Aguardando a primeira leitura de telemetria...")
    st.stop()

df = df.copy()

for column in ["latitude", "longitude", "accuracy", "speed", "altitude", "heading"]:
    if column in df.columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

df = df.dropna(subset=["latitude", "longitude"]).reset_index(drop=True)

if df.empty:
    st.warning("Há registros no banco, mas nenhuma latitude/longitude válida.")
    st.stop()

df["recorded_at_dt"] = pd.to_datetime(
    df["recorded_at"],
    errors="coerce",
    utc=True,
)

df["speed_kmh"] = df["speed"] * 3.6
# =========================================================
# DISPOSITIVO E SESSÃO ATUAL
# =========================================================

df = df.sort_values("recorded_at_dt").reset_index(drop=True)

# Ignora registros usados apenas para teste manual
df_real = df[
    ~df["device_id"]
    .astype(str)
    .str.lower()
    .str.startswith("teste-")
].copy()

if df_real.empty:
    df_real = df.copy()

# Dispositivo que enviou telemetria real mais recentemente
device_atual = str(df_real.iloc[-1]["device_id"])

df = df_real[
    df_real["device_id"].astype(str) == device_atual
].copy()

# Se houver mais de 2 minutos sem sinal,
# considera o início de uma nova sessão
df["gap_seconds"] = (
    df["recorded_at_dt"]
    .diff()
    .dt.total_seconds()
    .fillna(0)
)

df["session_id"] = (df["gap_seconds"] > 120).cumsum()

sessao_atual = df["session_id"].max()

df = (
    df[df["session_id"] == sessao_atual]
    .copy()
    .reset_index(drop=True)
)

latest = df.iloc[-1]

online, seconds_since = calculate_status(latest)

speed_now = safe_number(df["speed_kmh"].iloc[-1])
speed_avg = safe_number(df["speed_kmh"].mean())
speed_max = safe_number(df["speed_kmh"].max())
accuracy = safe_number(latest["accuracy"])
distance = calculate_distance(df)

latitude_now = float(latest["latitude"])
longitude_now = float(latest["longitude"])


# =========================================================
# CONTEXTO OPERACIONAL
# =========================================================

altitude_now = safe_number(latest["altitude"])
heading_now = safe_number(latest["heading"])

signal_quality = (
    "EXCELENTE" if accuracy <= 5
    else "BOA" if accuracy <= 15
    else "MODERADA" if accuracy <= 30
    else "BAIXA"
)

motion_state = (
    "EM MOVIMENTO" if speed_now >= 3
    else "MOVIMENTO LENTO" if speed_now >= 0.5
    else "PARADO"
)

session_started = df["recorded_at_dt"].min()

if pd.notna(session_started):
    session_seconds = max(
        (pd.Timestamp.now(tz="UTC") - session_started).total_seconds(),
        0,
    )
else:
    session_seconds = 0

session_minutes = int(session_seconds // 60)

operation_clock = (
    pd.Timestamp.now(tz="UTC")
    .tz_convert("America/Sao_Paulo")
    .strftime("%H:%M:%S")
)

last_signal_text = (
    f"{seconds_since:.0f}s"
    if seconds_since is not None
    else "—"
)


# =========================================================
# HEADER
# =========================================================

status_color = "#24e58b" if online else "#ff4d5d"
status_label = "ONLINE" if online else "OFFLINE"

st.markdown(
    f"""
    <div class="ops-header">
      <div class="ops-hero">
        <div>
          <div class="ops-title">TelemetryPulse <span>AI</span></div>
          <div class="ops-kicker">REAL-TIME MOBILE TELEMETRY · OPERATIONS COMMAND CENTER</div>
        </div>
        <div class="ops-pill">
          <span class="ops-dot" style="background:{status_color}"></span>
          {status_label} · GPS NODE
        </div>
      </div>

      <div class="ops-mini">
        <div class="ops-mini-label">DISPOSITIVO ATIVO</div>
        <div class="ops-mini-value">{device_atual}</div>
        <div class="ops-mini-sub">{motion_state} · sinal {signal_quality.lower()}</div>
      </div>

      <div class="ops-mini">
        <div class="ops-mini-label">OPERATION CLOCK</div>
        <div class="ops-mini-value">{operation_clock}</div>
        <div class="ops-mini-sub">sessão há {session_minutes} min · refresh 2s</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# KPIs
# =========================================================

cards = [
    ("STATUS", "ONLINE" if online else "OFFLINE", "telemetria do dispositivo"),
    ("VELOCIDADE ATUAL", f"{speed_now:.1f} km/h", "última leitura"),
    ("VELOCIDADE MÉDIA", f"{speed_avg:.1f} km/h", "média da sessão"),
    ("VELOCIDADE MÁXIMA", f"{speed_max:.1f} km/h", "pico registrado"),
    ("DISTÂNCIA", f"{distance:.2f} km", "trajeto acumulado"),
    ("PRECISÃO GPS", f"{accuracy:.0f} m", "última leitura"),
]

kpi_html = '<div class="kpi-grid">' + "".join(
    f'<div class="kpi"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div><div class="kpi-sub">{sub}</div></div>'
    for label, value, sub in cards
) + "</div>"

st.markdown(
    kpi_html,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="ops-strip">
      <div class="ops-strip-card"><div class="lbl">GPS QUALITY</div><div class="val">{signal_quality}</div></div>
      <div class="ops-strip-card"><div class="lbl">LAST SIGNAL</div><div class="val">{last_signal_text}</div></div>
      <div class="ops-strip-card"><div class="lbl">HEADING</div><div class="val">{heading_now:.0f}°</div></div>
      <div class="ops-strip-card"><div class="lbl">ALTITUDE</div><div class="val">{altitude_now:.1f} m</div></div>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# MAPA + PAINEL DO DISPOSITIVO
# =========================================================

map_col, device_col = st.columns(
    [4.8, 1.55],
    gap="small",
)

with map_col:
    section(
        "MAPA OPERACIONAL AO VIVO",
        "posição atual · histórico GPS · rota percorrida",
    )

    fig = go.Figure()

    if len(df) > 1:
        fig.add_trace(
            go.Scattermap(
                lat=df["latitude"],
                lon=df["longitude"],
                mode="lines",
                line=dict(
                    width=5,
                    color="#16d9ff",
                ),
                name="Rota",
                hoverinfo="skip",
            )
        )

    fig.add_trace(
        go.Scattermap(
            lat=df["latitude"],
            lon=df["longitude"],
            mode="markers",
            marker=dict(
                size=6,
                color="#2f80ed",
                opacity=0.35,
            ),
            name="Histórico",
            hovertemplate=(
                "Latitude: %{lat:.6f}<br>"
                "Longitude: %{lon:.6f}"
                "<extra></extra>"
            ),
        )
    )

    if len(df) > 1:
        fig.add_trace(
            go.Scattermap(
                lat=[float(df.iloc[0]["latitude"])],
                lon=[float(df.iloc[0]["longitude"])],
                mode="markers",
                marker=dict(
                    size=15,
                    color="#24e58b",
                    opacity=.95,
                ),
                name="Início",
                hovertemplate="<b>INÍCIO DA SESSÃO</b><extra></extra>",
            )
        )

    fig.add_trace(
        go.Scattermap(
            lat=[latitude_now],
            lon=[longitude_now],
            mode="markers",
            marker=dict(
                size=36,
                color="#ff4d5d",
                opacity=.14,
            ),
            name="Pulso",
            hoverinfo="skip",
            showlegend=False,
        )
    )

    fig.add_trace(
        go.Scattermap(
            lat=[latitude_now],
            lon=[longitude_now],
            mode="markers",
            marker=dict(
                size=18,
                color="#ff4d5d",
            ),
            name="Posição atual",
            hovertemplate=(
                "<b>Dispositivo atual</b><br>"
                "Latitude: %{lat:.6f}<br>"
                "Longitude: %{lon:.6f}"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        map=dict(
            style="carto-darkmatter",
            center=dict(
                lat=latitude_now,
                lon=longitude_now,
            ),
            zoom=16,
        ),
        height=610,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="#06131e",
        legend=dict(
            orientation="h",
            x=0.01,
            y=0.02,
            bgcolor="rgba(2,8,18,0.78)",
            font=dict(
                size=9,
                color="#d8e3ec",
            ),
        ),
    )

    st.plotly_chart(
        fig,
        key=f"live_map_{int(latest['id']) if 'id' in latest.index else len(df)}",
        config={
            "displayModeBar": False,
            "scrollZoom": True,
            "responsive": True,
        },
    )

with device_col:
    section(
        "DEVICE INTELLIGENCE",
        "última leitura recebida",
    )

    device_id = str(latest["device_id"])

    altitude_text = (
        f"{float(latest['altitude']):.1f} m"
        if pd.notna(latest["altitude"])
        else "—"
    )

    heading_text = (
        f"{float(latest['heading']):.0f}°"
        if pd.notna(latest["heading"])
        else "—"
    )

    device_card(
        "DEVICE ID",
        device_id,
        "Mobile telemetry node",
    )

    device_card(
        "LATITUDE",
        f"{latitude_now:.6f}",
    )

    device_card(
        "LONGITUDE",
        f"{longitude_now:.6f}",
    )

    device_card(
        "ALTITUDE",
        altitude_text,
    )

    device_card(
        "DIREÇÃO",
        heading_text,
    )

    if seconds_since is not None:
        device_card(
            "ÚLTIMO SINAL",
            f"{seconds_since:.0f}s",
            "desde a última posição",
        )


# =========================================================
# GRÁFICOS
# =========================================================

chart1, chart2 = st.columns(
    2,
    gap="small",
)

with chart1:
    section(
        "VELOCIDADE",
        "série temporal da sessão",
    )

    fig_speed = go.Figure()

    fig_speed.add_trace(
        go.Scatter(
            x=df["recorded_at_dt"],
            y=df["speed_kmh"],
            mode="lines+markers",
            line=dict(
                color="#16d9ff",
                width=3,
                shape="spline",
                smoothing=1.1,
            ),
            fill="tozeroy",
            fillcolor="rgba(24,215,255,0.07)",
            hovertemplate=(
                "<b>Velocidade</b><br>"
                "%{y:.1f} km/h"
                "<extra></extra>"
            ),
        )
    )

    fig_speed.update_layout(
        height=270,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="#06131e",
        plot_bgcolor="#06131e",
        font=dict(
            color="#afc1cf",
            size=9,
        ),
        showlegend=False,
    )

    fig_speed.update_xaxes(
        gridcolor="rgba(20,48,71,.50)",
        zeroline=False,
    )

    fig_speed.update_yaxes(
        gridcolor="rgba(20,48,71,.50)",
        zeroline=False,
        title="km/h",
    )

    st.plotly_chart(
        fig_speed,
        key="speed_chart",
        config={
            "displayModeBar": False,
            "responsive": True,
        },
    )

with chart2:
    section(
        "PRECISÃO GPS",
        "qualidade das leituras recebidas",
    )

    fig_accuracy = go.Figure()

    fig_accuracy.add_trace(
        go.Scatter(
            x=df["recorded_at_dt"],
            y=df["accuracy"],
            mode="lines+markers",
            line=dict(
                color="#8b5cf6",
                width=3,
                shape="spline",
                smoothing=1.1,
            ),
            fill="tozeroy",
            fillcolor="rgba(162,89,255,0.07)",
            hovertemplate=(
                "<b>Precisão</b><br>"
                "%{y:.0f} metros"
                "<extra></extra>"
            ),
        )
    )

    fig_accuracy.update_layout(
        height=270,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="#06131e",
        plot_bgcolor="#06131e",
        font=dict(
            color="#afc1cf",
            size=9,
        ),
        showlegend=False,
    )

    fig_accuracy.update_xaxes(
        gridcolor="rgba(20,48,71,.50)",
        zeroline=False,
    )

    fig_accuracy.update_yaxes(
        gridcolor="rgba(20,48,71,.50)",
        zeroline=False,
        title="metros",
    )

    st.plotly_chart(
        fig_accuracy,
        key="accuracy_chart",
        config={
            "displayModeBar": False,
            "responsive": True,
        },
    )


# =========================================================
# HISTÓRICO
# =========================================================

section(
    "EVENT STREAM",
    "últimos eventos recebidos pelo Command Center",
)

history_columns = [
    "recorded_at",
    "device_id",
    "latitude",
    "longitude",
    "accuracy",
    "speed",
    "altitude",
    "heading",
]

history_columns = [
    column
    for column in history_columns
    if column in df.columns
]

history = (
    df[history_columns]
    .tail(30)
    .iloc[::-1]
)

st.dataframe(
    history,
    hide_index=True,
    height=360,
    use_container_width=True,
)


# =========================================================
# FOOTER
# =========================================================

last_time = str(latest["recorded_at"])

st.markdown(
    f'<div class="footer-status"><span><strong>TelemetryPulse AI</strong> · Real-Time Mobile Telemetry</span><span>Leituras: <strong>{len(df)}</strong></span><span>Distância: <strong>{distance:.2f} km</strong></span><span>Última posição: <strong>{last_time}</strong></span></div>',
    unsafe_allow_html=True,
)
