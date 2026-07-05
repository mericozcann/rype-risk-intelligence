from __future__ import annotations

from typing import Tuple

import pandas as pd
import streamlit as st


def _origin_fmt(origin_options: pd.DataFrame, code: str) -> str:
    row = origin_options[origin_options["port_locode"] == code].iloc[0]
    return f"{code} — {row['port_name']}, {row['country_name']}"


def _dest_fmt(destination_options: pd.DataFrame, code: str) -> str:
    row = destination_options[destination_options["port_locode"] == code].iloc[0]
    return f"{code} — {row['port_name']}, {row['country_code']}"


def prepare_route_options(port_risk_df: pd.DataFrame, port_bridge_df: pd.DataFrame):
    origin_options = port_risk_df[["port_locode","port_name","country_name"]].drop_duplicates().sort_values(["country_name","port_name"])
    destination_options = port_bridge_df[["port_locode","port_name","country_code"]].drop_duplicates().sort_values(["country_code","port_name"])
    return origin_options, destination_options


def _init_state(origin_codes, destination_codes):
    st.session_state.setdefault("origin_port", "YEADE" if "YEADE" in origin_codes else origin_codes[0])
    st.session_state.setdefault("destination_port", "NLRTM" if "NLRTM" in destination_codes else destination_codes[0])
    st.session_state.setdefault("alternative_origin", "SGSIN" if "SGSIN" in origin_codes else origin_codes[0])
    st.session_state.setdefault("random_state", 42)


def render_route_controls(port_risk_df: pd.DataFrame, port_bridge_df: pd.DataFrame) -> Tuple[str, str, str, int]:
    """Render desktop sidebar controls and mobile-accessible Route Control Center."""
    origin_options, destination_options = prepare_route_options(port_risk_df, port_bridge_df)
    origin_codes = origin_options["port_locode"].tolist()
    destination_codes = destination_options["port_locode"].tolist()
    _init_state(origin_codes, destination_codes)

    # Desktop/sidebar controls
    st.sidebar.markdown("## ◈ RYPE Control Layer")
    st.sidebar.caption("Searchable route configuration and counterfactual design")
    st.sidebar.markdown("""
    <div class="sidebar-step"><div class="step-no">01 Route</div><div class="step-title">Select the active shipment corridor</div></div>
    <div class="sidebar-mini-note">Choose an origin risk node and a destination port. The origin node drives the current geopolitical-risk inference layer.</div>
    """, unsafe_allow_html=True)

    st.session_state.origin_port = st.sidebar.selectbox(
        "Origin risk node", origin_codes,
        index=origin_codes.index(st.session_state.origin_port) if st.session_state.origin_port in origin_codes else 0,
        format_func=lambda x: _origin_fmt(origin_options, x),
        key="sidebar_origin_port",
    )
    st.session_state.destination_port = st.sidebar.selectbox(
        "Destination port", destination_codes,
        index=destination_codes.index(st.session_state.destination_port) if st.session_state.destination_port in destination_codes else 0,
        format_func=lambda x: _dest_fmt(destination_options, x),
        key="sidebar_destination_port",
    )
    alternative_codes = [x for x in origin_codes if x != st.session_state.origin_port]
    if st.session_state.alternative_origin not in alternative_codes:
        st.session_state.alternative_origin = "SGSIN" if "SGSIN" in alternative_codes else alternative_codes[0]

    st.sidebar.markdown("""
    <div class="sidebar-step"><div class="step-no">02 Counterfactual</div><div class="step-title">Define the intervention candidate</div></div>
    <div class="sidebar-mini-note">The alternative origin is compared against the active route to quantify risk reduction and success-probability gain.</div>
    """, unsafe_allow_html=True)
    st.session_state.alternative_origin = st.sidebar.selectbox(
        "Counterfactual origin", alternative_codes,
        index=alternative_codes.index(st.session_state.alternative_origin) if st.session_state.alternative_origin in alternative_codes else 0,
        format_func=lambda x: _origin_fmt(origin_options, x),
        key="sidebar_alternative_origin",
    )

    with st.sidebar.expander("Advanced stochastic control", expanded=False):
        st.markdown("""**Simulation seed** fixes stochastic delay, reroute, customs and damage outcomes for reproducible demonstrations.""")
        st.session_state.random_state = st.number_input("Simulation seed", min_value=0, max_value=9999, value=int(st.session_state.random_state), step=1, key="sidebar_random_state")

    st.sidebar.markdown("---")
    st.sidebar.success("Tip: Click a selectbox and type a port code/name. Example: YEADE, SGSIN, Rotterdam.")
    st.sidebar.info("v0.6 keeps AIS as a planned extension; the current MVP focuses on explainable route risk propagation.")

    # Main-page mobile controls
    with st.expander("Route Control Center — mobile accessible controls", expanded=False):
        st.markdown("Critical route controls are duplicated here so mobile users do not depend on the collapsed Streamlit sidebar.")
        m1, m2, m3 = st.columns(3)
        with m1:
            mobile_origin = st.selectbox("Origin", origin_codes, index=origin_codes.index(st.session_state.origin_port), format_func=lambda x: _origin_fmt(origin_options, x), key="mobile_origin_port")
        with m2:
            mobile_destination = st.selectbox("Destination", destination_codes, index=destination_codes.index(st.session_state.destination_port), format_func=lambda x: _dest_fmt(destination_options, x), key="mobile_destination_port")
        mobile_alts = [x for x in origin_codes if x != mobile_origin]
        mobile_alt_default = st.session_state.alternative_origin if st.session_state.alternative_origin in mobile_alts else ("SGSIN" if "SGSIN" in mobile_alts else mobile_alts[0])
        with m3:
            mobile_alternative = st.selectbox("Counterfactual", mobile_alts, index=mobile_alts.index(mobile_alt_default), format_func=lambda x: _origin_fmt(origin_options, x), key="mobile_alternative_origin")
        with st.expander("Advanced Simulation Controls", expanded=False):
            mobile_seed = st.number_input("Simulation seed", min_value=0, max_value=9999, value=int(st.session_state.random_state), step=1, key="mobile_random_state")
        if st.button("Apply route controls", type="primary", use_container_width=True):
            st.session_state.origin_port = mobile_origin
            st.session_state.destination_port = mobile_destination
            st.session_state.alternative_origin = mobile_alternative
            st.session_state.random_state = mobile_seed
            st.rerun()

    return st.session_state.origin_port, st.session_state.destination_port, st.session_state.alternative_origin, int(st.session_state.random_state)
