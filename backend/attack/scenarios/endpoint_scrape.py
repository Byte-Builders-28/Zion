
"""Endpoint scraping attack scenario.

Sends a burst of requests to many different endpoints to simulate an attacker
enumerating routes. This is designed to be detected as `endpoint_scraping` by
the rule layer in `backend/ml/detector.py`.

Usage (from repo root):
  py backend/attack/scenarios/endpoint_scrape.py
  py backend/attack/scenarios/endpoint_scrape.py --base http://127.0.0.1:8000 --requests 300
"""

from __future__ import annotations

import argparse
import random
import string
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests


def _rand_seg(n: int = 8) -> str:
	return "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(n))


def _build_endpoints(unique: int) -> list[str]:
	# A mix of "real" and intentionally unknown endpoints.
	fixed = [
		"/",
		"/test",
		"/login",
		"/simulate/spam",
		"/anomalies/",
		"/chain/health",
		"/chain/log",
		"/rl/decision",
		"/rl/state",
		"/api/status",
		"/api/v1/users",
		"/api/v1/admin",
	]

	endpoints = list(dict.fromkeys(fixed))

	# Generate many distinct paths to drive endpoint variety.
	while len(endpoints) < unique:
		endpoints.append(f"/api/v1/{_rand_seg(6)}/{_rand_seg(6)}")

	return endpoints[:unique]


def run(
	base: str,
	total_requests: int,
	unique_endpoints: int,
	concurrency: int,
	spoofed_ip: str,
	timeout_s: float,
) -> None:
	base = base.rstrip("/")
	endpoints = _build_endpoints(unique_endpoints)

	headers = {
		"X-Forwarded-For": spoofed_ip,
		"User-Agent": "zion-sim/endpoint-scrape",
	}

	def _one(session: requests.Session, path: str) -> int:
		# Randomize method slightly, but mostly GETs.
		url = f"{base}{path}"
		try:
			r = session.get(url, headers=headers, timeout=timeout_s)
			return r.status_code
		except Exception:
			return 0

	started = time.time()
	status_counts: dict[int, int] = {}

	with requests.Session() as session:
		with ThreadPoolExecutor(max_workers=max(1, concurrency)) as pool:
			futures = []
			for _ in range(total_requests):
				path = random.choice(endpoints)
				futures.append(pool.submit(_one, session, path))

			for f in as_completed(futures):
				code = f.result()
				status_counts[code] = status_counts.get(code, 0) + 1

	elapsed = time.time() - started
	print(
		f"[endpoint_scrape] sent={total_requests} unique_endpoints={unique_endpoints} "
		f"ip={spoofed_ip} elapsed={elapsed:.2f}s status_counts={status_counts}"
	)


def main() -> None:
	p = argparse.ArgumentParser(description="Zion endpoint scraping attack scenario")
	p.add_argument("--base", default="http://127.0.0.1:8000", help="Backend base URL")
	p.add_argument("--requests", type=int, default=250, help="Total requests to send")
	p.add_argument("--unique-endpoints", type=int, default=50, help="Distinct endpoints to probe")
	p.add_argument("--concurrency", type=int, default=16, help="Worker threads")
	p.add_argument("--ip", default="198.51.100.10", help="Spoofed client IP via X-Forwarded-For")
	p.add_argument("--timeout", type=float, default=2.5, help="Per-request timeout (seconds)")
	args = p.parse_args()

	run(
		base=args.base,
		total_requests=max(1, args.requests),
		unique_endpoints=max(5, args.unique_endpoints),
		concurrency=max(1, args.concurrency),
		spoofed_ip=str(args.ip),
		timeout_s=max(0.5, args.timeout),
	)


if __name__ == "__main__":
	main()

