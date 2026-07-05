from __future__ import annotations

from typing import Optional, Tuple, List

import pandas as pd

ISO3_TO_ISO2 = {"AFG":"AF","ARE":"AE","CHN":"CN","EGY":"EG","NLD":"NL","SAU":"SA","SGP":"SG","YEM":"YE"}

FALLBACK_COORDS = {
    "YEADE": (12.78, 44.99), "SGSIN": (1.26, 103.82), "NLRTM": (51.92, 4.48),
    "CNSHA": (31.23, 121.47), "SAJED": (21.49, 39.19), "EGPSD": (31.26, 32.30),
    "EGALY": (31.20, 29.92),
}

MARITIME_WAYPOINTS = {
    ("YEADE", "NLRTM"): [(12.78,44.99),(12.6,43.3),(18.7,39.5),(27.5,33.8),(30.5,32.3),(35.3,20.0),(37.5,10.0),(36.0,-5.5),(43.5,-9.5),(49.0,-5.5),(51.92,4.48)],
    ("SGSIN", "NLRTM"): [(1.26,103.82),(5.5,95.0),(8.0,80.0),(12.0,60.0),(12.6,43.3),(27.5,33.8),(30.5,32.3),(35.3,20.0),(37.5,10.0),(36.0,-5.5),(43.5,-9.5),(49.0,-5.5),(51.92,4.48)],
    ("CNSHA", "NLRTM"): [(31.23,121.47),(24.0,120.0),(12.0,110.0),(1.26,103.82),(5.5,95.0),(12.6,43.3),(27.5,33.8),(30.5,32.3),(35.3,20.0),(37.5,10.0),(36.0,-5.5),(43.5,-9.5),(49.0,-5.5),(51.92,4.48)],
    ("SAJED", "NLRTM"): [(21.49,39.19),(22.0,38.0),(27.5,33.8),(30.5,32.3),(35.3,20.0),(37.5,10.0),(36.0,-5.5),(43.5,-9.5),(49.0,-5.5),(51.92,4.48)],
}


def build_port_risk_layer(geo_df: pd.DataFrame, port_bridge_df: pd.DataFrame) -> pd.DataFrame:
    """Build the port/location to external geopolitical-risk bridge."""
    geo = geo_df.copy()
    geo["country_code_iso2"] = geo["country_code"].map(ISO3_TO_ISO2)
    latest_geo = geo.sort_values("risk_month").groupby("country_code", as_index=False).tail(1)

    port_risk_df = port_bridge_df.merge(
        latest_geo,
        left_on="country_code",
        right_on="country_code_iso2",
        how="inner",
        suffixes=("_port", "_geo"),
    )

    return port_risk_df[[
        "port_locode", "port_name", "country_code_geo", "country_name", "risk_month",
        "conflict_index_real", "governance_fragility_risk", "sanctions_risk",
        "trade_restriction_risk", "geo_risk_score_real", "coordinates"
    ]].rename(columns={"country_code_geo": "country_code"})


def parse_unlocode_coord(x: object) -> Optional[Tuple[float, float]]:
    """Parse a UN/LOCODE coordinate string into latitude and longitude."""
    if pd.isna(x):
        return None
    try:
        parts = str(x).strip().split()
        if len(parts) != 2:
            return None
        lat_s, lon_s = parts
        lat = int(lat_s[:-1][:2]) + int(lat_s[:-1][2:]) / 60
        lon = int(lon_s[:-1][:3]) + int(lon_s[:-1][3:]) / 60
        if lat_s[-1] == "S":
            lat *= -1
        if lon_s[-1] == "W":
            lon *= -1
        return lat, lon
    except Exception:
        return None


def get_port_coord(code: str, port_bridge_df: pd.DataFrame) -> Optional[Tuple[float, float]]:
    """Return coordinates for a port/location code using fallback or UN/LOCODE coordinates."""
    if code in FALLBACK_COORDS:
        return FALLBACK_COORDS[code]
    row = port_bridge_df[port_bridge_df["port_locode"] == code]
    if row.empty:
        return None
    return parse_unlocode_coord(row.iloc[0].get("coordinates"))


def ocean_route(origin_code: str, dest_code: str, port_bridge_df: pd.DataFrame) -> Optional[List[Tuple[float, float]]]:
    """Return an illustrative maritime corridor, not an AIS-derived vessel trajectory."""
    if (origin_code, dest_code) in MARITIME_WAYPOINTS:
        return MARITIME_WAYPOINTS[(origin_code, dest_code)]
    start = get_port_coord(origin_code, port_bridge_df)
    end = get_port_coord(dest_code, port_bridge_df)
    if start is None or end is None:
        return None
    lat1, lon1 = start
    lat2, lon2 = end
    mid = ((lat1 + lat2) / 2 - 8, (lon1 + lon2) / 2)
    return [start, mid, end]
