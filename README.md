
# Zion

Zion is a local-first cyber defense demo that combines:

- **FastAPI** request interception + enforcement gates
- **ML anomaly scoring** (Isolation Forest) with a deterministic rules layer for **human-readable threat types**
- A **policy engine** (Smolify/HuggingFace optional) that turns detections into mitigation actions
- Optional **incident logging to Algorand TestNet** and **storage via Appwrite**

This repo includes a React/Vite dashboard for real-time visibility and several attack simulation scripts (token replay, credential stuffing, DDoS-style floods).

---

## Features

- **Threat typing (distinct categories)**: `ddos`, `rate_flood`, `token_replay`, `credential_stuffing`, `endpoint_scraping`, `anomaly`
- **Mitigations are not “block IP only”**:
  - DDoS-like traffic → **protect endpoint** (drop traffic with 503)
  - Token replay → **revoke token** (401 thereafter)
  - Rate floods / stuffing / scraping → **rate limit** (429)
- **Real-time logs** via WebSocket stream to the frontend
- **On-chain logging** (Algorand TestNet) for flagged incidents (optional but enabled by default)

---

## Architecture (high-level)

1. **Request enters FastAPI**
2. Middleware `interceptor`:
	- extracts `ip`, `endpoint`, `token`, `status_code`, `payload_size`, `timestamp`
	- runs **enforcement gates** (blocked IP / rate limit / revoked token / protected endpoint)
	- scores requests via `ml.detector.score_request()`
3. `ml.detector`:
	- extracts sliding-window features (`ml.feature_extractor`)
	- computes anomaly `risk_score` via Isolation Forest
	- applies a rules layer → `threat_type`
4. `policy.smolify_client.generate_policy()`:
	- chooses a mitigation action by `threat_type` (HuggingFace optional)
5. `policy.executor.execute_action()`:
	- enforces `block`, `rate_limit`, `invalidate_token`, `protect_endpoint`
6. Optional incident logging:
	- `blockchain.algorand_logger` logs flagged incidents to Algorand TestNet
	- cached records stored via `db.store` (Appwrite)

**Contracts between modules** are documented in [CONTRACTS.md](CONTRACTS.md).

---

## Repo layout

- `backend/` — FastAPI app, ML detector, policy executor, blockchain logging
- `frontend/` — React/Vite UI (dashboard + simulation screens)
- `backend/attack/scenarios/` — attack simulations (async floods, token replay, credential stuffing)
- `demo/` — traffic generators + quick log inspection
- `study/` — threat type explanations

---

## Prerequisites

- **Python 3.10+** (Windows: `py` launcher is fine)
- **Node.js 18+** (recommended) + npm

If you enable on-chain logging and cloud persistence (default behavior), you also need:

- An **Algorand TestNet wallet** (mnemonic + address)
- An **Appwrite** project (TablesDB) and API key

---

## Environment configuration

### 1) Backend `.env`

Zion loads env vars from `backend/.env`.

Create `backend/.env` with the following variables.

#### Algorand (required if blockchain logging is enabled)

```env
ALGO_MNEMONIC="word1 word2 ... word25"
ALGO_ADDRESS="YOUR_ALGORAND_ADDRESS"
```

Generate a new TestNet wallet:

```bash
cd backend
py blockchain/generate_wallet.py --write
```

Important:

- **Never commit** `backend/.env` (it contains your mnemonic)
- Fund the TestNet wallet from a faucet if you want successful TX confirmations

#### Appwrite (required for chain record storage)

```env
APPWRITE_ENDPOINT="https://YOUR_APPWRITE_HOST/v1"
APPWRITE_PROJECT_ID="..."
APPWRITE_API_KEY="..."
APPWRITE_DATABASE_ID="..."
APPWRITE_COLLECTION_ID="..."
```

#### HuggingFace / Smolify policy engine (optional)

If `HF_TOKEN` is **not** set, Zion uses deterministic fallback actions per threat type.

```env
HF_TOKEN="hf_..."
HF_API_URL="https://api-inference.huggingface.co/models/smolify/smolified-zion"
```

---

## Setup

### Backend

From repo root (Windows PowerShell):

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
```

Run the API:

```powershell
cd backend
py main.py release
```

Backend base URL: `http://127.0.0.1:8000`

### Frontend

In a new terminal:

```powershell
cd frontend
npm install
npm run dev
```

Frontend default URL: `http://localhost:5173`

---

## Attack simulations (one by one)

Start the backend first (`cd backend; py main.py release`). Then run any scenario below.

### 1) Token replay

Simulates a stolen token reused across many spoofed IPs.

```powershell
py backend/attack/scenarios/token_replay.py
```

Expected behavior:

- Detection: `token_replay`
- Mitigation: **invalidate token**
- You should see many `401` responses after revocation.

### 2) Credential stuffing

Simulates many failed logins against `/login`.

```powershell
py backend/attack/scenarios/credential_stuffing.py
```

Expected behavior:

- Detection: `credential_stuffing`
- Mitigation: **rate_limit** (429) for the offending IP

### 3) DDoS-style flood / rate abuse

Simulates a multi-worker flood to `/test` using many spoofed IPs.

```powershell
py backend/attack/scenarios/rate_abuse.py
```

Expected behavior:

- Detection: `ddos` (distributed/high fan-in)
- Mitigation: **protect endpoint** (503 drops) instead of “blocking 1 IP”

Notes:

- Some requests can still trigger per-IP rate limiting (429) depending on timing and sliding-window state.
- Endpoint protection is the primary DDoS mitigation in this demo.

---

## Demo helpers

### Normal traffic generator

```powershell
py demo/normal_traffic.py
```

### Basic attack traffic generator

```powershell
py demo/attack_traffic.py
```

### Inspect last logs + scores

```powershell
py demo/check_scores.py
```

---

## API reference (current)

Base: `http://127.0.0.1:8000`

### Health / demo endpoints

- `GET /` → `{ "msg": "Zion API running" }`
- `GET|POST /test` → `{ "msg": "hit" }`
- `POST /login` → always `401` unless password is `correct_password`

### Dashboard / logs

- `GET /dashboard/stats`
  - returns counts: blocked IPs, rate-limited IPs, revoked tokens, protected endpoints, total threats
- `GET /dashboard/raw_logs?limit=200`
  - snapshot recent logs (for scripts/debug)
- `WS /dashboard/logs`
  - live stream of log entries (frontend consumes this)

### Simulation

- `POST /simulate/spam?target=http://127.0.0.1:8000/test`

### Anomalies

- `GET /anomalies/` → basic suspicious IP counts from in-memory logs

### RL

- `POST /rl/start?episodes=10`
- `GET /rl/status`

### Chain (Algorand)

- `POST /chain/analyze` — score an arbitrary request payload; if flagged, logs in background
- `GET /chain/chain?limit=20` — returns cached chain history
- `GET /chain/chain/{tx_id}` — fetch pending transaction info from Algorand node

---

## Threat types (what they mean)

See [study/TYPES OF THREAT.md](study/TYPES%20OF%20THREAT.md) for details.

In short:

- `ddos`: many IPs + elevated short-window volume → protect endpoint
- `rate_flood`: very high rate from one/few IPs → rate limit
- `token_replay`: token reused across IPs → revoke token
- `credential_stuffing`: repeated failed logins → rate limit
- `endpoint_scraping`: high endpoint variety → rate limit
- `anomaly`: doesn’t match a named pattern strongly

---

## Troubleshooting

### Backend won’t start (Algorand/Appwrite errors)

If you see errors about missing `ALGO_MNEMONIC` / `ALGO_ADDRESS`:

- Create `backend/.env` and set the variables
- Or generate a wallet: `py backend/blockchain/generate_wallet.py --write`

If you see Appwrite errors, verify all `APPWRITE_*` variables.

### PowerShell “curl” prompt

PowerShell aliases `curl` to `Invoke-WebRequest` and may prompt about script parsing.
Use either:

- Python: `py -c "import requests; print(requests.get('http://127.0.0.1:8000/dashboard/stats').text)"`
- Or: `Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8000/dashboard/stats`

### pytest failures

Some blockchain tests depend on external services and local credentials; test collection can fail if environment variables are not set.

---

## Security notes

This is a demo system.

- Do not use the included attack scripts against systems you don’t own or have explicit permission to test.
- Do not commit secrets (Algorand mnemonic, Appwrite API key) to Git.

---

## License

See [LICENSE](LICENSE).

