"""Helper script to print Algorand wallet balance.

Run from the repo root (or anywhere) as:
    python Zion/backend/balance.py

This script ensures the backend folder is on sys.path so it can import the
`blockchain` package regardless of the current working directory.
"""

import os
import sys
from pathlib import Path

# Ensure the backend folder is importable even when running from repo root
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from blockchain.algorand_logger import print_balance

if __name__ == "__main__":
    print_balance()
