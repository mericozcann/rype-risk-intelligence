from src.rype.data_loader import load_rype_data
from src.rype.geo_risk import build_port_risk_layer
from src.rype.route_engine import analyze_route_real


def test_analyze_route_real_outputs_core_keys():
    geo_df, port_bridge_df, *_ = load_rype_data("data")
    port_risk_df = build_port_risk_layer(geo_df, port_bridge_df)
    result = analyze_route_real("YEADE", "NLRTM", port_risk_df, port_bridge_df, 42)
    for key in ["geo_pressure", "D1_supplier", "D2_port", "D3_route", "D4_lastmile", "p_success", "edge_risk_real"]:
        assert key in result
        assert 0 <= result[key] <= 1
