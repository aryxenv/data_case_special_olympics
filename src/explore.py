import pandas as pd
import os

raw_data_path = "../data/raw"

def analyze_file(filename):
    filepath = os.path.join(raw_data_path, filename)
    print(f"\nAnalyzing {filename}")
    try:
        xls = pd.ExcelFile(filepath)
        print(f"Sheets: {xls.sheet_names}")
        for sheet in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet, nrows=5)
            print(f"\nSheet: '{sheet}' | Columns: {list(df.columns)}")
            print(f"First row sample: {df.iloc[0].to_dict() if not df.empty else 'Empty'}")
    except Exception as e:
        print(f"Error reading {filename}: {e}")

# Analyze generic files
files_to_check = [
    "Thomas More Data Certifications.xlsx", 
    "Thomas More Data Clubs.xlsx", 
    "Thomas More Results 2024.xlsx" # analyzing one result file as proxy
]

for f in files_to_check:
    analyze_file(f)
