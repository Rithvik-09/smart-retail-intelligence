"""Data Generator Module.

Generates realistic retail inventory, sales velocity, discrepancy, and
replenishment delay datasets across diverse retail categories for SIH
demonstrations and training.
"""

from typing import Optional, Tuple
import numpy as np
import pandas as pd


CATEGORIES = [
    "Dairy & Fresh",
    "Beverages",
    "Packaged Foods",
    "Personal Care",
    "Household & Cleaning",
    "Snacks & Confectionery",
    "Electronics & Accessories",
    "Bakery",
]

PRODUCT_TEMPLATES = [
    # productId, name, category, base_price, base_velocity, lead_time_mean, reorder_point_base
    (101, "Organic Whole Milk 1L", "Dairy & Fresh", 65.0, 24.0, 3, 50),
    (102, "Greek Yogurt 400g", "Dairy & Fresh", 120.0, 15.0, 4, 30),
    (103, "Artisan Sourdough Bread", "Bakery", 95.0, 18.0, 2, 25),
    (104, "Sparkling Spring Water 500ml", "Beverages", 40.0, 35.0, 5, 80),
    (105, "Cold Pressed Orange Juice 1L", "Beverages", 180.0, 12.0, 4, 30),
    (106, "Premium Arabica Coffee 250g", "Packaged Foods", 450.0, 8.0, 7, 20),
    (107, "Organic Rolled Oats 1kg", "Packaged Foods", 210.0, 14.0, 6, 35),
    (108, "Dark Chocolate Bar 70%", "Snacks & Confectionery", 160.0, 20.0, 5, 45),
    (109, "Almond Granola Bites", "Snacks & Confectionery", 240.0, 10.0, 5, 25),
    (110, "Antibacterial Hand Wash 500ml", "Personal Care", 145.0, 16.0, 6, 40),
    (111, "Hydrating Shampoo 400ml", "Personal Care", 320.0, 9.0, 7, 25),
    (112, "Biodegradable Dish Soap 1L", "Household & Cleaning", 190.0, 11.0, 5, 30),
    (113, "Microfiber Cleaning Cloths 4-Pack", "Household & Cleaning", 180.0, 7.0, 8, 20),
    (114, "USB-C Fast Charging Cable 2m", "Electronics & Accessories", 399.0, 12.0, 10, 30),
    (115, "Wireless Optical Mouse", "Electronics & Accessories", 799.0, 6.0, 12, 18),
]


def generate_retail_dataset(
    n_samples: int = 1200,
    random_seed: int = 42,
    include_discrepancy_anomalies: bool = True,
) -> pd.DataFrame:
    """Generate a realistic retail inventory & sales dataset.

    Args:
        n_samples: Number of inventory observation rows to generate.
        random_seed: Random seed for reproducibility.
        include_discrepancy_anomalies: Whether to inject realistic discrepancy/phantom inventory anomalies.

    Returns:
        pd.DataFrame containing inventory features and stockout target.
    """
    np.random.seed(random_seed)
    records = []
    base_time = pd.Timestamp("2026-01-01 00:00:00")

    for i in range(n_samples):
        # Establish temporal sequence: records advance chronologically
        record_time = base_time + pd.Timedelta(hours=int(i * 3))
        snapshot_date = record_time.strftime("%Y-%m-%d")

        # Pick a product template or synthesize
        if i < len(PRODUCT_TEMPLATES):
            p_id, p_name, category, price, base_vel, base_lead, base_rop = PRODUCT_TEMPLATES[i]
        else:
            base_tuple = PRODUCT_TEMPLATES[i % len(PRODUCT_TEMPLATES)]
            p_id = 100 + (i % 250) + 1
            p_name = f"{base_tuple[1]} (Batch {i // len(PRODUCT_TEMPLATES)})"
            category = base_tuple[2]
            price = round(base_tuple[3] * np.random.uniform(0.9, 1.15), 2)
            base_vel = max(1.0, round(base_tuple[4] * np.random.uniform(0.7, 1.4), 1))
            base_lead = max(1, int(base_tuple[5] * np.random.uniform(0.8, 1.5)))
            base_rop = max(10, int(base_tuple[6] * np.random.uniform(0.8, 1.3)))

        # Velocity with seasonal/spike variations
        historical_sales = max(1.0, np.random.normal(loc=base_vel, scale=base_vel * 0.2))
        
        # Demand shock / surge simulation for some products
        demand_shock = np.random.choice([1.0, 1.0, 1.0, 1.4, 2.2, 0.5], p=[0.65, 0.15, 0.08, 0.07, 0.03, 0.02])
        sales_velocity_7d = max(0.5, round(historical_sales * demand_shock * np.random.uniform(0.85, 1.15), 1))
        sales_velocity_30d = max(0.5, round(historical_sales * np.random.uniform(0.9, 1.1), 1))

        # Supplier replenishment delay / lead time
        lead_time_delay_days = max(1, int(np.random.poisson(lam=base_lead)))
        # Occasional supplier delay spike (e.g. logistics disruption)
        if np.random.rand() < 0.08:
            lead_time_delay_days += np.random.randint(4, 10)

        # Reorder point & safety stock
        safety_stock = max(5, int(sales_velocity_30d * 2.5))
        reorder_point = max(10, int((sales_velocity_30d * lead_time_delay_days) + safety_stock))

        # Current recorded inventory at snapshot time
        # Variety of inventory states: low stock, healthy stock, overstock, depleted stock
        stock_state = np.random.choice(["critical_low", "near_rop", "healthy", "overstock"], p=[0.22, 0.28, 0.38, 0.12])
        if stock_state == "critical_low":
            current_inventory = int(np.random.uniform(0, max(1, int(reorder_point * 0.35))))
        elif stock_state == "near_rop":
            current_inventory = int(np.random.uniform(int(reorder_point * 0.4), int(reorder_point * 1.1)))
        elif stock_state == "healthy":
            current_inventory = int(np.random.uniform(int(reorder_point * 1.1), int(reorder_point * 2.2)))
        else:
            current_inventory = int(np.random.uniform(int(reorder_point * 2.2), int(reorder_point * 4.0)))

        # Physical inventory & discrepancies (phantom stock / shrinkage / unrecorded damage)
        is_anomaly_sample = False
        shrinkage_rate = round(float(np.clip(np.random.beta(a=1.5, b=25), 0.005, 0.25)), 4)
        exception_frequency = int(np.random.poisson(lam=1.5))
        inventory_adjustments = int(np.random.choice([0, 0, 0, -2, -5, 3, -10], p=[0.55, 0.15, 0.1, 0.08, 0.05, 0.04, 0.03]))

        physical_inventory = current_inventory

        if include_discrepancy_anomalies:
            # Anomaly type 1: Phantom inventory (System shows stock, shelf is empty/near zero due to theft/misplacement)
            if np.random.rand() < 0.08:
                is_anomaly_sample = True
                physical_inventory = max(0, int(current_inventory * np.random.uniform(0.0, 0.25)))
                inventory_adjustments -= np.random.randint(5, 20)
                exception_frequency += np.random.randint(4, 10)
                shrinkage_rate = round(float(np.random.uniform(0.12, 0.35)), 4)
            # Anomaly type 2: Sudden erratic adjustment or negative recorded divergence
            elif np.random.rand() < 0.05:
                is_anomaly_sample = True
                inventory_adjustments = -int(np.random.randint(15, 45))
                exception_frequency += np.random.randint(3, 8)

        # Expected demand over next 7 days horizon
        next_7d_expected_demand = sales_velocity_7d * 7.0
        effective_stock = physical_inventory if is_anomaly_sample else current_inventory

        # Ground truth target: whether stockout occurs within the next 7 days
        stockout_next_7d = 1 if (effective_stock - next_7d_expected_demand) <= 0 else 0

        # Special calibration for sample productId 101 to align with agreed API example
        if p_id == 101 and i < len(PRODUCT_TEMPLATES):
            current_inventory = 14
            physical_inventory = 4
            sales_velocity_7d = 28.0
            sales_velocity_30d = 22.0
            lead_time_delay_days = 5
            reorder_point = 120
            safety_stock = 25
            inventory_adjustments = -12
            exception_frequency = 7
            shrinkage_rate = 0.18
            stockout_next_7d = 1
            is_anomaly_sample = True

        records.append({
            "timestamp": record_time,
            "snapshotDate": snapshot_date,
            "productId": p_id,
            "productName": p_name,
            "category": category,
            "unitPrice": price,
            "currentInventory": current_inventory,
            "physicalInventory": physical_inventory,
            "historicalSales": round(historical_sales, 1),
            "salesVelocity7d": sales_velocity_7d,
            "salesVelocity30d": sales_velocity_30d,
            "inventoryAdjustments": inventory_adjustments,
            "replenishmentDelay": lead_time_delay_days,
            "exceptionFrequency": exception_frequency,
            "shrinkageIndicator": shrinkage_rate,
            "reorderPoint": reorder_point,
            "safetyStock": safety_stock,
            "isAnomalyLabel": 1 if is_anomaly_sample else 0,
            "stockoutWithinNext7Days": stockout_next_7d,
            "stockoutOccurred": stockout_next_7d,  # Backwards compatibility alias
        })

    df = pd.DataFrame(records)
    # Ensure chronological order
    df = df.sort_values("timestamp").reset_index(drop=True)
    return df


if __name__ == "__main__":
    df_sample = generate_retail_dataset(n_samples=20)
    print(f"Generated {len(df_sample)} synthetic retail records.")
    print(df_sample[["productId", "currentInventory", "salesVelocity7d", "replenishmentDelay", "stockoutOccurred"]].head(10))
