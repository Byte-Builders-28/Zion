import requests
import json

def main():
    resp = requests.get("http://127.0.0.1:8000/dashboard/raw_logs")
    logs = resp.json()
    if isinstance(logs, dict) and logs.get("msg") == "no data":
        print("No logs yet")
        return
        
    print(f"Total logs: {len(logs)}")
    for log in logs[-5:]:
        score = log.get("score_result", {})
        print(f"[{log['method']} {log['endpoint']}] IP: {log['ip']} | Risk: {score.get('risk_score')} | Raw: {score.get('raw_score')} | Min: {score.get('mn')} | Max: {score.get('mx')} | Type: {score.get('threat_type')} | Flag: {score.get('flag')}")

if __name__ == "__main__":
    main()