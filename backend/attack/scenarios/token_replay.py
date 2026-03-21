"""
Token Replay Attack Scenario

This script simulates an attacker reusing a stolen or leaked authentication token 
across multiple different IP addresses (e.g., through a proxy network or botnet) 
to access protected resources.

Zion's Defense Mechanism:
1. Feature Extraction: Zion tracks the `token_reuse_count` and `unique_ips` using the same token in a rolling window.
2. Anomaly Detection (Isolation Forest & Rule system): When `token_reuse >= 5` and `unique_ips >= 3` within the short correlation window, the ML model classifies it strongly as a "token_replay" attack.
3. Policy Enforcement: Smolify/Zion issues an "invalidate_token" action. 
4. Interceptor: The backend's Executor drops the token into a `revoked_tokens` cache. Any subsequent request with that specific token gets a 401 Unauthorized instantly, regardless of what IP they use.
"""

import asyncio
import random
import aiohttp

STOLEN_TOKEN = "eyJhbGc.super.secret.stolen.token.999"

# Tracking stats
total_requests = 0
success_requests = 0
failed_requests = 0
revoked_requests = 0

stop = False

def generate_fake_ip():
    return f"10.0.{random.randint(0, 255)}.{random.randint(1, 254)}"

async def botnet_worker(session, url, bot_id):
    global total_requests, success_requests, failed_requests, revoked_requests, stop
    
    while not stop:
        # Simulate different bots in the botnet using the same exact token
        headers = {
            "Authorization": f"Bearer {STOLEN_TOKEN}",
            "X-Forwarded-For": generate_fake_ip()
        }
        
        try:
            async with session.get(url, headers=headers, timeout=2.0) as resp:
                total_requests += 1
                if resp.status == 401:
                    # Target has successfully identified the token replay and revoked the token
                    revoked_requests += 1
                elif resp.status < 400:
                    success_requests += 1
                else:
                    failed_requests += 1
        except Exception:
            total_requests += 1
            failed_requests += 1

        # Think time for the individual bot
        await asyncio.sleep(random.uniform(0.1, 0.5))

async def metrics_printer():
    global total_requests, success_requests, failed_requests, revoked_requests, stop
    
    prev_total = 0
    
    while not stop:
        await asyncio.sleep(1)
        
        current = total_requests
        rps = current - prev_total
        prev_total = current
        
        print(f"[Stats] RPS: {rps:3} | Total: {current:4} | Success(200): {success_requests:4} | Blocked/Revoked(401): {revoked_requests:4}")

async def run_simulation(url, workers=20, duration=15):
    global stop
    
    connector = aiohttp.TCPConnector(limit=0)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        
        for i in range(workers):
            tasks.append(asyncio.create_task(botnet_worker(session, url, i)))
            
        tasks.append(asyncio.create_task(metrics_printer()))
        
        print("=========================================================================")
        print(f" [!] Initiating Token Replay Attack")
        print(f" [!] Stolen Token : {STOLEN_TOKEN}")
        print(f" [!] Workers      : {workers} spoofed IP attackers")
        print("=========================================================================")
        
        await asyncio.sleep(duration)
        stop = True
        await asyncio.gather(*tasks, return_exceptions=True)
        
    print("[Attack Scenario Finished]")

if __name__ == "__main__":
    url = "http://localhost:8000/test"
    asyncio.run(run_simulation(url, workers=40, duration=25))
