import json
import requests
import os

REQUIRED_KEYS = ["rule_name", "action",
                 "threshold", "severity", "affected_endpoint"]


def _ensure_valid_policy(policy: dict, fallback: dict) -> dict:
    """Return fallback if the API payload is missing required fields."""
    if not isinstance(policy, dict):
        return fallback
    for key in REQUIRED_KEYS:
        if policy.get(key) is None:
            return fallback
    return policy


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

    # Base action depends on risk and threat type
    if threat_type == "token_replay":
        default_action = "invalidate_token"
    elif threat_type == "endpoint_scraping":
        default_action = "block"
    else:
        default_action = "block" if risk_score > 0.8 else "rate_limit"

    # Fake fallback for when API is unreachable
    fallback_response = {
        "rule_name": f"auto_mitigate_{threat_type}",
        "action": default_action,
        "threshold": 100,
        "severity": "high" if risk_score > 0.8 else "medium",
        "affected_endpoint": endpoint
    }

    # HF Inference API for smolify/smolified-zion model
    api_url = os.getenv(
        "HF_API_URL", "https://api-inference.huggingface.co/models/smolify/smolified-zion")
    hf_token = os.getenv("HF_TOKEN", "")

    headers = {"Authorization": f"Bearer {hf_token}"} if hf_token else {}

    try:
        if hf_token:
            response = requests.post(api_url, headers=headers, json={
                                     "inputs": prompt}, timeout=5)
            response.raise_for_status()

            # The API might return a list with generated_text
            res_data = response.json()
            if isinstance(res_data, list) and len(res_data) > 0 and "generated_text" in res_data[0]:
                generated_text = res_data[0]["generated_text"]
                # Try parsing the generated text as JSON
                try:
                    # Sometimes HF models wrap JSON in markdown blocks
                    clean_text = generated_text.replace(
                        "```json", "").replace("```", "").strip()
                    # Find { and } if there's conversational text around it
                    start_idx = clean_text.find('{')
                    end_idx = clean_text.rfind('}') + 1
                    if start_idx != -1 and end_idx != -1:
                        clean_text = clean_text[start_idx:end_idx]

                    policy = json.loads(clean_text)
                    valid_policy = _ensure_valid_policy(
                        policy, fallback_response)
                    from db.store import add_policy
                    add_policy(valid_policy)
                    return valid_policy
                except Exception as e:
                    print(
                        f"[Smolify Warning] Failed to parse JSON from HF model response: {e}")
            else:
                print(f"[Smolify Warning] Unexpected response format from HF API.")
        else:
            print("[Smolify Warning] No HF_TOKEN provided, skipping HF API call.")

    except requests.exceptions.Timeout:
        print(
            f"[Smolify Warning] HF API Timeout. Using fallback policy for {threat_type}.")
    except requests.exceptions.ConnectionError:
        print(
            f"[Smolify Warning] HF API Unreachable. Using fallback policy for {threat_type}.")
    except Exception as e:
        print(f"[Smolify Error] Unexpected error during HF call: {e}")

    # Fallback path if HF call fails or no token
    from db.store import add_policy
    add_policy(fallback_response)

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

