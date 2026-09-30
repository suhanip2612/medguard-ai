"""Knowledge base: loads all CSV files from backend/data into memory."""
import csv
from difflib import get_close_matches
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"


def _read(name):
    with open(DATA / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def norm(s):
    return (s or "").strip().lower()


def _split(s):
    return [x.strip() for x in (s or "").split(";") if x.strip()]


class KnowledgeBase:
    def __init__(self):
        self.load()

    def load(self):
        self.drugs = {}              # generic -> {generic, class, brands, max_daily_dose_mg}
        self.name_to_generic = {}    # generic AND brand names (lowercase) -> generic
        for r in _read("drugs.csv"):
            g = norm(r["generic_name"])
            mx = r["max_daily_dose_mg"].strip()
            brands_col = r.get("brands") if "brands" in r else r.get("brand_names", "")
            self.drugs[g] = {
                "generic": g,
                "class": norm(r["drug_class"]),
                "brands": _split(brands_col),
                "max_daily_dose_mg": float(mx) if mx else None,
            }
            self.name_to_generic[g] = g
            for b in _split(brands_col):
                self.name_to_generic[norm(b)] = g

        self.interactions = [{k: norm(v) if k in ("drug_a", "drug_b", "severity") else v
                              for k, v in r.items()} for r in _read("interactions.csv")]
        self.drug_disease = [{k: norm(v) if k in ("drug_or_class", "condition", "severity") else v
                              for k, v in r.items()} for r in _read("drug_disease.csv")]
        self.patients = {}
        for r in _read("patients.csv"):
            self.patients[r["card_uid"].strip().upper()] = self._parse_patient(r)

    def _parse_patient(self, r):
        meds = []
        for item in _split(r["current_meds"]):
            parts = [p.strip() for p in item.split(":")]
            name = parts[0]
            generic, _ = self.resolve(name)
            if not generic:
                continue
            meds.append({
                "generic": generic,
                "dose_mg": float(parts[1]) if len(parts) > 1 and parts[1] else None,
                "times_per_day": int(parts[2]) if len(parts) > 2 and parts[2] else None,
                "brand": parts[3] if len(parts) > 3 and parts[3] else None,
            })
        return {
            "card_uid": r["card_uid"].strip().upper(),
            "name": r["name"],
            "age": int(r["age"]),
            "weight_kg": float(r["weight_kg"]),
            "conditions": [norm(c) for c in _split(r["conditions"])],
            "allergies": [norm(a) for a in _split(r["allergies"])],
            "current_meds": meds,
        }

    def resolve(self, name):
        """Turn a typed drug/brand name into a generic name.
        Returns (generic_or_None, how) where how is 'exact', 'prefix', 'fuzzy' or None."""
        n = norm(name)
        if not n:
            return None, None
        if n in self.name_to_generic:
            return self.name_to_generic[n], "exact"
        if len(n) >= 3:
            for key, g in self.name_to_generic.items():
                if key.startswith(n):
                    return g, "prefix"
        close = get_close_matches(n, list(self.name_to_generic.keys()), n=1, cutoff=0.75)
        if close:
            return self.name_to_generic[close[0]], "fuzzy"
        return None, None

    def all_names(self):
        """Every generic + brand name, for the UI autocomplete."""
        return sorted({d["generic"] for d in self.drugs.values()} |
                      {b for d in self.drugs.values() for b in d["brands"]}, key=str.lower)
