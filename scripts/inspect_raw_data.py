import pandas as pd
from pathlib import Path

csv_path = Path("backend/data/raw/A_Z_medicines_dataset_of_India.csv")

def normalize_composition(text):
    if pd.isna(text):
        return ""
    text = str(text).strip()
    # extract before first '('
    gen = text.split('(')[0].strip().lower()
    # normalise spelling
    gen = gen.replace("amoxycillin", "amoxicillin")
    gen = gen.replace("acetaminophen", "paracetamol")
    return gen

def main():
    print("=== STEP 1: INSPECTION REPORT ===")
    df = pd.read_csv(csv_path)
    total_rows = len(df)
    print(f"Total row count: {total_rows}")
    
    # count empty short_composition2
    empty_comp2 = df['short_composition2'].isna().sum() + (df['short_composition2'].fillna('').astype(str).str.strip() == '').sum() - df['short_composition2'].isna().sum()
    nan_comp2 = df['short_composition2'].isna().sum()
    print(f"Count of empty short_composition2 (NaN / empty): {nan_comp2 + empty_comp2}")
    
    # count Is_discontinued = True
    discontinued_count = (df['Is_discontinued'] == True).sum()
    print(f"Count of Is_discontinued=True: {discontinued_count}")
    
    drug_list = [
        "paracetamol",
        "ibuprofen",
        "aspirin",
        "diclofenac",
        "warfarin",
        "clopidogrel",
        "omeprazole",
        "pantoprazole",
        "metformin",
        "atorvastatin",
        "simvastatin",
        "rosuvastatin",
        "clarithromycin",
        "ciprofloxacin",
        "azithromycin",
        "lisinopril",
        "enalapril",
        "losartan",
        "telmisartan",
        "amlodipine",
        "spironolactone",
        "furosemide",
        "hydrochlorothiazide",
        "amoxicillin",
        "ampicillin",
        "sildenafil",
        "isosorbide mononitrate",
        "tramadol",
        "fluoxetine",
        "propranolol",
        "metoprolol",
        "digoxin",
        "amiodarone",
        "methotrexate",
        "levothyroxine",
        "gabapentin",
        "pregabalin",
        "cetirizine",
        "montelukast",
        "glimepiride"
    ]
    
    # Extract generic strings before '('
    df['generic_clean'] = df['short_composition1'].apply(normalize_composition)
    
    print("\n--- MATCHING GENERIC STRINGS PER DRUG ---")
    for drug in sorted(drug_list):
        matches = df[df['generic_clean'].str.contains(drug, regex=False, na=False)]
        counts = matches['generic_clean'].value_counts()
        exact_matches = (df['generic_clean'] == drug).sum()
        
        exact_status = "EXACT MATCH FOUND" if exact_matches > 0 else "** ZERO EXACT MATCHES **"
        print(f"\nDrug: '{drug}' (Exact matches: {exact_matches}) [{exact_status}]")
        if len(counts) == 0:
            print("  No containing strings found.")
        else:
            for gen_str, cnt in counts.items():
                print(f"  - '{gen_str}': {cnt} rows")

    print("\n--- SAMPLE ROWS FOR SPECIFIC BRANDS ---")
    target_brands = ["Envas", "Enapril", "Brufen", "Warf", "Uniwarfin", "Voveran", "Glycomet"]
    for brand in target_brands:
        print(f"\nSample rows for Brand: '{brand}':")
        brand_df = df[df['name'].fillna('').astype(str).str.lower().str.startswith(brand.lower())].head(5)
        if len(brand_df) == 0:
            print("  No rows found.")
        else:
            for idx, row in brand_df.iterrows():
                print(f"  id: {row['id']} | name: {row['name']} | comp1: {row['short_composition1']} | comp2: {row['short_composition2']} | discontinued: {row['Is_discontinued']}")

if __name__ == "__main__":
    main()
