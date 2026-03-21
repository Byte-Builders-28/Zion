# Zion Threat Types

This document explains the threat labels produced by the Zion backend, and when/why each label is used.

Zion combines an Isolation Forest anomaly model with rule-based logic on top of request features:

- `requests_per_min`: recent requests from the same IP in the last ~60s
- `unique_ips`: how many different IPs are using the same token
- `failed_logins`: recent failed login attempts from the same IP (time-windowed)
- `payload_size_bytes`: request body size
- `token_reuse_count`: how often a token is seen across IPs
- `endpoint_variety`: how many distinct endpoints this IP is hitting
- `hour_of_day`: coarse time context

The model produces a continuous `risk_score` in [0, 1] (0 = normal, 1 = critical), and the rules map patterns to human-readable threat types.

---

## anomaly

**What it means**
- A generic anomalous or out-of-distribution request that does not cleanly match a specific attack pattern.

**When it is used**
- The model sees some deviation from the original training distribution, but:
  - Request volume is low (e.g., a handful of requests per minute), and
  - There are no failed logins, no token reuse, and low endpoint variety.
- Typical examples:
  - A single user hits `/` or `/test` once or a few times.
  - A new, previously unseen endpoint is accessed occasionally.

**How it is treated**
- If overall risk is low, it is not flagged.
- For clearly benign, low-volume traffic, risk is explicitly capped to remain low so that casual browsing does not look like a critical incident.

---

## credential_stuffing

**What it means**
- Automated attempts to guess valid credentials by replaying many username/password combinations, usually against a login endpoint.

**When it is used**
- Recent failed login attempts for an IP are high, and
- Overall request rate from that IP is elevated.

Concretely (approximate rules):
- `failed_logins` is high in the last few minutes, and
- `requests_per_min` is also above a modest threshold.

**Typical examples**
- Bots cycling through credential lists on `/login`.
- Brute-force attacks using leaked user/password pairs.

---

## rate_flood

**What it means**
- A high-volume burst of requests from a single IP, overwhelming an endpoint or the service.

**When it is used**
- `requests_per_min` is very high for a single IP in the recent sliding window.

**Typical examples**
- A client or bot repeatedly calling `/test` or another endpoint with minimal think-time.
- DDoS-like behavior from a single source.

---

## token_replay

**What it means**
- A stolen or shared token is being reused across many requests and/or many different IPs.

**When it is used**
- `token_reuse_count` is high and
- `unique_ips` using the same token is elevated.

**Typical examples**
- A compromised JWT that appears from multiple IP addresses.
- A shared API key reused broadly from different clients.

---

## endpoint_scraping

**What it means**
- Systematic enumeration or scraping of many different endpoints from the same IP.

**When it is used**
- `endpoint_variety` (distinct endpoints touched by an IP) is high and
- Request rate is also elevated.

**Typical examples**
- A crawler discovering internal APIs by walking many routes.
- Attackers fuzzing URL paths or parameters to map the attack surface.

---

## distributed_attack

**What it means**
- Potentially coordinated activity across many IPs, often sharing credentials or tokens.

**When it is used**
- `unique_ips` is large for a given token or pattern, suggesting fan-out across many sources.

**Typical examples**
- A token or key used from many different IPs (botnet-style behavior).
- Coordinated scanning from a wide range of addresses.

---

## Operational Notes

- Only requests with sufficiently high `risk_score` are **flagged** and forwarded to the blockchain logging pipeline.
- Documentation endpoints like `/docs`, `/openapi.json`, and `/redoc` are treated as safe and are not scored as high-risk threats.
- Low-volume, clean traffic to generic endpoints (such as `/`) is intentionally kept at low risk and typically labeled as `anomaly` or ignored, to avoid false positives while still allowing the model to surface unusual high-risk patterns.
