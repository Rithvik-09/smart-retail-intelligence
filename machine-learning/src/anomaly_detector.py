"""Inventory Anomaly & Discrepancy Detector Module.

Uses an unsupervised Isolation Forest model combined with domain-specific
statistical rules to identify:
1. Phantom inventory (recorded stock significantly higher than physical stock)
2. Negative inventory discrepancies (negative stock counts or severe write-offs)
3. Unusual shrinkage (theft/loss rates exceeding standard retail baselines)
4. Sudden / unnatural sales-velocity changes (surges or abnormal demand collapses)
"""

from typing import Any, Dict, List, Optional, Tuple, Union
import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

try:
    from .feature_engineering import extract_features
except ImportError:
    from feature_engineering import extract_features


DEFAULT_ANOMALY_MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "models", "anomaly_model.pkl"
)

ANOMALY_FEATURE_COLS = [
    "inventoryAdjustments",
    "exceptionFrequency",
    "shrinkageIndicator",
    "discrepancyMagnitude",
    "velocityRatio",
    "daysOfSupply",
]


class InventoryAnomalyDetector:
    """Detects inventory anomalies using Isolation Forest and domain discrepancy heuristics."""

    def __init__(self, model_path: Optional[str] = None, contamination: float = 0.10):
        self.model_path = model_path or DEFAULT_ANOMALY_MODEL_PATH
        self.contamination = contamination
        self.model: Optional[IsolationForest] = None

    def fit(self, df: pd.DataFrame) -> None:
        """Fit the Isolation Forest model on historical inventory observations.

        Args:
            df: DataFrame containing inventory and adjustment metrics.
        """
        df_feat = extract_features(df)
        X = df_feat[ANOMALY_FEATURE_COLS].fillna(0.0)

        iso = IsolationForest(
            n_estimators=100,
            contamination=self.contamination,
            random_state=42,
            n_jobs=-1,
        )
        iso.fit(X)
        self.model = iso

        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(self.model, self.model_path)

    def load(self, model_path: Optional[str] = None) -> None:
        """Load fitted anomaly model from disk."""
        path = model_path or self.model_path
        if not os.path.exists(path):
            raise FileNotFoundError(f"Anomaly model not found at {path}. Fit model first.")
        self.model = joblib.load(path)

    def detect_row(self, row: pd.Series) -> Tuple[bool, float, str]:
        """Detect anomaly for a single record using hybrid ML + rule validation.

        Evaluates:
            1. Phantom inventory: Recorded stock is significantly higher than physical stock.
            2. Negative inventory / discrepancies: Negative stock or severe negative adjustments.
            3. Unusual shrinkage: Shrinkage rate substantially above normal retail baseline.
            4. Sudden / unnatural sales-velocity changes: Drastic demand surges or drops.
            5. Multidimensional statistical anomalies via Isolation Forest.

        Args:
            row: Series containing product inventory metrics.

        Returns:
            Tuple of (is_anomaly: bool, anomaly_score: float, anomaly_reason: str).
        """
        current_inv = float(row.get("currentInventory", 0.0))
        physical_inv = float(row.get("physicalInventory", current_inv))
        discrepancy = float(row.get("discrepancyMagnitude", abs(current_inv - physical_inv)))
        adj = float(row.get("inventoryAdjustments", 0.0))
        exceptions = float(row.get("exceptionFrequency", 0.0))
        shrinkage = float(row.get("shrinkageIndicator", 0.0))
        v_ratio = float(row.get("velocityRatio", 1.0))
        v30 = float(row.get("salesVelocity30d", 10.0))
        days_supply = float(row.get("daysOfSupply", 5.0))

        # Check 1: Negative Inventory or Severe Negative Discrepancy
        if current_inv < 0:
            return True, 0.95, f"Negative inventory discrepancy detected: system recorded stock is negative ({int(current_inv)} units)."

        if adj <= -8.0:
            return True, 0.85, f"Negative inventory discrepancy detected: severe negative stock adjustment ({int(adj)} units) indicating unrecorded write-offs."

        # Check 2: Phantom Inventory
        # System shows substantial stock on hand, but physical shelf count is substantially lower
        if current_inv > 0 and physical_inv < current_inv:
            stock_gap = current_inv - physical_inv
            if stock_gap >= 8.0 or (current_inv >= 10 and (stock_gap / current_inv) >= 0.40):
                return True, 0.90, f"Phantom inventory detected: system recorded stock ({int(current_inv)} units) is significantly higher than physical count ({int(physical_inv)} units)."

        if discrepancy >= 12.0 and current_inv > 0:
            return True, 0.88, f"Phantom inventory detected: recorded stock ({int(current_inv)} units) diverges significantly from shelf reality (discrepancy: {discrepancy:.1f} units)."

        # Check 3: Unusual Shrinkage
        # Normal retail shrinkage is 1-3%. Shrinkage >= 10% is anomalous
        if shrinkage >= 0.10:
            score = round(min(0.95, 0.70 + shrinkage), 2)
            return True, score, f"Unusual shrinkage detected: observed shrinkage rate ({shrinkage:.1%}) substantially exceeds normal retail loss baseline."

        if exceptions >= 5 and shrinkage >= 0.07:
            return True, 0.84, f"Unusual shrinkage detected: elevated shrinkage rate ({shrinkage:.1%}) coupled with high scan exception frequency ({int(exceptions)} incidents)."

        # Check 4: Sudden / Unnatural Sales-Velocity Changes
        if v_ratio >= 2.5:
            return True, 0.82, f"Sudden/unnatural sales-velocity surge: 7-day velocity is {v_ratio:.2f}x higher than 30-day baseline."

        if v_ratio <= 0.20 and v30 >= 5.0:
            return True, 0.78, f"Sudden/unnatural sales-velocity collapse: 7-day velocity dropped to {v_ratio:.2f}x of 30-day baseline."

        # Check 5: Multidimensional Isolation Forest Inference
        if self.model is not None:
            features = pd.DataFrame(
                [[adj, exceptions, shrinkage, discrepancy, v_ratio, days_supply]],
                columns=ANOMALY_FEATURE_COLS,
            )
            ml_pred = self.model.predict(features)[0]  # -1 for anomaly, 1 for inlier
            raw_score = float(-self.model.decision_function(features)[0])  # higher = more anomalous

            if ml_pred == -1:
                norm_score = round(float(np.clip(0.60 + raw_score, 0.60, 0.95)), 2)
                return True, norm_score, "Statistical multidimensional discrepancy anomaly identified by Isolation Forest."

        # Normal inventory
        return False, 0.12, "Normal inventory tracking pattern."

    def detect_batch(self, df: pd.DataFrame) -> List[Dict[str, Union[bool, float, str]]]:
        """Detect anomalies for a batch of inventory records.

        Args:
            df: DataFrame containing inventory records.

        Returns:
            List of dicts with 'anomaly' (bool), 'anomalyScore', and 'anomalyReason'.
        """
        if self.model is None and os.path.exists(self.model_path):
            try:
                self.load()
            except Exception:
                pass

        df_feat = extract_features(df)
        results = []

        for _, row in df_feat.iterrows():
            is_anom, score, reason = self.detect_row(row)
            results.append({
                "anomaly": bool(is_anom),
                "anomalyScore": round(float(score), 2),
                "anomalyReason": reason,
            })
        return results


if __name__ == "__main__":
    from data_generator import generate_retail_dataset

    train_data = generate_retail_dataset(n_samples=500)
    detector = InventoryAnomalyDetector()
    detector.fit(train_data)
    print("Anomaly detector trained successfully.")

    sample_test = train_data.head(5)
    anom_results = detector.detect_batch(sample_test)
    for i, res in enumerate(anom_results):
        print(f"Product {sample_test.iloc[i]['productId']}: anomaly={res['anomaly']} (score={res['anomalyScore']}) - {res['anomalyReason']}")
