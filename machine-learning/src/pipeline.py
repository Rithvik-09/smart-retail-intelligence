"""End-to-End Inventory AI Pipeline Module.

Orchestrates data ingestion, feature engineering, stock-out prediction,
anomaly detection, risk scoring, replenishment recommendations, and
standardized JSON serialization for Java backend ingestion.
"""

from typing import Any, Dict, List, Optional, Union
import json
import os
import pandas as pd

try:
    from .data_generator import generate_retail_dataset
    from .feature_engineering import extract_features
    from .stockout_predictor import StockoutPredictor, map_risk_level
    from .anomaly_detector import InventoryAnomalyDetector
    from .risk_scorer import InventoryRiskScorer
    from .replenishment_engine import ReplenishmentEngine
except ImportError:
    from data_generator import generate_retail_dataset
    from feature_engineering import extract_features
    from stockout_predictor import StockoutPredictor, map_risk_level
    from anomaly_detector import InventoryAnomalyDetector
    from risk_scorer import InventoryRiskScorer
    from replenishment_engine import ReplenishmentEngine


class InventoryAIPipeline:
    """Master AI pipeline for Smart Retail Intelligence."""

    def __init__(
        self,
        predictor_path: Optional[str] = None,
        anomaly_path: Optional[str] = None,
    ):
        self.predictor = StockoutPredictor(model_path=predictor_path)
        self.anomaly_detector = InventoryAnomalyDetector(model_path=anomaly_path)
        self.risk_scorer = InventoryRiskScorer()
        self.replenishment_engine = ReplenishmentEngine()

    def train(self, df: Optional[pd.DataFrame] = None, n_samples: int = 1500) -> Dict[str, Any]:
        """Train both stockout predictor and anomaly detector models.

        Args:
            df: Training DataFrame (if None, synthetic dataset is generated).
            n_samples: Number of synthetic training records if df is None.

        Returns:
            Dict containing training evaluation metrics.
        """
        if df is None:
            df = generate_retail_dataset(n_samples=n_samples, random_seed=42)

        feat_df = extract_features(df)

        # Train stockout classifier
        pred_metrics = self.predictor.train(feat_df)

        # Fit anomaly detector
        self.anomaly_detector.fit(feat_df)

        return {
            "stockout_predictor": pred_metrics,
            "anomaly_detector": {"status": "fitted", "samples": len(feat_df)},
        }

    def ensure_ready(self) -> None:
        """Ensure all required models are loaded or trained."""
        predictor_ready = False
        anomaly_ready = False

        try:
            self.predictor.load()
            predictor_ready = True
        except Exception:
            pass

        try:
            self.anomaly_detector.load()
            anomaly_ready = True
        except Exception:
            pass

        if not (predictor_ready and anomaly_ready):
            print("Models not found on disk. Initializing and training baseline models...")
            self.train()

    def run_inference(
        self,
        df: pd.DataFrame,
        enriched: bool = False,
    ) -> List[Dict[str, Any]]:
        """Run complete AI inference on an incoming batch of inventory records.

        Args:
            df: DataFrame containing inventory records.
            enriched: If False, returns strictly the agreed 5-field schema:
                      {
                          "productId": 101,
                          "stockoutProbability": 0.87,
                          "riskLevel": "HIGH",
                          "anomaly": true,
                          "recommendedAction": "REPLENISH"
                      }
                      If True, appends extended root-cause, priority, and order quantity context.

        Returns:
            List of dictionaries formatted for JSON serialization.
        """
        self.ensure_ready()

        # Step 1: Feature Engineering
        feat_df = extract_features(df)

        # Step 2: Stockout Prediction & Risk Level
        stockout_results = self.predictor.predict_batch(feat_df)
        stockout_probs = [r["stockoutProbability"] for r in stockout_results]

        # Step 3: Anomaly & Discrepancy Detection
        anomaly_results = self.anomaly_detector.detect_batch(feat_df)

        # Step 4: Stock Accuracy Risk & Demand Prioritization (using discrepancies, shrinkage, and anomalies)
        risk_results = self.risk_scorer.score_batch(feat_df, stockout_probs, anomaly_results=anomaly_results)

        # Step 5: Replenishment Action & Root Cause Suggestions
        action_results = self.replenishment_engine.evaluate_batch(
            feat_df, stockout_results, anomaly_results
        )

        # Step 6: Construct Final Structured Payload
        output_payloads = []
        for i, (_, row) in enumerate(feat_df.iterrows()):
            p_id = int(row.get("productId", i + 1))
            prob = float(stockout_results[i]["stockoutProbability"])
            r_level = str(stockout_results[i]["riskLevel"])
            anom = bool(anomaly_results[i]["anomaly"])
            action = str(action_results[i]["recommendedAction"])

            # Agreed 5-field core JSON payload
            payload = {
                "productId": p_id,
                "stockoutProbability": prob,
                "riskLevel": r_level,
                "anomaly": anom,
                "recommendedAction": action,
            }

            # Optional extended context
            if enriched:
                payload.update({
                    "stockAccuracyRiskScore": risk_results[i]["stockAccuracyRiskScore"],
                    "priorityScore": risk_results[i]["priorityScore"],
                    "priorityTier": risk_results[i]["priorityTier"],
                    "anomalyReason": anomaly_results[i]["anomalyReason"],
                    "recommendedOrderQuantity": action_results[i]["suggestedOrderQty"],
                    "rootCauseExplanation": action_results[i]["rootCauses"],
                })

            output_payloads.append(payload)

        return output_payloads

    def run_inference_json(self, df: pd.DataFrame, enriched: bool = False, indent: Optional[int] = 2) -> str:
        """Run inference and return serialized JSON string."""
        payloads = self.run_inference(df, enriched=enriched)
        return json.dumps(payloads, indent=indent)


if __name__ == "__main__":
    from data_generator import generate_retail_dataset

    sample_data = generate_retail_dataset(n_samples=10)
    pipeline = InventoryAIPipeline()
    pipeline.train()
    results = pipeline.run_inference(sample_data.head(3))
    print("Inference results (Strict 5-field schema):")
    print(json.dumps(results, indent=2))
