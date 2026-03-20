import requests, time

BASE = "http://localhost:8000"

print("[1] Sending attack request to /api/analyze...")
resp = requests.post(f"{BASE}/api/analyze", json={
    "ip": "103.45.21.9",
    "endpoint": "/login",
    "method": "POST",
    "token": "STOLEN_JWT_xyz987",
    "payload_size": 80,
    "status_code": 401,
})
if resp.status_code != 200:
    print("[1] /api/analyze returned", resp.status_code, resp.text)
else:
    result = resp.json()
    print(f"    Risk score:  {result.get('risk_score')}")
    print(f"    Threat type: {result.get('threat_type')}")
    print(f"    Flagged:     {result.get('flag')}")

print("\n[2] Waiting 7s for Algorand confirmation...")
time.sleep(7)

print("[3] Fetching /api/chain...")
chain = requests.get(f"{BASE}/api/chain").json()

if chain:
    latest = chain[0]
    print(f"\n    Incident:    {latest['incident_id']}")
    print(f"    TX ID:       {latest['tx_id']}")
    print(f"    Explorer:    {latest['explorer_url']}")
    print(f"    Type:        {latest['threat_type']}")
    print("\n    Open the explorer link to verify on-chain")
else:
    print("    No chain records yet — check Algorand thread in server logs")
