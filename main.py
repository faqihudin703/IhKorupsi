import argparse
import sys
from utils.data_loader import DataLoader
from core.engine import FraudEngine

def main():
    parser = argparse.ArgumentParser(description="IH-Korupsi: Open Source Forensic Data Toolkit")
    parser.add_argument("--input", type=str, help="Path to input data (CSV/JSON)")
    parser.add_argument("--type", type=str, choices=['csv', 'json', 'sample'], default='sample', help="Data format")
    parser.add_argument("--output", type=str, default="fraud_report.json", help="Output report path")
    
    args = parser.parse_args()

    print("--- IH-Korupsi Forensic Toolkit ---")
    
    if args.type == 'sample':
        print("Generating 500 rows of synthetic transaction data...")
        df = DataLoader.generate_sample_data(500)
    else:
        if not args.input:
            print("Error: --input is required for non-sample data.")
            sys.exit(1)
        df = DataLoader.load(args.input, args.type)

    engine = FraudEngine()
    report = engine.process(df)
    
    engine.save_report(report, args.output)
    print("Analysis complete. Review the JSON report for detailed mathematical evidence.")

if __name__ == "__main__":
    main()
