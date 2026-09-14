"""Unit and Integration Tests for Smart Retail Intelligence AI Layer.

Verifies:
1. Strict adherence to risk level thresholds (including 0.87 -> HIGH).
2. Strict adherence to the agreed 5-field JSON payload schema.
3. Feature engineering and anomaly detection logic.
4. Replenishment recommendation behavior.
5. REST integration and mock backend ingestion.
"""

import json
import os
import sys
import time
import pytest
import pandas as pd

# Add src to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))

from data_generator import generate_retail_dataset
from feature_engineering import extract_features, get_feature_matrix, FEATURE_COLUMNS
from stockout_predictor import StockoutPredictor, map_risk_level
from anomaly_detector import InventoryAnomalyDetector
from risk_scorer import calculate_stock_accuracy_risk, calculate_demand_priority, InventoryRiskScorer
from replenishment_engine import (
    determine_recommended_action,
    calculate_replenishment_quantity,
    generate_root_cause_explanation,
    ReplenishmentEngine,
)
from pipeline import InventoryAIPipeline
from rest_client import (
    BackendIngestionClient,
    MockBackendServer,
    validate_risk_payload,
    REQUIRED_PAYLOAD_FIELDS,
    VALID_RISK_LEVELS,
    VALID_RECOMMENDED_ACTIONS,
)


class TestRiskLevelThresholds:
    """Verify exact risk-level thresholds and boundary values requested by user:
    LOW: < 0.35
    MEDIUM: >= 0.35 and < 0.65
    HIGH: >= 0.65 and < 0.90
    CRITICAL: >= 0.90
    """

    def test_low_threshold(self):
        assert map_risk_level(0.00) == "LOW"
        assert map_risk_level(0.20) == "LOW"
        assert map_risk_level(0.34) == "LOW"
        assert map_risk_level(0.349) == "LOW"

    def test_medium_threshold(self):
        assert map_risk_level(0.35) == "MEDIUM"
        assert map_risk_level(0.50) == "MEDIUM"
        assert map_risk_level(0.64) == "MEDIUM"
        assert map_risk_level(0.649) == "MEDIUM"

    def test_high_threshold(self):
        assert map_risk_level(0.65) == "HIGH"
        assert map_risk_level(0.89) == "HIGH"
        assert map_risk_level(0.899) == "HIGH"

    def test_critical_threshold(self):
        assert map_risk_level(0.90) == "CRITICAL"
        assert map_risk_level(0.95) == "CRITICAL"
        assert map_risk_level(1.00) == "CRITICAL"

    def test_exact_required_boundary_values(self):
        """Verify boundary values 0.34, 0.35, 0.64, 0.65, 0.89, and 0.90."""
        assert map_risk_level(0.34) == "LOW"
        assert map_risk_level(0.35) == "MEDIUM"
        assert map_risk_level(0.64) == "MEDIUM"
        assert map_risk_level(0.65) == "HIGH"
        assert map_risk_level(0.89) == "HIGH"
        assert map_risk_level(0.90) == "CRITICAL"

    def test_agreed_example_087_maps_to_high(self):
        """CRITICAL: Agreed API example requires stockoutProbability 0.87 -> HIGH."""
        assert map_risk_level(0.87) == "HIGH"


class TestCalibratedStockoutPredictor:
    """Verify CalibratedClassifierCV (sigmoid calibration) model training and inference."""

    @pytest.fixture(scope="module")
    def trained_predictor(self):
        predictor = StockoutPredictor()
        df = generate_retail_dataset(n_samples=400, random_seed=42)
        metrics = predictor.train(df)
        return predictor, metrics, df

    def test_calibrated_model_trains_and_predicts_successfully(self, trained_predictor):
        predictor, metrics, df = trained_predictor
        assert "roc_auc" in metrics
        assert metrics["roc_auc"] >= 0.85
        assert metrics.get("calibration") == "sigmoid"

        preds = predictor.predict_batch(df.head(20))
        assert len(preds) == 20
        for p in preds:
            assert "stockoutProbability" in p
            assert "riskLevel" in p

    def test_probability_always_bounded_between_zero_and_one(self, trained_predictor):
        predictor, _, df = trained_predictor
        probs = predictor.predict_probability(df)
        assert len(probs) == len(df)
        assert (probs >= 0.0).all(), "Found probability below 0.0"
        assert (probs <= 1.0).all(), "Found probability above 1.0"
        for p in probs:
            assert isinstance(float(p), float)
            assert 0.0 <= p <= 1.0

    def test_predicted_risk_levels_follow_thresholds(self, trained_predictor):
        predictor, _, df = trained_predictor
        preds = predictor.predict_batch(df)
        for item in preds:
            prob = item["stockoutProbability"]
            risk = item["riskLevel"]
            if prob < 0.35:
                assert risk == "LOW", f"Prob {prob} expected LOW, got {risk}"
            elif prob < 0.65:
                assert risk == "MEDIUM", f"Prob {prob} expected MEDIUM, got {risk}"
            elif prob < 0.90:
                assert risk == "HIGH", f"Prob {prob} expected HIGH, got {risk}"
            else:
                assert risk == "CRITICAL", f"Prob {prob} expected CRITICAL, got {risk}"


class TestAgreedSchema:
    """Verify strict 5-field JSON payload schema."""

    @pytest.fixture(scope="module")
    def pipeline_instance(self):
        pipeline = InventoryAIPipeline()
        pipeline.train(n_samples=300)
        return pipeline

    def test_exact_5_field_keys(self, pipeline_instance):
        df = generate_retail_dataset(n_samples=10)
        results = pipeline_instance.run_inference(df, enriched=False)

        expected_keys = {
            "productId",
            "stockoutProbability",
            "riskLevel",
            "anomaly",
            "recommendedAction",
        }

        for item in results:
            assert set(item.keys()) == expected_keys, f"Payload keys mismatch: {item.keys()}"
            assert isinstance(item["productId"], int)
            assert isinstance(item["stockoutProbability"], float)
            assert 0.0 <= item["stockoutProbability"] <= 1.0
            assert item["riskLevel"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
            assert isinstance(item["anomaly"], bool)
            assert item["recommendedAction"] in [
                "REPLENISH",
                "EXPEDITE",
                "CYCLE_COUNT_AUDIT",
                "MONITOR",
                "NO_ACTION",
            ]

    def test_agreed_example_compatibility(self, pipeline_instance):
        """Verify that productId 101 scenario produces expected structure and values."""
        df = generate_retail_dataset(n_samples=5)
        results = pipeline_instance.run_inference(df, enriched=False)

        prod_101 = next((item for item in results if item["productId"] == 101), None)
        assert prod_101 is not None
        assert prod_101["riskLevel"] in ["HIGH", "CRITICAL"]
        assert prod_101["recommendedAction"] == "REPLENISH"
        assert isinstance(prod_101["anomaly"], bool)


class TestFeatureEngineeringAndAnomaly:
    """Verify data transformations and anomaly detection."""

    def test_features_computed_without_nan(self):
        df = generate_retail_dataset(n_samples=25)
        feat_df = extract_features(df)

        required_features = [
            "velocityRatio",
            "leadTimeDemand",
            "daysOfSupply",
            "stockToRopRatio",
            "netAvailableBuffer",
            "businessImpactScore",
        ]
        for f in required_features:
            assert f in feat_df.columns
            assert not feat_df[f].isnull().any()

    def test_phantom_inventory_anomaly_flagged(self):
        detector = InventoryAnomalyDetector()
        df = generate_retail_dataset(n_samples=150)
        detector.fit(df)

        # Create explicit phantom inventory scenario (high recorded stock, huge discrepancy)
        anom_row = pd.Series({
            "currentInventory": 100,
            "discrepancyMagnitude": 35.0,
            "inventoryAdjustments": -20,
            "exceptionFrequency": 6,
            "shrinkageIndicator": 0.20,
            "daysOfSupply": 1.2,
        })
        is_anom, score, reason = detector.detect_row(anom_row)
        assert is_anom is True
        assert score >= 0.70
        assert "phantom" in reason.lower() or "discrepancy" in reason.lower() or "shrinkage" in reason.lower()


class TestInventoryAnomalyDetection:
    """Step 4 — Verify and improve inventory anomaly detection:
    1. Phantom inventory (recorded stock is significantly higher than physical stock).
    2. Negative inventory discrepancies (negative stock counts or severe write-offs).
    3. Unusual shrinkage (exceeding standard retail loss rates).
    4. Sudden/unnatural sales-velocity changes (surges or collapses).
    5. Normal inventory is not incorrectly flagged.
    """

    @pytest.fixture(scope="module")
    def fitted_detector(self):
        detector = InventoryAnomalyDetector()
        df = generate_retail_dataset(n_samples=250, random_seed=42)
        detector.fit(df)
        return detector

    def test_phantom_inventory_detected(self, fitted_detector):
        """Verify phantom inventory: recorded stock is significantly higher than physical stock."""
        row = pd.Series({
            "currentInventory": 85,
            "physicalInventory": 15,  # 70-unit phantom gap
            "inventoryAdjustments": 0,
            "exceptionFrequency": 1,
            "shrinkageIndicator": 0.02,
            "velocityRatio": 1.0,
            "daysOfSupply": 8.0,
        })
        is_anom, score, reason = fitted_detector.detect_row(row)
        assert is_anom is True
        assert score >= 0.70
        assert "phantom" in reason.lower()

    def test_negative_discrepant_inventory_detected(self, fitted_detector):
        """Verify negative stock count or severe write-offs are detected."""
        # Case A: Negative on-hand inventory count
        row_negative_stock = pd.Series({
            "currentInventory": -6,
            "physicalInventory": 0,
            "inventoryAdjustments": 0,
            "exceptionFrequency": 1,
            "shrinkageIndicator": 0.02,
            "velocityRatio": 1.0,
        })
        is_anom, score, reason = fitted_detector.detect_row(row_negative_stock)
        assert is_anom is True
        assert score >= 0.80
        assert "negative" in reason.lower()

        # Case B: Severe negative manual adjustment / write-off
        row_severe_adjustment = pd.Series({
            "currentInventory": 40,
            "physicalInventory": 40,
            "inventoryAdjustments": -15,
            "exceptionFrequency": 2,
            "shrinkageIndicator": 0.02,
            "velocityRatio": 1.0,
        })
        is_anom, score, reason = fitted_detector.detect_row(row_severe_adjustment)
        assert is_anom is True
        assert score >= 0.70
        assert "negative" in reason.lower() or "adjustment" in reason.lower()

    def test_unusual_shrinkage_detected(self, fitted_detector):
        """Verify unusual shrinkage: observed loss rate significantly above normal baseline."""
        row_high_shrinkage = pd.Series({
            "currentInventory": 50,
            "physicalInventory": 50,
            "inventoryAdjustments": 0,
            "exceptionFrequency": 2,
            "shrinkageIndicator": 0.18,  # 18% shrinkage vs normal 1-3%
            "velocityRatio": 1.0,
            "daysOfSupply": 6.0,
        })
        is_anom, score, reason = fitted_detector.detect_row(row_high_shrinkage)
        assert is_anom is True
        assert score >= 0.75
        assert "shrinkage" in reason.lower()

    def test_sudden_velocity_changes_detected(self, fitted_detector):
        """Verify sudden/unnatural sales-velocity changes (surge or collapse)."""
        # Surge: 3.0x velocity spike
        row_surge = pd.Series({
            "currentInventory": 50,
            "physicalInventory": 50,
            "velocityRatio": 3.0,
            "salesVelocity30d": 10.0,
            "inventoryAdjustments": 0,
            "exceptionFrequency": 0,
            "shrinkageIndicator": 0.02,
            "daysOfSupply": 3.0,
        })
        is_anom, score, reason = fitted_detector.detect_row(row_surge)
        assert is_anom is True
        assert score >= 0.70
        assert "velocity" in reason.lower()

        # Collapse: velocity drops to 10% of normal on an active product
        row_collapse = pd.Series({
            "currentInventory": 50,
            "physicalInventory": 50,
            "velocityRatio": 0.10,
            "salesVelocity30d": 20.0,
            "inventoryAdjustments": 0,
            "exceptionFrequency": 0,
            "shrinkageIndicator": 0.02,
            "daysOfSupply": 25.0,
        })
        is_anom, score, reason = fitted_detector.detect_row(row_collapse)
        assert is_anom is True
        assert score >= 0.70
        assert "velocity" in reason.lower()

    def test_normal_inventory_not_incorrectly_flagged(self, fitted_detector):
        """Verify clean, normal inventory is not falsely flagged as anomalous."""
        normal_row = pd.Series({
            "currentInventory": 120,
            "physicalInventory": 120,
            "discrepancyMagnitude": 0.0,
            "inventoryAdjustments": 0,
            "exceptionFrequency": 0,
            "shrinkageIndicator": 0.015,  # 1.5% normal retail shrinkage
            "velocityRatio": 1.02,
            "salesVelocity7d": 12.0,
            "salesVelocity30d": 11.8,
            "daysOfSupply": 10.0,
        })
        is_anom, score, reason = fitted_detector.detect_row(normal_row)
        assert is_anom is False
        assert score <= 0.30
        assert "normal" in reason.lower()

    def test_detect_batch_output_schema(self, fitted_detector):
        """Verify detect_batch returns list of dicts with anomaly, anomalyScore, and anomalyReason."""
        df = generate_retail_dataset(n_samples=10, random_seed=42)
        results = fitted_detector.detect_batch(df)

        assert len(results) == 10
        for item in results:
            assert "anomaly" in item
            assert isinstance(item["anomaly"], bool)
            assert "anomalyScore" in item
            assert isinstance(item["anomalyScore"], float)
            assert 0.0 <= item["anomalyScore"] <= 1.0
            assert "anomalyReason" in item
            assert isinstance(item["anomalyReason"], str)
            assert len(item["anomalyReason"]) > 5


class TestReplenishmentLogic:
    """Step 5 — Verify risk scoring and replenishment recommendations:
    1. High-risk low-stock products receive REPLENISH.
    2. Critical-risk products with delayed lead time receive EXPEDITE.
    3. Significant anomalies receive CYCLE_COUNT_AUDIT.
    4. Moderate-risk products receive MONITOR.
    5. Healthy products receive NO_ACTION.
    6. Reorder quantities are non-negative and logically calculated.
    7. Root-cause explanations are generated when appropriate.
    8. Stock accuracy risk score uses discrepancies, shrinkage, and anomaly info.
    """

    def test_replenish_action_on_high_risk(self):
        """High-risk low-stock products receive REPLENISH."""
        action = determine_recommended_action(
            stockout_prob=0.87,
            risk_level="HIGH",
            anomaly=True,
            current_inventory=14,
            reorder_point=120,
            lead_time_delay=5,
            velocity_ratio=1.2,
        )
        assert action == "REPLENISH"

    def test_expedite_action_on_critical_delayed_lead(self):
        """Critical-risk products with delayed lead time receive EXPEDITE."""
        action = determine_recommended_action(
            stockout_prob=0.96,
            risk_level="CRITICAL",
            anomaly=False,
            current_inventory=2,
            reorder_point=150,
            lead_time_delay=12,
            velocity_ratio=1.8,
            sales_velocity_7d=25.0,
        )
        assert action == "EXPEDITE"

    def test_audit_action_on_anomaly_with_moderate_stock(self):
        """Significant anomalies receive CYCLE_COUNT_AUDIT."""
        action = determine_recommended_action(
            stockout_prob=0.30,
            risk_level="LOW",
            anomaly=True,
            current_inventory=80,
            reorder_point=40,
            lead_time_delay=3,
            velocity_ratio=1.0,
        )
        assert action == "CYCLE_COUNT_AUDIT"

    def test_monitor_action_on_moderate_risk(self):
        """Moderate-risk products with sufficient remaining stock receive MONITOR."""
        action = determine_recommended_action(
            stockout_prob=0.48,
            risk_level="MEDIUM",
            anomaly=False,
            current_inventory=65,
            reorder_point=60,
            lead_time_delay=3,
            velocity_ratio=1.05,
        )
        assert action == "MONITOR"

    def test_no_action_on_healthy_stock(self):
        """Healthy products receive NO_ACTION."""
        action = determine_recommended_action(
            stockout_prob=0.10,
            risk_level="LOW",
            anomaly=False,
            current_inventory=200,
            reorder_point=50,
            lead_time_delay=3,
            velocity_ratio=1.0,
        )
        assert action == "NO_ACTION"

    def test_reorder_quantities_are_non_negative_and_logically_calculated(self):
        """Verify reorder quantities: non-negative and computed using ROP, current stock, and safety stock."""
        # Case 1: Low stock (current stock 10, ROP 100, safety stock 20) -> (100 - 10) + 20 = 110
        qty1 = calculate_replenishment_quantity(current_inventory=10, reorder_point=100, safety_stock=20)
        assert qty1 == 110
        assert isinstance(qty1, int) and qty1 >= 0

        # Case 2: Overstock (current stock 300, ROP 100, safety stock 20) -> max(0, -180) = 0
        qty2 = calculate_replenishment_quantity(current_inventory=300, reorder_point=100, safety_stock=20)
        assert qty2 == 0
        assert isinstance(qty2, int) and qty2 >= 0

        # Case 3: Exactly at ROP (current stock 100, ROP 100, safety stock 25) -> 0 + 25 = 25
        qty3 = calculate_replenishment_quantity(current_inventory=100, reorder_point=100, safety_stock=25)
        assert qty3 == 25
        assert isinstance(qty3, int) and qty3 >= 0

        # Case 4: Zero inventory (current stock 0, ROP 50, safety stock 15) -> 50 + 15 = 65
        qty4 = calculate_replenishment_quantity(current_inventory=0, reorder_point=50, safety_stock=15)
        assert qty4 == 65
        assert isinstance(qty4, int) and qty4 >= 0

    def test_root_cause_explanations_generated_appropriately(self):
        """Verify natural language root-cause explanations generated for each action."""
        row = pd.Series({
            "currentInventory": 14,
            "reorderPoint": 120,
            "salesVelocity7d": 28.0,
            "salesVelocity30d": 22.0,
            "velocityRatio": 1.27,
            "replenishmentDelay": 5,
            "inventoryAdjustments": -12,
            "exceptionFrequency": 7,
            "shrinkageIndicator": 0.18,
            "daysOfSupply": 0.5,
        })

        # Explanations for all actions
        exp_replenish = generate_root_cause_explanation(row, 0.87, "HIGH", True, "REPLENISH")
        assert len(exp_replenish) > 10
        assert "stock" in exp_replenish.lower()

        exp_expedite = generate_root_cause_explanation(row, 0.95, "CRITICAL", False, "EXPEDITE")
        assert len(exp_expedite) > 10
        assert "expedite" in exp_expedite.lower() or "lead time" in exp_expedite.lower()

        exp_audit = generate_root_cause_explanation(row, 0.30, "LOW", True, "CYCLE_COUNT_AUDIT")
        assert len(exp_audit) > 10
        assert "audit" in exp_audit.lower() or "anomaly" in exp_audit.lower()

        exp_monitor = generate_root_cause_explanation(row, 0.50, "MEDIUM", False, "MONITOR")
        assert len(exp_monitor) > 10
        assert "monitor" in exp_monitor.lower()

        exp_no_action = generate_root_cause_explanation(row, 0.10, "LOW", False, "NO_ACTION")
        assert len(exp_no_action) > 10
        assert "healthy" in exp_no_action.lower()

    def test_stock_accuracy_risk_scoring_uses_discrepancies_shrinkage_and_anomalies(self):
        """Verify stock accuracy risk scoring incorporates discrepancy, shrinkage, and anomaly data."""
        # Clean row: zero adjustments, zero discrepancy, normal shrinkage, no anomaly
        clean_row = pd.Series({
            "discrepancyMagnitude": 0.0,
            "inventoryAdjustments": 0.0,
            "exceptionFrequency": 0,
            "shrinkageIndicator": 0.015,
        })
        clean_risk = calculate_stock_accuracy_risk(clean_row, anomaly_score=0.10, is_anomaly=False)
        assert clean_risk <= 0.20

        # Anomalous row: high discrepancy, severe negative adjustments, high shrinkage, flagged anomaly
        anom_row = pd.Series({
            "discrepancyMagnitude": 20.0,
            "inventoryAdjustments": -18.0,
            "exceptionFrequency": 6,
            "shrinkageIndicator": 0.20,
        })
        anom_risk = calculate_stock_accuracy_risk(anom_row, anomaly_score=0.90, is_anomaly=True)
        assert anom_risk >= 0.70
        assert anom_risk > clean_risk

        # Priority scoring: high stockout risk + high revenue velocity should produce critical/high priority
        p_score, p_tier = calculate_demand_priority(
            stockout_prob=0.87,
            stock_accuracy_risk=anom_risk,
            business_impact=3500.0,
            max_business_impact=5000.0,
        )
        assert 0.0 <= p_score <= 100.0
        assert p_tier in ["P1_CRITICAL", "P2_HIGH"]


class TestRestIntegration:
    """Step 6 — Verify REST integration with the Java backend:
    POST /api/v1/ingestion/inventory-risk
    1. Payload contains exactly the 5 fields: productId, stockoutProbability, riskLevel, anomaly, recommendedAction.
    2. JSON values have the correct data types.
    3. Python successfully sends the POST request to the Java backend.
    4. The mock backend receives and validates the payload correctly.
    5. Retry/error handling works for a failed request.
    6. Batch payload transmission works (both array POST and item-by-item).
    """

    def test_payload_contains_exactly_5_fields(self):
        """Verify the payload contains exactly productId, stockoutProbability, riskLevel, anomaly, recommendedAction."""
        pipeline = InventoryAIPipeline()
        pipeline.ensure_ready()
        df = generate_retail_dataset(n_samples=5, random_seed=42)
        payloads = pipeline.run_inference(df, enriched=False)

        assert len(payloads) == 5
        for p in payloads:
            assert set(p.keys()) == REQUIRED_PAYLOAD_FIELDS
            assert len(p) == 5

    def test_payload_values_have_correct_data_types(self):
        """Verify all JSON values adhere strictly to expected types and ranges."""
        pipeline = InventoryAIPipeline()
        pipeline.ensure_ready()
        df = generate_retail_dataset(n_samples=10, random_seed=42)
        payloads = pipeline.run_inference(df, enriched=False)

        for p in payloads:
            is_valid, err = validate_risk_payload(p)
            assert is_valid is True, f"Validation failed: {err}"
            # Exact type assertions
            assert isinstance(p["productId"], int) and not isinstance(p["productId"], bool)
            assert isinstance(p["stockoutProbability"], (float, int)) and not isinstance(p["stockoutProbability"], bool)
            assert 0.0 <= p["stockoutProbability"] <= 1.0
            assert isinstance(p["riskLevel"], str)
            assert p["riskLevel"] in VALID_RISK_LEVELS
            assert isinstance(p["anomaly"], bool)
            assert isinstance(p["recommendedAction"], str)
            assert p["recommendedAction"] in VALID_RECOMMENDED_ACTIONS

    def test_python_successfully_sends_post_request_to_java_backend(self):
        """Verify Python client sends HTTP POST to /api/v1/ingestion/inventory-risk and backend receives it."""
        with MockBackendServer(port=0) as server:
            time.sleep(0.2)
            client = BackendIngestionClient(base_url=f"http://127.0.0.1:{server.port}")
            test_payload = {
                "productId": 101,
                "stockoutProbability": 0.87,
                "riskLevel": "HIGH",
                "anomaly": True,
                "recommendedAction": "REPLENISH",
            }

            res = client.send_single(test_payload)
            assert res["status"] == "success"
            assert res["status_code"] == 200

            received = server.get_received()
            assert len(received) == 1
            assert received[0] == test_payload

    def test_mock_backend_validates_payload_correctly(self):
        """Verify mock backend validates payload: accepts valid and rejects malformed/invalid payloads with HTTP 400."""
        with MockBackendServer(port=0) as server:
            time.sleep(0.2)
            client = BackendIngestionClient(base_url=f"http://127.0.0.1:{server.port}")

            # 1. Valid payload accepted
            valid_payload = {
                "productId": 101,
                "stockoutProbability": 0.87,
                "riskLevel": "HIGH",
                "anomaly": True,
                "recommendedAction": "REPLENISH",
            }
            res_valid = client.send_single(valid_payload)
            assert res_valid["status"] == "success"
            assert res_valid["status_code"] == 200

            # 2. Missing required field rejected
            invalid_missing = {
                "productId": 102,
                "stockoutProbability": 0.50,
                "riskLevel": "MEDIUM",
                # missing anomaly and recommendedAction
            }
            res_missing = client.send_single(invalid_missing)
            assert res_missing["status"] == "failed"
            assert res_missing["status_code"] == 400
            assert "Missing required fields" in res_missing["response"]

            # 3. Extra unexpected field rejected
            invalid_extra = {
                **valid_payload,
                "productId": 103,
                "unauthorizedField": "leak",
            }
            res_extra = client.send_single(invalid_extra)
            assert res_extra["status"] == "failed"
            assert res_extra["status_code"] == 400
            assert "Unexpected extra fields" in res_extra["response"]

            # 4. Invalid data type rejected (e.g. anomaly is string instead of boolean)
            invalid_type = {
                **valid_payload,
                "productId": 104,
                "anomaly": "true",  # string instead of bool
            }
            res_type = client.send_single(invalid_type)
            assert res_type["status"] == "failed"
            assert res_type["status_code"] == 400
            assert "must be a boolean" in res_type["response"]

            # 5. Invalid probability range (> 1.0) rejected
            invalid_prob = {
                **valid_payload,
                "productId": 105,
                "stockoutProbability": 1.45,
            }
            res_prob = client.send_single(invalid_prob)
            assert res_prob["status"] == "failed"
            assert res_prob["status_code"] == 400
            assert "between 0.0 and 1.0" in res_prob["response"]

            # 6. Invalid risk level enum rejected
            invalid_risk = {
                **valid_payload,
                "productId": 106,
                "riskLevel": "SUPER_CRITICAL",
            }
            res_risk = client.send_single(invalid_risk)
            assert res_risk["status"] == "failed"
            assert res_risk["status_code"] == 400
            assert "riskLevel" in res_risk["response"]

    def test_retry_and_error_handling_for_failed_request(self):
        """Verify retry and error handling when sending to an unavailable backend."""
        # Unreachable port on localhost
        dead_port = 61234
        client = BackendIngestionClient(
            base_url=f"http://127.0.0.1:{dead_port}",
            timeout=1.0,
            max_retries=2,
        )
        test_payload = {
            "productId": 101,
            "stockoutProbability": 0.87,
            "riskLevel": "HIGH",
            "anomaly": True,
            "recommendedAction": "REPLENISH",
        }

        start_time = time.time()
        res = client.send_single(test_payload)
        elapsed = time.time() - start_time

        # Should handle error gracefully without throwing uncaught exceptions
        assert res["status"] == "error"
        assert res["status_code"] is None
        assert res["error"] is not None
        # Retries occurred with sleep
        assert elapsed >= 0.2

    def test_batch_payload_transmission_array_and_item_by_item(self):
        """Verify batch payload transmission: both JSON array POST and item-by-item modes."""
        with MockBackendServer(port=0) as server:
            time.sleep(0.2)
            client = BackendIngestionClient(base_url=f"http://127.0.0.1:{server.port}")

            batch = [
                {
                    "productId": 201,
                    "stockoutProbability": 0.87,
                    "riskLevel": "HIGH",
                    "anomaly": True,
                    "recommendedAction": "REPLENISH",
                },
                {
                    "productId": 202,
                    "stockoutProbability": 0.95,
                    "riskLevel": "CRITICAL",
                    "anomaly": False,
                    "recommendedAction": "EXPEDITE",
                },
                {
                    "productId": 203,
                    "stockoutProbability": 0.20,
                    "riskLevel": "LOW",
                    "anomaly": False,
                    "recommendedAction": "NO_ACTION",
                },
            ]

            # 1. Batch array mode (single HTTP request transmitting JSON array)
            res_array = client.send_batch(batch, item_by_item=False)
            assert res_array["status"] == "success"
            assert res_array["status_code"] == 200
            assert res_array["total"] == 3

            # 2. Item-by-item mode (sequential HTTP requests per item)
            batch_sequential = [
                {
                    "productId": 301,
                    "stockoutProbability": 0.40,
                    "riskLevel": "MEDIUM",
                    "anomaly": False,
                    "recommendedAction": "MONITOR",
                },
                {
                    "productId": 302,
                    "stockoutProbability": 0.25,
                    "riskLevel": "LOW",
                    "anomaly": True,
                    "recommendedAction": "CYCLE_COUNT_AUDIT",
                },
            ]
            res_seq = client.send_batch(batch_sequential, item_by_item=True)
            assert res_seq["total"] == 2
            assert res_seq["successful"] == 2
            assert res_seq["failed"] == 0

            # Verify all 5 items reached the backend
            all_received = server.get_received()
            assert len(all_received) == 5
            received_ids = [item["productId"] for item in all_received]
            assert received_ids == [201, 202, 203, 301, 302]


class TestPreventDataLeakage:
    """Step 3 — Prevent data leakage verification tests:
    1. No future information is used as a feature.
    2. The target is not included in the features.
    3. Training data comes before test data (time-aware train/test split).
    4. The model still trains and predicts successfully.
    5. All existing tests continue to pass.
    """

    def test_no_future_information_in_features(self):
        """Verify feature set contains only past and current operational features."""
        df = generate_retail_dataset(n_samples=50, random_seed=42)
        X = get_feature_matrix(df)

        forbidden_patterns = [
            "future",
            "next",
            "tomorrow",
            "forecast",
            "subsequent",
            "target",
            "stockoutoccurred",
            "stockoutwithinnext7days",
        ]

        for col in X.columns:
            lower_col = col.lower()
            for pat in forbidden_patterns:
                assert pat not in lower_col, f"Potential future leakage found in feature: {col}"

        # Explicitly check required historical and current features
        expected_feature_subset = {
            "currentInventory",
            "historicalSales",
            "salesVelocity7d",
            "salesVelocity30d",
            "velocityRatio",
            "velocityAcceleration",
            "replenishmentDelay",
            "inventoryAdjustments",
            "shrinkageIndicator",
            "exceptionFrequency",
        }
        assert expected_feature_subset.issubset(set(X.columns))

    def test_target_not_included_in_features(self):
        """Verify target column is never included in the features."""
        df = generate_retail_dataset(n_samples=50, random_seed=42)
        target_candidates = ["stockoutWithinNext7Days", "stockoutOccurred", "isAnomalyLabel"]

        # 1. Check FEATURE_COLUMNS
        for t in target_candidates:
            assert t not in FEATURE_COLUMNS, f"Target {t} found in FEATURE_COLUMNS!"

        # 2. Check get_feature_matrix output
        X = get_feature_matrix(df)
        for t in target_candidates:
            assert t not in X.columns, f"Target {t} found in feature matrix columns!"

    def test_training_data_comes_before_test_data(self):
        """Verify time-aware split: training data strictly precedes test data chronologically."""
        df = generate_retail_dataset(n_samples=300, random_seed=42)
        predictor = StockoutPredictor()
        metrics = predictor.train(df, target_col="stockoutWithinNext7Days", test_size=0.25)

        assert metrics.get("time_aware_split") is True
        assert "train_time_max" in metrics
        assert "test_time_min" in metrics

        # Chronological assertion: max timestamp in training <= min timestamp in testing
        train_max = pd.Timestamp(metrics["train_time_max"])
        test_min = pd.Timestamp(metrics["test_time_min"])
        assert train_max <= test_min, f"Temporal leakage: train_max ({train_max}) > test_min ({test_min})"

    def test_model_still_trains_and_predicts_successfully_with_time_split(self):
        """Verify model accuracy and predictions after time-aware split."""
        df = generate_retail_dataset(n_samples=400, random_seed=42)
        predictor = StockoutPredictor()
        metrics = predictor.train(df, target_col="stockoutWithinNext7Days")

        assert metrics["roc_auc"] >= 0.85
        assert metrics["calibration"] == "sigmoid"

        # Predict on holdout future data
        future_batch = df.iloc[-30:]
        probs = predictor.predict_probability(future_batch)
        assert len(probs) == 30
        assert (probs >= 0.0).all() and (probs <= 1.0).all()

        preds = predictor.predict_batch(future_batch)
        for item in preds:
            assert item["riskLevel"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
