import json
import requests
import os

def generate_policy(threat_report: dict) -> dict:
    """
    Calls the Smallify AI API with a structured prompt.
    Input: threat_report containing threat_type, endpoint, ip, risk_score
    Output: JSON with rule_name, action, threshold, severity, affected_endpoint
    """
    threat_type = threat_report.get("threat_type", "unknown")
    endpoint = threat_report.get("endpoint", "/")
    ip = threat_report.get("ip", "unknown")
    risk_score = threat_report.get("risk_score", 0.0)

    prompt = f"""
    Given the following security threat report:
    Threat Type: {threat_type}
    Endpoint: {endpoint}
    IP: {ip}
    Risk Score: {risk_score}
    
    Generate a mitigation policy in strictly valid JSON format with the following keys:
    - rule_name
    - action (e.g., "block", "rate_limit", "challenge")
    - threshold (a numeric limit if applicable, else 0)
    - severity (e.g., "high", "medium", "low")
    - affected_endpoint
    """
    
    # Fake fallback for when API is unreachable
    fallback_response = {
        "rule_name": f"auto_mitigate_{threat_type}",
        "action": "block" if risk_score > 0.8 else "rate_limit",
        "threshold": 100,
        "severity": "high" if risk_score > 0.8 else "medium",
        "affected_endpoint": endpoint
    }
    
    # We will try a dummy/mock URL or return the fallback if we don't know the exact endpoint.
    # Replace this with the actual Smallify AI API endpoint.
    api_url = os.getenv("SMALLIFY_API_URL", "http://localhost:8000/api/generate_policy")
    
    try:
        response = requests.post(api_url, json={"prompt": prompt}, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        print(f"[Smolify Warning] API Timeout. Using fallback policy for {threat_type}.")
    except requests.exceptions.ConnectionError:
        print(f"[Smolify Warning] API Unreachable. Using fallback policy for {threat_type}.")
    except json.JSONDecodeError:
        print(f"[Smolify Error] Invalid JSON received from API. Using fallback.")
    except Exception as e:
        print(f"[Smolify Error] Unexpected error: {e}")
        
    return fallback_response

if __name__ == "__main__":
    fake_report = {
        "threat_type": "rate_flood",
        "endpoint": "/login",
        "ip": "192.168.1.100",
        "risk_score": 0.95
    }
    policy = generate_policy(fake_report)
    print("Generated Policy:", json.dumps(policy, indent=2))
