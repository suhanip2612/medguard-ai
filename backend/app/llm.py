"""LLM is used ONLY to rewrite an already-decided alert into plain language.
It never decides whether something is dangerous. A template is the fallback."""
import os
from concurrent.futures import ThreadPoolExecutor

_pool = ThreadPoolExecutor(max_workers=4)
_cache = {}


def template_explanation(alert):
    return f"{alert['title']}. {alert['mechanism']} Suggested action: {alert['recommendation']}"


def _prompt(alert, patient):
    return (
        "You are helping a doctor read a drug safety alert. Rewrite the facts below as 2 or 3 short, "
        "plain sentences. Use ONLY the facts given. Do not add any medical claim, dose, or drug name "
        "that is not in the facts. Do not give new advice.\n\n"
        f"Patient: {patient['age']} years, conditions: {', '.join(patient['conditions']) or 'none'}.\n"
        f"Alert: {alert['title']}\nSeverity: {alert['severity']}\n"
        f"Mechanism: {alert['mechanism']}\nRecommended action: {alert['recommendation']}"
    )


def _call_gemini(prompt):
    from google import genai
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    resp = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"), contents=prompt)
    return (resp.text or "").strip()


def explain(alert, patient):
    key = (alert["title"], alert["severity"], patient["card_uid"])
    if key in _cache:
        return _cache[key]
    result = {"text": template_explanation(alert), "source": "template"}
    if os.getenv("USE_LLM", "true").lower() == "true" and os.getenv("GEMINI_API_KEY"):
        try:
            text = _pool.submit(_call_gemini, _prompt(alert, patient)).result(timeout=6)
            if text and len(text) < 700:
                result = {"text": text, "source": "llm"}
        except Exception as e:  # timeout, quota, network... fall back silently
            print("LLM fallback:", type(e).__name__)
    _cache[key] = result
    return result
