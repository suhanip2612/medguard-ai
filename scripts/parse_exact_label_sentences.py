import json
import re
import sys
import pandas as pd
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

LABELS_DIR = Path("backend/data/raw/labels_doses")
DRUGS_CSV = Path("backend/data/drugs.csv")

# 40 list drugs
DRUGS = [
    "paracetamol", "ibuprofen", "aspirin", "diclofenac", "warfarin",
    "clopidogrel", "omeprazole", "pantoprazole", "metformin", "atorvastatin",
    "simvastatin", "rosuvastatin", "clarithromycin", "ciprofloxacin", "azithromycin",
    "lisinopril", "enalapril", "losartan", "telmisartan", "amlodipine",
    "spironolactone", "furosemide", "hydrochlorothiazide", "amoxicillin", "ampicillin",
    "sildenafil", "isosorbide_mononitrate", "tramadol", "fluoxetine", "propranolol",
    "metoprolol", "digoxin", "amiodarone", "methotrexate", "levothyroxine",
    "gabapentin", "pregabalin", "cetirizine", "montelukast", "glimepiride"
]

def get_label_details(generic):
    json_path = LABELS_DIR / f"{generic}.json"
    if not json_path.exists():
        return None
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

def extract_evidence():
    results = {}
    
    for drug in DRUGS:
        data = get_label_details(drug)
        if not data:
            results[drug] = {"set_id": "N/A", "brand": "N/A", "text": "File missing"}
            continue
            
        set_id = data.get("set_id", "unknown")
        brand = data.get("openfda_brand_name", "unknown")
        
        dos_admin = " ".join(data.get("dosage_and_administration", []))
        warnings = " ".join(data.get("warnings", []))
        indications = " ".join(data.get("indications_and_usage", []))
        
        full = f"{dos_admin} {warnings} {indications}"
        
        results[drug] = {
            "set_id": set_id,
            "brand": brand,
            "dos_admin": dos_admin,
            "warnings": warnings,
            "indications": indications,
            "full": full
        }
    return results

def main():
    ev = extract_evidence()
    print("=== SUMMARY OF ALL 40 LABELS FOR DOSE EVIDENCE ===\n")
    for drug in DRUGS:
        info = ev[drug]
        print(f"[{drug.upper()}] (SetID: {info['set_id']})")
        print(f"  Brand: {info['brand']}")
        text = info['full']
        # search for mg sentences
        sens = re.split(r'(?<=[.!?])\s+', text)
        matched = [s.strip() for s in sens if any(k in s.lower() for k in ["maximum", "exceed", "up to", "total daily", "mg/day", "mg daily", "per day"])]
        if matched:
            for m in matched[:3]:
                print(f"  -> Sentence: \"{m}\"")
        else:
            print(f"  -> First 200 chars: {text[:200]}")
        print()

if __name__ == "__main__":
    main()
