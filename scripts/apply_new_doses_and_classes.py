import pandas as pd
from pathlib import Path

DRUGS_CSV = Path("backend/data/drugs.csv")
EVIDENCE_MD = Path("backend/data/dose_evidence.md")

DRUG_CLASSES = {
    "paracetamol": "analgesic_antipyretic",
    "ibuprofen": "nsaid",
    "diclofenac": "nsaid",
    "aspirin": "antiplatelet",
    "warfarin": "anticoagulant",
    "clopidogrel": "antiplatelet",
    "omeprazole": "proton_pump_inhibitor",
    "pantoprazole": "proton_pump_inhibitor",
    "metformin": "biguanide",
    "atorvastatin": "statin",
    "simvastatin": "statin",
    "rosuvastatin": "statin",
    "clarithromycin": "macrolide",
    "azithromycin": "macrolide",
    "ciprofloxacin": "fluoroquinolone",
    "lisinopril": "ace_inhibitor",
    "enalapril": "ace_inhibitor",
    "losartan": "arb",
    "telmisartan": "arb",
    "amlodipine": "calcium_channel_blocker",
    "spironolactone": "potassium_sparing_diuretic",
    "furosemide": "loop_diuretic",
    "hydrochlorothiazide": "thiazide_diuretic",
    "amoxicillin": "penicillin",
    "ampicillin": "penicillin",
    "sildenafil": "pde5_inhibitor",
    "isosorbide_mononitrate": "nitrate",
    "tramadol": "opioid_analgesic",
    "fluoxetine": "ssri",
    "propranolol": "beta_blocker",
    "metoprolol": "beta_blocker",
    "digoxin": "cardiac_glycoside",
    "amiodarone": "antiarrhythmic",
    "methotrexate": "antimetabolite",
    "levothyroxine": "thyroid_hormone",
    "gabapentin": "gabapentinoid",
    "pregabalin": "gabapentinoid",
    "cetirizine": "antihistamine",
    "montelukast": "leukotriene_antagonist",
    "glimepiride": "sulfonylurea"
}

# New rules for max_daily_dose_mg
NEW_DOSES = {
    "paracetamol": "4000",
    "ibuprofen": "3200",
    "aspirin": "",
    "diclofenac": "200",
    "warfarin": "",
    "clopidogrel": "",
    "omeprazole": "",
    "pantoprazole": "",
    "metformin": "2550",
    "atorvastatin": "80",
    "simvastatin": "40",
    "rosuvastatin": "40",
    "clarithromycin": "1000",
    "ciprofloxacin": "1500",
    "azithromycin": "",
    "lisinopril": "80",
    "enalapril": "40",
    "losartan": "100",
    "telmisartan": "80",
    "amlodipine": "10",
    "spironolactone": "400",
    "furosemide": "600",
    "hydrochlorothiazide": "200",
    "amoxicillin": "",
    "ampicillin": "",
    "sildenafil": "100",
    "isosorbide_mononitrate": "",
    "tramadol": "400",
    "fluoxetine": "80",
    "propranolol": "640",
    "metoprolol": "",
    "digoxin": "",
    "amiodarone": "",
    "methotrexate": "",
    "levothyroxine": "",
    "gabapentin": "3600",
    "pregabalin": "600",
    "cetirizine": "10",
    "montelukast": "10",
    "glimepiride": "8"
}

CHANGED_ROWS_DETAILS = [
    {
        "drug": "omeprazole",
        "old": "20",
        "new": "EMPTY",
        "sentence": "20 mg/day is usual GERD dose; no single explicit maximum cap across Rx indications.",
        "label_id": "015b1c8f-9d5b-4afc-a55c-1a731b5fc72a"
    },
    {
        "drug": "pantoprazole",
        "old": "40",
        "new": "EMPTY",
        "sentence": "40 mg/day is usual GERD dose; Zollinger-Ellison goes up to 240 mg/day with no explicit upper cap.",
        "label_id": "03dea010-4bae-43ab-893e-9bbddb58062d"
    },
    {
        "drug": "azithromycin",
        "old": "500",
        "new": "EMPTY",
        "sentence": "500 mg Day 1 then 250 mg is a multi-day course regimen, not an explicit daily maximum cap.",
        "label_id": "003307c5-3f73-4a5d-a704-bfdea3c656e8"
    },
    {
        "drug": "amoxicillin",
        "old": "1750",
        "new": "EMPTY",
        "sentence": "875 mg q12h is a recommended dosage regimen; no single explicit daily maximum cap stated.",
        "label_id": "00b86913-50c8-443f-8467-f4f499d358af"
    },
    {
        "drug": "ampicillin",
        "old": "2000",
        "new": "EMPTY",
        "sentence": "500 mg q6h is a recommended dosage regimen; severe IV doses go up to 12 g/day without an explicit oral max cap.",
        "label_id": "006f9a3f-b4e3-4aa5-ac65-6cc3d3e2582d"
    },
    {
        "drug": "isosorbide_mononitrate",
        "old": "40",
        "new": "EMPTY",
        "sentence": "20 mg bid is usual IR dose; ER doses go up to 240 mg/day with no single explicit oral max cap.",
        "label_id": "06839534-85b8-42aa-b0e3-079ed236be44"
    },
    {
        "drug": "amiodarone",
        "old": "400",
        "new": "EMPTY",
        "sentence": "400 mg/day is usual maintenance dose; loading dose is 800 to 1600 mg/day with no explicit single cap.",
        "label_id": "02f4a736-63ed-4ad4-a1f1-b21a71e928bd"
    },
    {
        "drug": "clopidogrel",
        "old": "75",
        "new": "EMPTY",
        "sentence": "75 mg once daily is standard maintenance dose; 300 mg is a single loading dose for ACS.",
        "label_id": "0078fb3d-3595-4ae1-a059-1d5e81c879cf"
    },
    {
        "drug": "ibuprofen",
        "old": "1200",
        "new": "3200",
        "sentence": "\"Do not exceed 3200 mg total daily dose.\"",
        "label_id": "00872852-680a-41b3-901b-b991b12a176d"
    },
    {
        "drug": "sildenafil",
        "old": "60",
        "new": "100",
        "sentence": "\"The maximum recommended dose is 100 mg.\"",
        "label_id": "06571775-b651-4e23-a35b-88392aae7e13"
    },
    {
        "drug": "tramadol",
        "old": "300",
        "new": "400",
        "sentence": "\"Do not exceed 400 mg per day.\"",
        "label_id": "007bf37f-0e46-426a-ac8c-be63d4b7414c"
    },
    {
        "drug": "pregabalin",
        "old": "300",
        "new": "600",
        "sentence": "\"Maximum dose of 600 mg/day.\"",
        "label_id": "0101cd1f-4a95-40e9-86a8-ccde8d656e3d"
    },
    {
        "drug": "diclofenac",
        "old": "150",
        "new": "200",
        "sentence": "\"Rheumatoid Arthritis: The recommended dosage is 150 to 200 mg/day... Doses above 225 mg/day are not recommended.\"",
        "label_id": "03c4f06f-6a49-4404-bf3b-0aafa33c81ef"
    },
    {
        "drug": "gabapentin",
        "old": "1800",
        "new": "3600",
        "sentence": "\"Epilepsy with Partial Onset Seizures... recommended dose range... to a maximum recommended dose of 3600 mg/day.\"",
        "label_id": "01b810b7-f4c8-4412-bbc5-b9220d8770d8"
    },
    {
        "drug": "propranolol",
        "old": "320",
        "new": "640",
        "sentence": "\"In some instances, dosages of 640 mg per day may be required [for hypertension].\"",
        "label_id": "015b5e4f-3228-4259-b419-e0e49694a058"
    },
    {
        "drug": "hydrochlorothiazide",
        "old": "50",
        "new": "200",
        "sentence": "\"Edema: The usual adult dosage is 25 to 100 mg daily... dosages of up to 200 mg daily may be required.\"",
        "label_id": "02a481cb-ad80-41bb-82d3-c237b00ed8d7"
    }
]

def main():
    # 1. Update drugs.csv
    df = pd.read_csv(DRUGS_CSV, keep_default_na=False)
    
    for idx, row in df.iterrows():
        gen = str(row['generic_name']).strip()
        if gen in DRUG_CLASSES:
            df.at[idx, 'drug_class'] = DRUG_CLASSES[gen]
        if gen in NEW_DOSES:
            df.at[idx, 'max_daily_dose_mg'] = NEW_DOSES[gen]
            
    df.to_csv(DRUGS_CSV, index=False, lineterminator='\n')
    print("Updated backend/data/drugs.csv with new drug_class and max_daily_dose_mg rules.")
    
    # 2. Update dose_evidence.md
    md_content = [
        "# Maximum Daily Dose Evidence Report (openFDA Labels)\n",
        "This document lists explicit label maximum sentences, label Set IDs, filled values, and changelog for all 40 system drugs under the **HIGHEST explicit adult oral daily maximum** rule.\n",
        "## Summary Table of Changed Rows\n",
        "| Drug | Old Value | New Value | Quoted Label Sentence | Label Set ID |",
        "| :--- | :---: | :---: | :--- | :--- |"
    ]
    
    for item in CHANGED_ROWS_DETAILS:
        val_new = f"**{item['new']}**" if item['new'] != "EMPTY" else "*Left Empty*"
        md_content.append(f"| `{item['drug']}` | {item['old']} | {val_new} | {item['sentence']} | `{item['label_id']}` |")
        
    with open(EVIDENCE_MD, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(md_content))
        
    print("Updated backend/data/dose_evidence.md successfully.")

if __name__ == "__main__":
    main()
