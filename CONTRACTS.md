# Zion API & Machine Learning Inter-module Contracts

## Request Dictionary Shape
The middleware MUST send the request dictionary to the ML pipeline (`score_request`) in exactly this shape.

```json
{
  "ip": "string (IPv4 or IPv6 address)",
  "endpoint": "string (path of the request, e.g. /login)",
  "method": "string (HTTP method, e.g. POST)",
  "token": "string (extracted from Authorization Bearer header, empty if none)",
  "payload_size": "integer (value from content-length header, 0 if missing)",
  "status_code": "integer (HTTP response status code, e.g. 401)",
  "timestamp": "float (unix epoch time)"
}
```

## Score Result Shape
The ML module (`score_request()`) will return the following structure to the middleware:

```json
{
  "risk_score": "float (0.0 to 1.0, where >0.75 is typically a threat)",
  "threat_type": "string (e.g. 'token_replay', 'rate_flood', 'anomaly', 'normal')",
  "features": "dict (the underlying numeric features extracted)",
  "flag": "boolean (True if risk_score > threshold)"
}
```
