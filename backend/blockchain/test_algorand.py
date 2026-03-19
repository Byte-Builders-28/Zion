from algorand_logger import log_incident

result = log_incident({
    "id": "SG-TEST-001",
    "type": "token_replay",
    "endpoint": "/login",
    "ip": "103.45.21.9",
    "risk": 0.96,
    "policy": "token_revoked+ip_blocked",
})

print(f"\nTX ID:   {result['tx_id']}")
print(f"Link:    {result['explorer_url']}")
print("\nOpen the link - you should see the TX with full incident JSON in the note field")
