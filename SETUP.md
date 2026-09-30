# MedGuard AI: Setup Guide (Antigravity + GitHub)

Follow the parts in order. Each step has a **CHECK** so you know it worked before moving on.
Windows commands are shown (PowerShell). Mac/Linux differences are noted.

---

## PART 0: Install these once

| Tool | Get it from | CHECK (run in terminal) |
|---|---|---|
| Git | git-scm.com | `git --version` |
| Python 3.11+ | python.org (tick "Add to PATH") | `python --version` |
| Node.js LTS | nodejs.org | `node --version` and `npm --version` |
| Arduino IDE 2.x | arduino.cc | opens without error |
| Antigravity | Google's download page | opens, you can sign in |

One-time Git identity:
```
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

---

## PART 1: GitHub repo and Antigravity

1. On github.com: **New repository** → name `medguard-ai` → Private (switch to Public later if the hackathon needs it) → **do NOT tick README/.gitignore** → Create.
2. Copy the repo URL (`https://github.com/<you>/medguard-ai.git`).
3. Make a folder for your projects, for example `D:\projects`. Open a terminal there and run:
   ```
   git clone https://github.com/<you>/medguard-ai.git
   ```
   (An empty-repo warning is normal.)
4. Open **Antigravity → File → Open Folder** and choose the cloned `medguard-ai` folder.
5. Unzip `medguard-ai.zip` (the file I gave you). **Copy the CONTENTS of the unzipped folder** (`backend`, `frontend`, `firmware`, `docs`, `README.md`, `SETUP.md`, `.gitignore`) into your cloned `medguard-ai` folder. Do not nest a second `medguard-ai` folder inside.
6. Open the terminal inside Antigravity (View → Terminal, or Ctrl + `). Then:
   ```
   git add .
   git commit -m "Initial scaffold: backend, frontend, firmware"
   git branch -M main
   git push -u origin main
   ```
   A browser window may ask you to sign in to GitHub. Do it.

**CHECK:** refresh the GitHub repo page. You should see the folders. `.env` must NOT appear (it's in `.gitignore`).

---

## PART 2: Backend (Python)

Run all of this from the Antigravity terminal.

1. Go to the backend folder and create a virtual environment:
   ```
   cd backend
   python -m venv venv
   venv\Scripts\activate
   ```
   Mac/Linux: `source venv/bin/activate`
   If PowerShell blocks activation: run `Set-ExecutionPolicy -Scope Process Bypass` and try again.
   **CHECK:** the prompt now starts with `(venv)`.
2. Install packages:
   ```
   pip install -r requirements.txt
   ```
3. Run the tests:
   ```
   pytest
   ```
   **CHECK:** `7 passed`. If not, paste the error to the Antigravity agent or to me.
4. Create your settings file:
   ```
   copy .env.example .env
   ```
   (Mac/Linux: `cp .env.example .env`). Leave it as is for now.
5. Start the server:
   ```
   uvicorn app.main:app
   ```
   Do NOT add `--reload` (it can clash with the serial port later).
6. Open **http://localhost:8000/docs** in a browser. This page lets you test every endpoint.
   **CHECK:** open http://localhost:8000/health and see `{"status":"ok","patients":4,...}`.
7. Leave this terminal running. Open a **new terminal tab** for the next parts.

---

## PART 3: Frontend (React)

In the new terminal tab:
```
cd frontend
npm install
npm run dev
```
Open the URL it prints (usually **http://localhost:5173**).

**CHECK:** you see "MedGuard AI". Use the **Simulate tap** dropdown, choose "Suresh Reddy", type `Crocin`, dose `650`, times `4`, click **Check safety**. You should see a duplicate-therapy alert and a dose alert.

If it says "Cannot reach backend": the backend terminal from Part 2 is not running.

### The 4 demo scenarios (already in `patients.csv`)

| Patient | Type this | Expected alert |
|---|---|---|
| Ramesh Kumar | `Ecosprin`, 75, 1 | Warfarin + aspirin, major |
| Lakshmi Devi | `Brufen`, 400, 3 | NSAID in CKD, plus ACE inhibitor + NSAID |
| Suresh Reddy | `Crocin`, 650, 4 | Duplicate (already on Dolo 650) plus dose too high |
| Anita Sharma | `Amoxicillin`, 500, 3 | Penicillin allergy, contraindicated |

Commit your progress now:
```
git add .
git commit -m "Working software demo with simulated taps"
git push
```

---

## PART 4: Hardware (ESP32 + RC522)

1. **Wire it** (power OFF / unplugged while wiring; RC522 uses **3.3V only**):

   | RC522 | ESP32 |
   |---|---|
   | SDA | GPIO 5 |
   | SCK | GPIO 18 |
   | MOSI | GPIO 23 |
   | MISO | GPIO 19 |
   | RST | GPIO 22 |
   | 3.3V | 3V3 |
   | GND | GND |
   | IRQ | not connected |

2. **Arduino IDE setup (first time only):**
   - File → Preferences → "Additional boards manager URLs": add `https://espressif.github.io/arduino-esp32/package_esp32_index.json`
   - Tools → Board → Boards Manager → search **esp32** (by Espressif) → Install.
   - Sketch → Include Library → Manage Libraries → search **MFRC522** (by GithubCommunity) → Install.
3. Open `firmware/rfid_reader/rfid_reader.ino` in Arduino IDE. Tools → Board → **ESP32 Dev Module**. Tools → Port → choose your ESP32's port. Click **Upload**.
   If upload hangs at "Connecting...", hold the **BOOT** button on the ESP32 until it starts.
4. Tools → Serial Monitor → set **115200 baud**. Tap a card.
   **CHECK:** you see `UID:A3F19C2B` (your own value).
5. Tap **each card once** and write the UIDs down.
6. In Antigravity open `backend/data/patients.csv`. Replace `UID_PATIENT_A`, `_B`, `_C`, `_D` with the four real UIDs (uppercase, no spaces). Save.
7. **Close the Arduino Serial Monitor** (only one program can use the port).
8. Find your port name: Windows Device Manager → Ports (COM & LPT) → for example `COM3`. Mac/Linux: `ls /dev/tty.*` or `/dev/ttyUSB*`.
9. Open `backend/.env` and set `SERIAL_PORT=COM3` (your port).
10. Stop the backend (Ctrl+C in its terminal) and start it again: `uvicorn app.main:app`.
    **CHECK:** the terminal prints `Serial connected on COM3`. Tap a card: it prints `Tap: <UID>` and the web page loads that patient automatically.

If nothing reads: re-check wiring (SDA vs SS, 3.3V), and make sure the USB cable carries data.
**Always keep the Simulate tap dropdown as your backup for the demo.**

Commit:
```
git add .
git commit -m "Hardware integrated: real card UIDs"
git push
```
(Card UIDs are not sensitive, but keep `.env` out of Git.)

---

## PART 5: Gemini explanations (optional, do last)

1. Go to aistudio.google.com → Get API key → create a key.
2. Open `backend/.env` and set `GEMINI_API_KEY=your_key`.
3. Restart the backend.
4. Run a check in the UI, click "Why? Show details". It should say "Explanation written by: AI (wording only)".
   If it says "fixed template", the key or model name is wrong. Check the current model name in AI Studio and set `GEMINI_MODEL=` in `.env`. The template fallback means the app never breaks.

---

## PART 6: Making the data real (most important for judges)

Everything lives in `backend/data/`. Edit in Excel/Google Sheets and save as CSV (UTF-8):

| File | What to add |
|---|---|
| `drugs.csv` | generic name, drug class, Indian brand names (`;` separated), max daily dose in mg |
| `interactions.csv` | drug_a, drug_b (generic OR class name), severity, mechanism, recommendation, alternative, source |
| `drug_disease.csv` | drug or class, condition (lowercase_with_underscores), severity, reason, recommendation, alternative, source |
| `patients.csv` | your synthetic patients; meds as `generic:dose_mg:times_per_day:Brand` separated by `;` |

Rules:
- Severity must be one of: `contraindicated`, `major`, `moderate`, `minor`.
- Use class names (for example `nsaid`, `ace_inhibitor`) to cover many drugs with one row.
- Every row needs a real `source`. Remove `(VERIFY)` only after you have checked the row against DDInter or the openFDA label.
- Target 80 to 100 interaction rows. Do not use AI-generated rows without checking.
- After editing, restart the backend and run `pytest`.

---

## PART 7: Final checklist

- [ ] `pytest` passes
- [ ] All 4 demo scenarios work with real taps AND with the simulator
- [ ] Backup screen recording of a full run
- [ ] `.env` not on GitHub
- [ ] README updated, slides match what you built (delete guidelines slide, fill team slide)
- [ ] You can answer: "Why is the LLM only used for wording?" "Where does your data come from?" "What if the AI is wrong?"

## Troubleshooting quick table

| Problem | Fix |
|---|---|
| `python` not found | Reinstall Python with "Add to PATH" ticked, reopen terminal |
| `pip install` fails | Make sure `(venv)` is active |
| Port 8000 busy | `uvicorn app.main:app --port 8001` and set `VITE_API=http://localhost:8001` before `npm run dev` |
| UI says "Cannot reach backend" | Backend terminal not running |
| Card taps do nothing | Serial Monitor still open, wrong `SERIAL_PORT`, or UID not in `patients.csv` |
| "Unknown card" in UI | UID in `patients.csv` doesn't match (uppercase, no spaces) |
| Git push rejected | `git pull --rebase origin main` then `git push` |

## Using the Antigravity agent

It's fine to ask the agent for help, but give it a precise job, for example: "Read backend/app/rules.py and add a check for patients over 65 with drug X. Keep the rules in Python with no LLM, and add a pytest test." Always run `pytest` after it changes rules. Never let it invent rows in the CSV files.
