from collections import defaultdict
import time

# In-memory sliding window — tracks recent requests per IP
request_window = defaultdict(list)   # ip → [timestamps]
token_ip_map   = defaultdict(set)    # token → set of IPs
failed_logins  = defaultdict(int)    # ip → count
endpoint_hits  = defaultdict(set)    # ip → set of endpoints

FEATURES = [
    "requests_per_min",
    "unique_ips",
    "failed_logins",
    "payload_size_bytes",
    "token_reuse_count",
    "endpoint_variety",
    "hour_of_day",
]

def extract(request: dict) -> list[float]:
    """
    request = {
        "ip": "103.45.21.9",
        "endpoint": "/login",
        "method": "POST",
        "token": "eyJhb...",
        "payload_size": 240,
        "status_code": 401,
        "timestamp": 1710234567.0
    }
    returns: [req_per_min, unique_ips, failed, payload, token_reuse, variety, hour]
    """
    ip       = request.get("ip", "unknown")
    endpoint = request.get("endpoint", "/")
    token    = request.get("token", "")
    payload  = request.get("payload_size", 0)
    status   = request.get("status_code", 200)
    ts       = request.get("timestamp", time.time())

    # Update sliding window (last 60 seconds)
    now = time.time()
    request_window[ip].append(now)
    request_window[ip] = [t for t in request_window[ip] if now - t < 60]

    # Track token reuse across IPs
    if token:
        token_ip_map[token].add(ip)

    # Track failed logins
    if status in (401, 403) and "login" in endpoint:
        failed_logins[ip] += 1

    # Track endpoint variety
    endpoint_hits[ip].add(endpoint)

    return [
        len(request_window[ip]),               # requests_per_min
        len(token_ip_map.get(token, {ip})),     # unique_ips using this token
        failed_logins[ip],                      # failed_logins
        payload,                                # payload_size_bytes
        len(token_ip_map.get(token, set())),    # token_reuse_count
        len(endpoint_hits[ip]),                 # endpoint_variety
        int(time.strftime("%H")),              # hour_of_day
    ]

def reset_state():
    "Call this between demo runs to clear memory"
    request_window.clear()
    token_ip_map.clear()
    failed_logins.clear()
    endpoint_hits.clear()
