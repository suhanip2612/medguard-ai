import json
import time
import urllib.request
import urllib.parse
import pandas as pd
from pathlib import Path

DRUGS_CSV = Path("backend/data/drugs.csv")
LABELS_DIR = Path("backend/data/raw/labels_doses")

SYNONYMS = {
    "paracetamol": ["acetaminophen", "paracetamol"]
}

def fetch_label_for_drug(generic_name):
    query_name = generic_name.replace("_", " ")
    names_to_try = SYNONYMS.get(generic_name, [query_name])
    
    for qname in names_to_try:
        urls_to_try = [
            f'https://api.fda.gov/drug/label.json?search=openfda.generic_name:"{urllib.parse.quote(qname)}"&limit=10',
            f'https://api.fda.gov/drug/label.json?search=openfda.substance_name:"{urllib.parse.quote(qname)}"&limit=10',
            f'https://api.fda.gov/drug/label.json?search={urllib.parse.quote(qname)}&limit=10'
        ]
        
        for url in urls_to_try:
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'MedGuardAI/1.0'})
                with urllib.request.urlopen(req, timeout=10) as response:
                    if response.status == 200:
                        data = json.loads(response.read().decode('utf-8'))
                        results = data.get('results', [])
                        if results:
                            # Filter results to ensure openfdageneric_name matches or substance matches
                            filtered = []
                            for r in results:
                                openfda = r.get('openfda', {})
                                gen_names = [g.lower() for g in openfda.get('generic_name', []) + openfda.get('substance_name', [])]
                                if any(qname.lower() in gn for gn in gen_names) or qname == "acetaminophen":
                                    filtered.append(r)
                            return filtered if filtered else results, url
            except Exception as e:
                time.sleep(0.3)
                continue
                
    return None, None

def select_best_label(results, generic_name):
    if not results:
        return None
        
    best = None
    best_score = -100
    
    for item in results:
        score = 0
        openfda = item.get('openfda', {})
        route = [r.lower() for r in openfda.get('route', [])]
        dosage_form = [f.lower() for f in openfda.get('dosage_form', [])]
        
        dosage_admin = " ".join(item.get('dosage_and_administration', [])).lower()
        indications = " ".join(item.get('indications_and_usage', [])).lower()
        
        if 'oral' in route or 'oral' in dosage_admin:
            score += 10
        if any(f in dosage_form or f in dosage_admin for f in ['tablet', 'capsule']):
            score += 10
        if 'adult' in dosage_admin or 'adult' in indications:
            score += 5
        if not any(x in dosage_admin for x in ['extended-release', 'sustained-release', 'xr', 'er', 'sr', 'pr']):
            score += 2
            
        if score > best_score:
            best_score = score
            best = item
            
    return best if best else results[0]

def main():
    LABELS_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(DRUGS_CSV)
    
    failed_drugs = []
    success_drugs = []
    
    print(f"Fetching openFDA drug labels for {len(df)} drugs...")
    
    for idx, row in df.iterrows():
        gen = str(row['generic_name']).strip()
        print(f"[{idx+1}/{len(df)}] Fetching label for: {gen}...")
        
        results, query_url = fetch_label_for_drug(gen)
        if not results:
            print(f"   FAILED: No label found on openFDA for {gen}")
            failed_drugs.append(gen)
            continue
            
        label = select_best_label(results, gen)
        set_id = label.get('set_id', label.get('id', 'unknown'))
        openfda_info = label.get('openfda', {})
        brand_name = openfda_info.get('brand_name', ['Unknown'])[0] if openfda_info.get('brand_name') else 'Unknown'
        
        saved_data = {
            "generic_name": gen,
            "set_id": set_id,
            "id": label.get('id'),
            "openfda_brand_name": brand_name,
            "query_url": query_url,
            "dosage_and_administration": label.get('dosage_and_administration', []),
            "dosage_forms_and_strengths": label.get('dosage_forms_and_strengths', []),
            "warnings": label.get('warnings', []),
            "boxed_warning": label.get('boxed_warning', []),
            "indications_and_usage": label.get('indications_and_usage', []),
            "contraindications": label.get('contraindications', []),
            "overdosage": label.get('overdosage', []),
            "openfda": openfda_info
        }
        
        out_file = LABELS_DIR / f"{gen}.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(saved_data, f, indent=2)
            
        print(f"   SUCCESS: Saved label {set_id} ({brand_name}) to {out_file.name}")
        success_drugs.append(gen)
        time.sleep(0.2)
        
    print("\n--- FETCH SUMMARY ---")
    print(f"Successfully fetched: {len(success_drugs)} / {len(df)}")
    if failed_drugs:
        print(f"Failed drugs ({len(failed_drugs)}): {', '.join(failed_drugs)}")
    else:
        print("Failed drugs: None")

if __name__ == "__main__":
    main()
