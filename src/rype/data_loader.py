from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Tuple

import pandas as pd

REQUIRED_FILES = {
    "geo": "01_external/real_external_geo_risk_table.csv",
    "ports": "01_external/real_port_country_bridge.csv",
    "propagation": "02_processed/propagation_df.csv",
    "scenario": "02_processed/scenario_df.csv",
    "temporal": "02_processed/temporal_df.csv",
    "resilience": "02_processed/resilience_df.csv",
    "hitl": "02_processed/hitl_df.csv",
    "metadata": "metadata/metadata.json",
}


def _resolve_data_path(data_path: str | Path = "data") -> Path:
    """Resolve the data directory for both v0.6 and legacy v0.5 layouts."""
    base = Path(data_path)
    if (base / "01_external").exists():
        return base
    return base


def validate_data_files(data_path: str | Path = "data") -> Dict[str, Path]:
    """Validate required RYPE data files and return resolved paths."""
    base = _resolve_data_path(data_path)
    paths: Dict[str, Path] = {}
    missing = []

    for key, rel in REQUIRED_FILES.items():
        candidate = base / rel
        legacy = base / Path(rel).name
        if candidate.exists():
            paths[key] = candidate
        elif legacy.exists():
            paths[key] = legacy
        else:
            missing.append(str(candidate))

    if missing:
        raise FileNotFoundError("Missing RYPE data files: " + ", ".join(missing))
    return paths


def load_rype_data(data_path: str | Path = "data") -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    """Load all data tables required by the RYPE dashboard."""
    paths = validate_data_files(data_path)

    geo_df = pd.read_csv(paths["geo"])
    port_bridge_df = pd.read_csv(paths["ports"])
    propagation_df = pd.read_csv(paths["propagation"])
    scenario_df = pd.read_csv(paths["scenario"])
    temporal_df = pd.read_csv(paths["temporal"])
    resilience_df = pd.read_csv(paths["resilience"])
    hitl_df = pd.read_csv(paths["hitl"])

    with open(paths["metadata"], "r", encoding="utf-8") as f:
        metadata = json.load(f)

    geo_df["risk_month"] = pd.to_datetime(geo_df["risk_month"])
    return geo_df, port_bridge_df, propagation_df, scenario_df, temporal_df, resilience_df, hitl_df, metadata
