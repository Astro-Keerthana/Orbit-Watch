import io
import re
import math
import time
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta, timezone
from PIL import Image, ImageEnhance
import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG — must be first Streamlit call
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title  = "OrbitWatch",
    page_icon   = "🚀",
    layout      = "wide",
    initial_sidebar_state = "expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# CUSTOM CSS — deep space dark theme
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Global dark space theme ── */
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&display=swap');

html, body, [class*="css"] {
    background-color: #08080f !important;
    color: #e0e8ff !important;
}

/* ── Main container ── */
.main .block-container {
    background-color: #08080f;
    padding-top: 1rem;
    max-width: 100%;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a0a1a 0%, #0d1230 100%);
    border-right: 1px solid #1e3a7a;
}

/* ── Metric cards ── */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #0d1230 0%, #141e45 100%);
    border: 1px solid #1e3a7a;
    border-radius: 12px;
    padding: 16px;
    box-shadow: 0 0 20px rgba(0, 140, 255, 0.15);
}

[data-testid="metric-container"] label {
    color: #6080c0 !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.1em;
}

[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #00dcff !important;
    font-family: 'Orbitron', monospace !important;
    font-size: 1.4rem !important;
    font-weight: 700;
}

/* ── Headers ── */
h1, h2, h3 {
    font-family: 'Orbitron', monospace !important;
    letter-spacing: 0.05em;
}

h1 { color: #00dcff !important; text-shadow: 0 0 20px rgba(0,220,255,0.5); }
h2 { color: #0096ff !important; }
h3 { color: #00c878 !important; }

/* ── Divider glow ── */
hr {
    border: none;
    height: 1px;
    background: linear-gradient(90deg,
        transparent, #0096ff, #00dcff, #0096ff, transparent);
    margin: 1.5rem 0;
}

/* ── Threat badge styles ── */
.threat-critical { background:#ff1a1a; color:#fff; padding:3px 10px;
                   border-radius:6px; font-weight:bold; font-size:0.8rem; }
.threat-watch    { background:#cc2200; color:#fff; padding:3px 10px;
                   border-radius:6px; font-weight:bold; font-size:0.8rem; }
.threat-alert    { background:#cc6600; color:#fff; padding:3px 10px;
                   border-radius:6px; font-weight:bold; font-size:0.8rem; }
.threat-monitor  { background:#996600; color:#fff; padding:3px 10px;
                   border-radius:6px; font-weight:bold; font-size:0.8rem; }
.threat-elevated { background:#887700; color:#fff; padding:3px 10px;
                   border-radius:6px; font-weight:bold; font-size:0.8rem; }
.threat-safe     { background:#006633; color:#fff; padding:3px 10px;
                   border-radius:6px; font-weight:bold; font-size:0.8rem; }

/* ── PHA badge ── */
.pha-badge { background:#dc1e1e; color:#fff; padding:2px 8px;
             border-radius:4px; font-size:0.75rem; font-weight:bold;
             margin-left:6px; }

/* ── NEO card ── */
.neo-card {
    background: linear-gradient(135deg, #0a0f28 0%, #111830 100%);
    border: 1px solid #1e3a7a;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 10px;
    box-shadow: 0 2px 12px rgba(0,80,200,0.2);
    transition: border-color 0.2s;
}
.neo-card:hover { border-color: #0096ff; }

/* ── Stmetric delta ── */
[data-testid="stMetricDelta"] { color: #00c878 !important; }

/* ── Dataframe ── */
.stDataFrame { border: 1px solid #1e3a7a; border-radius: 8px; }

/* ── Selectbox / slider ── */
.stSelectbox label, .stSlider label {
    color: #6080c0 !important;
    font-family: 'Share Tech Mono', monospace !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    background: #0d1230 !important;
    border: 1px solid #1e3a7a !important;
    border-radius: 8px !important;
    color: #00dcff !important;
    font-family: 'Share Tech Mono', monospace !important;
}

/* ── Button ── */
.stButton button {
    background: linear-gradient(135deg, #003080, #0050c0);
    color: #00dcff;
    border: 1px solid #0096ff;
    border-radius: 8px;
    font-family: 'Share Tech Mono', monospace;
    letter-spacing: 0.05em;
    transition: all 0.2s;
}
.stButton button:hover {
    background: linear-gradient(135deg, #0050c0, #0080ff);
    box-shadow: 0 0 15px rgba(0,150,255,0.4);
}

/* ── Tab styling ── */
.stTabs [data-baseweb="tab-list"] {
    background: #0a0f28;
    border-bottom: 1px solid #1e3a7a;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    color: #6080c0;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.85rem;
    letter-spacing: 0.05em;
    border-radius: 6px 6px 0 0;
}
.stTabs [aria-selected="true"] {
    color: #00dcff !important;
    background: #0d1a40 !important;
    border-bottom: 2px solid #00dcff !important;
}

/* ── Progress bar ── */
.stProgress > div > div {
    background: linear-gradient(90deg, #003080, #00dcff) !important;
}

/* ── Info/warning boxes ── */
.stAlert {
    background: #0a0f28 !important;
    border-left: 4px solid #0096ff !important;
    color: #e0e8ff !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
# At the TOP of nasa_dashboard.py — replace the old constants block
# ─────────────────────────────────────────────────────────────────────────────




NASA_API_KEY   = "slGnKhhfZrANBVSzT3sLN1CEuuXaszvb9IIC5NBW"
BASE_URL       = "https://api.nasa.gov"
IMG_LIB_URL    = "https://images-api.nasa.gov"
MOON_DIST_KM   = 384_400
ARTEMIS_LAUNCH = datetime(2026, 4, 1, 22, 35, 12, tzinfo=timezone.utc)

THREAT_LEVELS = [
    (1_000_000,   "CRITICAL",  "#ff1a1a"),
    (5_000_000,   "WATCH",     "#cc2200"),
    (10_000_000,  "ALERT",     "#cc6600"),
    (20_000_000,  "MONITOR",   "#cc8800"),
    (40_000_000,  "ELEVATED",  "#888800"),
    (float("inf"),"SAFE",      "#006633"),
]

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def get_threat(miss_km: float) -> tuple:
    for threshold, level, color in THREAT_LEVELS:
        if miss_km < threshold:
            return level, color
    return "SAFE", "#006633"


def size_label(avg_m: float) -> str:
    if avg_m < 10:   return "🚗 car"
    if avg_m < 25:   return "🏠 house"
    if avg_m < 60:   return "✈️ aircraft"
    if avg_m < 150:  return "🏟️ stadium"
    if avg_m < 400:  return "🏙️ skyscraper"
    if avg_m < 1000: return "⛰️ mountain"
    return "🌆 city-sized"


# ─────────────────────────────────────────────────────────────────────────────
# DATA FETCHERS — all cached for performance
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)   # cache 1 hour
def fetch_apod() -> dict:
    """Fetch APOD with 3-layer fallback."""
    for attempt in range(3):
        try:
            r = requests.get(
                f"{BASE_URL}/planetary/apod",
                params={"api_key": NASA_API_KEY},
                timeout=20,
            )
            r.raise_for_status()
            return r.json()
        except Exception:
            time.sleep((attempt + 1) * 3)

    # Web scrape fallback
    try:
        r = requests.get(
            "https://apod.nasa.gov/apod/astropix.html",
            headers={"User-Agent": "Orbit-Watch/1.0"},
            timeout=15,
        )
        if r.status_code == 200:
            html = r.text
            title_m = re.search(
                r"<title>APOD:\s*[\d\s]+[-–]\s*(.+?)</title>",
                html, re.IGNORECASE
            )
            expl_m = re.search(
                r"<p>\s*<b>\s*Explanation:\s*</b>\s*(.*?)\s*</p>",
                html, re.DOTALL | re.IGNORECASE
            )
            img_m = re.search(r'<a href="(image/[^"]+)"', html, re.IGNORECASE)
            return {
                "title":       title_m.group(1).strip() if title_m
                               else "Today's Astronomy Picture",
                "date":        datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                "explanation": re.sub(r"<[^>]+>", "",
                               expl_m.group(1))[:800] if expl_m else "",
                "media_type":  "image",
                "url":         f"https://apod.nasa.gov/apod/{img_m.group(1)}"
                               if img_m else "https://apod.nasa.gov",
                "hdurl":       f"https://apod.nasa.gov/apod/{img_m.group(1)}"
                               if img_m else "",
            }
    except Exception:
        pass

    return {
        "title": "NASA Astronomy Picture of the Day",
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "explanation": "APOD temporarily unavailable. Visit apod.nasa.gov",
        "media_type": "image", "url": "https://apod.nasa.gov", "hdurl": "",
    }


@st.cache_data(ttl=1800)   # cache 30 min
def fetch_neo_feed(days: int = 7) -> list:
    """Fetch and enrich NEO feed."""
    now      = datetime.now(timezone.utc)
    all_neos = []
    chunk    = now

    while chunk < now + timedelta(days=days):
        end = min(chunk + timedelta(days=7), now + timedelta(days=days))
        try:
            r = requests.get(
                f"{BASE_URL}/neo/rest/v1/feed",
                params={
                    "start_date": chunk.strftime("%Y-%m-%d"),
                    "end_date":   end.strftime("%Y-%m-%d"),
                    "api_key":    NASA_API_KEY,
                },
                timeout=20,
            )
            r.raise_for_status()
            for date_str, objs in r.json().get(
                "near_earth_objects", {}
            ).items():
                for obj in objs:
                    all_neos.append(_enrich(obj, date_str))
        except Exception:
            pass
        chunk = end + timedelta(days=1)
        time.sleep(0.2)

    all_neos.sort(key=lambda x: x["miss_km"])
    return all_neos


def _enrich(obj: dict, date_str: str) -> dict:
    d     = obj.get("estimated_diameter", {}).get("meters", {})
    dmin  = d.get("estimated_diameter_min", 0)
    dmax  = d.get("estimated_diameter_max", 0)
    ca    = obj["close_approach_data"][0]
    mkm   = float(ca["miss_distance"]["kilometers"])
    mau   = float(ca["miss_distance"]["astronomical"])
    mld   = float(ca["miss_distance"]["lunar"])
    vkms  = float(ca["relative_velocity"]["kilometers_per_second"])
    vkmh  = float(ca["relative_velocity"]["kilometers_per_hour"])
    threat, color = get_threat(mkm)
    return {
        "name":     obj["name"].strip("()"),
        "date":     date_str,
        "ca_date":  ca["close_approach_date_full"],
        "miss_km":  mkm,  "miss_au": mau,  "miss_ld": mld,
        "diam_min": dmin, "diam_max": dmax,
        "diam_avg": (dmin + dmax) / 2,
        "vel_kms":  vkms, "vel_kmh": vkmh,
        "hazardous":obj["is_potentially_hazardous_asteroid"],
        "abs_mag":  obj.get("absolute_magnitude_h", 0),
        "threat":   threat, "color": color,
        "size_lbl": size_label((dmin + dmax) / 2),
        "orb_class":obj.get("orbital_data", {}).get(
                    "orbit_class", {}).get("orbit_class_type", "NEA"),
    }


@st.cache_data(ttl=3600)
def fetch_mars_photos() -> list:
    """Fetch Mars rover photos."""
    try:
        r = requests.get(
            f"{IMG_LIB_URL}/search",
            params={
                "q": "perseverance jezero mars surface 2025",
                "media_type": "image",
                "year_start": "2024",
                "page_size": "12",
            },
            timeout=15,
        )
        if r.status_code == 200:
            items = r.json().get("collection", {}).get("items", [])
            photos = []
            for item in items[:6]:
                d = item.get("data", [{}])[0]
                links = item.get("links", [{}])
                src = links[0].get("href", "") if links else ""
                if src:
                    photos.append({
                        "id":     d.get("nasa_id", "N/A"),
                        "date":   d.get("date_created", "")[:10],
                        "title":  d.get("title", "Mars Surface"),
                        "url":    src,
                        "camera": d.get("secondary_creator", "NASA Camera"),
                    })
            if photos:
                return photos
    except Exception:
        pass

    return [
        {"id": "PIA26571", "date": "2025-04-10",
         "title": "Perseverance on Mars",
         "url": "https://photojournal.jpl.nasa.gov/jpeg/PIA26571.jpg",
         "camera": "Mastcam-Z"},
        {"id": "PIA26528", "date": "2025-04-03",
         "title": "Jezero Crater",
         "url": "https://photojournal.jpl.nasa.gov/jpeg/PIA26528.jpg",
         "camera": "Navigation Camera"},
        {"id": "PIA26529", "date": "2025-04-10",
         "title": "Rocky Martian Terrain",
         "url": "https://photojournal.jpl.nasa.gov/jpeg/PIA26529.jpg",
         "camera": "Mastcam-Z Right"},
    ]


def get_artemis_status() -> dict:
    now     = datetime.now(timezone.utc)
    elapsed = (now - ARTEMIS_LAUNCH).total_seconds() / 3600

    # ✅ FIXED: Corrected phase boundaries based on confirmed April 10 splashdown
    # Launch:     April 1  22:35 UTC = MET 0h
    # Lunar flyby:April 6  ~22:35 UTC = MET ~96h
    # Splashdown: April 10 ~00:06 UTC = MET ~217.5h
    PHASES = [
        (0,     2,    "LAUNCH & ASCENT",   0,                    400),
        (2,     8,    "EARTH ORBIT / TLI", 400,                  50_000),
        (8,     72,   "TRANSLUNAR COAST",  50_000,               MOON_DIST_KM),
        (72,    96,   "LUNAR FLYBY",       MOON_DIST_KM,         MOON_DIST_KM - 8_000),
        (96,    210,  "RETURN COAST",      MOON_DIST_KM - 8_000, 0),   # ✅ was 192
        (210,   217,  "REENTRY",           0,                    0),    # ✅ was 192–240
        (217,   float("inf"), "MISSION COMPLETE", 0,             0),    # ✅ added
    ]

    if elapsed < 0:
        cd  = ARTEMIS_LAUNCH - now
        d   = cd.days
        h   = cd.seconds // 3600
        m   = (cd.seconds % 3600) // 60
        return {
            "phase":       "PRE-LAUNCH",
            "status":      f"T−{d}d {h:02d}h {m:02d}m",
            "distance_km": 0,
            "moon_pct":    0.0,
            "mission_pct": 0.0,   # ✅ NEW field
            "launched":    False,
            "crew": ["Reid Wiseman", "Victor Glover",
                     "Christina Koch", "Jeremy Hansen"],
        }

    # ── Phase + distance interpolation ───────────────────────────────────────
    phase = "MISSION COMPLETE"
    dist  = 0
    for h0, h1, name, d0, d1 in PHASES:
        if h0 <= elapsed < h1:
            # guard against float("inf") in denominator
            span = h1 - h0 if h1 != float("inf") else 1
            t     = (elapsed - h0) / span
            phase = name
            dist  = int(d0 + t * (d1 - d0))
            break

    # ── MET timer ────────────────────────────────────────────────────────────
    d_e = int(elapsed // 24)
    h_e = int(elapsed  % 24)
    m_e = int((elapsed  % 1) * 60)

    # ✅ FIX 2: mission_pct = overall mission progress (0→100%)
    #    Based on confirmed 217.5h total mission duration
    TOTAL_MISSION_H = 217.5
    mission_pct = min(100.0, max(0.0, elapsed / TOTAL_MISSION_H * 100))

    # moon_pct kept for trajectory chart (distance-based, clamped 0–100)
    moon_pct = min(100.0, max(0.0, dist / MOON_DIST_KM * 100))

    return {
        "phase":       phase,
        "status":      f"MET +{d_e}d {h_e:02d}h {m_e:02d}m",
        "distance_km": dist,
        "moon_pct":    moon_pct,       # used by trajectory chart only
        "mission_pct": mission_pct,    # ✅ used by metric + progress bar
        "launched":    True,
        "crew": ["Reid Wiseman", "Victor Glover",
                 "Christina Koch", "Jeremy Hansen"],
    }


@st.cache_data(ttl=300)
def load_image_url(url: str):
    """Download and return PIL image from URL."""
    if not url:
        return None
    try:
        r = requests.get(
            url,
            headers={"User-Agent": "Orbit-Warch/1.0"},
            timeout=15,
        )
        if r.status_code == 200:
            return Image.open(io.BytesIO(r.content)).convert("RGB")
    except Exception:
        pass
    return None


# ─────────────────────────────────────────────────────────────────────────────
# PLOTLY CHART BUILDERS
# ─────────────────────────────────────────────────────────────────────────────
def neo_scatter_chart(neos: list) -> go.Figure:
    """Interactive scatter: miss distance vs velocity, sized by diameter."""
    df = pd.DataFrame([{
        "Name":      o["name"][:20],
        "Miss (Mkm)":o["miss_km"] / 1e6,
        "Miss (LD)": o["miss_ld"],
        "Vel (km/s)":o["vel_kms"],
        "Diam (m)":  o["diam_avg"],
        "Threat":    o["threat"],
        "PHA":       "⚠ YES" if o["hazardous"] else "no",
        "Color":     o["color"],
        "Date":      o["ca_date"][:10],
    } for o in neos[:40]])

    color_map = {
        "CRITICAL": "#ff1a1a", "WATCH":    "#cc2200",
        "ALERT":    "#cc6600", "MONITOR":  "#cc8800",
        "ELEVATED": "#ccaa00", "SAFE":     "#00aa55",
    }

    fig = go.Figure()
    for threat, grp in df.groupby("Threat"):
        fig.add_trace(go.Scatter(
            x    = grp["Miss (LD)"],
            y    = grp["Vel (km/s)"],
            mode = "markers",
            name = threat,
            marker = dict(
                size  = (grp["Diam (m)"].clip(5, 500) / 10).clip(6, 40),
                color = color_map.get(threat, "#888"),
                opacity = 0.85,
                line  = dict(color="#ffffff", width=0.5),
            ),
            text = grp.apply(
                lambda r: (
                    f"<b>{r['Name']}</b><br>"
                    f"Date: {r['Date']}<br>"
                    f"Distance: {r['Miss (Mkm)']:.3f}M km "
                    f"({r['Miss (LD)']:.2f} LD)<br>"
                    f"Velocity: {r['Vel (km/s)']:.2f} km/s<br>"
                    f"Diameter: {r['Diam (m)']:.0f}m<br>"
                    f"PHA: {r['PHA']}"
                ), axis=1
            ),
            hovertemplate = "%{text}<extra></extra>",
        ))

    fig.update_layout(
        title       = dict(
            text      = "☄  NEO Threat Map — Miss Distance vs Velocity",
            font      = dict(color="#00dcff", size=16, family="monospace"),
            x         = 0.5,
        ),
        paper_bgcolor = "#08080f",
        plot_bgcolor  = "#0a0f28",
        font          = dict(color="#a0b8e0", family="monospace"),
        xaxis = dict(
            title      = "Miss Distance (Lunar Distances)",
            gridcolor  = "#1a2a4a",
            zerolinecolor = "#1a2a4a",
            tickfont   = dict(color="#6080c0"),
        ),
        yaxis = dict(
            title      = "Relative Velocity (km/s)",
            gridcolor  = "#1a2a4a",
            zerolinecolor = "#1a2a4a",
            tickfont   = dict(color="#6080c0"),
        ),
        legend = dict(
            bgcolor     = "#0a0f28",
            bordercolor = "#1e3a7a",
            borderwidth = 1,
            font        = dict(color="#a0b8e0"),
        ),
        height = 480,
        margin = dict(l=60, r=20, t=60, b=60),
    )
    return fig


def neo_timeline_chart(neos: list) -> go.Figure:
    """Bar chart: NEOs per day this week."""
    from collections import Counter
    counts = Counter(o["date"] for o in neos)
    dates  = sorted(counts.keys())
    vals   = [counts[d] for d in dates]

    pha_counts = Counter(
        o["date"] for o in neos if o["hazardous"]
    )
    pha_vals = [pha_counts.get(d, 0) for d in dates]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x    = dates, y = vals,
        name = "Total NEOs",
        marker_color = "#0050c0",
        marker_line  = dict(color="#0096ff", width=1),
    ))
    fig.add_trace(go.Bar(
        x    = dates, y = pha_vals,
        name = "PHA (Hazardous)",
        marker_color = "#cc2200",
        marker_line  = dict(color="#ff4400", width=1),
    ))
    fig.update_layout(
        title       = dict(
            text  = "📅  NEO Activity — Objects Per Day",
            font  = dict(color="#00dcff", size=16, family="monospace"),
            x     = 0.5,
        ),
        paper_bgcolor = "#08080f",
        plot_bgcolor  = "#0a0f28",
        font          = dict(color="#a0b8e0", family="monospace"),
        barmode       = "overlay",
        xaxis = dict(gridcolor="#1a2a4a", tickfont=dict(color="#6080c0")),
        yaxis = dict(
            title     = "Number of Objects",
            gridcolor = "#1a2a4a",
            tickfont  = dict(color="#6080c0"),
        ),
        legend = dict(
            bgcolor="#0a0f28", bordercolor="#1e3a7a",
            borderwidth=1, font=dict(color="#a0b8e0"),
        ),
        height = 320,
        margin = dict(l=60, r=20, t=60, b=60),
    )
    return fig


def artemis_trajectory_chart(art: dict) -> go.Figure:
    """Animated arc showing Orion's position."""
    theta = [i for i in range(0, 181, 2)]
    x_arc = [math.cos(math.radians(t)) for t in theta]
    y_arc = [math.sin(math.radians(t)) for t in theta]

    fig = go.Figure()

    # Trajectory arc
    fig.add_trace(go.Scatter(
        x=x_arc, y=y_arc,
        mode="lines",
        line=dict(color="#1e3a7a", width=2, dash="dot"),
        name="Trajectory",
        hoverinfo="skip",
    ))

    # Earth
    fig.add_trace(go.Scatter(
        x=[-1], y=[0],
        mode="markers+text",
        marker=dict(size=30, color="#0050c0",
                    line=dict(color="#00dcff", width=2)),
        text=["🌍"], textposition="top center",
        name="Earth",
        hovertemplate="Earth<extra></extra>",
    ))

    # Moon
    fig.add_trace(go.Scatter(
        x=[1], y=[0],
        mode="markers+text",
        marker=dict(size=24, color="#c0c8d8",
                    line=dict(color="#e0e8ff", width=2)),
        text=["🌕"], textposition="top center",
        name="Moon",
        hovertemplate="Moon (384,400 km)<extra></extra>",
    ))

    # Orion spacecraft position
        # ✅ FIX 3: clamp moon_pct safely — prevents chart crash during RETURN COAST
    # OLD: if art["launched"] and art["moon_pct"] <= 100:
    #          frac = art["moon_pct"] / 100
    # NEW ↓
    if art["launched"]:
        frac  = min(1.0, max(0.0, art["moon_pct"] / 100))   # ✅ always 0.0–1.0
        angle = 180 - frac * 180
        rad   = math.radians(angle)
        sx    = math.cos(rad)
        sy    = math.sin(rad)
        fig.add_trace(go.Scatter(
            x=[sx], y=[sy],
            mode="markers+text",
            marker=dict(
                size   = 18,
                color  = "#ffffff",
                symbol = "diamond",
                line   = dict(color="#00dcff", width=3),
            ),
            text             = ["🚀"],
            textposition     = "top center",
            name             = "Orion",
            hovertemplate    = (
                f"<b>Orion Capsule</b><br>"
                f"Phase: {art['phase']}<br>"
                f"Distance: {art['distance_km']:,} km<br>"
                f"Mission: {art['mission_pct']:.1f}% complete"   # ✅ updated label
                "<extra></extra>"
            ),
        ))


    fig.update_layout(
        title = dict(
            text  = "🚀  Artemis II — Live Trajectory",
            font  = dict(color="#00dcff", size=16, family="monospace"),
            x     = 0.5,
        ),
        paper_bgcolor = "#08080f",
        plot_bgcolor  = "#0a0f28",
        showlegend    = True,
        legend = dict(
            bgcolor="#0a0f28", bordercolor="#1e3a7a",
            borderwidth=1, font=dict(color="#a0b8e0"),
        ),
        xaxis = dict(
            range=[-1.4, 1.4], showgrid=False,
            zeroline=False, showticklabels=False,
        ),
        yaxis = dict(
            range=[-0.3, 1.3], showgrid=False,
            zeroline=False, showticklabels=False,
            scaleanchor="x",
        ),
        height = 380,
        margin = dict(l=20, r=20, t=60, b=20),
    )
    return fig


def neo_size_distribution(neos: list) -> go.Figure:
    """Histogram of asteroid diameters."""
    diams = [o["diam_avg"] for o in neos if o["diam_avg"] > 0]
    fig = go.Figure(go.Histogram(
        x          = diams,
        nbinsx     = 30,
        marker_color = "#0050c0",
        marker_line  = dict(color="#00dcff", width=0.5),
        opacity    = 0.85,
        name       = "Diameter (m)",
    ))
    fig.update_layout(
        title = dict(
            text  = "📏  Asteroid Size Distribution",
            font  = dict(color="#00dcff", size=16, family="monospace"),
            x     = 0.5,
        ),
        paper_bgcolor = "#08080f",
        plot_bgcolor  = "#0a0f28",
        font          = dict(color="#a0b8e0", family="monospace"),
        xaxis = dict(
            title     = "Estimated Diameter (m)",
            gridcolor = "#1a2a4a",
            tickfont  = dict(color="#6080c0"),
        ),
        yaxis = dict(
            title     = "Count",
            gridcolor = "#1a2a4a",
            tickfont  = dict(color="#6080c0"),
        ),
        height = 320,
        margin = dict(l=60, r=20, t=60, b=60),
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding:20px 0 10px'>
        <div style='font-family:Orbitron,monospace; font-size:1.4rem;
                    color:#00dcff; text-shadow:0 0 15px rgba(0,220,255,0.5);
                    letter-spacing:0.1em;'>
            🚀 MISSION<br>CONTROL
        </div>
        <div style='font-family:monospace; font-size:0.7rem;
                    color:#4060a0; margin-top:6px; letter-spacing:0.15em;'>
            NASA OPEN DATA DASHBOARD
        </div>
    </div>
    <hr>
    """, unsafe_allow_html=True)

    now_utc = datetime.now(timezone.utc)
    st.markdown(f"""
    <div style='font-family:monospace; font-size:0.75rem;
                color:#6080c0; text-align:center; margin-bottom:12px;'>
        🕐 {now_utc.strftime('%Y-%m-%d %H:%M:%S')} UTC
    </div>
    """, unsafe_allow_html=True)

    neo_days = st.slider(
        "NEO Scan Window (days)", 1, 7, 7,
        help="How many days ahead to scan for asteroids"
    )
    show_pha_only = st.checkbox("Show PHA only", False)
    threat_filter = st.multiselect(
        "Filter by Threat Level",
        ["CRITICAL","WATCH","ALERT","MONITOR","ELEVATED","SAFE"],
        default=["CRITICAL","WATCH","ALERT","MONITOR","ELEVATED","SAFE"],
    )

    st.markdown("<hr>", unsafe_allow_html=True)

    if st.button("🔄  Refresh All Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown("""
    <hr>
    <div style='font-family:monospace; font-size:0.7rem; color:#304060;
                text-align:center; line-height:1.8;'>
        Data: NASA NeoWs API<br>
        NASA APOD API<br>
        NASA Image Library<br>
        JPL Photojournal<br><br>
        <span style='color:#1e3a7a;'>Built with Streamlit + Plotly</span>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center; padding:30px 0 10px;'>
    <div style='font-family:Orbitron,monospace; font-size:2.8rem; font-weight:900;
                color:#00dcff; text-shadow:0 0 30px rgba(0,220,255,0.6);
                letter-spacing:0.08em; line-height:1.1;'>
        Orbit Watch
    </div>
    <div style='font-family:monospace; font-size:0.9rem; color:#4060a0;
                letter-spacing:0.2em; margin-top:8px;'>
        LIVE DATA DASHBOARD  •  ARTEMIS II  •  NEO TRACKER  •  MARS ROVER
    </div>
</div>
<hr>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# LOAD DATA — with spinner
# ─────────────────────────────────────────────────────────────────────────────
with st.spinner("🛰️  Connecting to NASA APIs..."):
    apod      = fetch_apod()
    neos_raw  = fetch_neo_feed(days=neo_days)
    mars_pics = fetch_mars_photos()
    art       = get_artemis_status()

# Apply filters
neos = neos_raw
if show_pha_only:
    neos = [o for o in neos if o["hazardous"]]
if threat_filter:
    neos = [o for o in neos if o["threat"] in threat_filter]

# ─────────────────────────────────────────────────────────────────────────────
# TOP METRICS ROW
# ─────────────────────────────────────────────────────────────────────────────
m1, m2, m3, m4, m5, m6, m7 = st.columns(7)

closest = neos_raw[0] if neos_raw else {}
pha_n   = sum(1 for o in neos_raw if o["hazardous"])

with m1:
    st.metric("☄ NEOs THIS WEEK",    str(len(neos_raw)))
with m2:
    st.metric("⚠ PHA COUNT",         str(pha_n),
              delta="Potentially Hazardous")
with m3:
    st.metric("📍 CLOSEST (LD)",
              f"{closest.get('miss_ld',0):.2f}",
              delta=closest.get("name","?")[:12])
with m4:
    st.metric("🚀 ARTEMIS PHASE",    art["phase"][:10])
with m5:
    st.metric("🌕 MOON PROGRESS",
              f"{art['moon_pct']:.0f}%",
              delta=art["status"])
with m6:
    st.metric("📸 MARS PHOTOS",      str(len(mars_pics)))
with m7:
    st.metric("🌟 APOD",
              apod.get("media_type","?").upper(),
              delta=apod.get("date","?"))

st.markdown("<hr>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "☄  NEO TRACKER",
    "🚀  ARTEMIS II",
    "🔴  MARS ROVER",
    "🌟  APOD",
    "📊  ANALYTICS",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — NEO TRACKER
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("### ☄  Near-Earth Object Threat Assessment")
    st.markdown(
        f"*Showing **{len(neos)}** objects "
        f"({'filtered from ' + str(len(neos_raw)) if len(neos) != len(neos_raw) else 'all'} tracked) "
        f"• Sorted by miss distance • Live NASA NeoWs data*"
    )

    # Scatter chart
    st.plotly_chart(neo_scatter_chart(neos_raw), use_container_width=True)

    # NEO cards
    #

    # Full data table
    with st.expander("📋  Full NEO Data Table", expanded=False):
        df = pd.DataFrame([{
            "Name":        o["name"][:24],
            "Date":        o["ca_date"][:10],
            "Threat":      o["threat"],
            "km (M)":      round(o["miss_km"]/1e6, 3),
            "AU":          round(o["miss_au"], 4),
            "LD":          round(o["miss_ld"], 2),
            "Diam min (m)":round(o["diam_min"]),
            "Diam max (m)":round(o["diam_max"]),
            "Vel (km/s)":  round(o["vel_kms"], 2),
            "PHA":         "YES" if o["hazardous"] else "no",
            "Class":       o.get("orb_class","NEA"),
        } for o in neos])
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Threat": st.column_config.TextColumn("Threat"),
                "LD":     st.column_config.NumberColumn(
                    "LD 🌕", format="%.2f"),
                "PHA":    st.column_config.TextColumn("PHA ⚠"),
            }
        )
        csv = df.to_csv(index=False)
        st.download_button(
            "⬇  Download CSV",
            csv,
            "neo_data.csv",
            "text/csv",
            use_container_width=True,
        )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — ARTEMIS II  (FIXED)
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### 🚀  Artemis II — Live Mission Tracker")

    col_a, col_b = st.columns([1, 1])

    with col_a:
        phase_colors = {
            "PRE-LAUNCH":        "#ccaa00",
            "LAUNCH & ASCENT":   "#cc2200",
            "EARTH ORBIT / TLI": "#cc6600",
            "TRANSLUNAR COAST":  "#0088cc",
            "LUNAR FLYBY":       "#cc44aa",
            "RETURN COAST":      "#006633",
            "REENTRY":           "#cc2200",
            "MISSION COMPLETE":  "#404060",
        }
        pc           = phase_colors.get(art["phase"], "#0088cc")
        phase_label  = art["phase"]
        status_label = art["status"]

        st.markdown(f"""
        <div style="background:{pc}22; border:2px solid {pc};
                    border-radius:12px; padding:20px; margin-bottom:16px;
                    text-align:center;">
            <div style="font-family:Orbitron,monospace; font-size:1.4rem;
                        color:{pc}; font-weight:bold; letter-spacing:0.1em;">
                {phase_label}
            </div>
            <div style="font-family:monospace; font-size:1rem;
                        color:#a0b8e0; margin-top:8px;">
                {status_label}
            </div>
        </div>
        """, unsafe_allow_html=True)

        with m5:
            st.metric(
                "🚀 MISSION PROGRESS",                        # ✅ renamed label
                f"{art['mission_pct']:.0f}%",                 # ✅ overall mission %
                delta=art["status"],
            )

        if art["launched"]:
            st.metric(
                "Distance from Earth",
                f"{art['distance_km']:,} km",
                delta=f"Mission {art['mission_pct']:.1f}% complete",   # ✅ clearer label
            )
            st.progress(min(1.0, art["mission_pct"] / 100))  
        else:
            st.info(f"⏳ Launch: April 1, 2026 at 22:35:12 UTC\n\n{art['status']}")

        st.markdown("#### 👨‍🚀 Crew Manifest")
        icons = ["👨‍🚀", "👨‍🚀", "👩‍🚀", "👨‍🚀"]
        roles = ["Commander", "Pilot", "Mission Specialist", "CSA Astronaut"]
        for icon, member, role in zip(icons, art["crew"], roles):
            st.markdown(f"""
            <div style="background:#0a0f28; border:1px solid #1e3a7a;
                        border-radius:8px; padding:10px 16px;
                        margin-bottom:8px; font-family:monospace;">
                <span style="font-size:1.2rem;">{icon}</span>
                <span style="color:#e0e8ff; font-weight:bold;
                             margin-left:10px;">{member}</span>
                <span style="color:#4060a0; font-size:0.8rem;
                             margin-left:8px;">&#8212; {role}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div style="font-family:monospace; font-size:0.8rem;
                    color:#4060a0; margin-top:12px;">
            Vehicle: <span style="color:#ccaa00;">Orion / SLS Block 1</span>
            &nbsp;|&nbsp;
            Launch: <span style="color:#6080c0;">2026-04-01 22:35:12 UTC</span>
        </div>
        """, unsafe_allow_html=True)

    with col_b:
        st.plotly_chart(
            artemis_trajectory_chart(art),
            use_container_width=True,
        )

        st.markdown("#### 📋 Mission Timeline")
        # ✅ FIXED: timing labels match corrected PHASES boundaries
        phases_info = [
            ("LAUNCH & ASCENT",   "0&#8211;2h",     "SLS ignition &#8594; Earth orbit insertion"),
            ("EARTH ORBIT / TLI", "2&#8211;8h",     "Orbital checkout &#8594; Trans-Lunar Injection"),
            ("TRANSLUNAR COAST",  "8&#8211;72h",    "3-day coast to the Moon"),
            ("LUNAR FLYBY",       "72&#8211;96h",   "Close lunar flyby at ~8,900 km altitude"),
            ("RETURN COAST",      "96&#8211;210h",  "4.7-day return journey to Earth"),  # ✅ was 192
            ("REENTRY",           "210&#8211;217h", "Orion reentry &#8594; Pacific splashdown"),  # ✅ was 192–240
            ("MISSION COMPLETE",  "217h+",          "Splashdown — April 10, 2026 ~00:06 UTC"),    # ✅ added
        ]


        for ph, timing, desc in phases_info:
            # ── Pre-compute all conditional values ────────────────────────────
            is_current  = ph == art["phase"]
            bg_color    = "#1a2a0a" if is_current else "#0a0f28"
            bd_color    = "#00aa55" if is_current else "#1e3a7a"
            t_color     = "#00c878" if is_current else "#6080c0"
            ph_color    = "#e0e8ff" if is_current else "#a0b8e0"
            ph_weight   = "bold"    if is_current else "normal"
            arrow       = "&#9654; " if is_current else "&nbsp;&nbsp;"

            st.markdown(f"""
            <div style="background:{bg_color}; border:1px solid {bd_color};
                        border-radius:6px; padding:8px 14px;
                        margin-bottom:6px; font-family:monospace;
                        font-size:0.78rem;">
                {arrow}
                <span style="color:{t_color};">{timing}</span>
                <span style="color:{ph_color}; font-weight:{ph_weight};
                             margin-left:8px;">{ph}</span>
                <div style="color:#4060a0; margin-left:24px;
                            margin-top:2px;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — MARS ROVER
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### 🔴  Mars Rover — Live Photo Gallery")

    cols = st.columns(3)
    for i, photo in enumerate(mars_pics[:6]):
        with cols[i % 3]:
            img = load_image_url(photo["url"])
            if img:
                enhanced = ImageEnhance.Color(img).enhance(1.3)
                st.image(enhanced, use_container_width=True)
            else:
                st.markdown("""
                <div style="background:#1a0a08; border:1px solid #4a1a10;
                            border-radius:8px; height:180px;
                            display:flex; align-items:center;
                            justify-content:center; color:#4a1a10;
                            font-family:monospace;">
                    NO IMAGE
                </div>
                """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="font-family:monospace; font-size:0.75rem;
                        color:#cc4422; font-weight:bold; margin-top:4px;">
                {photo.get('title','Mars Surface')[:35]}
            </div>
            <div style="font-family:monospace; font-size:0.7rem;
                        color:#4060a0;">
                {photo.get('camera','NASA Camera')[:28]}<br>
                {photo.get('date','N/A')}
                &nbsp;|&nbsp; ID: {photo.get('id','?')}
            </div>
            """, unsafe_allow_html=True)
            st.markdown("")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("#### 🌍 Mars Quick Facts")
    fc1, fc2, fc3, fc4 = st.columns(4)
    with fc1:
        st.metric("Distance from Earth", "~225M km",
                  delta="56M–401M km range")
    with fc2:
        st.metric("Surface Temperature", "−60°C avg",
                  delta="−125°C to +20°C")
    with fc3:
        st.metric("Gravity", "3.72 m/s²", delta="38% of Earth")
    with fc4:
        st.metric("Sol Length", "24h 37m", delta="1 Martian day")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — APOD
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("### 🌟  Astronomy Picture of the Day")

    col_img, col_txt = st.columns([1.2, 1])

    with col_img:
        img_url = apod.get("hdurl") or apod.get("url", "")
        if apod.get("media_type") == "video":
            st.video(img_url)
        elif img_url:
            img = load_image_url(img_url)
            if img:
                st.image(img, use_container_width=True)
            else:
                st.markdown(f"""
                <div style="background:#0a0a1a; border:1px solid #1e3a7a;
                            border-radius:8px; padding:20px; text-align:center;
                            font-family:monospace; color:#4060a0;">
                    🌌 Image loading...<br>
                    <a href="{img_url}" target="_blank"
                       style="color:#0096ff;">View on NASA ↗</a>
                </div>
                """, unsafe_allow_html=True)

    with col_txt:
        st.markdown(f"""
        <div style="background:#0a0f28; border:1px solid #1e3a7a;
                    border-radius:12px; padding:24px;">
            <div style="font-family:monospace; font-size:0.75rem;
                        color:#4060a0; letter-spacing:0.1em; margin-bottom:8px;">
                {apod.get('date','N/A')}
                &nbsp;|&nbsp;
                {apod.get('media_type','image').upper()}
            </div>
            <div style="font-family:Orbitron,monospace; font-size:1.2rem;
                        color:#00dcff; font-weight:bold; margin-bottom:16px;
                        line-height:1.3;">
                {apod.get('title','?')}
            </div>
            <div style="font-family:Georgia, serif; font-size:0.9rem;
                        color:#a0b8e0; line-height:1.7;">
                {apod.get('explanation','')[:800]}
            </div>
        </div>
        """, unsafe_allow_html=True)

        if apod.get("copyright"):
            st.markdown(f"""
            <div style="font-family:monospace; font-size:0.75rem;
                        color:#304060; margin-top:10px;">
                © {apod['copyright']}
            </div>
            """, unsafe_allow_html=True)

        if img_url:
            st.markdown(f"""
            <a href="{img_url}" target="_blank"
               style="display:inline-block; margin-top:12px;
                      background:#003080; color:#00dcff;
                      padding:8px 20px; border-radius:6px;
                      font-family:monospace; font-size:0.8rem;
                      text-decoration:none; border:1px solid #0096ff;">
                🔗 View Full Resolution ↗
            </a>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — ANALYTICS
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown("### 📊  Mission Analytics")

    col_l, col_r = st.columns(2)
    with col_l:
        st.plotly_chart(
            neo_timeline_chart(neos_raw),
            use_container_width=True
        )
    with col_r:
        st.plotly_chart(
            neo_size_distribution(neos_raw),
            use_container_width=True
        )

    # Threat breakdown pie
    from collections import Counter
    threat_counts = Counter(o["threat"] for o in neos_raw)
    tc_colors = {
        "CRITICAL":"#ff1a1a","WATCH":"#cc2200","ALERT":"#cc6600",
        "MONITOR":"#cc8800","ELEVATED":"#ccaa00","SAFE":"#006633",
    }
    fig_pie = go.Figure(go.Pie(
        labels = list(threat_counts.keys()),
        values = list(threat_counts.values()),
        marker = dict(
            colors = [tc_colors.get(k,"#888") for k in threat_counts],
            line   = dict(color="#08080f", width=2),
        ),
        textfont = dict(family="monospace", color="#e0e8ff"),
        hole     = 0.45,
    ))
    fig_pie.update_layout(
  

        title = dict(
            text  = "🎯  Threat Level Distribution",
            font  = dict(color="#00dcff", size=16, family="monospace"),
            x     = 0.5,
        ),
        paper_bgcolor = "#08080f",
        plot_bgcolor  = "#08080f",
        font          = dict(color="#a0b8e0", family="monospace"),
        legend = dict(
            bgcolor="#0a0f28", bordercolor="#1e3a7a",
            borderwidth=1, font=dict(color="#a0b8e0"),
        ),
        height = 360,
        margin = dict(l=20, r=20, t=60, b=20),
        annotations = [dict(
            text      = f"<b>{len(neos_raw)}</b><br>NEOs",
            x=0.5, y=0.5, showarrow=False,
            font      = dict(color="#00dcff", size=18, family="Orbitron"),
        )],
    )
    st.plotly_chart(fig_pie, use_container_width=True)

    # Stats summary table
    st.markdown("#### 📋  Statistical Summary")
    if neos_raw:
        df_stats = pd.DataFrame([{
            "Metric":    "Total NEOs tracked",
            "Value":     str(len(neos_raw)),
            "Note":      f"Next {neo_days} days",
        }, {
            "Metric":    "Potentially Hazardous (PHA)",
            "Value":     str(pha_n),
            "Note":      f"{pha_n/len(neos_raw)*100:.1f}% of total",
        }, {
            "Metric":    "Closest approach",
            "Value":     f"{closest.get('miss_km',0)/1e6:.3f}M km",
            "Note":      f"{closest.get('miss_ld',0):.2f} LD — {closest.get('name','?')}",
        }, {
            "Metric":    "Fastest asteroid",
            "Value":     f"{max(o['vel_kms'] for o in neos_raw):.2f} km/s",
            "Note":      max(neos_raw, key=lambda x: x['vel_kms'])['name'][:24],
        }, {
            "Metric":    "Largest asteroid",
            "Value":     f"{max(o['diam_avg'] for o in neos_raw):.0f}m avg diam",
            "Note":      max(neos_raw, key=lambda x: x['diam_avg'])['name'][:24],
        }, {
            "Metric":    "Average miss distance",
            "Value":     f"{sum(o['miss_km'] for o in neos_raw)/len(neos_raw)/1e6:.1f}M km",
            "Note":      f"{sum(o['miss_ld'] for o in neos_raw)/len(neos_raw):.1f} LD average",
        }])
        st.dataframe(df_stats, use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(f"""
<div style='text-align:center; font-family:monospace; font-size:0.75rem;
            color:#304060; padding:16px 0 8px; line-height:2;'>
    🚀 OrbitWatch v1.0
    &nbsp;|&nbsp;
    Built NASA Open APIs
    <br>
    Data: NASA NeoWs · APOD · NASA Image Library · JPL CNEOS
    &nbsp;|&nbsp;
    Last updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC
    <br>
    <span style='color:#1e3a7a;'>
        Affiliated with araCreate Group — uses NASA Open Data (api.nasa.gov)
    </span>
</div>
""", unsafe_allow_html=True)
