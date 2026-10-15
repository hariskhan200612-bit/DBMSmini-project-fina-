"""Dataset loading and type normalization."""
from pathlib import Path
import pandas as pd

NUMERIC_CANDIDATES = [
    "Max_Temperature_C", "Min_Temperature_C", "Hist_Normal_MaxTemp_C",
    "Temp_Anomaly_C", "Relative_Humidity_Pct", "Wind_Speed_kmh",
    "Elevation_m", "Latitude", "Longitude", "Consecutive_Hot_Days",
]

def read_dataset(path: str | Path) -> pd.DataFrame:
    """Read the CSV and normalize known numeric/date columns safely."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)
    data = pd.read_csv(path)
    data.columns = [str(column).strip() for column in data.columns]
    for column in NUMERIC_CANDIDATES:
        if column in data.columns:
            data[column] = pd.to_numeric(data[column], errors="coerce")
    if "Timestamp" in data.columns:
        # Dataset dates are day-first (e.g. 14-10-2026).
        data["Timestamp"] = pd.to_datetime(data["Timestamp"], errors="coerce", dayfirst=True)
    return data
