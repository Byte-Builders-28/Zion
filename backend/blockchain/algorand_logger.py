import json
import os
import threading

from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from backend/.env (regardless of current working directory)
DOTENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=DOTENV_PATH)

# Fallback: allow env vars to be set via the default .env location too
load_dotenv()

# ── optional Algorand config ───────────────────────────────────
ALGOD_ENABLED = False
ALGOD_ADDRESS = "https://testnet-api.algonode.cloud"
ALGOD_TOKEN = ""  # Algonode doesn't need a token

client = None
private_key = None
address = None

mn = os.getenv("ALGO_MNEMONIC")
addr = os.getenv("ALGO_ADDRESS")

if mn and addr:
    try:
        from algosdk import mnemonic, transaction
        from algosdk.error import WrongMnemonicLengthError
        from algosdk.v2client import algod

        client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)
        private_key = mnemonic.to_private_key(mn)
        address = addr
        ALGOD_ENABLED = True
    except WrongMnemonicLengthError as e:
        print(
            f"[ALGO] Disabled: ALGO_MNEMONIC looks invalid (must be 25 words). "
            f"Update {DOTENV_PATH}. Error: {e}"
        )
        ALGOD_ENABLED = False
    except Exception as e:
        print(f"[ALGO] Disabled: failed to initialize client: {e}")
        ALGOD_ENABLED = False
else:
    # Keep disabled by default for local runs.
    ALGOD_ENABLED = False


def _submit_to_chain(incident: dict):
    """Internal background worker; writes to Algorand and local SQLite."""
    try:
        if not ALGOD_ENABLED:
            # No-op when Algorand credentials are not configured.
            return

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

        # Optional Appwrite persistence (falls back to in-memory if not configured).
        from db.store import save_chain_record
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
    if not ALGOD_ENABLED:
        return {"success": False, "disabled": True}
    _submit_to_chain(incident)
    return {"success": True, "disabled": False}


def get_balance() -> float:
    """Return the wallet balance in ALGO (testnet)."""
    if not ALGOD_ENABLED:
        raise RuntimeError(
            f"Algorand integration disabled. Set ALGO_MNEMONIC and ALGO_ADDRESS in {DOTENV_PATH} to enable."
        )
    acct = client.account_info(address)
    micro_algos = acct.get("amount", 0)
    return micro_algos / 1_000_000


def print_balance() -> None:
    """Print wallet address and current balance."""
    balance = get_balance()
    micro_algos = int(balance * 1_000_000)
    print(f"Address: {address}")
    print(f"Balance: {balance:.6f} ALGO ({micro_algos} microAlgos)")
