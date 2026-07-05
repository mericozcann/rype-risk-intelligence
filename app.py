
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.rype.counterfactual import compare_routes_real
from src.rype.data_loader import load_rype_data
from src.rype.decision_signals import decision_signal, risk_label
from src.rype.geo_risk import build_port_risk_layer, get_port_coord, ocean_route
from src.rype.route_engine import load_yaml_config, DEFAULT_RISK_WEIGHTS, DEFAULT_PROPAGATION
from src.rype.ui_controls import render_route_controls
from src.rype.ui_helpers import metric_card, risk_badge, plotly_theme, dataframe_dark

# ============================================================
# RYPE MVP v0.5 — Feature Freeze Decision Intelligence Interface
# ============================================================

st.set_page_config(
    page_title="RYPE | Explainable Operational Risk Intelligence",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded"
)

DATA_PATH = "data"

# ============================================================
# DESIGN SYSTEM — DARK EXECUTIVE THEME
# ============================================================

st.markdown("""
<style>
:root{
    --bg:#070a0f;
    --panel:#0f1723;
    --panel2:#121c2a;
    --panel3:#172233;
    --text:#f5f7fb;
    --muted:#9aa8ba;
    --muted2:#65758b;
    --line:#233246;
    --accent:#d85b3f;
    --blue:#4ea1ff;
    --green:#54d39a;
    --amber:#f0b85a;
    --red:#ff6f61;
}
.stApp{
    background:
        radial-gradient(circle at 12% 8%, rgba(78,161,255,0.13), transparent 26%),
        radial-gradient(circle at 88% 12%, rgba(216,91,63,0.11), transparent 28%),
        linear-gradient(135deg, #070a0f 0%, #0b111b 55%, #070a0f 100%);
    color:var(--text);
}
.block-container{padding-top:1.35rem; padding-bottom:4rem; max-width:1560px;}
[data-testid="stSidebar"]{background:#080c12; border-right:1px solid var(--line);}
[data-testid="stSidebar"] *{color:#e8eef8;}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stNumberInput label{font-weight:800; letter-spacing:.02em; color:#d8e1ee;}
hr{border-color:var(--line)!important;}
h1,h2,h3,h4,p,span,div{font-family:Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;}
.rype-nav{
    display:flex; align-items:center; justify-content:space-between;
    background:rgba(7,10,15,.76); border:1px solid var(--line);
    border-radius:18px; padding:14px 18px; margin-bottom:20px;
    backdrop-filter: blur(14px);
}
.brand{display:flex; align-items:center; gap:12px;}
.brand-mark{width:38px; height:38px; border-radius:12px; background:linear-gradient(135deg,var(--accent),#8f2f20); display:flex; align-items:center; justify-content:center; font-weight:900; color:white;}
.brand-title{font-size:1.08rem; font-weight:900; letter-spacing:-.03em; color:white;}
.brand-sub{font-size:.72rem; color:var(--muted); margin-top:2px;}
.nav-pill{font-size:.7rem; color:#b7c3d4; border:1px solid var(--line); border-radius:999px; padding:6px 10px; background:rgba(255,255,255,.03);}
.rype-eyebrow{display:block; color:#ff8a6e; font-size:.72rem; font-weight:900; letter-spacing:.20em; text-transform:uppercase; margin-bottom:.55rem;}
.rype-title{font-size:3.35rem; font-weight:950; line-height:.95; letter-spacing:-.065em; color:#fff; margin-bottom:.7rem;}
.rype-subtitle{color:#aab8ca; font-size:1.02rem; max-width:1040px; line-height:1.68; margin-bottom:1rem;}
.hero-card{background:linear-gradient(145deg, rgba(15,23,35,.96), rgba(11,17,27,.96)); border:1px solid var(--line); border-radius:22px; padding:1.25rem 1.35rem; box-shadow:0 18px 50px rgba(0,0,0,.26);}
.metric-card{background:linear-gradient(145deg,#101927,#0b111b); color:#f8fbff; border:1px solid var(--line); border-radius:18px; padding:1.15rem; min-height:142px; box-shadow:0 14px 38px rgba(0,0,0,.22);}
.metric-label{font-size:.67rem; color:#8392a7; text-transform:uppercase; letter-spacing:.14em; font-weight:900;}
.metric-value{font-size:2.05rem; font-weight:950; letter-spacing:-.055em; margin-top:.45rem; color:white;}
.metric-note{font-size:.78rem; color:#93a3b8; margin-top:.55rem; line-height:1.45;}
.kpi-grid{display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:14px; margin:15px 0 18px 0;}
.signal{background:linear-gradient(135deg,#111b2a,#0b111b); border:1px solid var(--line); border-left:5px solid var(--accent); color:#f6f8fb; border-radius:18px; padding:1.1rem 1.25rem; margin:1rem 0; box-shadow:0 14px 40px rgba(0,0,0,.2);}
.signal-title{font-size:.7rem; color:#ff8a6e; letter-spacing:.18em; text-transform:uppercase; font-weight:950;}
.signal-main{font-size:1.2rem; font-weight:900; margin-top:.4rem; color:white;}
.signal-sub{color:#a8b6c8; font-size:.88rem; margin-top:.38rem; line-height:1.55;}
.panel{background:rgba(15,23,35,.94); border:1px solid var(--line); border-radius:20px; padding:1.2rem; box-shadow:0 14px 38px rgba(0,0,0,.18);}
.panel-light{background:#101927; border:1px solid var(--line); border-radius:18px; padding:1.05rem;}
.method-note{background:rgba(15,23,35,.98); border-left:4px solid var(--blue); border-radius:12px; padding:1rem 1.15rem; color:#b7c4d6; font-size:.88rem; line-height:1.65;}
.driver-row{display:flex; align-items:center; gap:10px; margin-bottom:10px;}
.driver-name{width:155px; color:#9eacc0; font-size:.82rem;}
.driver-track{height:9px; flex:1; border-radius:999px; background:#1c2a3b; overflow:hidden;}
.driver-fill{height:100%; border-radius:999px; background:linear-gradient(90deg,var(--blue),var(--accent));}
.driver-val{width:58px; text-align:right; color:white; font-weight:800; font-size:.82rem;}
.badge-high{color:#ff9a8c; background:rgba(255,111,97,.13); border:1px solid rgba(255,111,97,.28); padding:4px 9px; border-radius:999px; font-size:.72rem; font-weight:900;}
.badge-mod{color:#ffd18a; background:rgba(240,184,90,.13); border:1px solid rgba(240,184,90,.28); padding:4px 9px; border-radius:999px; font-size:.72rem; font-weight:900;}
.badge-low{color:#7ff0ba; background:rgba(84,211,154,.13); border:1px solid rgba(84,211,154,.28); padding:4px 9px; border-radius:999px; font-size:.72rem; font-weight:900;}
.stTabs [data-baseweb="tab-list"]{gap:6px; border-bottom:1px solid var(--line);}
.stTabs [data-baseweb="tab"]{background:#101927; border:1px solid var(--line); border-bottom:0; border-radius:12px 12px 0 0; padding:8px 14px; color:#d8e3f2;}
.stTabs [aria-selected="true"]{background:#172338!important; color:#fff!important;}
div[data-testid="stDataFrame"]{border:1px solid var(--line); border-radius:14px; overflow:hidden;}
@media(max-width:1000px){.kpi-grid{grid-template-columns:repeat(2,minmax(0,1fr));}.rype-title{font-size:2.4rem;}}

/* STREAMLIT CHROME: lock the app to the intended dark research interface */
[data-testid="stToolbar"]{display:none!important;}
[data-testid="stHeader"]{background:transparent!important; height:0!important;}
[data-testid="stDecoration"]{display:none!important;}
#MainMenu{visibility:hidden!important;}
footer{visibility:hidden!important;}
[data-testid="stStatusWidget"]{visibility:hidden!important;}
.block-container{padding-top:2.4rem!important; padding-bottom:4rem; max-width:1560px;}
.rype-nav{margin-top:.35rem!important; overflow:visible!important; position:relative; z-index:5;}
.brand-mark{
    width:44px; height:44px; border-radius:14px;
    background:linear-gradient(145deg,rgba(78,161,255,.16),rgba(84,211,154,.10));
    border:1px solid rgba(117,196,255,.30);
    box-shadow:inset 0 0 22px rgba(78,161,255,.08),0 10px 28px rgba(0,0,0,.22);
    display:flex; align-items:center; justify-content:center;
}
.brand-mark svg{width:31px;height:31px;display:block;}
.brand-title{line-height:1.2;}
.brand-sub{line-height:1.35;}
.section-kicker{font-size:.68rem;color:#7f90a8;letter-spacing:.15em;text-transform:uppercase;font-weight:900;margin-bottom:.25rem;}
.insight-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:.75rem 0 1rem;}
.insight-card{background:linear-gradient(145deg,#101927,#0b111b);border:1px solid var(--line);border-radius:16px;padding:1rem;}
.insight-label{font-size:.65rem;color:#7f90a8;letter-spacing:.12em;text-transform:uppercase;font-weight:900;}
.insight-value{font-size:1.15rem;color:#fff;font-weight:900;margin-top:.38rem;}
.insight-note{font-size:.76rem;color:#95a5ba;line-height:1.45;margin-top:.35rem;}
.decision-brief{background:linear-gradient(135deg,rgba(78,161,255,.08),rgba(216,91,63,.06));border:1px solid var(--line);border-radius:18px;padding:1.05rem 1.15rem;margin:.8rem 0 1rem;}
.decision-brief strong{color:#fff;}
.plot-caption{color:#8798ae;font-size:.78rem;line-height:1.55;margin-top:-.25rem;margin-bottom:.8rem;}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p{line-height:1.5;}
@media(max-width:1000px){
  .insight-grid{grid-template-columns:1fr;}
  .rype-nav{align-items:flex-start;gap:12px;}
  .nav-pill{display:none;}
}


/* v0.5 sidebar hierarchy and final polish */
.sidebar-step{
    margin:.95rem 0 .45rem;
    padding:.62rem .72rem;
    border-radius:13px;
    background:rgba(255,255,255,.045);
    border:1px solid rgba(255,255,255,.08);
}
.sidebar-step .step-no{
    color:#D85B3F;
    font-size:.62rem;
    font-weight:900;
    letter-spacing:.16em;
    text-transform:uppercase;
}
.sidebar-step .step-title{
    color:#FFFFFF;
    font-size:.82rem;
    font-weight:850;
    margin-top:.12rem;
}
.sidebar-mini-note{
    color:#9AA8BA;
    font-size:.74rem;
    line-height:1.45;
    margin:.25rem 0 .55rem;
}
.route-legend{
    background:rgba(7,11,18,.86);
    border:1px solid rgba(139,200,255,.22);
    border-radius:16px;
    padding:.9rem 1rem;
    color:#CFDAE8;
    margin-top:.65rem;
}
.route-legend b{color:#fff;}

</style>
""", unsafe_allow_html=True)

# ============================================================
# DATA + ENGINE SETUP
# ============================================================

DATA_PATH = "data"

@st.cache_data
def cached_load_rype_data(data_path: str = DATA_PATH):
    return load_rype_data(data_path)

try:
    geo_df, port_bridge_df, propagation_df, scenario_df, temporal_df, resilience_df, hitl_df, metadata = cached_load_rype_data(DATA_PATH)
    port_risk_df = build_port_risk_layer(geo_df, port_bridge_df)
except Exception as exc:
    st.error("RYPE could not load its required data layer.")
    st.exception(exc)
    st.stop()

risk_weights = load_yaml_config(Path("config/risk_weights.yaml"), DEFAULT_RISK_WEIGHTS)
propagation_weights = load_yaml_config(Path("config/propagation.yaml"), DEFAULT_PROPAGATION)

origin_port, destination_port, alternative_origin, random_state = render_route_controls(port_risk_df, port_bridge_df)

# ============================================================
# RUN ENGINE
# ============================================================

original, alternative, comparison_df = compare_routes_real(origin_port, destination_port, alternative_origin, port_risk_df, port_bridge_df, int(random_state), risk_weights, propagation_weights)
action, tone, risk_red, success_gain = decision_signal(original, alternative)

# ============================================================
# HEADER
# ============================================================

st.markdown("""
<div class="rype-nav">
  <div class="brand">
    <div class="brand-mark" aria-label="RYPE network shield mark">
      <svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M20 4.5L32 9.2V18.8C32 26.7 27.1 32.7 20 35.5C12.9 32.7 8 26.7 8 18.8V9.2L20 4.5Z" stroke="#8BC8FF" stroke-width="1.7"/>
        <path d="M12.5 14.2L18.2 18.5L24.4 12.8L29 17.1M18.2 18.5L22.2 25.5L28.1 22.2" stroke="#75D7B2" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/>
        <circle cx="12.5" cy="14.2" r="2.1" fill="#8BC8FF"/>
        <circle cx="18.2" cy="18.5" r="2.1" fill="#D9C58A"/>
        <circle cx="24.4" cy="12.8" r="2.1" fill="#75D7B2"/>
        <circle cx="29" cy="17.1" r="2.1" fill="#8BC8FF"/>
        <circle cx="22.2" cy="25.5" r="2.1" fill="#75D7B2"/>
        <circle cx="28.1" cy="22.2" r="2.1" fill="#D9C58A"/>
      </svg>
    </div>
    <div>
      <div class="brand-title">RYPE — Risk Yield Propagation Engine</div>
      <div class="brand-sub">Explainable geopolitical supply-chain risk intelligence prototype</div>
    </div>
  </div>
  <div class="nav-pill">Research MVP v0.5 · Feature Freeze</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<span class="rype-eyebrow">EXPLAINABLE OPERATIONAL RISK INTELLIGENCE</span>', unsafe_allow_html=True)
st.markdown('<div class="rype-title">Operational risk, explained as a decision.</div>', unsafe_allow_html=True)
st.markdown("""
<div class="rype-subtitle">
RYPE connects externally grounded geopolitical risk signals with causal operational regeneration,
D1–D4 propagation, counterfactual intervention analysis and human-in-the-loop decision support.
The objective is not only to score risk, but to explain where it comes from and what a decision-maker can do next.
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="signal">
  <div class="signal-title">Decision Signal</div>
  <div class="signal-main">{action}</div>
  <div class="signal-sub">{tone}<br>
  Edge risk change: <b>{risk_red:+.3f}</b> · Success probability gain: <b>{success_gain*100:+.2f} percentage points</b></div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="kpi-grid">', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
with c1: metric_card("Edge Risk", f"{original['edge_risk_real']:.3f}", risk_label(original["edge_risk_real"]))
with c2: metric_card("Geo Pressure", f"{original['geo_pressure']:.3f}", "External risk signal at origin node")
with c3: metric_card("P(success)", f"{original['p_success']*100:.2f}%", "Propagation-adjusted success probability")
with c4: metric_card("Expected Delay", f"{original['delay_hours']:.1f} h", "Causally regenerated delay estimate")
st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# TABS
# ============================================================

tabs = st.tabs(["Executive Overview", "Route Map", "Propagation", "Counterfactual", "Scenario Lab", "Temporal & Resilience", "HITL", "Methodology"])

# ============================================================
# EXECUTIVE OVERVIEW
# ============================================================

with tabs[0]:
    left, right = st.columns([1.15, .85])
    with left:
        st.markdown("### Executive route intelligence")
        st.markdown(f"""
        <div class="hero-card">
        <div style="font-size:1.25rem;font-weight:900;color:white;margin-bottom:.5rem;">
        {original['origin_name']} ({origin_port}) → {original['destination_name']} ({destination_port})
        </div>
        <div style="color:#aebbd0;line-height:1.65;">
        Current route status: {risk_badge(original['edge_risk_real'])}<br><br>
        The dominant external trigger is the geopolitical pressure score at the origin risk node.
        RYPE then regenerates operational states and propagates them through supplier, port, route and last-mile mechanisms.
        </div>
        </div>
        """, unsafe_allow_html=True)

        drivers = pd.DataFrame({
            "Driver": ["Geopolitical pressure", "Delay normalization", "Reroute probability", "Customs probability", "Damage probability", "D4 last-mile"],
            "Value": [original["geo_pressure"], original["delay_normalized"], original["reroute_probability"], original["customs_probability"], original["damage_probability"], original["D4_lastmile"]]
        }).sort_values("Value", ascending=True)
        fig = px.bar(drivers, x="Value", y="Driver", orientation="h", title="Risk Driver Decomposition", text="Value")
        fig.update_traces(texttemplate="%{text:.2f}", textposition="outside", cliponaxis=False)
        fig.update_xaxes(range=[0, 1.08])
        st.plotly_chart(plotly_theme(fig, 440), width="stretch")

    with right:
        st.markdown("### Operational state interpretation")
        state_items = [
            ("Reroute", original["rerouted"], f"Probability {original['reroute_probability']:.2f}"),
            ("Customs issue", original["customs_issue"], f"Probability {original['customs_probability']:.2f}"),
            ("Cargo damage", original["damaged"], f"Probability {original['damage_probability']:.2f}"),
            ("Disruption", original["disrupted"], f"Score {original['disruption_score']:.2f}"),
        ]
        for name, val, note in state_items:
            color = "#ff6f61" if val else "#54d39a"
            st.markdown(f"""
            <div class="panel-light" style="margin-bottom:10px;">
              <div style="display:flex;justify-content:space-between;align-items:center;">
                <div style="font-weight:900;color:white;">{name}</div>
                <div style="color:{color};font-weight:900;">{'ACTIVE' if val else 'NO'}</div>
              </div>
              <div style="color:#91a1b6;font-size:.82rem;margin-top:3px;">{note}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("### Edge-risk contribution")
        xai = pd.DataFrame({
            "Feature": ["geo_pressure", "D4_lastmile", "disrupted", "rerouted", "1 - p_success"],
            "Contribution": [0.30*original["geo_pressure"], 0.25*original["D4_lastmile"], 0.20*original["disrupted"], 0.15*original["rerouted"], 0.10*(1-original["p_success"])]
        }).sort_values("Contribution", ascending=True)
        fig = px.bar(xai, x="Contribution", y="Feature", orientation="h", title="XAI-style contribution structure", text="Contribution")
        fig.update_traces(texttemplate="%{text:.3f}", textposition="outside", cliponaxis=False)
        fig.update_xaxes(range=[0, max(.32, xai["Contribution"].max()*1.2)])
        st.plotly_chart(plotly_theme(fig, 360), width="stretch")

# ============================================================
# ROUTE MAP
# ============================================================

with tabs[1]:
    st.markdown("### Maritime route map")
    route = ocean_route(origin_port, destination_port, port_bridge_df)
    origin_coord = get_port_coord(origin_port, port_bridge_df)
    dest_coord = get_port_coord(destination_port, port_bridge_df)
    if route and origin_coord and dest_coord:
        route_lats = [p[0] for p in route]
        route_lons = [p[1] for p in route]
        lat_o, lon_o = origin_coord
        lat_d, lon_d = dest_coord
        risk_color = "#ff6f61" if original["edge_risk_real"] >= .70 else "#f0b85a" if original["edge_risk_real"] >= .40 else "#54d39a"
        fig = go.Figure()
        fig.add_trace(go.Scattergeo(
            lon=route_lons, lat=route_lats, mode="lines", name="Estimated maritime corridor",
            line=dict(width=4.5, color=risk_color),
            hovertemplate="Estimated maritime corridor<extra></extra>"
        ))
        fig.add_trace(go.Scattergeo(
            lon=[lon_o, lon_d], lat=[lat_o, lat_d], mode="markers", name="Ports",
            marker=dict(size=[18,16], color=["#ff6f61", "#4ea1ff"], line=dict(width=2, color="white")),
            text=[f"Origin: {original['origin_name']} ({origin_port})<br>Geo pressure: {original['geo_pressure']:.3f}<br>Edge risk: {original['edge_risk_real']:.3f}",
                  f"Destination: {original['destination_name']} ({destination_port})<br>Route context node"],
            hovertemplate="%{text}<extra></extra>"
        ))
        fig.update_layout(
            height=650, margin=dict(l=0,r=0,t=10,b=0), paper_bgcolor="rgba(0,0,0,0)",
            geo=dict(
                projection_type="natural earth", showland=True, landcolor="#1d2735", showocean=True, oceancolor="#0b1522",
                showcountries=True, countrycolor="rgba(255,255,255,.18)", coastlinecolor="rgba(255,255,255,.22)", showframe=False,
                bgcolor="rgba(0,0,0,0)"
            ),
            font=dict(color="#eaf0f8"),
            legend=dict(bgcolor="rgba(15,23,35,.75)")
        )
        st.plotly_chart(fig, width="stretch")
        st.markdown(f"""
        <div class="method-note">
        The route is rendered as an estimated maritime corridor using known sea-waypoints for major lanes such as the Red Sea, Suez and European approach.
        It is not a live AIS track. AIS vessel position, speed anomaly and ETA drift remain a planned extension layer.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("Coordinate information is missing for one of the selected ports.")

# ============================================================
# PROPAGATION
# ============================================================

with tabs[2]:
    st.markdown('<div class="section-kicker">Mechanism path · downstream concentration</div>', unsafe_allow_html=True)
    st.markdown("### D1–D4 propagation intelligence")

    prop = pd.DataFrame({
        "Node": ["D1 Supplier", "D2 Port", "D3 Route", "D4 Last-mile"],
        "Risk": [
            original["D1_supplier"],
            original["D2_port"],
            original["D3_route"],
            original["D4_lastmile"]
        ]
    })

    prop["Step"] = range(1, len(prop) + 1)
    prop["Delta_from_previous"] = prop["Risk"].diff().fillna(0.0)
    dominant = prop.sort_values("Risk", ascending=False).iloc[0]
    largest_jump = prop.iloc[prop["Delta_from_previous"].abs().idxmax()]
    downstream_concentration = float(prop[prop["Node"].isin(["D3 Route","D4 Last-mile"])]["Risk"].mean())
    upstream_average = float(prop[prop["Node"].isin(["D1 Supplier","D2 Port"])]["Risk"].mean())
    concentration_delta = downstream_concentration - upstream_average

    st.markdown(f"""
    <div class="insight-grid">
      <div class="insight-card"><div class="insight-label">Dominant propagation node</div><div class="insight-value">{dominant['Node']}</div><div class="insight-note">Highest active node risk: {dominant['Risk']:.3f}.</div></div>
      <div class="insight-card"><div class="insight-label">Largest node-to-node movement</div><div class="insight-value">{largest_jump['Node']}</div><div class="insight-note">Δ from previous node: {largest_jump['Delta_from_previous']:+.3f}.</div></div>
      <div class="insight-card"><div class="insight-label">Downstream concentration</div><div class="insight-value">{downstream_concentration:.3f}</div><div class="insight-note">D3–D4 average versus D1–D2: {concentration_delta:+.3f}.</div></div>
    </div>
    """, unsafe_allow_html=True)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=prop["Node"], y=prop["Risk"],
        mode="lines+markers",
        line=dict(width=4, color="#8BC8FF"),
        marker=dict(size=14, color=["#D9C58A","#8BC8FF","#75D7B2","#D85B3F"], line=dict(width=2, color="#E8EEF8")),
        fill="tozeroy",
        fillcolor="rgba(139,200,255,0.10)",
        hovertemplate="<b>%{x}</b><br>Risk=%{y:.3f}<extra></extra>"
    ))
    fig.update_yaxes(range=[0, 1], title="Risk intensity")
    fig.update_xaxes(title=None)
    fig.update_layout(title="Sequential propagation path: supplier → port → route → last-mile")
    st.plotly_chart(plotly_theme(fig, 500), width="stretch")

    st.markdown(f"""
    <div class="decision-brief">
      <strong>Propagation brief.</strong> The current route does not merely have a scalar risk value; it has a risk <em>shape</em>.
      The highest mechanism state is <strong>{dominant['Node']}</strong>. Downstream concentration is
      <strong>{downstream_concentration:.3f}</strong>, indicating whether exposure accumulates toward route/last-mile operations.
      This supports targeted review: upstream supplier remediation is different from downstream route or terminal intervention.
    </div>
    """, unsafe_allow_html=True)

    st.dataframe(
        dataframe_dark(prop[["Node","Risk","Delta_from_previous"]], {"Risk":"{:.3f}","Delta_from_previous":"{:+.3f}"}),
        hide_index=True, width="stretch"
    )

# ============================================================
# COUNTERFACTUAL
# ============================================================

with tabs[3]:
    st.markdown("### Counterfactual intervention analysis")
    a, b, c = st.columns(3)
    with a: metric_card("Risk Reduction", f"{risk_red:+.3f}", "Positive value means counterfactual reduces edge risk")
    with b: metric_card("P(success) Gain", f"{success_gain*100:+.2f} pp", "Percentage-point change under counterfactual")
    with c: metric_card("Alternative", f"{alternative_origin}", f"{alternative['origin_name']} as substituted origin")
    cf_long = comparison_df.melt(id_vars=["Scenario","Route"], value_vars=["Geo Pressure","D1 Supplier","D2 Port","D3 Route","D4 Last-mile","Edge Risk"], var_name="Metric", value_name="Value")
    fig = px.bar(cf_long, x="Metric", y="Value", color="Scenario", barmode="group", title="Original vs Counterfactual Risk Structure", text="Value")
    fig.update_traces(texttemplate="%{text:.2f}", textposition="outside", cliponaxis=False)
    fig.update_yaxes(range=[0,1.08])
    st.plotly_chart(plotly_theme(fig, 520), width="stretch")
    st.dataframe(dataframe_dark(comparison_df, {"Geo Pressure":"{:.3f}","D1 Supplier":"{:.3f}","D2 Port":"{:.3f}","D3 Route":"{:.3f}","D4 Last-mile":"{:.3f}","P Success":"{:.4f}","Edge Risk":"{:.3f}"}), hide_index=True, width="stretch")

# ============================================================
# SCENARIO LAB
# ============================================================

with tabs[4]:
    st.markdown('<div class="section-kicker">Stress testing · comparative sensitivity</div>', unsafe_allow_html=True)
    st.markdown("### Scenario stress laboratory")

    scenario_rank = scenario_df.copy()
    scenario_rank["Risk_Shock"] = scenario_rank["Delta_Risk"]
    scenario_rank["Success_Impact_pp"] = scenario_rank["Delta_P_Success"] * 100
    worst_risk = scenario_rank.sort_values("Risk_Shock", ascending=False).iloc[0]
    worst_success = scenario_rank.sort_values("Success_Impact_pp").iloc[0]
    compound_row = scenario_rank[scenario_rank["Scenario"].str.contains("Compound", case=False, na=False)]
    compound_name = compound_row.iloc[0]["Scenario"] if not compound_row.empty else scenario_rank.sort_values("Chain_Risk", ascending=False).iloc[0]["Scenario"]

    st.markdown(f"""
    <div class="insight-grid">
      <div class="insight-card"><div class="insight-label">Largest chain-risk shock</div><div class="insight-value">{worst_risk['Scenario']}</div><div class="insight-note">Δ risk {worst_risk['Risk_Shock']:+.3f} versus baseline.</div></div>
      <div class="insight-card"><div class="insight-label">Largest success deterioration</div><div class="insight-value">{worst_success['Scenario']}</div><div class="insight-note">{worst_success['Success_Impact_pp']:+.2f} percentage-point impact.</div></div>
      <div class="insight-card"><div class="insight-label">Multi-stressor reference</div><div class="insight-value">{compound_name}</div><div class="insight-note">Use as the compound-stress comparison case.</div></div>
    </div>
    """, unsafe_allow_html=True)

    fig = px.scatter(
        scenario_rank, x="Chain_Risk", y="P_Success", color="Scenario",
        size=np.abs(scenario_rank["Delta_Risk"]) + 0.025,
        title="Scenario risk–success space",
        hover_name="Scenario",
        hover_data={"Chain_Risk":":.4f","P_Success":":.4f","Delta_Risk":":.4f","Delta_P_Success":":.4f","Scenario":False}
    )
    fig.update_traces(mode="markers", marker=dict(line=dict(width=1.2, color="#E8EEF8"), sizemin=10))
    fig.update_xaxes(range=[max(0, scenario_rank["Chain_Risk"].min()-0.04), min(1, scenario_rank["Chain_Risk"].max()+0.06)], title="Chain risk →")
    fig.update_yaxes(range=[0, max(.05, scenario_rank["P_Success"].max()+0.02)], title="Propagation-adjusted P(success) →")
    fig.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.22, xanchor="left", x=0))
    st.plotly_chart(plotly_theme(fig, 600), width="stretch")
    st.markdown('<div class="plot-caption">Interpretation: upper-left is directionally preferable—lower chain risk with higher propagation-adjusted success. Bubble size represents absolute risk displacement from baseline; scenario identity is available on hover and in the legend.</div>', unsafe_allow_html=True)

    prop_long = propagation_df.melt(id_vars="Scenario", var_name="Node", value_name="Risk")
    fig = px.bar(prop_long, x="Scenario", y="Risk", color="Node", barmode="group", title="D1–D4 propagation under stress")
    fig.update_yaxes(range=[0,1], title="Node risk")
    fig.update_xaxes(tickangle=-18, title=None)
    fig.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.28, xanchor="left", x=0), bargap=.18, bargroupgap=.05)
    st.plotly_chart(plotly_theme(fig, 610), width="stretch")
    st.markdown(f"""
    <div class="decision-brief">
      <strong>Decision interpretation.</strong> The stress laboratory should be read as a sensitivity surface, not as a live optimizer.
      In the current export, <strong>{worst_risk['Scenario']}</strong> creates the largest incremental chain-risk shock, while
      <strong>{worst_success['Scenario']}</strong> produces the strongest deterioration in propagation-adjusted success.
      A decision-maker should therefore distinguish <em>risk amplification</em> from <em>success-probability erosion</em>; they are related but not identical response variables.
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# TEMPORAL & RESILIENCE
# ============================================================

with tabs[5]:
    st.markdown('<div class="section-kicker">Dynamics · recovery behavior</div>', unsafe_allow_html=True)
    st.markdown("### Temporal propagation and resilience intelligence")

    temp_nodes = ["D1_Supplier", "D2_Port", "D3_Route", "D4_Lastmile"]
    temp_risk_matrix = temporal_df[temp_nodes]
    peak_node = temp_risk_matrix.max().idxmax()
    peak_step = int(temporal_df.loc[temp_risk_matrix[peak_node].idxmax(), "Step"])
    peak_value = float(temp_risk_matrix[peak_node].max())
    min_success_step = int(temporal_df.loc[temporal_df["P_Success"].idxmin(), "Step"])
    min_success = float(temporal_df["P_Success"].min())

    res_start = float(resilience_df["D4_Lastmile"].iloc[0])
    res_end = float(resilience_df["D4_Lastmile"].iloc[-1])
    d4_reduction = res_start - res_end
    success_start = float(resilience_df["P_Success"].iloc[0])
    success_end = float(resilience_df["P_Success"].iloc[-1])
    success_recovery_pp = (success_end - success_start) * 100

    st.markdown(f"""
    <div class="insight-grid">
      <div class="insight-card"><div class="insight-label">Peak temporal risk</div><div class="insight-value">{peak_node}</div><div class="insight-note">Step {peak_step} · peak intensity {peak_value:.3f}.</div></div>
      <div class="insight-card"><div class="insight-label">Minimum success point</div><div class="insight-value">Step {min_success_step}</div><div class="insight-note">Lowest P(success): {min_success*100:.2f}%.</div></div>
      <div class="insight-card"><div class="insight-label">Resilience recovery</div><div class="insight-value">{success_recovery_pp:+.2f} pp</div><div class="insight-note">Final success-probability change versus initial resilience state.</div></div>
    </div>
    """, unsafe_allow_html=True)

    temp_long = temporal_df.melt(
        id_vars="Step",
        value_vars=temp_nodes,
        var_name="Node",
        value_name="Risk"
    )

    fig = px.line(temp_long, x="Step", y="Risk", color="Node", markers=True, title="Temporal risk propagation")
    fig.update_yaxes(range=[0, 1], title="Risk intensity")
    fig.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.24, xanchor="left", x=0))
    st.plotly_chart(plotly_theme(fig, 560), width="stretch")

    res_long = resilience_df.melt(
        id_vars="Step",
        value_vars=temp_nodes,
        var_name="Node",
        value_name="Risk"
    )

    fig = px.line(res_long, x="Step", y="Risk", color="Node", markers=True, title="Resilience intervention trajectory")
    fig.update_yaxes(range=[0, 1], title="Risk intensity")
    fig.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.24, xanchor="left", x=0))
    st.plotly_chart(plotly_theme(fig, 560), width="stretch")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=resilience_df["Step"], y=resilience_df["P_Success"],
        mode="lines+markers",
        line=dict(width=4, color="#75D7B2"),
        marker=dict(size=10, line=dict(width=1.5, color="#E8EEF8")),
        fill="tozeroy",
        fillcolor="rgba(117,215,178,.12)",
        hovertemplate="Step %{x}<br>P(success)=%{y:.4f}<extra></extra>"
    ))
    fig.update_layout(title="Success probability recovery under resilience intervention")
    fig.update_yaxes(range=[0, max(0.20, resilience_df["P_Success"].max()+0.04)], title="P(success)")
    fig.update_xaxes(title="Step")
    st.plotly_chart(plotly_theme(fig, 460), width="stretch")

    st.markdown(f"""
    <div class="decision-brief">
      <strong>Temporal-resilience brief.</strong> The temporal export shows where instability peaks before intervention,
      while the resilience trajectory shows whether a staged mitigation path improves the operating state.
      In this run, D4 last-mile risk changes from <strong>{res_start:.3f}</strong> to <strong>{res_end:.3f}</strong>
      ({d4_reduction:+.3f} reduction), while P(success) recovers by <strong>{success_recovery_pp:+.2f} percentage points</strong>.
      This helps separate early warning from recovery planning.
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# HITL
# ============================================================

with tabs[6]:
    st.markdown('<div class="section-kicker">Expert override · governed intervention</div>', unsafe_allow_html=True)
    st.markdown("### Human-in-the-loop decision space")

    hitl_view = hitl_df.copy()
    baseline_hitl = hitl_view[hitl_view["Scenario"] == "Baseline"]
    base_risk = float(baseline_hitl["Chain_Risk"].iloc[0]) if not baseline_hitl.empty else float(hitl_view["Chain_Risk"].median())
    base_success = float(baseline_hitl["P_Success"].iloc[0]) if not baseline_hitl.empty else float(hitl_view["P_Success"].median())
    hitl_view["Success_Gain_pp"] = (hitl_view["P_Success"] - base_success) * 100
    hitl_view["Risk_Change"] = hitl_view["Chain_Risk"] - base_risk
    hitl_view["Decision_Utility"] = hitl_view["Success_Gain_pp"] - 25 * hitl_view["Risk_Change"]
    best = hitl_view.sort_values(["Decision_Utility","P_Success"], ascending=False).iloc[0]
    highest_success = hitl_view.sort_values("P_Success", ascending=False).iloc[0]

    st.markdown(f"""
    <div class="insight-grid">
      <div class="insight-card"><div class="insight-label">Highest success outcome</div><div class="insight-value">{highest_success['Scenario']}</div><div class="insight-note">{highest_success['P_Success']*100:.2f}% precomputed P(success).</div></div>
      <div class="insight-card"><div class="insight-label">Decision-utility leader</div><div class="insight-value">{best['Scenario']}</div><div class="insight-note">Ranks success gain jointly with chain-risk movement.</div></div>
      <div class="insight-card"><div class="insight-label">Governance principle</div><div class="insight-value">Human override ≠ automatic improvement</div><div class="insight-note">Interventions are compared against the baseline and remain auditable.</div></div>
    </div>
    """, unsafe_allow_html=True)

    fig = px.scatter(
        hitl_view, x="Chain_Risk", y="P_Success", color="Scenario",
        size=np.clip(np.abs(hitl_view["Success_Gain_pp"]) + 2, 2, None),
        hover_name="Scenario",
        hover_data={"Chain_Risk":":.4f","P_Success":":.4f","Success_Gain_pp":":+.2f","Risk_Change":":+.4f","Decision_Utility":":+.2f","Scenario":False},
        title="Expert intervention decision space"
    )
    fig.add_vline(x=base_risk, line_width=1, line_dash="dash", line_color="#65758B")
    fig.add_hline(y=base_success, line_width=1, line_dash="dash", line_color="#65758B")
    fig.update_traces(marker=dict(line=dict(width=1.2, color="#E8EEF8"), sizemin=10))
    fig.update_xaxes(range=[0,1], title="Chain risk → lower is preferable")
    fig.update_yaxes(range=[0, max(.5, hitl_view["P_Success"].max()+.05)], title="P(success) → higher is preferable")
    fig.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.22, xanchor="left", x=0))
    st.plotly_chart(plotly_theme(fig, 610), width="stretch")
    st.markdown('<div class="plot-caption">Dashed lines mark the baseline. The preferred directional quadrant is upper-left: higher success with lower chain risk. This view deliberately avoids permanent point labels; scenario details are exposed through hover to prevent annotation collisions.</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="signal">
      <div class="signal-title">HITL decision brief</div>
      <div class="signal-main">{best['Scenario']}</div>
      <div class="signal-sub">
      Under the prototype utility view, this intervention offers the strongest balance between success improvement and chain-risk movement.
      Success gain versus baseline: <b>{best['Success_Gain_pp']:+.2f} pp</b> · Chain-risk change: <b>{best['Risk_Change']:+.3f}</b>.
      This is a comparative research signal, not an autonomous execution instruction.
      </div>
    </div>
    """, unsafe_allow_html=True)

    display_hitl = hitl_view[["Scenario","Chain_Risk","P_Success","Risk_Change","Success_Gain_pp","Decision_Utility"]].sort_values("Decision_Utility", ascending=False)
    st.dataframe(
        dataframe_dark(display_hitl, {
            "Chain_Risk":"{:.3f}","P_Success":"{:.4f}","Risk_Change":"{:+.3f}",
            "Success_Gain_pp":"{:+.2f}","Decision_Utility":"{:+.2f}"
        }),
        hide_index=True, width="stretch"
    )

# ============================================================
# METHODOLOGY
# ============================================================

with tabs[7]:
    st.markdown("### Methodological disclosure")
    st.markdown("""
    <div class="method-note">
    <b>RYPE is a research prototype for explainable operational risk intelligence.</b><br><br>
    The contribution is the integration of externally grounded geopolitical risk indicators, causal operational regeneration,
    D1–D4 propagation, counterfactual intervention analysis and human-in-the-loop decision support within one coherent MVP.
    The current dynamic route engine uses origin-node geopolitical pressure as the main external trigger; the destination port provides route context and visualization.
    Scenario, temporal, resilience and HITL panels display precomputed research export outputs.<br><br>
    <b>Planned extension:</b> AIS vessel position, ETA drift, speed anomaly, route deviation, ERP shipment logs and live port congestion feeds.
    </div>
    """, unsafe_allow_html=True)
    st.markdown("### Data and version layer")
    st.json({
        "geo_df": list(geo_df.shape),
        "port_bridge_df": list(port_bridge_df.shape),
        "port_risk_df": list(port_risk_df.shape),
        "metadata_project": metadata.get("project"),
        "metadata_version": metadata.get("version"),
        "app_version": "RYPE MVP v0.6 modular architecture"
    })
