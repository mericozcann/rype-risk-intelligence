from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd
import yaml

DEFAULT_RISK_WEIGHTS: Dict[str, Any] = {
    "geo_pressure": {"conflict_index_real": 0.40, "governance_fragility_risk": 0.25, "sanctions_risk": 0.20, "trade_restriction_risk": 0.15},
    "operational_state": {"delay_base_hours": 8, "delay_geo_multiplier": 55, "delay_noise_std": 4, "delay_normalization_denominator": 66},
    "reroute": {"base_probability": 0.05, "geo_multiplier": 0.65},
    "customs": {"base_probability": 0.03, "trade_restriction_multiplier": 0.60, "sanctions_multiplier": 0.20},
    "damage": {"base_probability": 0.02, "conflict_multiplier": 0.25, "reroute_multiplier": 0.15},
    "disruption_score": {"delay_normalized": 0.35, "rerouted": 0.25, "customs_issue": 0.20, "damaged": 0.20, "threshold": 0.45},
    "edge_risk": {"geo_pressure": 0.30, "d4_lastmile": 0.25, "disrupted": 0.20, "rerouted": 0.15, "failure_probability": 0.10},
}

DEFAULT_PROPAGATION: Dict[str, Any] = {
    "d1_supplier": {"geo_pressure": 0.50, "delay_normalized": 0.50},
    "d2_port": {"d1_supplier": 0.40, "customs_issue": 0.35, "rerouted": 0.25},
    "d3_route": {"d2_port": 0.45, "rerouted": 0.35, "geo_pressure": 0.20},
    "d4_lastmile": {"d3_route": 0.50, "delay_normalized": 0.30, "damaged": 0.20},
}


def load_yaml_config(path: str | Path, fallback: Dict[str, Any]) -> Dict[str, Any]:
    """Load YAML config with a safe fallback for Streamlit Cloud deployments."""
    p = Path(path)
    if not p.exists():
        return fallback
    with open(p, "r", encoding="utf-8") as f:
        loaded = yaml.safe_load(f) or {}
    return loaded


def analyze_route_real(
    origin_port: str,
    destination_port: str,
    port_risk_df: pd.DataFrame,
    port_bridge_df: pd.DataFrame,
    random_state: int = 42,
    risk_weights: Dict[str, Any] | None = None,
    propagation_weights: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """Analyze a route using external geopolitical pressure and D1-D4 propagation."""
    risk_weights = risk_weights or DEFAULT_RISK_WEIGHTS
    propagation_weights = propagation_weights or DEFAULT_PROPAGATION

    origin_rows = port_risk_df[port_risk_df["port_locode"] == origin_port]
    destination_rows = port_bridge_df[port_bridge_df["port_locode"] == destination_port]
    if origin_rows.empty:
        raise ValueError(f"Origin port not found in real risk layer: {origin_port}")
    if destination_rows.empty:
        raise ValueError(f"Destination port not found: {destination_port}")

    origin = origin_rows.iloc[0]
    destination = destination_rows.iloc[0]

    gw = risk_weights["geo_pressure"]
    geo_pressure = float(np.clip(
        gw["conflict_index_real"] * origin["conflict_index_real"] +
        gw["governance_fragility_risk"] * origin["governance_fragility_risk"] +
        gw["sanctions_risk"] * origin["sanctions_risk"] +
        gw["trade_restriction_risk"] * origin["trade_restriction_risk"], 0, 1
    ))

    rng = np.random.default_rng(random_state)
    ow = risk_weights["operational_state"]
    delay_hours = max(1, ow["delay_base_hours"] + ow["delay_geo_multiplier"] * geo_pressure + rng.normal(0, ow["delay_noise_std"]))
    delay_normalized = np.clip((delay_hours - 1) / ow["delay_normalization_denominator"], 0, 1)

    rw = risk_weights["reroute"]
    reroute_probability = np.clip(rw["base_probability"] + rw["geo_multiplier"] * geo_pressure, 0, 1)
    rerouted = int(rng.random() < reroute_probability)

    cw = risk_weights["customs"]
    customs_probability = np.clip(cw["base_probability"] + cw["trade_restriction_multiplier"] * origin["trade_restriction_risk"] + cw["sanctions_multiplier"] * origin["sanctions_risk"], 0, 1)
    customs_issue = int(rng.random() < customs_probability)

    dw = risk_weights["damage"]
    damage_probability = np.clip(dw["base_probability"] + dw["conflict_multiplier"] * origin["conflict_index_real"] + dw["reroute_multiplier"] * rerouted, 0, 1)
    damaged = int(rng.random() < damage_probability)

    sw = risk_weights["disruption_score"]
    disruption_score = sw["delay_normalized"] * delay_normalized + sw["rerouted"] * rerouted + sw["customs_issue"] * customs_issue + sw["damaged"] * damaged
    disrupted = int(disruption_score > sw["threshold"])

    p = propagation_weights
    D1 = p["d1_supplier"]["geo_pressure"] * geo_pressure + p["d1_supplier"]["delay_normalized"] * delay_normalized
    D2 = p["d2_port"]["d1_supplier"] * D1 + p["d2_port"]["customs_issue"] * customs_issue + p["d2_port"]["rerouted"] * rerouted
    D3 = p["d3_route"]["d2_port"] * D2 + p["d3_route"]["rerouted"] * rerouted + p["d3_route"]["geo_pressure"] * geo_pressure
    D4 = p["d4_lastmile"]["d3_route"] * D3 + p["d4_lastmile"]["delay_normalized"] * delay_normalized + p["d4_lastmile"]["damaged"] * damaged

    p_success = (1-D1) * (1-D2) * (1-D3) * (1-D4)

    ew = risk_weights["edge_risk"]
    edge_risk_real = ew["geo_pressure"] * geo_pressure + ew["d4_lastmile"] * D4 + ew["disrupted"] * disrupted + ew["rerouted"] * rerouted + ew["failure_probability"] * (1 - p_success)

    return {
        "origin_port": origin_port, "origin_name": origin["port_name"], "origin_country": origin["country_name"],
        "destination_port": destination_port, "destination_name": destination["port_name"], "destination_country_code": destination["country_code"],
        "risk_month": origin["risk_month"], "geo_pressure": float(geo_pressure), "delay_hours": float(delay_hours),
        "delay_normalized": float(delay_normalized), "reroute_probability": float(reroute_probability), "rerouted": int(rerouted),
        "customs_probability": float(customs_probability), "customs_issue": int(customs_issue), "damage_probability": float(damage_probability),
        "damaged": int(damaged), "disruption_score": float(disruption_score), "disrupted": int(disrupted),
        "D1_supplier": float(D1), "D2_port": float(D2), "D3_route": float(D3), "D4_lastmile": float(D4),
        "p_success": float(p_success), "edge_risk_real": float(edge_risk_real),
    }
