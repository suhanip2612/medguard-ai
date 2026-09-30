from app.kb import KnowledgeBase
from app.rules import run_checks

kb = KnowledgeBase()


def pat(uid):
    return kb.patients[uid]


def types(res):
    return {a["type"] for a in res["alerts"]}


def test_A_warfarin_plus_aspirin_is_major():
    res = run_checks(kb, pat("UID_PATIENT_A"), "Ecosprin", 75, 1)
    assert any(a["type"] == "drug-drug" and a["severity"] == "major" for a in res["alerts"])
    assert res["resolved_generic"] == "aspirin"


def test_B_ckd_plus_ibuprofen():
    res = run_checks(kb, pat("UID_PATIENT_B"), "Brufen", 400, 3)
    assert "drug-disease" in types(res)      # NSAID in CKD
    assert "drug-drug" in types(res)         # ACE inhibitor + NSAID


def test_C_duplicate_brand_names_and_dose():
    res = run_checks(kb, pat("UID_PATIENT_C"), "Crocin", 650, 4)
    assert "duplicate" in types(res)
    assert "dose" in types(res)              # 2600 new + 1950 existing > 4000


def test_D_penicillin_allergy():
    res = run_checks(kb, pat("UID_PATIENT_D"), "Amoxicillin", 500, 3)
    assert any(a["type"] == "allergy" and a["severity"] == "contraindicated" for a in res["alerts"])


def test_safe_prescription_has_no_alerts():
    res = run_checks(kb, pat("UID_PATIENT_D"), "Paracetamol", 500, 3)
    assert res["alerts"] == []


def test_unknown_drug():
    res = run_checks(kb, pat("UID_PATIENT_A"), "zzzzqq")
    assert res["unknown"] is True


def test_typo_is_fuzzy_matched():
    generic, how = kb.resolve("warfrin")
    assert generic == "warfarin" and how == "fuzzy"
