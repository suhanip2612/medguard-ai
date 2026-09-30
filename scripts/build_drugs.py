import pandas as pd
import numpy as np
from pathlib import Path

RAW_CSV = Path("backend/data/raw/A_Z_medicines_dataset_of_India.csv")
RAW_DIR = Path("backend/data/raw")
DATA_DIR = Path("backend/data")

# 40 list drugs in lowercase_with_underscores
DRUG_LIST = [
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
    "isosorbide_mononitrate",
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

DEMO_BRANDS_MAP = {
    "enalapril": ["Envas", "Enapril"],
    "ibuprofen": ["Brufen"],
    "warfarin": ["Warf", "Uniwarfin"],
    "diclofenac": ["Voveran"],
    "metformin": ["Glycomet"]
}

def extract_raw_generic(text):
    if pd.isna(text):
        return ""
    text = str(text).strip()
    gen = text.split('(')[0].strip().lower()
    # Spelling normalisation
    if gen == "paracetamol/acetaminophen":
        return "paracetamol"
    gen = gen.replace("amoxycillin", "amoxicillin")
    gen = gen.replace("acetaminophen", "paracetamol")
    return gen

def map_to_list_generic(raw_gen):
    if not raw_gen:
        return None
    
    # Excluded variants
    excluded = {
        "s-amlodipine", "levocetirizine", "esomeprazole", "dexibuprofen",
        "enalaprilat", "bacampicillin", "diclofenac diethylamine",
        "s-metoprolol succinate", "dextrothyroxine"
    }
    if raw_gen in excluded:
        return None
        
    # Variant mappings
    if raw_gen in ["metoprolol succinate", "metoprolol tartrate"]:
        return "metoprolol"
    if raw_gen == "thyroxine":
        return "levothyroxine"
    if raw_gen in ["paracetamol"]:
        return "paracetamol"
    if raw_gen == "isosorbide mononitrate":
        return "isosorbide_mononitrate"
        
    # Exact match for standard generic names
    for drug in DRUG_LIST:
        drug_clean = drug.replace("_", " ")
        if raw_gen == drug_clean or raw_gen == drug:
            return drug
            
    return None

def title_case_brand(word):
    if not word:
        return ""
    return word[0].upper() + word[1:].lower()

def main():
    print("Loading dataset...")
    df = pd.read_csv(RAW_CSV)
    print(f"Loaded {len(df)} total rows.")
    
    # Rule 3: Separate combination rows
    is_empty_comp2 = df['short_composition2'].isna() | (df['short_composition2'].astype(str).str.strip() == '')
    combos_df = df[~is_empty_comp2]
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    combos_df.to_csv(RAW_DIR / "combos_skipped.csv", index=False)
    print(f"Skipped {len(combos_df)} combination rows written to combos_skipped.csv.")
    
    single_df = df[is_empty_comp2].copy()
    print(f"Single-ingredient rows: {len(single_df)}")
    
    # Rule 4: Drop discontinued
    single_active_df = single_df[single_df['Is_discontinued'] != True].copy()
    print(f"Active single-ingredient rows (not discontinued): {len(single_active_df)}")
    
    # Rule 1 & 2: Map generics
    single_active_df['raw_generic'] = single_active_df['short_composition1'].apply(extract_raw_generic)
    single_active_df['list_generic'] = single_active_df['raw_generic'].apply(map_to_list_generic)
    
    matched_df = single_active_df[single_active_df['list_generic'].notna()].copy()
    print(f"Rows matching drug list generics: {len(matched_df)}")
    
    # Rule 5: Extract brand
    def extract_brand(name):
        if pd.isna(name):
            return ""
        words = str(name).strip().split()
        if not words:
            return ""
        first_word = words[0]
        # Title-case word (e.g. ENVAS -> Envas, Brufen -> Brufen)
        brand = title_case_brand(first_word)
        # Drop brands shorter than 3 chars
        if len(brand) < 3:
            return ""
        # Drop brands starting with "Genericart" or "Generic"
        if brand.lower().startswith("generic"):
            return ""
        return brand

    matched_df['brand'] = matched_df['name'].apply(extract_brand)
    matched_df = matched_df[matched_df['brand'] != ""].copy()
    print(f"Rows after valid brand extraction: {len(matched_df)}")
    
    # Rule 6: Ambiguity check
    brand_to_generics = matched_df.groupby('brand')['list_generic'].unique()
    ambiguous_brands = {}
    for brand, gen_set in brand_to_generics.items():
        if len(gen_set) > 1:
            ambiguous_brands[brand] = sorted(list(gen_set))
            
    # Write ambiguous_brands.csv
    amb_rows = [{"brand": b, "generics": ";".join(g)} for b, g in ambiguous_brands.items()]
    amb_df = pd.DataFrame(amb_rows)
    amb_df.to_csv(RAW_DIR / "ambiguous_brands.csv", index=False)
    print(f"Found {len(amb_df)} ambiguous brands written to ambiguous_brands.csv.")
    
    # Filter out ambiguous brands
    unambiguous_df = matched_df[~matched_df['brand'].isin(ambiguous_brands.keys())].copy()
    
    # Rule 7: Write brand_candidates.csv
    candidate_summary = unambiguous_df.groupby(['list_generic', 'brand']).agg(
        row_count=('id', 'count'),
        example_name=('name', 'first')
    ).reset_index()
    
    candidate_summary = candidate_summary.sort_values(by=['list_generic', 'row_count', 'brand'], ascending=[True, False, True])
    
    # Take top 8 per generic
    top8_candidates = candidate_summary.groupby('list_generic').head(8)
    top8_candidates.rename(columns={'list_generic': 'generic'}).to_csv(RAW_DIR / "brand_candidates.csv", index=False)
    print(f"Wrote brand_candidates.csv ({len(top8_candidates)} candidate rows).")
    
    # Rule 8: Select up to 3 brands per generic including DEMO BRANDS
    print("\n--- DEMO BRANDS VERIFICATION & SOURCE ROWS ---")
    
    final_drugs_rows = []
    
    for generic in DRUG_LIST:
        gen_df = unambiguous_df[unambiguous_df['list_generic'] == generic]
        available_brands = candidate_summary[candidate_summary['list_generic'] == generic].copy()
        brand_count_map = dict(zip(available_brands['brand'], available_brands['row_count']))
        
        selected_brands = []
        demo_targets = DEMO_BRANDS_MAP.get(generic, [])
        
        for demo in demo_targets:
            # Check if demo brand is valid
            # Find in matched_df or raw single_active_df to see why if it failed
            demo_match = gen_df[gen_df['brand'].str.lower() == demo.lower()]
            if len(demo_match) > 0:
                actual_brand_name = demo_match['brand'].iloc[0]
                if actual_brand_name not in selected_brands:
                    selected_brands.append(actual_brand_name)
                # Print source rows
                print(f"Demo Brand '{demo}' for generic '{generic}': PASS ({len(demo_match)} matching rows)")
                for _, srow in demo_match.head(3).iterrows():
                    print(f"   id: {srow['id']} | name: {srow['name']} | comp1: {srow['short_composition1']}")
            else:
                # Check why it failed
                raw_demo_match = df[df['name'].fillna('').astype(str).str.lower().str.startswith(demo.lower())]
                print(f"Demo Brand '{demo}' for generic '{generic}': FAILED/NOT IN UNAMBIGUOUS MATCHES.")
                if len(raw_demo_match) == 0:
                    print("   Reason: Not found in raw dataset.")
                else:
                    sample = raw_demo_match.iloc[0]
                    print(f"   Sample row id: {sample['id']} | name: {sample['name']} | comp1: {sample['short_composition1']} | comp2: {sample['short_composition2']} | discontinued: {sample['Is_discontinued']}")
        
        # Fill remaining spots up to 3 from top candidates
        other_candidates = available_brands[~available_brands['brand'].isin(selected_brands)]
        for _, crow in other_candidates.iterrows():
            if len(selected_brands) >= 3:
                break
            selected_brands.append(crow['brand'])
            
        brands_str = ";".join(selected_brands)
        final_drugs_rows.append({
            "generic_name": generic,
            "drug_class": "",
            "brands": brands_str,
            "max_daily_dose_mg": ""
        })
        
    drugs_csv_df = pd.DataFrame(final_drugs_rows)
    drugs_csv_df.to_csv(DATA_DIR / "drugs.csv", index=False)
    print(f"\nWrote backend/data/drugs.csv ({len(drugs_csv_df)} rows).")

if __name__ == "__main__":
    main()
