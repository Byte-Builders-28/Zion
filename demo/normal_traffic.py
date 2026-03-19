import requests
import random
import time

URL = "http://127.0.0.1:8000/test"

def run_normal():
    print("[*] Sending normal traffic to backend (Low Frequency, Clean Payloads)...")
    for i in range(100):
        try:
            val = random.randint(1000, 9999)
            resp = requests.post(URL + f"?id={val}", json={"user": f"guest_{val}", "data": "clean"}, timeout=5)
            # print(f"[+] Normal request {i+1}/100: status {resp.status_code}")
        except Exception as e:
            pass
            # print(f"[!] Error: {e}")
        time.sleep(0.05) # Realistic low frequency

    print("\n[*] Normal traffic simulation complete.")

if __name__ == "__main__":
    run_normal()
