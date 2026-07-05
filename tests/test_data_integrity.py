from pathlib import Path
from src.rype.data_loader import validate_data_files


def test_required_data_files_exist():
    paths = validate_data_files(Path("data"))
    assert "geo" in paths
    assert "ports" in paths
    assert all(path.exists() for path in paths.values())
