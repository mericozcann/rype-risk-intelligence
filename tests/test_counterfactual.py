from src.rype.data_loader import load_rype_data
from src.rype.geo_risk import build_port_risk_layer
from src.rype.counterfactual import compare_routes_real


def test_compare_routes_real_returns_two_rows():
    geo_df, port_bridge_df, *_ = load_rype_data("data")
    port_risk_df = build_port_risk_layer(geo_df, port_bridge_df)
    _, _, df = compare_routes_real("YEADE", "NLRTM", "SGSIN", port_risk_df, port_bridge_df, 42)
    assert len(df) == 2
    assert set(df["Scenario"]) == {"Original", "Counterfactual"}
