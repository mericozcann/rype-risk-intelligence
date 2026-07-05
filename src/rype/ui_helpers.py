from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from .decision_signals import risk_label


def metric_card(label: str, value: str, note: str) -> None:
    st.markdown((
        '<div class="metric-card">'
        f'<div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div>'
        f'<div class="metric-note">{note}</div>'
        '</div>'
    ), unsafe_allow_html=True)


def risk_badge(x: float) -> str:
    cls = "badge-high" if x >= .70 else "badge-mod" if x >= .40 else "badge-low"
    return f'<span class="{cls}">{risk_label(x)}</span>'


def plotly_theme(fig: go.Figure, height: int = 440) -> go.Figure:
    fig.update_layout(
        template="plotly_dark", height=height, margin=dict(l=20,r=20,t=58,b=28),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#0f1723", font=dict(color="#d7e0ec"),
        title_font=dict(size=18, color="#f7fbff"), legend=dict(bgcolor="rgba(0,0,0,0)")
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,.08)", zerolinecolor="rgba(255,255,255,.15)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,.08)", zerolinecolor="rgba(255,255,255,.15)")
    return fig


def dataframe_dark(df, fmt=None):
    styler = df.style
    if fmt:
        styler = styler.format(fmt)
    return styler
def inject_css(css: str) -> None:
    """Inject application-level CSS into the Streamlit interface."""
    if not isinstance(css, str):
        raise TypeError("css must be a string")

    st.markdown(
        f"<style>{css}</style>",
        unsafe_allow_html=True,
    )
