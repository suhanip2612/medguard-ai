import json
import os
import sqlite3
import threading
import time
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()

from app.kb import KnowledgeBase  # noqa: E402
from app.llm import explain  # noqa: E402
from app.rules import run_checks  # noqa: E402

kb = KnowledgeBase()
DB_PATH = Path(__file__).resolve().parent.parent / "medguard.db"
tap = {"uid": None, "seq": 0, "ts": None}


def db():
    con = sqlite3.connect(DB_PATH)
    con.execute("""CREATE TABLE IF NOT EXISTS decisions (
        id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, uid TEXT, drug TEXT,
        action TEXT, reason TEXT, alerts_json TEXT)""")
    return con


def serial_reader():
    port = os.getenv("SERIAL_PORT", "").strip()
    if not port:
        print("SERIAL_PORT empty -> running without hardware (use Simulate Tap).")
        return
    import serial
    while True:
        try:
            ser = serial.Serial(port, int(os.getenv("SERIAL_BAUD", "115200")), timeout=1)
            print("Serial connected on", port)
            while True:
                line = ser.readline().decode(errors="ignore").strip()
                if line.startswith("UID:"):
                    tap["uid"] = line[4:].strip().upper()
                    tap["seq"] += 1
                    tap["ts"] = time.time()
                    print("Tap:", tap["uid"])
        except Exception as e:
            print("Serial error:", e, "- retrying in 3s")
            time.sleep(3)


@asynccontextmanager
async def lifespan(app):
    threading.Thread(target=serial_reader, daemon=True).start()
    yield


app = FastAPI(title="MedGuard AI", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class CheckReq(BaseModel):
    uid: str
    drug: str
    dose_mg: float | None = None
    times_per_day: int | None = None


class DecisionReq(BaseModel):
    uid: str
    drug: str
    action: str  # accept | override | change
    reason: str = ""
    alerts: list = []


@app.get("/health")
def health():
    return {"status": "ok", "patients": len(kb.patients), "drugs": len(kb.drugs),
            "interactions": len(kb.interactions)}


@app.get("/last_tap")
def last_tap():
    return tap


@app.get("/patients")
def patients():
    return [{"uid": p["card_uid"], "name": p["name"]} for p in kb.patients.values()]


@app.get("/patient/{uid}")
def patient(uid: str):
    p = kb.patients.get(uid.strip().upper())
    if not p:
        raise HTTPException(404, "Unknown card. Not registered to any patient.")
    return p


@app.get("/drugs")
def drugs():
    return kb.all_names()


@app.post("/check")
def check(req: CheckReq):
    p = kb.patients.get(req.uid.strip().upper())
    if not p:
        raise HTTPException(404, "Unknown patient card.")
    result = run_checks(kb, p, req.drug, req.dose_mg, req.times_per_day)
    for a in result["alerts"]:
        e = explain(a, p)
        a["explanation"], a["explanation_source"] = e["text"], e["source"]
    return result


@app.post("/decision")
def decision(req: DecisionReq):
    con = db()
    con.execute("INSERT INTO decisions (ts, uid, drug, action, reason, alerts_json) VALUES (?,?,?,?,?,?)",
                (time.strftime("%Y-%m-%d %H:%M:%S"), req.uid, req.drug, req.action, req.reason,
                 json.dumps(req.alerts)))
    con.commit()
    con.close()
    return {"saved": True}


@app.get("/decisions")
def decisions():
    con = db()
    rows = con.execute("SELECT ts, uid, drug, action, reason FROM decisions ORDER BY id DESC LIMIT 50").fetchall()
    con.close()
    return [dict(zip(["ts", "uid", "drug", "action", "reason"], r)) for r in rows]
