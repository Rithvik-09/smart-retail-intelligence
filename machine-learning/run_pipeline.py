#!/usr/bin/env python3
"""Master CLI Entry Point for Smart Retail Intelligence AI Layer.

Usage:
    # Run end-to-end inference and display strict 5-field JSON output
    python run_pipeline.py

    # Retrain models with 2000 samples
    python run_pipeline.py --train --samples 2000

    # Run inference and send results to live Java backend
    python run_pipeline.py --send --backend-url http://localhost:8080

    # Run inference and verify against the built-in mock Java backend
    python run_pipeline.py --send --mock-backend

    # Save output to JSON file
    python run_pipeline.py --output output_risks.json
"""

import argparse
import json
import os
import sys
import time
import pandas as pd

# Add src to module search path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from data_generator import generate_retail_dataset
from pipeline import InventoryAIPipeline
from rest_client import BackendIngestionClient, MockBackendServer


def main():
    parser = argparse.ArgumentParser(
        description="Smart Retail Intelligence — Member 3 ML Inventory AI Engine"
    )
    parser.add_argument(
        "--train",
        action="store_true",
        help="Force retrain models before running inference.",
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=500,
        help="Number of samples to generate if no input CSV is provided (default: 500).",
    )
    parser.add_argument(
        "--input-csv",
        type=str,
        default=None,
        help="Path to an input CSV with inventory records. If omitted, synthetic data is generated.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Path to write the resulting JSON predictions.",
    )
    parser.add_argument(
        "--send",
        action="store_true",
        help="Send predictions to the Java backend endpoint.",
    )
    parser.add_argument(
        "--backend-url",
        type=str,
        default="http://127.0.0.1:8080",
        help="Base URL of Java Spring Boot backend (default: http://127.0.0.1:8080).",
    )
    parser.add_argument(
        "--mock-backend",
        action="store_true",
        help="Start in-process mock Java backend to receive and test POST ingestion.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate REST dispatch without sending network traffic.",
    )
    parser.add_argument(
        "--enriched",
        action="store_true",
        help="Include extended analytics context (rootCauses, priorityScore) alongside core 5 fields.",
    )
    parser.add_argument(
        "--preview-count",
        type=int,
        default=5,
        help="Number of items to preview in terminal output (default: 5).",
    )

    args = parser.parse_args()

    print("================================================================")
    print(" Smart Retail Intelligence — Inventory AI Engine (Member 3)")
    print("================================================================")

    pipeline = InventoryAIPipeline()

    # Step 1: Training if requested or needed
    if args.train:
        print(f"[*] Retraining models using {args.samples} synthetic samples...")
        metrics = pipeline.train(n_samples=args.samples)
        print(f"[OK] Training complete. Predictor ROC-AUC: {metrics['stockout_predictor']['roc_auc']}")
    else:
        pipeline.ensure_ready()
        print("[OK] AI models loaded and ready.")

    # Step 2: Ingest Data
    if args.input_csv and os.path.exists(args.input_csv):
        print(f"[*] Loading inventory records from CSV: {args.input_csv}")
        df = pd.read_csv(args.input_csv)
    else:
        print(f"[*] Generating realistic retail inventory batch ({args.samples} records)...")
        df = generate_retail_dataset(n_samples=args.samples, random_seed=42)

    # Step 3: Run AI Inference
    print(f"[*] Running AI risk scoring, anomaly detection, and replenishment logic...")
    results = pipeline.run_inference(df, enriched=args.enriched)
    print(f"[OK] Successfully generated assessments for {len(results)} products.")

    # Step 4: Preview Output
    print("\n---------------- Sample Output JSON Preview ----------------")
    preview_items = results[:args.preview_count]
    print(json.dumps(preview_items, indent=2))
    print("------------------------------------------------------------\n")

    # Step 5: Save to File if requested
    if args.output:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print(f"[OK] Full results saved to: {args.output}")

    # Step 6: REST Integration Dispatch
    if args.send or args.dry_run:
        mock_server = None
        if args.mock_backend:
            print("[*] Launching Mock Java Backend on port 8080...")
            mock_server = MockBackendServer(port=8080)
            mock_server.start()
            time.sleep(0.5)

        try:
            print(f"[*] Dispatching assessments to Java backend: {args.backend_url}/api/v1/ingestion/inventory-risk")
            client = BackendIngestionClient(base_url=args.backend_url)

            # Transmit first batch of items (e.g. preview items or full list)
            items_to_send = results[:10]  # send top 10 for demonstration
            dispatch_res = client.send_batch(
                items_to_send,
                dry_run=args.dry_run,
                item_by_item=True,
            )

            print(f"[OK] REST Dispatch Summary: Total={dispatch_res['total']}, Successful={dispatch_res['successful']}, Failed={dispatch_res['failed']}")

            if mock_server:
                received = mock_server.get_received()
                print(f"[OK] Mock Java Backend verified receipt of {len(received)} payloads.")
                if received:
                    print(f"    First verified payload in backend:")
                    print("   ", json.dumps(received[0]))

        finally:
            if mock_server:
                mock_server.stop()

    print("\n================================================================")
    print(" Execution finished successfully.")
    print("================================================================\n")


if __name__ == "__main__":
    main()
