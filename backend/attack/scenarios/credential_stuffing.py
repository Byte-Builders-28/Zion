import requests
import time

# This script simulates a credential stuffing attack locally
# to test the Zion ML detector and Smolify rule engine limiters.
TARGET_URL = "http://127.0.0.1:8000/login"

# A list of dummy credentials.
# This mimics testing common compromised password combinations.
DUMMY_CREDENTIALS = [
    {"user": "admin", "password": "password123"},
    {"user": "admin", "password": "123456"},
    {"user": "admin", "password": "admin"},
    {"user": "root", "password": "root"},
    {"user": "test", "password": "test"},
] + [{"user": f"guest{i}", "password": f"pass{i}"} for i in range(1, 15)]


def run_simulation(url=TARGET_URL):
    print(
        f"[*] Starting local credential stuffing simulation against {TARGET_URL}")
    print(f"[*] Sending {len(DUMMY_CREDENTIALS)} unauthorized attempts...\n")

    success_hits = 0
    fail_hits = 0

    for i, creds in enumerate(DUMMY_CREDENTIALS):
        try:
            # We purposely hit the target with incorrect credentials to trigger 401s
            response = requests.post(url, json=creds, timeout=3)
            status = response.status_code

            if status == 200:
                success_hits += 1
            else:
                fail_hits += 1

            print(
                f"[Attempt {i+1}/{len(DUMMY_CREDENTIALS)}] POST /login ({creds['user']}:***) - Status: {status}")

        except requests.exceptions.RequestException as e:
            print(f"[!] Connection failed: {e}")
            break

        # Small delay to keep the requests flowing rapidly but realistically
        time.sleep(0.1)

    print("\n[*] Simulation complete.")
    print(
        f"[*] Summary: {fail_hits} Failed Logins, {success_hits} Success Logins.")
    print("[*] Please check the Zion backend logs to verify that the 'credential_stuffing' incident was flagged and logged to the blockchain.")


if __name__ == "__main__":
    run_simulation()
