import json
import re
import sys
from pathlib import Path

# Force UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

LABELS_DIR = Path("backend/data/raw/labels_doses")

DRUG_LIST = [
    "paracetamol", "ibuprofen", "aspirin", "diclofenac", "warfarin",
    "clopidogrel", "omeprazole", "pantoprazole", "metformin", "atorvastatin",
    "simvastatin", "rosuvastatin", "clarithromycin", "ciprofloxacin", "azithromycin",
    "lisinopril", "enalapril", "losartan", "telmisartan", "amlodipine",
    "spironolactone", "furosemide", "hydrochlorothiazide", "amoxicillin", "ampicillin",
    "sildenafil", "isosorbide_mononitrate", "tramadol", "fluoxetine", "propranolol",
    "metoprolol", "digoxin", "amiodarone", "methotrexate", "levothyroxine",
    "gabapentin", "pregabalin", "cetirizine", "montelukast", "glimepiride"
]

def analyze_drug_label(generic):
    json_path = LABELS_DIR / f"{generic}.json"
    if not json_path.exists():
        return generic, None, "File missing", []
        
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    set_id = data.get("set_id", "unknown")
    brand = data.get("openfda_brand_name", "unknown")
    
    dosage_lines = data.get("dosage_and_administration", [])
    warning_lines = data.get("warnings", []) + data.get("boxed_warning", [])
    
    full_text = " ".join(dosage_lines + warning_lines)
    
    # Extract sentences
    sentences = re.split(r'(?<=[.!?])\s+', full_text)
    
    return generic, set_id, brand, full_text, sentences

def main():
    print("=== DETAILED ANALYSIS OF ALL 40 DRUG LABELS FOR MAXIMUM DAILY DOSE ===\n")
    
    for drug in DRUG_LIST:
        generic, set_id, brand, full_text, sentences = analyze_drug_label(drug)
        print(f"==================================================")
        print(f"DRUG: {generic.upper()} | Brand: {brand} | SetID: {set_id}")
        print(f"--------------------------------------------------")
        
        # Look for explicit mg statements or caps
        relevant = []
        for s in sentences:
            sl = s.lower()
            if any(k in sl for k in ["maximum", "exceed", "up to", "total daily", "not to exceed", "mg/day", "mg daily", "per day", "a day"]):
                relevant.append(s.strip())
                
        if not relevant:
            print("FULL DOSAGE TEXT SNIPPET:")
            print(full_text[:400] + ("..." if len(full_text) > 400 else ""))
        else:
            for r_sen in relevant:
                print(f"  • {r_sen}")
        print()

if __name__ == "__main__":
    main()
