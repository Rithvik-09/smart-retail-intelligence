"""Feature Engineering Module.

Computes operational retail metrics, velocity trends, lead-time demand,
stock-accuracy risk indicators, and demand-aware business scores.
"""

from typing import List, Tuple
import numpy as np
import pandas as pd


# Explicit list of valid features: past and current metrics only
FEATURE_COLUMNS: List[str] = [
    "currentInventory",
    "historicalSales",
    "salesVelocity7d",
    "salesVelocity30d",
    "velocityRatio",
    "velocityAcceleration",
    "replenishmentDelay",
    "leadTimeDemand",
    "daysOfSupply",
    "stockToRopRatio",
    "netAvailableBuffer",
    "inventoryAdjustments",
    "exceptionFrequency",
    "shrinkageIndicator",
    "unitPrice",
    "businessImpactScore",
]

# Forbidden column names to prevent future data leakage
FORBIDDEN_LEAKAGE_COLUMNS = {
    "stockoutOccurred",
    "stockoutWithinNext7Days",
    "targetStockout",
    "isAnomalyLabel",
    "futureSales",
    "futureInventory",
    "futureStockout",
}


def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    """Extract and engineer predictive features from retail inventory and sales data.

    All features represent past or current operational metrics known at prediction time.
    Future information is strictly excluded.

    Args:
        df: Raw DataFrame containing sales, inventory, and supplier attributes.

    Returns:
        pd.DataFrame containing original and derived feature columns.
    """
    df = df.copy()

    # Sales velocity ratio (short-term 7d velocity vs baseline 30d velocity)
    df["velocityRatio"] = (df["salesVelocity7d"] / (df["salesVelocity30d"] + 1e-4)).round(3)

    # Past sales acceleration: change in daily rate normalized by 30-day velocity
    df["velocityAcceleration"] = (
        (df["salesVelocity7d"] - df["salesVelocity30d"]) / (df["salesVelocity30d"] + 1e-4)
    ).round(3)

    # Lead-time demand: Total expected sales consumption during current supplier lead time
    df["leadTimeDemand"] = (df["salesVelocity7d"] * df["replenishmentDelay"]).round(2)

    # Days of supply remaining with current inventory velocity
    df["daysOfSupply"] = (df["currentInventory"] / (df["salesVelocity7d"] + 1e-4)).round(2)

    # Stock to Reorder Point (ROP) ratio
    df["stockToRopRatio"] = (df["currentInventory"] / (df["reorderPoint"] + 1e-4)).round(3)

    # Net available buffer: inventory on hand minus lead-time demand
    df["netAvailableBuffer"] = (df["currentInventory"] - df["leadTimeDemand"]).round(2)

    # Net buffer relative to safety stock
    df["safetyStockRatio"] = (df["currentInventory"] / (df["safetyStock"] + 1e-4)).round(3)

    # Business impact score: Daily revenue at risk ($/day) = unitPrice * salesVelocity7d
    df["businessImpactScore"] = (df["unitPrice"] * df["salesVelocity7d"]).round(2)

    # Estimated discrepancy magnitude (using physical inventory if present, else proxy via adjustments & exceptions)
    if "physicalInventory" in df.columns:
        df["discrepancyMagnitude"] = (df["currentInventory"] - df["physicalInventory"]).abs()
    else:
        df["discrepancyMagnitude"] = (df["inventoryAdjustments"].abs() * 0.7 + df["exceptionFrequency"] * 1.5).round(2)

    # Ensure required feature columns exist and fill any NaN
    for col in FEATURE_COLUMNS:
        if col not in df.columns:
            df[col] = 0.0

    return df


def get_feature_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Return only the numeric feature matrix used for ML training and inference.

    Validates that no future information or target columns are included in the features.

    Args:
        df: DataFrame processed with extract_features.

    Returns:
        pd.DataFrame containing only columns defined in FEATURE_COLUMNS.
    """
    # Guardrail check: verify FEATURE_COLUMNS does not contain target or future columns
    leakage_found = set(FEATURE_COLUMNS).intersection(FORBIDDEN_LEAKAGE_COLUMNS)
    if leakage_found:
        raise ValueError(f"Data leakage detected in FEATURE_COLUMNS: {leakage_found}")

    if "velocityRatio" not in df.columns or "leadTimeDemand" not in df.columns or "velocityAcceleration" not in df.columns:
        df = extract_features(df)

    matrix = df[FEATURE_COLUMNS].fillna(0.0)

    # Verify no target columns are present in output matrix
    for forbidden in FORBIDDEN_LEAKAGE_COLUMNS:
        if forbidden in matrix.columns:
            raise ValueError(f"Data leakage: {forbidden} present in feature matrix!")

    return matrix


if __name__ == "__main__":
    from data_generator import generate_retail_dataset
    raw_df = generate_retail_dataset(n_samples=5)
    feat_df = extract_features(raw_df)
    print("Features extracted successfully:")
    print(feat_df[["productId", "currentInventory", "leadTimeDemand", "daysOfSupply", "businessImpactScore"]])
