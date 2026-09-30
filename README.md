# MedGuard AI

Explainable medication-safety checks with RFID tap-to-load patient records.
Hackathon project: Healthcare PS4, AI-Based Detection of Medication Errors and Dangerous Drug Interactions.

- **Detection** is done by fixed rules over curated CSV data (`backend/data/`). No AI decides danger.
- **Gemini** only rewrites an already-decided alert into plain language (with a template fallback).
- **RFID**: ESP32 + RC522 sends the card UID over USB serial to the backend.
- The doctor always makes the final decision. Demo uses synthetic patients only.

```
firmware/   ESP32 Arduino code
backend/    FastAPI + rules engine + CSV knowledge base + tests
frontend/   React (Vite) doctor dashboard
docs/       slides, notes
```

Full setup: see **SETUP.md**.

> Clinical data in `backend/data/*.csv` is a demo seed marked `(VERIFY)`. Verify each row against
> DDInter / openFDA labels before presenting it as fact.
