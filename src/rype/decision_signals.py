from __future__ import annotations

from typing import Dict, Tuple, Any


def risk_label(x: float) -> str:
    if x >= 0.70:
        return "HIGH RISK"
    if x >= 0.40:
        return "MODERATE RISK"
    return "LOW RISK"


def decision_signal(original: Dict[str, Any], alternative: Dict[str, Any]) -> Tuple[str, str, float, float]:
    """Generate the route-level decision signal used by the dashboard."""
    risk_red = original["edge_risk_real"] - alternative["edge_risk_real"]
    success_gain = alternative["p_success"] - original["p_success"]
    if risk_red > 0.10 and success_gain > 0:
        return "Evaluate counterfactual origin substitution.", "The alternative origin materially reduces propagated edge risk and improves route success probability.", risk_red, success_gain
    if original["edge_risk_real"] >= 0.70:
        return "Escalate shipment review before execution.", "The selected route remains exposed to high operational propagation risk under the current scenario state.", risk_red, success_gain
    return "Proceed with monitoring.", "The selected route remains within an acceptable prototype risk band, but should still be monitored for external shocks.", risk_red, success_gain
