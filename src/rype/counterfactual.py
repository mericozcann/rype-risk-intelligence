from __future__ import annotations

from typing import Any, Dict, Tuple

import pandas as pd

from .route_engine import analyze_route_real


def compare_routes_real(
    original_origin: str,
    destination: str,
    alternative_origin: str,
    port_risk_df: pd.DataFrame,
    port_bridge_df: pd.DataFrame,
    random_state: int = 42,
    risk_weights: Dict[str, Any] | None = None,
    propagation_weights: Dict[str, Any] | None = None,
) -> Tuple[Dict[str, Any], Dict[str, Any], pd.DataFrame]:
    """Compare an original route against a counterfactual origin substitution."""
    original = analyze_route_real(original_origin, destination, port_risk_df, port_bridge_df, random_state, risk_weights, propagation_weights)
    alternative = analyze_route_real(alternative_origin, destination, port_risk_df, port_bridge_df, random_state, risk_weights, propagation_weights)
    comparison = pd.DataFrame([
        {"Scenario":"Original", "Route":f"{original_origin} → {destination}", "Geo Pressure":original["geo_pressure"], "D1 Supplier":original["D1_supplier"], "D2 Port":original["D2_port"], "D3 Route":original["D3_route"], "D4 Last-mile":original["D4_lastmile"], "P Success":original["p_success"], "Edge Risk":original["edge_risk_real"]},
        {"Scenario":"Counterfactual", "Route":f"{alternative_origin} → {destination}", "Geo Pressure":alternative["geo_pressure"], "D1 Supplier":alternative["D1_supplier"], "D2 Port":alternative["D2_port"], "D3 Route":alternative["D3_route"], "D4 Last-mile":alternative["D4_lastmile"], "P Success":alternative["p_success"], "Edge Risk":alternative["edge_risk_real"]},
    ])
    return original, alternative, comparison
