import time

blocked_ips = set()
rate_limited_ips = {}
revoked_tokens = set()


def execute_action(action: str, context: dict) -> dict:
    ip = context.get("ip")
    token = context.get("token")
    endpoint = context.get("endpoint", "/")
    risk = context.get("risk", 0.0)

    if action == "block":
        blocked_ips.add(ip)
        print(f"[Executor] BLOCKED IP: {ip}")
        return {"executed": "block_ip", "ip": ip}

    elif action == "rate_limit":
        limit = 10 if risk > 0.8 else 20
        rate_limited_ips[ip] = {
            "limit": limit,
            "window": 60,
            "endpoint": endpoint,
            "since": time.time()
        }
        print(f"[Executor] RATE LIMITED IP: {ip} → {limit} req/min")
        return {"executed": "rate_limit", "ip": ip, "limit": limit}

    elif action == "invalidate_token":
        if token:
            revoked_tokens.add(token)
            print(f"[Executor] REVOKED TOKEN: {token[:16]}...")
        return {"executed": "invalidate_token"}

    else:
        print(f"[Executor] MONITORING IP: {ip}")
        return {"executed": "monitor", "ip": ip}


def is_blocked(ip: str) -> bool:
    return ip in blocked_ips


def is_rate_limited(ip: str) -> bool:
    if ip not in rate_limited_ips:
        return False
    entry = rate_limited_ips[ip]
    if time.time() - entry["since"] > entry["window"]:
        del rate_limited_ips[ip]
        return False
    return True


def is_token_revoked(token: str) -> bool:
    return token in revoked_tokens


def get_enforcement_state() -> dict:
    return {
        "blocked_ips": list(blocked_ips),
        "rate_limited_ips": {
            k: v for k, v in rate_limited_ips.items()
        },
        "revoked_tokens_count": len(revoked_tokens)
    }