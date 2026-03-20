import json
import os
import base64
import threading

from algosdk import mnemonic, transaction
from algosdk.error import WrongMnemonicLengthError
from algosdk.v2client import algod
from dotenv import load_dotenv
from pathlib import Path

from db.store import save_chain_record

# Load environment variables from backend/.env (regardless of current working directory)
DOTENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=DOTENV_PATH)

# Fallback: allow env vars to be set via the default .env location too
load_dotenv()

# ── connect to Algorand testnet node ──────────────────────────
ALGOD_ADDRESS = "https://testnet-api.algonode.cloud"
ALGOD_TOKEN = ""  # Algonode doesn't need a token
client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)

# ── load wallet from .env ─────────────────────────────────────
mn = os.getenv("ALGO_MNEMONIC")
if not mn:
    raise RuntimeError(
        f"ALGO_MNEMONIC is not set. Create a .env file at {DOTENV_PATH} with ALGO_MNEMONIC and ALGO_ADDRESS."
    )

try:
    private_key = mnemonic.to_private_key(mn)
except WrongMnemonicLengthError as e:
    raise RuntimeError(
        f"ALGO_MNEMONIC looks invalid (must be 25 words).\n"
        f"Please update the file at {DOTENV_PATH} with the mnemonic output from generate_wallet.py.\n"
        f"Original error: {e}"
    ) from e

address = os.getenv("ALGO_ADDRESS")
if not address:
    raise RuntimeError(
        f"ALGO_ADDRESS is not set. Create a .env file at {DOTENV_PATH} with ALGO_MNEMONIC and ALGO_ADDRESS."
    )


def _submit_to_chain(incident: dict):
    """Internal background worker; writes to Algorand and local SQLite."""
    try:
        note = json.dumps({
            "id": incident.get("id"),
            "type": incident.get("type"),
            "endpoint": incident.get("endpoint"),
            "ip": incident.get("ip"),
            "risk": incident.get("risk"),
            "policy": incident.get("policy", "none"),
            "source": "ZION_DEFENSE_SYSTEM",
        }).encode()

        params = client.suggested_params()
        txn = transaction.PaymentTxn(
            sender=address,
            sp=params,
            receiver=address,
            amt=0,
            note=note,
        )

        signed_txn = txn.sign(private_key)
        tx_id = client.send_transaction(signed_txn)

        transaction.wait_for_confirmation(client, tx_id, wait_rounds=6)

        explorer_url = f"https://testnet.algoexplorer.io/tx/{tx_id}"

        save_chain_record({
            "incident_id": incident.get("id"),
            "tx_id": tx_id,
            "explorer_url": explorer_url,
            "threat_type": incident.get("type"),
            "risk": incident.get("risk"),
            "endpoint": incident.get("endpoint"),
        })

        print(f"[ALGO] ✓ {incident.get('id')} -> {tx_id[:16]}...")
    except Exception as e:
        print(f"[ALGO] ✗ Failed to log incident {incident.get('id')}: {e}")


def log_incident_async(incident: dict):
    """Public helper for FastAPI route. Non-blocking, returns immediately."""
    thread = threading.Thread(target=_submit_to_chain, args=(incident,), daemon=True)
    thread.start()
    print(f"[ALGO] Logging incident {incident.get('id')} in background...")


def get_chain_history(limit=20) -> list:
    """Return cached historic chain records from local SQLite store."""
    from db.store import fetch_chain_records
    return fetch_chain_records(limit)


def log_incident(incident: dict) -> dict:
    """Legacy sync call preserved in case some import uses it."""
    _submit_to_chain(incident)
    return {"success": True}


def get_balance() -> float:
    """Return the wallet balance in ALGO (testnet)."""
    acct = client.account_info(address)
    micro_algos = acct.get("amount", 0)
    return micro_algos / 1_000_000


def print_balance() -> None:
    """Print wallet address and current balance."""
    balance = get_balance()
    micro_algos = int(balance * 1_000_000)
    print(f"Address: {address}")
    print(f"Balance: {balance:.6f} ALGO ({micro_algos} microAlgos)")
