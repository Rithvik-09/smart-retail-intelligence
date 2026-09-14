"""Script to build the demonstration Jupyter notebook."""

import json
import os

notebook_cells = [
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "# Smart Retail Intelligence — Inventory AI Engine\n",
            "### Member 3: ML / Inventory AI Developer\n",
            "\n",
            "**Core Capabilities:**\n",
            "1. **Stock-Out Prediction**: Supervised machine learning classifying future stock-out likelihood within replenishment lead-time.\n",
            "2. **Inventory Anomaly Detection**: Discrepancy detection identifying phantom inventory, unrecorded shrinkage, and damaged stock.\n",
            "3. **Stock Accuracy Risk Scoring**: Probabilistic confidence quantification of shelf reality vs ERP ledger counts.\n",
            "4. **Demand-Aware Prioritization**: Revenue velocity and business impact scoring for task ranking.\n",
            "5. **Replenishment Recommendations & Root-Cause Diagnostics**: Actionable operational recommendations (`REPLENISH`, `EXPEDITE`, `CYCLE_COUNT_AUDIT`, `MONITOR`, `NO_ACTION`).\n",
            "6. **Agreed REST Ingestion**: Direct pipeline transmission to Java backend (`POST /api/v1/ingestion/inventory-risk`)."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "import sys\n",
            "import os\n",
            "import json\n",
            "import pandas as pd\n",
            "import numpy as np\n",
            "import matplotlib.pyplot as plt\n",
            "\n",
            "# Add src to module search path\n",
            "sys.path.insert(0, os.path.abspath('../src'))\n",
            "\n",
            "from data_generator import generate_retail_dataset\n",
            "from feature_engineering import extract_features\n",
            "from stockout_predictor import StockoutPredictor, map_risk_level\n",
            "from anomaly_detector import InventoryAnomalyDetector\n",
            "from risk_scorer import InventoryRiskScorer\n",
            "from replenishment_engine import ReplenishmentEngine\n",
            "from pipeline import InventoryAIPipeline\n",
            "from rest_client import BackendIngestionClient, MockBackendServer\n",
            "\n",
            "print('Environment and AI modules successfully initialized.')"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 1. Realistic Retail Data Generation\n",
            "Generates multi-category retail inventory data including seasonal demand, replenishment delays, manual adjustments, and shrinkage indicators."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "df_raw = generate_retail_dataset(n_samples=1000, random_seed=42)\n",
            "print(f'Total inventory records generated: {len(df_raw)}')\n",
            "df_raw[['productId', 'productName', 'category', 'currentInventory', 'salesVelocity7d', 'replenishmentDelay', 'stockoutOccurred']].head(8)"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 2. Feature Engineering\n",
            "Computes key operational retail features: Sales Velocity Ratios, Lead-Time Demand, Days of Supply, and Business Impact Scores."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "df_features = extract_features(df_raw)\n",
            "\n",
            "# Visualization of operational distributions\n",
            "fig, axes = plt.subplots(1, 3, figsize=(16, 4))\n",
            "\n",
            "axes[0].hist(df_features['salesVelocity7d'], bins=25, color='#2b5c8f', edgecolor='black', alpha=0.8)\n",
            "axes[0].set_title('Sales Velocity (7-Day Daily Avg)')\n",
            "axes[0].set_xlabel('Units / Day')\n",
            "axes[0].set_ylabel('Frequency')\n",
            "\n",
            "axes[1].hist(df_features['leadTimeDemand'], bins=25, color='#e67e22', edgecolor='black', alpha=0.8)\n",
            "axes[1].set_title('Lead-Time Demand Distribution')\n",
            "axes[1].set_xlabel('Expected Units Demanded During Lead Time')\n",
            "\n",
            "axes[2].hist(df_features['daysOfSupply'].clip(upper=40), bins=25, color='#27ae60', edgecolor='black', alpha=0.8)\n",
            "axes[2].set_title('Days of Supply Distribution')\n",
            "axes[2].set_xlabel('Days of Stock Remaining')\n",
            "\n",
            "plt.tight_layout()\n",
            "plt.show()"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 3. Stock-Out Prediction Model\n",
            "Trains a Random Forest classifier to predict stock-out probabilities within the replenishment window, applying calibrated risk level thresholds:\n",
            "- `LOW`: $< 0.35$\n",
            "- `MEDIUM`: $\\ge 0.35$ and $< 0.65$\n",
            "- `HIGH`: $\\ge 0.65$ and $< 0.90$ (e.g. $0.87 \\rightarrow \\text{HIGH}$)\n",
            "- `CRITICAL`: $\\ge 0.90$"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "predictor = StockoutPredictor()\n",
            "metrics = predictor.train(df_features)\n",
            "print(f'Model Training Performance: ROC-AUC = {metrics[\"roc_auc\"]}')\n",
            "\n",
            "# Feature Importance Visualization\n",
            "importances = predictor.get_feature_importances()\n",
            "top_feats = list(importances.keys())[:8]\n",
            "top_vals = [importances[k] for k in top_feats]\n",
            "\n",
            "plt.figure(figsize=(10, 4))\n",
            "plt.barh(top_feats[::-1], top_vals[::-1], color='#34495e', edgecolor='black')\n",
            "plt.title('Top Predictive Features for Stock-Out Risk')\n",
            "plt.xlabel('Relative Feature Importance')\n",
            "plt.tight_layout()\n",
            "plt.show()"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 4. Anomaly & Discrepancy Detection\n",
            "Combines an unsupervised Isolation Forest with domain discrepancy rules to detect phantom stock (system shows inventory while physical shelf is empty), unrecorded shrinkage, and negative stock drift."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "detector = InventoryAnomalyDetector()\n",
            "detector.fit(df_features)\n",
            "\n",
            "anomaly_results = detector.detect_batch(df_features)\n",
            "df_features['isAnomalyDetected'] = [r['anomaly'] for r in anomaly_results]\n",
            "\n",
            "# Scatter plot: Recorded Stock vs Physical Stock with Anomaly highlights\n",
            "plt.figure(figsize=(9, 6))\n",
            "normal_mask = ~df_features['isAnomalyDetected']\n",
            "anom_mask = df_features['isAnomalyDetected']\n",
            "\n",
            "plt.scatter(df_features.loc[normal_mask, 'currentInventory'], df_features.loc[normal_mask, 'physicalInventory'],\n",
            "            c='#2ecc71', alpha=0.6, label='Normal Stock Record', s=35)\n",
            "plt.scatter(df_features.loc[anom_mask, 'currentInventory'], df_features.loc[anom_mask, 'physicalInventory'],\n",
            "            c='#e74c3c', marker='x', s=70, label='Discrepancy / Phantom Inventory Anomaly')\n",
            "\n",
            "plt.plot([0, 300], [0, 300], 'k--', alpha=0.4, label='Perfect Alignment (1:1)')\n",
            "plt.title('Inventory Ledger vs Physical Count: Discrepancy Detection')\n",
            "plt.xlabel('Recorded System Inventory')\n",
            "plt.ylabel('Actual Physical Inventory')\n",
            "plt.legend()\n",
            "plt.tight_layout()\n",
            "plt.show()"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 5. End-to-End AI Pipeline & Agreed 5-Field JSON Serialization\n",
            "Executes the full pipeline and inspects the exact agreed 5-field schema output."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "pipeline = InventoryAIPipeline()\n",
            "pipeline.ensure_ready()\n",
            "\n",
            "# Run inference on sample set\n",
            "test_sample = df_raw.head(5)\n",
            "agreed_output = pipeline.run_inference(test_sample, enriched=False)\n",
            "\n",
            "print('Agreed 5-Field JSON Output for Java Ingestion:')\n",
            "print(json.dumps(agreed_output, indent=2))"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 6. Simulated REST Dispatch to Java Backend\n",
            "Demonstrates direct API transmission to `POST /api/v1/ingestion/inventory-risk` using the built-in mock backend server."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Launch local mock server to verify HTTP contract\n",
            "import time\n",
            "mock_server = MockBackendServer(port=8080)\n",
            "mock_server.start()\n",
            "time.sleep(0.5)\n",
            "\n",
            "try:\n",
            "    client = BackendIngestionClient(base_url='http://127.0.0.1:8080')\n",
            "    summary = client.send_batch(agreed_output, item_by_item=True)\n",
            "    print(f'REST Dispatch Status: {summary[\"successful\"]} / {summary[\"total\"]} payloads ingested successfully.')\n",
            "    \n",
            "    # Inspect what the backend received\n",
            "    received = mock_server.get_received()\n",
            "    print(f'Backend successfully verified receipt of {len(received)} items.')\n",
            "    print('Sample verified item at backend:', json.dumps(received[0], indent=2))\n",
            "finally:\n",
            "    mock_server.stop()"
        ]
    }
]

notebook_dict = {
    "cells": notebook_cells,
    "metadata": {
        "language_info": {
            "name": "python",
            "version": "3.11.9"
        },
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 2
}

output_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "notebooks",
    "inventory_intelligence_demo.ipynb"
)
os.makedirs(os.path.dirname(output_path), exist_ok=True)

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(notebook_dict, f, indent=2)

print(f"Generated demonstration notebook at: {output_path}")
