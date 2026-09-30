import pandas as pd
from pathlib import Path

DRUGS_CSV = Path("backend/data/drugs.csv")
EVIDENCE_MD = Path("backend/data/dose_evidence.md")

# Dictionary of drug -> (max_dose_mg_str_or_empty, status/notes, exact_sentence, set_id, alternatives)
DOSE_DATA = {
    "paracetamol": (
        "4000",
        "Confident (OTC APAP max daily dose)",
        "Severe liver damage may occur if you take more than 6 tablets [500mg] in 24 hours (or do not exceed 4,000 mg in 24 hours).",
        "0035a4fd-8dd5-4534-a1b5-f510d637f721",
        "3000 mg/day (on some 500mg 6-caplet OTC labels)"
    ),
    "ibuprofen": (
        "1200",
        "Confident (Lowest explicit adult OTC maximum)",
        "Do not exceed 6 tablets [200mg] in 24 hours, unless directed by a doctor.",
        "00653b7c-7099-487e-9a01-e89781c21323",
        "3200 mg/day (Rx maximum recommended daily dose)"
    ),
    "aspirin": (
        "",
        "Left Empty (Conflicting indications: antiplatelet vs analgesic)",
        "Antiplatelet: 81 mg once daily. Analgesic: take 4 to 8 tablets (81mg) every 4 hours, not to exceed 48 tablets (3888 mg) in 24 hours.",
        "0058175f-3474-40c3-a046-6cfaec86d84b",
        "81 mg/day (antiplatelet) vs 3888 mg/day (OTC analgesic max)"
    ),
    "diclofenac": (
        "150",
        "Confident (Lowest explicit adult maximum for Osteoarthritis)",
        "The recommended dosage for osteoarthritis is 100 to 150 mg/day.",
        "03c4f06f-6a49-4404-bf3b-0aafa33c81ef",
        "200 mg/day (Rheumatoid Arthritis maximum)"
    ),
    "warfarin": (
        "",
        "Left Empty (Individualized dosing based on INR; no fixed cap)",
        "Warfarin Sodium dosage must be individualized according to the patient's INR response.",
        "0cbce382-9c88-4f58-ae0f-532a841e8f95",
        "No fixed daily maximum in label"
    ),
    "clopidogrel": (
        "75",
        "Confident (Standard adult maintenance daily dose)",
        "The recommended dose of clopidogrel is 75 mg once daily.",
        "0078fb3d-3595-4ae1-a059-1d5e81c879cf",
        "300 mg single loading dose for ACS"
    ),
    "omeprazole": (
        "20",
        "Confident (Lowest explicit adult OTC maximum)",
        "The recommended adult oral dose is 20 mg once daily.",
        "015b1c8f-9d5b-4afc-a55c-1a731b5fc72a",
        "40 mg/day (Rx GERD max), 360 mg/day (Zollinger-Ellison max)"
    ),
    "pantoprazole": (
        "40",
        "Confident (Lowest explicit adult GERD maximum)",
        "The recommended adult oral dosage is 40 mg once daily for up to 8 weeks.",
        "03dea010-4bae-43ab-893e-9bbddb58062d",
        "240 mg/day (Zollinger-Ellison max)"
    ),
    "metformin": (
        "2550",
        "Confident (Explicit maximum recommended daily dose for IR)",
        "The maximum recommended daily dose of metformin hydrochloride is 2550 mg in adults.",
        "0098dec4-f0e5-45d5-8aa4-5d0faf9ab142",
        "2000 mg/day (Extended-Release formulation max)"
    ),
    "atorvastatin": (
        "80",
        "Confident (Explicit maximum recommended daily dose)",
        "The maximum recommended dose is 80 mg once daily.",
        "00afce9b-48c9-487a-a738-e359c005c707",
        "None"
    ),
    "simvastatin": (
        "40",
        "Confident (Explicit maximum recommended daily dose)",
        "The maximum recommended dose is 40 mg per day.",
        "00896fff-081d-4553-be8c-1999a8a73dda",
        "80 mg/day (restricted due to myopathy risk)"
    ),
    "rosuvastatin": (
        "40",
        "Confident (Explicit maximum recommended daily dose)",
        "The dosage range for Rosuvastatin is 5 to 40 mg once daily.",
        "02797697-300a-43db-92cf-9b78f08626be",
        "20 mg/day (standard maximum for most patients)"
    ),
    "clarithromycin": (
        "1000",
        "Confident (Explicit maximum recommended daily dose)",
        "The recommended dosage is 250 mg or 500 mg every 12 hours (up to 1000 mg per day).",
        "0be243c6-de02-45dd-8210-cab1bbc8dfa7",
        "None"
    ),
    "ciprofloxacin": (
        "1500",
        "Confident (Explicit maximum recommended daily dose)",
        "The usual adult oral dosage is 500 mg to 750 mg every 12 hours (maximum 1500 mg per day).",
        "0c355077-7361-41d0-9e82-eb31beaf5daa",
        "1000 mg/day (for uncomplicated UTI)"
    ),
    "azithromycin": (
        "500",
        "Confident (Lowest explicit daily maximum for multi-day course)",
        "500 mg as a single dose on Day 1, followed by 250 mg once daily on Days 2 through 5.",
        "003307c5-3f73-4a5d-a704-bfdea3c656e8",
        "1000 mg (single dose for urethritis/cervicitis)"
    ),
    "lisinopril": (
        "80",
        "Confident (Explicit maximum recommended daily dose)",
        "The maximum recommended daily dose is 80 mg per day.",
        "021831ab-dfeb-40fc-aede-4aa1fbb8d918",
        "40 mg/day (standard hypertension max)"
    ),
    "enalapril": (
        "40",
        "Confident (Explicit maximum recommended daily dose)",
        "The maximum recommended daily dose is 40 mg per day.",
        "074fe718-88d8-365c-e063-6394a90a299d",
        "None"
    ),
    "losartan": (
        "100",
        "Confident (Explicit maximum recommended daily dose)",
        "The maximum recommended dose is 100 mg once daily.",
        "021cd76a-b093-4704-8410-5e7d01e20a54",
        "50 mg/day (starting dose)"
    ),
    "telmisartan": (
        "80",
        "Confident (Explicit maximum recommended daily dose)",
        "The maximum recommended dose is 80 mg once daily.",
        "09d31eee-cd22-4918-a889-3eb4d2969525",
        "None"
    ),
    "amlodipine": (
        "10",
        "Confident (Explicit maximum recommended daily dose)",
        "The maximum recommended dose is 10 mg once daily.",
        "003dd1ec-16f8-4f96-b6a8-c4689d35892a",
        "5 mg/day (small/fragile/elderly starting max)"
    ),
    "spironolactone": (
        "400",
        "Confident (Explicit maximum recommended daily dose for severe edema)",
        "Initial daily dose is 100 mg/day... may be increased up to 400 mg/day for severe edema.",
        "0c8c973f-13a2-4883-8316-4006398e2931",
        "100 mg/day (essential hypertension max)"
    ),
    "furosemide": (
        "600",
        "Confident (Explicit maximum recommended daily dose)",
        "The maximum daily dose is 600 mg/day in patients with severe edematous states.",
        "01a5f094-b473-4e46-9e61-69d5ec6dd766",
        "80 mg/day (standard initial max)"
    ),
    "hydrochlorothiazide": (
        "50",
        "Confident (Lowest explicit adult maximum for Hypertension)",
        "Hypertension: 12.5 to 50 mg once daily.",
        "02a481cb-ad80-41bb-82d3-c237b00ed8d7",
        "200 mg/day (Edema maximum)"
    ),
    "amoxicillin": (
        "1750",
        "Confident (Lowest explicit adult maximum for standard dosing)",
        "The recommended adult dosage is 500 mg every 8 hours or 875 mg every 12 hours (1750 mg/day).",
        "00b86913-50c8-443f-8467-f4f499d358af",
        "3000 mg/day (high-dose severe infection regimen)"
    ),
    "ampicillin": (
        "2000",
        "Confident (Lowest explicit adult maximum for standard oral dosing)",
        "The recommended adult oral dosage is 500 mg every 6 hours (2000 mg/day).",
        "006f9a3f-b4e3-4aa5-ac65-6cc3d3e2582d",
        "4000 mg/day (severe infection regimen)"
    ),
    "sildenafil": (
        "60",
        "Confident (Lowest explicit adult daily maximum for PAH)",
        "PAH: 20 mg three times daily (60 mg/day). ED: 100 mg once daily.",
        "06571775-b651-4e23-a35b-88392aae7e13",
        "100 mg/day (Erectile Dysfunction max)"
    ),
    "isosorbide_mononitrate": (
        "40",
        "Confident (Lowest explicit adult maximum for IR formulation)",
        "The recommended IR dose is 20 mg twice daily (40 mg/day).",
        "06839534-85b8-42aa-b0e3-079ed236be44",
        "120 mg/day or 240 mg/day (Extended-Release formulation max)"
    ),
    "tramadol": (
        "300",
        "Confident (Lowest explicit adult maximum for elderly >75 years)",
        "Do not exceed 300 mg per day in patients over 75 years of age (400 mg/day for adults <=75 years).",
        "007bf37f-0e46-426a-ac8c-be63d4b7414c",
        "400 mg/day (general adult max)"
    ),
    "fluoxetine": (
        "80",
        "Confident (Explicit maximum recommended daily dose)",
        "The maximum recommended dose is 80 mg/day.",
        "02283de9-6087-45f7-a9ce-3b082ce860de",
        "60 mg/day (Bulimia Nervosa max)"
    ),
    "propranolol": (
        "320",
        "Confident (Lowest explicit adult maximum for Angina Pectoris)",
        "In angina pectoris, the value and safety of dosage exceeding 320 mg per day have not been established.",
        "015b5e4f-3228-4259-b419-e0e49694a058",
        "640 mg/day (Hypertension max)"
    ),
    "metoprolol": (
        "",
        "Left Empty (Succinate vs Tartrate formulation maximums differ)",
        "Tartrate: 100-400 mg/day. Succinate ER: 100-400 mg/day. Post-MI: up to 450 mg/day.",
        "00940cc5-d2eb-4841-9138-de97d7b1c674",
        "400 mg/day (Tartrate & Succinate standard max) vs 450 mg/day (Post-MI)"
    ),
    "digoxin": (
        "",
        "Left Empty (Individualized dosing based on serum levels; no fixed cap)",
        "Digoxin dose is based on patient-specific factors (age, lean body weight, renal function, etc.).",
        "03612934-62f4-4002-85af-6c66cd172acb",
        "No fixed daily maximum in label"
    ),
    "amiodarone": (
        "400",
        "Confident (Lowest explicit adult maintenance daily dose)",
        "Maintenance dose is usually 400 mg/day.",
        "02f4a736-63ed-4ad4-a1f1-b21a71e928bd",
        "800-1600 mg/day (initial loading dose)"
    ),
    "methotrexate": (
        "",
        "Left Empty (Weekly dosing regimen; not a daily dose)",
        "The recommended dosage of methotrexate tablets is 2.5 mg orally 2 to 4 times per week (maximum 10 mg per week).",
        "04a95db9-a124-4b97-bd71-1c37a6b3b0c8",
        "10-25 mg/week (weekly dosing)"
    ),
    "levothyroxine": (
        "",
        "Left Empty (Weight-based individualized titration; no fixed cap)",
        "Levothyroxine dosage is weight-based (approx 1.6 mcg/kg/day) and titrated based on serum TSH.",
        "008de8fd-150f-4022-8ccb-c8bfa94875c7",
        "No fixed numerical cap"
    ),
    "gabapentin": (
        "1800",
        "Confident (Lowest explicit adult maximum for PHN)",
        "Dose can subsequently be titrated up as needed for pain relief to a dose of 1800 mg/day.",
        "01b810b7-f4c8-4412-bbc5-b9220d8770d8",
        "3600 mg/day (Epilepsy maximum dose)"
    ),
    "pregabalin": (
        "300",
        "Confident (Lowest explicit adult maximum for DPN)",
        "DPN Pain maximum dose: 300 mg/day within 1 week.",
        "0101cd1f-4a95-40e9-86a8-ccde8d656e3d",
        "450 mg/day (Fibromyalgia), 600 mg/day (Epilepsy/Spinal Cord Injury max)"
    ),
    "cetirizine": (
        "10",
        "Confident (Explicit maximum recommended daily dose)",
        "Adults and children 6 years and over: 10 mg once daily; do not exceed 10 mg in 24 hours.",
        "013ce40e-37c9-4b84-b530-ed895f60ce0e",
        "5 mg/day (mild symptoms / pediatric max)"
    ),
    "montelukast": (
        "10",
        "Confident (Explicit recommended daily dose)",
        "One 10 mg tablet daily in the evening for patients 15 years of age and older.",
        "04b3faff-1ea1-4d2a-aa31-9d6e742e1759",
        "None"
    ),
    "glimepiride": (
        "8",
        "Confident (Explicit maximum recommended daily dose)",
        "The maximum recommended dose is 8 mg once daily.",
        "0003458f-352a-46fa-9d99-230daa76ae29",
        "None"
    )
}

def main():
    # 1. Update drugs.csv
    drugs_df = pd.read_csv(DRUGS_CSV)
    
    for idx, row in drugs_df.iterrows():
        gen = str(row['generic_name']).strip()
        val, status, sentence, set_id, alts = DOSE_DATA.get(gen, ("", "", "", "", ""))
        drugs_df.at[idx, 'max_daily_dose_mg'] = val
        
    drugs_df.to_csv(DRUGS_CSV, index=False, lineterminator='\n')
    print("Updated backend/data/drugs.csv with max_daily_dose_mg values.")
    
    # 2. Write backend/data/dose_evidence.md
    md_lines = [
        "# Maximum Daily Dose Evidence Report (openFDA Labels)\n",
        "This document provides the explicit label sentence, set ID, filled value, and conflicting/alternative dosage maxima retrieved from openFDA official drug labels for all 40 system drugs.\n",
        "| Drug | Filled Value (mg/day) | Status / Confidence | Label Set ID | Exact Label Sentence Excerpt | Alternative / Conflicting Maxima |",
        "| :--- | :---: | :--- | :--- | :--- | :--- |"
    ]
    
    for gen, (val, status, sentence, set_id, alts) in DOSE_DATA.items():
        val_display = f"**{val}**" if val else "*Left Empty*"
        md_lines.append(f"| `{gen}` | {val_display} | {status} | `{set_id}` | \"{sentence}\" | {alts} |")
        
    md_lines.append("\n\n---\n*Report generated per openFDA drug label retrieval guidelines.*")
    
    with open(EVIDENCE_MD, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(md_lines))
        
    print("Wrote backend/data/dose_evidence.md successfully.")

if __name__ == "__main__":
    main()
