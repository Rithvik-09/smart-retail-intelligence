# Smart Retail Intelligence — Inventory AI Engine
> **Member 3 Handoff: ML / Inventory AI Developer**  
> Smart India Hackathon (SIH) Prototype

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests: 13 Passed](https://img.shields.io/badge/tests-13%20passed-brightgreen.svg)]()
[![Backend Contract: Compliant](https://img.shields.io/badge/REST%20Contract-POST%20%2Fapi%2Fv1%2Fingestion%2Finventory--risk-orange.svg)]()

---

## 📌 Executive Summary & Role Goal

The **Inventory AI Engine** delivers an intelligent, demand-aware prediction and anomaly detection layer for autonomous retail inventory management. Designed specifically as a high-performance, lightweight microservice for the SIH prototype, it bridges physical store realities (shrinkage, shelf misplacement, scan errors) with predictive restocking logic.

### Core Responsibilities
- **Stock-Out Prediction**: Supervised ML models calculating calibrated probabilities of stock depletion within supplier replenishment windows.
- **Inventory Anomaly & Discrepancy Detection**: Dual-layer detection (Isolation Forest + statistical rules) flagging phantom inventory, unrecorded shrinkage, and physical count divergence.
- **Stock Accuracy Risk Scoring**: Quantifying confidence in ledger counts based on manual adjustment rates, exception scans, and shrinkage history.
- **Demand-Aware Prioritization**: Dynamic business impact ranking (revenue velocity $\times$ margin $\times$ urgency tier).
- **Replenishment Recommendations & Root-Cause Diagnostics**: Generating actionable recommendations (`REPLENISH`, `EXPEDITE`, `CYCLE_COUNT_AUDIT`, `MONITOR`, `NO_ACTION`) coupled with human-interpretable explanations.
- **Decoupled REST Ingestion**: Directly feeding structured risk assessments to the Java Spring Boot backend without frontend coupling.

---

## 🏛️ System Architecture

```
  +-------------------------------------------------------------------------+
  |                              DATA INGESTION                             |
  |  - Sales Transactions      - On-Hand Inventory    - Cycle Counts        |
  |  - Adjustments / Thefts    - Scan Exceptions      - Supplier Lead Times |
  +------------------------------------+------------------------------------+
                                       |
                                       v
  +-------------------------------------------------------------------------+
  |                       FEATURE ENGINEERING ENGINE                        |
  |  - 7d / 30d Sales Velocity         - Lead-Time Demand Calculation       |
  |  - Days of Supply Remaining        - Discrepancy & Shrinkage Indicators |
  |  - Velocity Surge Acceleration     - Business Impact Score ($/day)      |
  +------------------------------------+------------------------------------+
                                       |
                   +-------------------+-------------------+
                   |                                       |
                   v                                       v
  +---------------------------------+     +---------------------------------+
  |      STOCK-OUT PREDICTOR        |     |    INVENTORY ANOMALY DETECTOR   |
  |  Random Forest Classifier       |     |  Isolation Forest (Multidim)    |
  |  Calibrated Stockout Risk (0-1) |     |  + Discrepancy & Shrinkage Z-Scr|
  +----------------+----------------+     +----------------+----------------+
                   |                                       |
                   +-------------------+-------------------+
                                       |
                                       v
  +-------------------------------------------------------------------------+
  |              DECISION ENGINE & ROOT-CAUSE EXPLAINER                     |
  |  - Action Policy: REPLENISH, EXPEDITE, CYCLE_COUNT_AUDIT, MONITOR       |
  |  - Suggested Order Quantity: (ROP - CurrentStock) + SafetyStock         |
  |  - Root Cause Diagnostician: Natural language causality strings         |
  +------------------------------------+------------------------------------+
                                       |
                                       v
  +-------------------------------------------------------------------------+
  |                       AGREED REST INGESTION CLIENT                      |
  |             POST /api/v1/ingestion/inventory-risk                       |
  |  Payload: {"productId", "stockoutProbability", "riskLevel",             |
  |            "anomaly", "recommendedAction"}                             |
  +------------------------------------+------------------------------------+
                                       |
                                       v
                     [ Java Spring Boot Backend Service ]
```

---

## 📋 Agreed Backend REST API Contract

### Integration Rule
> **Strict Separation of Concerns**: The AI engine does not connect to the frontend. All analytical results are ingested into the Java backend via HTTP POST.

- **Endpoint**: `POST /api/v1/ingestion/inventory-risk`
- **Content-Type**: `application/json`

### Expected Output Payload (Strict 5-Field Schema)
```json
{
  "productId": 101,
  "stockoutProbability": 0.87,
  "riskLevel": "HIGH",
  "anomaly": true,
  "recommendedAction": "REPLENISH"
}
```

### Risk Level Threshold Definitions
To strictly maintain consistency with the agreed standard example (`stockoutProbability: 0.87` $\rightarrow$ `riskLevel: "HIGH"`), the engine uses the following thresholds:

| Risk Level | Probability Threshold Range | Operational Meaning |
| :--- | :--- | :--- |
| **`LOW`** | $\text{prob} < 0.35$ | Buffer is healthy; demand consumption normal. |
| **`MEDIUM`** | $0.35 \le \text{prob} < 0.65$ | Moderate consumption; watch replenishment window. |
| **`HIGH`** | $0.65 \le \text{prob} < 0.90$ | High stock-out risk; reorder triggered immediately. *(0.87 maps here)* |
| **`CRITICAL`** | $\text{prob} \ge 0.90$ | Stockout imminent within lead time; expedited restocking. |

### Operational Action Catalog
- **`REPLENISH`**: Inventory at or below reorder point with high/critical stockout probability.
- **`EXPEDITE`**: Critical stockout risk combined with extended supplier lead times and surging demand.
- **`CYCLE_COUNT_AUDIT`**: Anomaly/phantom discrepancy detected while stockout risk is not yet imminent; physical count required before ledger propagation.
- **`MONITOR`**: Medium risk or safe stock level near reorder point.
- **`NO_ACTION`**: Healthy inventory levels.

---

## 📁 Repository Structure

```
SIHPRO/
│
├── data/
│   ├── raw/
│   │   └── inventory_sample.csv       # Multi-category synthetic raw retail data
│   └── processed/
│       └── engineered_features.csv    # Computed operational features
│
├── models/
│   ├── stockout_model.pkl             # Trained Random Forest classifier
│   └── anomaly_model.pkl              # Fitted Isolation Forest model
│
├── notebooks/
│   └── inventory_intelligence_demo.ipynb # Judge-friendly presentation notebook
│
├── src/
│   ├── __init__.py
│   ├── data_generator.py              # Retail scenario synthesizer
│   ├── feature_engineering.py         # Velocity, days of supply & discrepancy features
│   ├── stockout_predictor.py          # Supervised stockout classification & thresholds
│   ├── anomaly_detector.py            # Isolation Forest + statistical discrepancy detector
│   ├── risk_scorer.py                 # Stock accuracy risk & demand-aware prioritization
│   ├── replenishment_engine.py        # Recommendations & root-cause generator
│   ├── pipeline.py                    # Master end-to-end inference pipeline
│   └── rest_client.py                 # REST client + Mock Java backend server
│
├── tests/
│   └── test_pipeline.py               # Comprehensive pytest test suite (13 tests)
│
├── run_pipeline.py                    # Master CLI executable
├── requirements.txt                   # Dependency list
└── README.md                          # Project documentation
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites & Installation
Ensure Python 3.10+ is installed:
```bash
pip install -r requirements.txt
```

### 2. Run the End-to-End AI Engine (CLI)
Run inference on realistic retail inventory and preview the strict 5-field JSON output:
```bash
python run_pipeline.py
```

### 3. Verify REST Integration with Built-in Mock Backend
Test the full network ingestion loop. This spins up an in-process Java backend emulator on port 8080 and verifies the HTTP POST contract:
```bash
python run_pipeline.py --send --mock-backend
```

### 4. Retrain Models
To retrain both models on a larger simulated retail sample:
```bash
python run_pipeline.py --train --samples 1500
```

### 5. Run the Automated Test Suite
Execute the unit and integration tests verifying thresholds, payload schema, anomaly detection, and REST transmission:
```bash
pytest tests/test_pipeline.py -v
```

### 6. Interactive Presentation Notebook
For live demonstrations and evaluating visual analytics during the SIH evaluation:
```bash
jupyter notebook notebooks/inventory_intelligence_demo.ipynb
```

---

## 🔍 Feature Engineering Details

| Feature | Computation | Operational Significance |
| :--- | :--- | :--- |
| `salesVelocity7d` | Moving 7-day daily average sales | Short-term current demand rate |
| `velocityRatio` | $\text{salesVelocity7d} / \text{salesVelocity30d}$ | Detects demand surges or sudden drops |
| `leadTimeDemand` | $\text{salesVelocity7d} \times \text{replenishmentDelay}$ | Units consumed during supplier delivery window |
| `daysOfSupply` | $\text{currentInventory} / \text{salesVelocity7d}$ | Days until total stock exhaustion |
| `stockToRopRatio` | $\text{currentInventory} / \text{reorderPoint}$ | Position relative to safe replenishment trigger |
| `businessImpactScore` | $\text{unitPrice} \times \text{salesVelocity7d}$ | Daily revenue at risk ($/day) |
| `discrepancyMagnitude` | $|\text{currentInventory} - \text{physicalInventory}|$ | Quantifies phantom stock / unrecorded loss |

---

## 🎯 SIH Presentation Pitch Highlights

1. **Practical & Explainable AI**: Utilizes calibrated Random Forests and Isolation Forests rather than black-box deep learning, achieving sub-millisecond inference and transparent root-cause diagnostics.
2. **Combats Phantom Inventory**: Traditional systems assume ledger counts are 100% accurate. Our dual-layer discrepancy engine detects unrecorded shrinkage and physical mismatches before stockouts occur.
3. **Enterprise-Grade Integration**: Follows clean microservice boundaries. The AI layer communicates strictly via the agreed REST contract (`POST /api/v1/ingestion/inventory-risk`), allowing seamless plug-and-play with the Java backend.
4. **Demand-Aware Optimization**: Prioritizes restocking tasks not solely by stock percentage, but by revenue velocity and critical business impact.
