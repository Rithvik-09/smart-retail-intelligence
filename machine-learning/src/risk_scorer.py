"""Stock Accuracy Risk Scoring & Demand-Aware Prioritization Module.

Quantifies the risk that recorded inventory is inaccurate (phantom stock / shrinkage)
and prioritizes stock management actions by business impact and sales velocity.
"""

from typing import Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd

try:
    from .feature_engineering import extract_features
except ImportError:
    from feature_engineering import extract_features


def calculate_stock_accuracy_risk(
    row: pd.Series,
    anomaly_score: Optional[float] = None,
    is_anomaly: Optional[bool] = None,
) -> float:
    """Calculate normalized stock accuracy risk score (0.0 = reliable, 1.0 = highly untrustworthy).

    Formula incorporates:
        - Discrepancy magnitude (weight: 0.30)
        - Inventory adjustments magnitude (weight: 0.20)
        - Scan exception frequency (weight: 0.15)
        - Baseline shrinkage rate (weight: 0.15)
        - Anomaly information (anomaly score / flag) (weight: 0.20)

    Args:
        row: Series containing inventory feature metrics.
        anomaly_score: Optional continuous anomaly score from anomaly detector.
        is_anomaly: Optional boolean anomaly flag.

    Returns:
        float score between 0.0 and 1.0.
    """
    discrepancy = float(row.get("discrepancyMagnitude", 0.0))
    adj = abs(float(row.get("inventoryAdjustments", 0.0)))
    exceptions = float(row.get("exceptionFrequency", 0.0))
    shrinkage = float(row.get("shrinkageIndicator", 0.0))

    # Incorporate anomaly information if available in row or arguments
    if anomaly_score is None:
        if "anomalyScore" in row:
            anomaly_score = float(row["anomalyScore"])
        elif row.get("isAnomalyDetected") or row.get("anomaly"):
            anomaly_score = 0.85
        else:
            anomaly_score = 0.10

    if is_anomaly is None:
        is_anomaly = bool(row.get("isAnomalyDetected", row.get("anomaly", False)))

    # Normalized component risks
    r_disc = min(1.0, discrepancy / 15.0)
    r_adj = min(1.0, adj / 20.0)
    r_exc = min(1.0, exceptions / 8.0)
    r_shrink = min(1.0, shrinkage / 0.15)
    r_anom = min(1.0, max(0.0, anomaly_score if is_anomaly else anomaly_score * 0.2))

    risk_score = (
        0.30 * r_disc +
        0.20 * r_adj +
        0.15 * r_exc +
        0.15 * r_shrink +
        0.20 * r_anom
    )
    return round(float(np.clip(risk_score, 0.0, 1.0)), 2)


def calculate_demand_priority(
    stockout_prob: float,
    stock_accuracy_risk: float,
    business_impact: float,
    max_business_impact: float = 10000.0,
) -> Tuple[float, str]:
    """Calculate combined demand-aware priority score and ranking tier.

    Combines operational urgency (stockout probability), inventory uncertainty
    (stock accuracy risk), and financial criticality (revenue velocity: unitPrice * salesVelocity).

    Args:
        stockout_prob: Probability of stockout [0.0 - 1.0].
        stock_accuracy_risk: Stock accuracy risk score [0.0 - 1.0].
        business_impact: Revenue velocity (unitPrice * dailyVelocity).
        max_business_impact: Normalization scale factor for business impact.

    Returns:
        Tuple of (priority_score: float [0-100], priority_tier: str).
    """
    norm_impact = min(1.0, business_impact / max(1.0, max_business_impact))

    # Priority score formula: 50% stockout risk, 25% financial demand impact, 25% stock uncertainty
    score = (0.50 * stockout_prob + 0.25 * norm_impact + 0.25 * stock_accuracy_risk) * 100.0
    score = round(float(np.clip(score, 0.0, 100.0)), 1)

    if score >= 75.0:
        tier = "P1_CRITICAL"
    elif score >= 50.0:
        tier = "P2_HIGH"
    elif score >= 30.0:
        tier = "P3_MEDIUM"
    else:
        tier = "P4_ROUTINE"

    return score, tier


class InventoryRiskScorer:
    """Computes comprehensive inventory risk scores and demand prioritization."""

    def score_batch(
        self,
        df: pd.DataFrame,
        stockout_probs: List[float],
        anomaly_results: Optional[List[Dict[str, Union[bool, float, str]]]] = None,
    ) -> List[Dict[str, Union[float, str]]]:
        """Score a batch of inventory records.

        Args:
            df: DataFrame containing inventory records.
            stockout_probs: List of corresponding stockout probabilities.
            anomaly_results: Optional list of anomaly detection results.

        Returns:
            List of dicts with stock accuracy risk scores and priority rankings.
        """
        df_feat = extract_features(df)
        max_impact = df_feat["businessImpactScore"].max() if "businessImpactScore" in df_feat.columns else 5000.0
        max_impact = max(max_impact, 1000.0)

        results = []
        for i, (_, row) in enumerate(df_feat.iterrows()):
            p = stockout_probs[i]
            anom_score = None
            is_anom = None
            if anomaly_results and i < len(anomaly_results):
                anom_score = float(anomaly_results[i].get("anomalyScore", 0.10))
                is_anom = bool(anomaly_results[i].get("anomaly", False))

            accuracy_risk = calculate_stock_accuracy_risk(
                row, anomaly_score=anom_score, is_anomaly=is_anom
            )
            impact = float(row.get("businessImpactScore", 0.0))
            priority_score, priority_tier = calculate_demand_priority(
                p, accuracy_risk, impact, max_business_impact=max_impact
            )

            results.append({
                "stockAccuracyRiskScore": accuracy_risk,
                "priorityScore": priority_score,
                "priorityTier": priority_tier,
                "businessImpactScore": impact,
            })
        return results


if __name__ == "__main__":
    from data_generator import generate_retail_dataset

    df = generate_retail_dataset(n_samples=5)
    scorer = InventoryRiskScorer()
    mock_probs = [0.87, 0.30, 0.65, 0.12, 0.92]
    scores = scorer.score_batch(df, mock_probs)
    for i, s in enumerate(scores):
        print(f"Product {df.iloc[i]['productId']}: AccRisk={s['stockAccuracyRiskScore']}, Priority={s['priorityScore']} ({s['priorityTier']})")
