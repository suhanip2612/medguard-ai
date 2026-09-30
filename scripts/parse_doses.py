import json
import re
from pathlib import Path

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

def search_max_dose_text(generic):
    json_path = LABELS_DIR / f"{generic}.json"
    if not json_path.exists():
        return generic, None, "File not found"
        
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    set_id = data.get("set_id", "unknown")
    brand = data.get("openfda_brand_name", "unknown")
    
    sections = [
        ("dosage_and_administration", data.get("dosage_and_administration", [])),
        ("warnings", data.get("warnings", [])),
        ("boxed_warning", data.get("boxed_warning", [])),
        ("indications_and_usage", data.get("indications_and_usage", []))
    ]
    
    full_text = []
    for sec_name, lines in sections:
        for line in lines:
            full_text.append(line)
            
    text_block = " ".join(full_text)
    
    # Sentences containing keywords
    sentences = re.split(r'(?<=[.!?])\s+', text_block)
    relevant_sentences = []
    keywords = ["maximum", "max", "exceed", "daily", "mg/day", "mg a day", "per day", "dose"]
    
    for s in sentences:
        s_lower = s.lower()
        if any(kw in s_lower for kw in keywords):
            if any(term in s_lower for term in ["maximum", "exceed", "up to", "total daily", "not to exceed"]):
                relevant_sentences.append(s.strip())
                
    return generic, set_id, brand, relevant_sentences

def main():
    print("=== INSPECTING LABEL TEXT FOR MAXIMUM DAILY DOSES ===\n")
    for drug in DRUG_LIST:
        res = search_max_dose_text(drug)
        generic, set_id, brand, sentences = res
        print(f"[{generic.upper()}] (SetID: {set_id}, Brand: {brand})")
        if not sentences:
            print("   No explicit maximum dose sentences matched simple keywords.")
        else:
            for s in sentences[:5]:  # print top 5 candidate sentences
                print(f"   -> \"{s}\"")
        print()

if __name__ == "__main__":
    main()
