"""Stock-out Predictor Module.

Trains and runs supervised ML classification models to predict stockout probability
and categorize stockout risk levels based on calibrated probabilities.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
import os
import joblib
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
from sklearn.model_selection import train_test_split

try:
    from .feature_engineering import FEATURE_COLUMNS, get_feature_matrix
except ImportError:
    from feature_engineering import FEATURE_COLUMNS, get_feature_matrix


DEFAULT_MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "models", "stockout_model.pkl"
)


def map_risk_level(stockout_prob: float) -> str:
    """Map stock-out probability to agreed business risk categories.

    Threshold definitions strictly enforced:
        - LOW:      prob < 0.35
        - MEDIUM:   0.35 <= prob < 0.65
        - HIGH:     0.65 <= prob < 0.90   (e.g., 0.87 -> HIGH)
        - CRITICAL: prob >= 0.90

    Args:
        stockout_prob: Probability value between 0.0 and 1.0.

    Returns:
        Risk level string: 'LOW', 'MEDIUM', 'HIGH', or 'CRITICAL'.
    """
    prob = float(np.clip(stockout_prob, 0.0, 1.0))
    if prob < 0.35:
        return "LOW"
    elif prob < 0.65:
        return "MEDIUM"
    elif prob < 0.90:
        return "HIGH"
    else:
        return "CRITICAL"


class StockoutPredictor:
    """Predicts calibrated stock-out probability using RandomForest + CalibratedClassifierCV."""

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or DEFAULT_MODEL_PATH
        self.model: Optional[Union[CalibratedClassifierCV, RandomForestClassifier]] = None
        self.feature_names: List[str] = FEATURE_COLUMNS

    def train(
        self,
        df: pd.DataFrame,
        target_col: Optional[str] = None,
        test_size: float = 0.2,
        random_state: int = 42,
    ) -> Dict[str, Any]:
        """Train CalibratedClassifierCV on past features using a time-aware train/test split.

        The model is trained strictly on earlier chronological data and evaluated on later
        chronological data to prevent temporal data leakage. No future information or target
        data is exposed to the model features.

        Args:
            df: DataFrame containing historical inventory records with timestamps and target.
            target_col: Target column name (defaults to 'stockoutWithinNext7Days' or 'stockoutOccurred').
            test_size: Fraction of chronological data reserved for testing (default: 0.2).
            random_state: Random state seed for base estimators.

        Returns:
            Dictionary with training evaluation metrics and temporal split metadata.
        """
        # Determine target column: prefer stockoutWithinNext7Days
        if target_col is None:
            if "stockoutWithinNext7Days" in df.columns:
                target_col = "stockoutWithinNext7Days"
            elif "stockoutOccurred" in df.columns:
                target_col = "stockoutOccurred"
            else:
                raise KeyError("Neither 'stockoutWithinNext7Days' nor 'stockoutOccurred' found in dataframe.")
        elif target_col not in df.columns:
            raise KeyError(f"Target column '{target_col}' not found in dataframe.")

        # Ensure chronological ordering to prevent temporal data leakage
        if "timestamp" in df.columns:
            df_sorted = df.sort_values(by="timestamp").reset_index(drop=True)
        elif "snapshotDate" in df.columns:
            df_sorted = df.sort_values(by="snapshotDate").reset_index(drop=True)
        else:
            df_sorted = df.copy().reset_index(drop=True)

        # Time-aware split: earlier data for training, later data for testing
        n_samples = len(df_sorted)
        split_idx = int(n_samples * (1.0 - test_size))
        train_df = df_sorted.iloc[:split_idx].copy()
        test_df = df_sorted.iloc[split_idx:].copy()

        # Extract features (strictly past/current information)
        X_train = get_feature_matrix(train_df)
        y_train = train_df[target_col].astype(int)

        X_test = get_feature_matrix(test_df)
        y_test = test_df[target_col].astype(int)

        # Guardrail: Assert target is never included in features
        assert target_col not in X_train.columns, f"Data leakage: {target_col} found in X_train features!"
        assert target_col not in X_test.columns, f"Data leakage: {target_col} found in X_test features!"

        base_rf = RandomForestClassifier(
            n_estimators=120,
            max_depth=8,
            min_samples_split=4,
            min_samples_leaf=2,
            class_weight="balanced",
            random_state=random_state,
            n_jobs=-1,
        )

        # Sigmoid calibration (Platt scaling) via CalibratedClassifierCV
        calibrated_clf = CalibratedClassifierCV(
            estimator=base_rf,
            method="sigmoid",
            cv=5,
        )
        calibrated_clf.fit(X_train, y_train)
        self.model = calibrated_clf

        # Evaluate on subsequent chronological test set
        y_prob = calibrated_clf.predict_proba(X_test)[:, 1]
        roc_auc = float(roc_auc_score(y_test, y_prob))

        metrics = {
            "roc_auc": round(roc_auc, 4),
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "calibration": "sigmoid",
            "time_aware_split": True,
            "target_column": target_col,
        }

        if "timestamp" in df_sorted.columns:
            metrics["train_time_max"] = str(train_df["timestamp"].max())
            metrics["test_time_min"] = str(test_df["timestamp"].min())

        # Auto-save model
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(self.model, self.model_path)
        return metrics

    def load(self, model_path: Optional[str] = None) -> None:
        """Load trained model from disk."""
        path = model_path or self.model_path
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model file not found at {path}. Please train model first.")
        self.model = joblib.load(path)

    def predict_probability(self, df: pd.DataFrame) -> np.ndarray:
        """Predict probability of stockout for incoming records.

        Args:
            df: DataFrame with inventory and sales data.

        Returns:
            1D numpy array of probabilities [0.0, 1.0].
        """
        if self.model is None:
            if os.path.exists(self.model_path):
                self.load()
            else:
                raise RuntimeError("Model is not trained or loaded.")

        X = get_feature_matrix(df)
        probabilities = self.model.predict_proba(X)[:, 1]
        bounded_probs = np.clip(probabilities, 0.0, 1.0)
        return np.round(bounded_probs, 2)

    def predict_batch(self, df: pd.DataFrame) -> List[Dict[str, Union[float, str]]]:
        """Predict probabilities and categorize risk levels for a batch of products.

        Args:
            df: DataFrame containing inventory records.

        Returns:
            List of dicts with 'stockoutProbability' and 'riskLevel'.
        """
        probs = self.predict_probability(df)
        results = []
        for p in probs:
            p_val = round(float(p), 2)
            results.append({
                "stockoutProbability": p_val,
                "riskLevel": map_risk_level(p_val),
            })
        return results

    def get_feature_importances(self) -> Dict[str, float]:
        """Return dictionary of feature importances from trained model."""
        if self.model is None:
            raise RuntimeError("Model is not trained.")

        if hasattr(self.model, "calibrated_classifiers_"):
            # Average feature importances across calibrated folds
            all_importances = [
                clf.estimator.feature_importances_
                for clf in self.model.calibrated_classifiers_
                if hasattr(clf, "estimator") and hasattr(clf.estimator, "feature_importances_")
            ]
            if all_importances:
                importances = np.mean(all_importances, axis=0)
            else:
                importances = np.zeros(len(self.feature_names))
        elif hasattr(self.model, "feature_importances_"):
            importances = self.model.feature_importances_
        else:
            importances = np.zeros(len(self.feature_names))

        return {
            feat: round(float(imp), 4)
            for feat, imp in sorted(
                zip(self.feature_names, importances),
                key=lambda item: item[1],
                reverse=True,
            )
        }


if __name__ == "__main__":
    from data_generator import generate_retail_dataset

    train_data = generate_retail_dataset(n_samples=600)
    predictor = StockoutPredictor()
    metrics = predictor.train(train_data)
    print(f"Model trained successfully. Metrics: {metrics}")
    print("Top feature importances:", predictor.get_feature_importances())

    # Test calibration on sample
    test_sample = train_data.head(5)
    sample_preds = predictor.predict_batch(test_sample)
    print("Sample batch predictions:", sample_preds)
