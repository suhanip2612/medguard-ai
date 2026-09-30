"""Rule engine. PURE PYTHON, NO LLM. Every alert comes from a CSV row or a fixed rule."""

SEVERITY_ORDER = {"contraindicated": 0, "major": 1, "moderate": 2, "minor": 3}
# Classes where two different drugs together are NOT treated as a duplicate.
NON_DUP_CLASSES = {"analgesic_antipyretic_none"}


def _tags(kb, generic):
    return {generic, kb.drugs[generic]["class"]}


def _alert(kind, severity, title, drugs, mechanism, recommendation, alternative="", source=""):
    return {
        "type": kind, "severity": severity, "title": title, "drugs": drugs,
        "mechanism": mechanism, "recommendation": recommendation,
        "alternative": alternative or "", "source": source or "Rule engine",
    }


def check_interactions(kb, new, meds):
    best = {}  # one alert per existing medicine (keep the most severe matching row)
    new_tags = _tags(kb, new)
    for m in meds:
        med_tags = _tags(kb, m["generic"])
        for row in kb.interactions:
            a, b = row["drug_a"], row["drug_b"]
            if (a in new_tags and b in med_tags) or (b in new_tags and a in med_tags):
                al = _alert("drug-drug", row["severity"],
                            f"{new.title()} + {m['generic'].title()}: interaction",
                            [new, m["generic"]], row["mechanism"], row["recommendation"],
                            row["alternative"], row["source"])
                cur = best.get(m["generic"])
                if cur is None or SEVERITY_ORDER[al["severity"]] < SEVERITY_ORDER[cur["severity"]]:
                    best[m["generic"]] = al
    return list(best.values())


def check_drug_disease(kb, new, conditions):
    out, new_tags = [], _tags(kb, new)
    for row in kb.drug_disease:
        if row["drug_or_class"] in new_tags and row["condition"] in conditions:
            cond = row["condition"].replace("_", " ")
            out.append(_alert("drug-disease", row["severity"],
                              f"{new.title()} in a patient with {cond}", [new],
                              row["reason"], row["recommendation"], row["alternative"], row["source"]))
    return out


def check_duplicates(kb, new, meds, typed_name):
    out, new_class = [], kb.drugs[new]["class"]
    for m in meds:
        if m["generic"] == new:
            existing = m["brand"] or m["generic"].title()
            typed = typed_name.strip().title()
            out.append(_alert("duplicate", "major",
                              f"Duplicate therapy: {new.title()} already prescribed", [new],
                              f"Patient already takes {existing} which contains {new}. "
                              f"'{typed}' is the same active ingredient under a different name.",
                              "Do not prescribe both. Adjust the existing prescription instead.",
                              "", "Brand-to-generic mapping"))
        elif kb.drugs[m["generic"]]["class"] == new_class and new_class not in NON_DUP_CLASSES:
            out.append(_alert("duplicate", "moderate",
                              f"Therapeutic duplication ({new_class.replace('_', ' ')})",
                              [new, m["generic"]],
                              f"{new.title()} and {m['generic'].title()} belong to the same drug class.",
                              "Confirm two drugs from the same class are intended.",
                              "", "Drug-class mapping"))
    return out


def check_dose(kb, new, dose_mg, per_day, meds):
    mx = kb.drugs[new]["max_daily_dose_mg"]
    if not dose_mg or not per_day or not mx:
        return []
    new_daily = dose_mg * per_day
    existing = sum((m["dose_mg"] or 0) * (m["times_per_day"] or 0) for m in meds if m["generic"] == new)
    total = new_daily + existing
    if total > mx:
        return [_alert("dose", "major", f"{new.title()}: daily dose too high", [new],
                       f"Total daily dose would be {total:.0f} mg "
                       f"({new_daily:.0f} mg new + {existing:.0f} mg existing). "
                       f"The reference maximum in this system is {mx:.0f} mg/day.",
                       "Reduce the dose or frequency.", "", "Reference max daily dose (VERIFY)")]
    return []


def check_allergy(kb, new, allergies):
    out, tags = [], _tags(kb, new)
    for a in allergies:
        if a in tags:
            out.append(_alert("allergy", "contraindicated",
                              f"Allergy: patient is allergic to {a}", [new],
                              f"{new.title()} belongs to '{kb.drugs[new]['class']}' and the patient has a "
                              f"recorded {a} allergy.",
                              "Do not prescribe.",
                              "Choose a drug from a different class per local guidelines.",
                              "Patient allergy record"))
    return out


def run_checks(kb, patient, drug_name, dose_mg=None, per_day=None):
    generic, how = kb.resolve(drug_name)
    if not generic:
        return {"unknown": True, "input": drug_name, "resolved_generic": None,
                "matched_via": None, "alerts": []}
    meds = patient["current_meds"]
    alerts = (check_allergy(kb, generic, patient["allergies"])
              + check_interactions(kb, generic, meds)
              + check_drug_disease(kb, generic, patient["conditions"])
              + check_duplicates(kb, generic, meds, drug_name)
              + check_dose(kb, generic, dose_mg, per_day, meds))
    alerts.sort(key=lambda a: SEVERITY_ORDER[a["severity"]])
    for i, a in enumerate(alerts):
        a["id"] = f"a{i}"
    return {"unknown": False, "input": drug_name, "resolved_generic": generic,
            "matched_via": how, "alerts": alerts}
