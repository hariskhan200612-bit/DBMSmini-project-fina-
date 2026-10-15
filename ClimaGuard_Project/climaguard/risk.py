"""Transparent project-level risk scoring helpers.

These scores are illustrative analytics for this student project, not official
IMD warning thresholds or an operational forecasting model.
"""
import pandas as pd

def risk_from_temperature(temp, anomaly=0, hot_days=0):
    """Return an illustrative 0–100 score and its project risk band."""
    temp = float(temp) if pd.notna(temp) else 0.0
    anomaly = float(anomaly) if pd.notna(anomaly) else 0.0
    hot_days = float(hot_days) if pd.notna(hot_days) else 0.0
    if temp >= 45: score = 60
    elif temp >= 42: score = 50
    elif temp >= 40: score = 38
    elif temp >= 37: score = 22
    else: score = 8
    if anomaly >= 5: score += 20
    elif anomaly >= 3: score += 14
    elif anomaly >= 1: score += 8
    else: score += 2
    score = min(100, score + min(max(hot_days, 0) * 4, 20))
    if score >= 80: level = "CRITICAL"
    elif score >= 60: level = "HIGH"
    elif score >= 40: level = "WATCH"
    else: level = "NORMAL"
    return score, level

def add_project_risk(data: pd.DataFrame, temp_col, anomaly_col=None, hot_days_col=None) -> pd.DataFrame:
    """Return a copy of the dataset with project risk score and band columns."""
    result = data.copy()
    if temp_col and temp_col in result.columns:
        scores = []
        for _, row in result.iterrows():
            anomaly = row[anomaly_col] if anomaly_col and anomaly_col in result.columns else 0
            hot_days = row[hot_days_col] if hot_days_col and hot_days_col in result.columns else 0
            scores.append(risk_from_temperature(row[temp_col], anomaly, hot_days))
        result["_Project_Risk_Score"] = [item[0] for item in scores]
        result["_Project_Risk_Level"] = [item[1] for item in scores]
    else:
        result["_Project_Risk_Score"] = 0
        result["_Project_Risk_Level"] = "NORMAL"
    return result
