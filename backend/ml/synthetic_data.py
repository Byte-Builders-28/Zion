import numpy as np
import pandas as pd
import random, time

def generate_normal(n=500):
    """Normal user behaviour — low freq, consistent, valid"""
    rows = []
    for _ in range(n):
        rows.append({
            "requests_per_min":  random.randint(1, 15),
            "unique_ips":          random.randint(1, 2),
            "failed_logins":       random.randint(0, 2),
            "payload_size_bytes":  random.randint(100, 800),
            "token_reuse_count":   random.randint(0, 1),
            "endpoint_variety":    random.randint(1, 5),
            "hour_of_day":         random.randint(8, 22),
            "label": 0   # 0 = normal 
        })
    return pd.DataFrame(rows)

def generate_attack(n=100):
    """Attack patterns — high freq, many IPs, token abuse"""
    rows = []
    for _ in range(n):
        attack_type = random.choice([
            "rate_flood", "token_replay", "credential_stuff", "scrape"
        ])
        if attack_type == "rate_flood":
            row = {
                "requests_per_min":  random.randint(200, 600),
                "unique_ips":          random.randint(1, 3),
                "failed_logins":       random.randint(0, 5),
                "payload_size_bytes":  random.randint(50, 200),
                "token_reuse_count":   random.randint(0, 2),
                "endpoint_variety":    random.randint(1, 2),
                "hour_of_day":         random.randint(0, 23),
            }
        elif attack_type == "token_replay":
            row = {
                "requests_per_min":  random.randint(5, 30),
                "unique_ips":          random.randint(8, 25),
                "failed_logins":       random.randint(0, 3),
                "payload_size_bytes":  random.randint(100, 400),
                "token_reuse_count":   random.randint(15, 50),
                "endpoint_variety":    random.randint(1, 3),
                "hour_of_day":         random.randint(0, 23),
            }
        elif attack_type == "credential_stuff":
            row = {
                "requests_per_min":  random.randint(20, 80),
                "unique_ips":          random.randint(3, 10),
                "failed_logins":       random.randint(15, 50),
                "payload_size_bytes":  random.randint(100, 300),
                "token_reuse_count":   random.randint(0, 5),
                "endpoint_variety":    random.randint(1, 2),
                "hour_of_day":         random.randint(0, 23),
            }
        else:  # scrape
            row = {
                "requests_per_min":  random.randint(30, 100),
                "unique_ips":          random.randint(1, 3),
                "failed_logins":       random.randint(0, 1),
                "payload_size_bytes":  random.randint(50, 150),
                "token_reuse_count":   random.randint(0, 2),
                "endpoint_variety":    random.randint(20, 80),
                "hour_of_day":         random.randint(0, 23),
            }
        row["label"] = 1
        rows.append(row)
    return pd.DataFrame(rows)

if __name__ == "__main__":
    normal = generate_normal(500)
    attack = generate_attack(100)
    df = pd.concat([normal, attack], ignore_index=True)
    
    import os
    os.makedirs("data", exist_ok=True)
    
    df.to_csv("data/synthetic_traffic.csv", index=False)
    print(f"Generated {len(df)} rows — {len(normal)} normal, {len(attack)} attack")
