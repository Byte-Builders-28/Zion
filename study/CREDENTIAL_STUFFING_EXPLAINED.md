# Credential Stuffing Simulation

## What is Credential Stuffing?
Credential stuffing is an automated cyberattack where malicious actors use lists of compromised user credentials (usernames and passwords) acquired from a data breach on one service, and attempt to use them to gain unauthorized access to an entirely different service. This attack vector relies on the common human behavior of reusing the same passwords and emails across multiple platforms.

## How the Simulation Works
The script located at `backend/attack/scenarios/credential_stuffing.py` mimics a live credential stuffing campaign specifically designed to validate the **Zion Pipeline's** defensive mechanics. 

It accomplishes this by:
1. Iterating through a generated list of commonly utilized dummy credentials (e.g., `admin/123456`, `guest1/pass1`).
2. Rapidly sending HTTP POST requests to the local environment's authentication endpoint (`http://127.0.0.1:8000/login`).
3. Collecting consecutive authentication failures (HTTP status `401 Unauthorized` or `403 Forbidden`) originating from the local IP.

## Defensive Tracking (How Zion Catches It)
Zion doesn't just look for bad passwords; it relies on high-velocity state metrics extracted by the middleware and Isolation Forest Machine Learning model. Specifically, it watches:
- `failed_logins`: The sliding-window count of unauthorized attempts hitting a `/login` URL path.
- `requests_per_min`: The raw volume of requests sent by the client.

Once `failed_logins` bypasses the defined threshold (e.g., `>= 6` failures within a brief time-frame combined with an elevated request speed), the ML Detector immediately transitions the Threat Type from unflagged `anomaly` to critical `credential_stuffing`. 

After being flagged, Zion will instantly:
1. Send the incident metadata to **Smolify** to generate a defensive rule (e.g., IP Drop / Rate Limiting).
2. Document the exact sequence on the immutable **Algorand Blockchain** for audit recording.

> **Disclaimer**: This script and explanation are strictly for auditing, educational evaluation, and strengthening your internal Zero-Trust Zion framework. It only points to local testing environments.
