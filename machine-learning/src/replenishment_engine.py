"""Replenishment Engine & Root-Cause Recommendation Module.

Synthesizes stock-out risks, anomaly flags, demand velocity, and lead-time constraints
into actionable recommendations (REPLENISH, EXPEDITE, CYCLE_COUNT_AUDIT, MONITOR, NO_ACTION)
with human-interpretable root-cause diagnostic suggestions.
"""

from typing import Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd


def determine_recommended_action(
    stockout_prob: float,
    risk_level: str,
    anomaly: bool,
    current_inventory: float,
    reorder_point: float,
    lead_time_delay: int = 3,
    velocity_ratio: float = 1.0,
    sales_velocity_7d: float = 10.0,
) -> str:
    """Determine the operational replenishment action.

    Action Hierarchy:
        1. EXPEDITE: High/Critical stockout risk with delayed supplier lead time (>=7 days) and high demand.
        2. REPLENISH: High/Critical stockout risk with insufficient stock (at or below reorder threshold).
        3. CYCLE_COUNT_AUDIT: Significant inventory anomaly/discrepancy detected requiring physical audit.
        4. MONITOR: Moderate risk with sufficient remaining stock.
        5. NO_ACTION: Healthy inventory buffer and low risk.

    Args:
        stockout_prob: Probability of stockout [0.0 - 1.0].
        risk_level: Risk classification ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL').
        anomaly: Boolean flag indicating discrepancy/phantom stock.
        current_inventory: Current on-hand stock count.
        reorder_point: Reorder point threshold.
        lead_time_delay: Supplier lead time in days.
        velocity_ratio: Ratio of 7-day velocity to 30-day velocity.
        sales_velocity_7d: Recent 7-day daily sales velocity.

    Returns:
        Recommended action string.
    """
    # 1. EXPEDITE: High or Critical risk with extended supplier lead time and surging/high demand
    if risk_level in ["HIGH", "CRITICAL"] and lead_time_delay >= 7 and (velocity_ratio >= 1.3 or sales_velocity_7d >= 15.0):
        return "EXPEDITE"

    # 2. REPLENISH: High or Critical stockout risk with insufficient stock
    if risk_level in ["HIGH", "CRITICAL"]:
        return "REPLENISH"

    # 3. CYCLE_COUNT_AUDIT: Significant inventory anomaly/discrepancy detected
    if anomaly:
        return "CYCLE_COUNT_AUDIT"

    # 4. MONITOR: Moderate risk or stock approaching reorder point
    if risk_level == "MEDIUM" or (current_inventory <= reorder_point * 1.20):
        return "MONITOR"

    # 5. NO_ACTION: Healthy inventory buffer
    return "NO_ACTION"


def generate_root_cause_explanation(
    row: pd.Series,
    stockout_prob: float,
    risk_level: str,
    anomaly: bool,
    action: str,
) -> str:
    """Generate explainable, natural language root-cause suggestions for store managers.

    Args:
        row: Series containing product attributes and features.
        stockout_prob: Calculated stockout probability.
        risk_level: 'LOW', 'MEDIUM', 'HIGH', or 'CRITICAL'.
        anomaly: Whether anomaly was detected.
        action: Recommended operational action.

    Returns:
        Explanatory root-cause diagnostic string.
    """
    causes = []

    stock = float(row.get("currentInventory", 0.0))
    rop = float(row.get("reorderPoint", 50.0))
    vel7 = float(row.get("salesVelocity7d", 0.0))
    vel30 = float(row.get("salesVelocity30d", 0.0))
    v_ratio = float(row.get("velocityRatio", 1.0))
    lead = int(row.get("replenishmentDelay", 3))
    adj = float(row.get("inventoryAdjustments", 0.0))
    exc = int(row.get("exceptionFrequency", 0))
    shrinkage = float(row.get("shrinkageIndicator", 0.0))
    days_supply = float(row.get("daysOfSupply", 99.0))

    if action == "EXPEDITE":
        causes.append(
            f"Critically low stock ({int(stock)} units) combined with extended supplier lead time ({lead} days) "
            f"and high sales velocity ({vel7:.1f} units/day). Expedited replenishment required to prevent stockout."
        )
    elif action == "REPLENISH":
        if stock <= rop * 0.4:
            causes.append(f"Depleted stock on hand ({int(stock)} units vs ROP {int(rop)}) with only {days_supply:.1f} days of supply remaining.")
        else:
            causes.append(f"Stock on hand ({int(stock)} units) has fallen below reorder threshold ({int(rop)} units).")
        if v_ratio >= 1.25:
            causes.append(f"Sales velocity surged {v_ratio:.2f}x ({vel7:.1f} units/day vs {vel30:.1f} 30-day avg).")
        if lead >= 6:
            causes.append(f"Extended supplier replenishment lead time ({lead} days) compounds stockout vulnerability.")
    elif action == "CYCLE_COUNT_AUDIT":
        causes.append(
            f"Significant inventory anomaly detected (discrepancy: {float(row.get('discrepancyMagnitude', 0.0)):.1f} units, "
            f"shrinkage: {shrinkage:.1%}). Physical cycle count audit required before further ledger updates."
        )
    elif action == "MONITOR":
        causes.append(
            f"Moderate stock-out consumption risk ({stockout_prob:.2f}); current inventory ({int(stock)} units) "
            f"is near reorder point ({int(rop)} units). Continuous monitoring recommended."
        )
    else:  # NO_ACTION
        causes.append(
            f"Healthy inventory levels ({int(stock)} units) exceeding reorder threshold ({int(rop)} units) "
            f"with stable demand ({vel7:.1f} units/day)."
        )

    # Additional diagnostic observations
    if adj <= -5.0 and action != "EXPEDITE" and action != "CYCLE_COUNT_AUDIT":
        causes.append(f"Negative inventory adjustments ({int(adj)} units) reflect unrecorded shrinkage or damaged goods.")

    if exc >= 4 and action != "EXPEDITE" and action != "CYCLE_COUNT_AUDIT":
        causes.append(f"Elevated scan exception frequency ({exc} incidents) suggests shelf-tag or barcode scanning discrepancies.")

    return " | ".join(causes)


def calculate_replenishment_quantity(
    current_inventory: float,
    reorder_point: float,
    safety_stock: float = 0.0,
    lead_time_demand: float = 0.0,
) -> int:
    """Calculate suggested reorder batch quantity using dynamic buffer sizing.

    Quantity = max(0, (ReorderPoint - CurrentInventory) + SafetyStock)

    Args:
        current_inventory: Current on hand count.
        reorder_point: Reorder threshold.
        safety_stock: Buffer stock (default: 0.0).
        lead_time_demand: Expected demand during lead time (default: 0.0).

    Returns:
        Suggested order quantity as non-negative integer.
    """
    needed = (reorder_point - current_inventory) + safety_stock
    return max(0, int(np.ceil(needed)))


class ReplenishmentEngine:
    """Evaluates inventory health and produces operational actions and explanations."""

    def evaluate_batch(
        self,
        df: pd.DataFrame,
        stockout_results: List[Dict[str, Union[float, str]]],
        anomaly_results: List[Dict[str, Union[bool, float, str]]],
    ) -> List[Dict[str, Union[str, int]]]:
        """Evaluate recommendations and root-cause diagnostics for a batch.

        Args:
            df: DataFrame containing inventory records.
            stockout_results: List of dicts with 'stockoutProbability' and 'riskLevel'.
            anomaly_results: List of dicts with 'anomaly'.

        Returns:
            List of dicts with 'recommendedAction', 'rootCauses', and 'suggestedOrderQty'.
        """
        results = []

        for i, (_, row) in enumerate(df.iterrows()):
            s_prob = float(stockout_results[i]["stockoutProbability"])
            r_level = str(stockout_results[i]["riskLevel"])
            anom = bool(anomaly_results[i]["anomaly"])

            stock = float(row.get("currentInventory", 0.0))
            rop = float(row.get("reorderPoint", 50.0))
            lead = int(row.get("replenishmentDelay", 3))
            vel_ratio = float(row.get("velocityRatio", 1.0))
            safety = float(row.get("safetyStock", 15.0))
            lead_demand = float(row.get("leadTimeDemand", 20.0))

            vel_7 = float(row.get("salesVelocity7d", 10.0))

            action = determine_recommended_action(
                stockout_prob=s_prob,
                risk_level=r_level,
                anomaly=anom,
                current_inventory=stock,
                reorder_point=rop,
                lead_time_delay=lead,
                velocity_ratio=vel_ratio,
                sales_velocity_7d=vel_7,
            )

            root_cause = generate_root_cause_explanation(
                row=row,
                stockout_prob=s_prob,
                risk_level=r_level,
                anomaly=anom,
                action=action,
            )

            order_qty = calculate_replenishment_quantity(
                current_inventory=stock,
                reorder_point=rop,
                safety_stock=safety,
                lead_time_demand=lead_demand,
            )

            results.append({
                "recommendedAction": action,
                "rootCauses": root_cause,
                "suggestedOrderQty": order_qty,
            })

        return results


if __name__ == "__main__":
    action = determine_recommended_action(
        stockout_prob=0.87,
        risk_level="HIGH",
        anomaly=True,
        current_inventory=14,
        reorder_point=120,
        lead_time_delay=5,
        velocity_ratio=1.27,
    )
    print(f"Test Action for 0.87 probability: {action}")
    assert action == "REPLENISH", f"Expected REPLENISH, got {action}"
