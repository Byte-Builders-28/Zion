
"""Parameter fuzzing attack scenario.

This project currently scores requests using path-level endpoints (query string
isn't a first-class feature). To simulate "parameter fuzzing" in a way Zion can
detect, this script repeatedly probes a *small* set of path-variant endpoints
at high rate (moderate endpoint variety + high RPS).

Designed to be detected as `param_fuzzing` by the rule layer in
`backend/ml/detector.py`.

Usage (from repo root):
  py backend/attack/scenarios/param_fuzzing.py
  py backend/attack/scenarios/param_fuzzing.py --base http://127.0.0.1:8000 --requests 400
"""

from __future__ import annotations

import argparse
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests


def _mutation_paths(count: int) -> list[str]:
	# Keep variety moderate (8-20) to avoid looking like endpoint scraping.
	# These will often 404, which is fine: interceptor still logs + scores them.
	base = "/test"
	paths = []
	for i in range(count):
		# Keep the *path* stable so endpoint_variety stays moderate.
		# We'll vary the fuzzed values in the query string instead.
		# Example: /test/fuzz/p7?v=123&mode=abc
		paths.append(f"{base}/fuzz/p{i}")
	return paths


def run(
	base: str,
	total_requests: int,
	mutations: int,
	concurrency: int,
	spoofed_ip: str,
	timeout_s: float,
) -> None:
	base = base.rstrip("/")
	templates = _mutation_paths(mutations)

	headers = {
		"X-Forwarded-For": spoofed_ip,
		"User-Agent": "zion-sim/param-fuzzing",
	}

	def _one(session: requests.Session) -> int:
		template = random.choice(templates)
		# Vary "params" aggressively but keep endpoint path stable.
		value = random.randint(0, 10**9)
		mode = random.randint(0, 9999)
		url = f"{base}{template}?v={value}&mode={mode}"
		try:
			r = session.get(url, headers=headers, timeout=timeout_s)
			return r.status_code
		except Exception:
			return 0

	started = time.time()
	status_counts: dict[int, int] = {}

	with requests.Session() as session:
		with ThreadPoolExecutor(max_workers=max(1, concurrency)) as pool:
			futures = [pool.submit(_one, session) for _ in range(total_requests)]
			for f in as_completed(futures):
				code = f.result()
				status_counts[code] = status_counts.get(code, 0) + 1

	elapsed = time.time() - started
	print(
		f"[param_fuzzing] sent={total_requests} mutations={mutations} "
		f"ip={spoofed_ip} elapsed={elapsed:.2f}s status_counts={status_counts}"
	)


def main() -> None:
	p = argparse.ArgumentParser(description="Zion parameter fuzzing attack scenario")
	p.add_argument("--base", default="http://127.0.0.1:8000", help="Backend base URL")
	p.add_argument("--requests", type=int, default=350, help="Total requests to send")
	p.add_argument("--mutations", type=int, default=12, help="How many unique probe paths to cycle")
	p.add_argument("--concurrency", type=int, default=24, help="Worker threads")
	p.add_argument("--ip", default="198.51.100.20", help="Spoofed client IP via X-Forwarded-For")
	p.add_argument("--timeout", type=float, default=2.5, help="Per-request timeout (seconds)")
	args = p.parse_args()

	# Clamp mutations into the classifier's intended band.
	mutations = int(args.mutations)
	if mutations < 8:
		mutations = 8
	if mutations > 18:
		mutations = 18

	run(
		base=args.base,
		total_requests=max(1, int(args.requests)),
		mutations=mutations,
		concurrency=max(1, int(args.concurrency)),
		spoofed_ip=str(args.ip),
		timeout_s=max(0.5, float(args.timeout)),
	)


if __name__ == "__main__":
	main()

