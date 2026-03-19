import json
import os
import base64

from algosdk import mnemonic, transaction
from algosdk.error import WrongMnemonicLengthError
from algosdk.v2client import algod
from dotenv import load_dotenv
from pathlib import Path

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


def log_incident(incident: dict) -> dict:
    """Write a cyber incident to Algorand testnet as a payment transaction.

    The incident JSON is stored in the `note` field (up to 1000 bytes).

    Returns a dict with tx_id, explorer_url, and success flag.
    """

    # Full incident JSON in the note field — no truncation needed
    note = json.dumps({
        "id": incident.get("id"),
        "type": incident.get("type"),
        "endpoint": incident.get("endpoint"),
        "ip": incident.get("ip"),
        "risk": incident.get("risk"),
        "policy": incident.get("policy", "none"),
        "source": "ZION_DEFENSE_SYSTEM",
    }).encode()

    # Get suggested params (fee, round etc) from network
    params = client.suggested_params()

    # Build a 0-ALGO payment TX to ourselves — just to carry the note
    txn = transaction.PaymentTxn(
        sender=address,
        sp=params,
        receiver=address,
        amt=0,
        note=note,
    )

    # Sign and send
    signed_txn = txn.sign(private_key)
    tx_id = client.send_transaction(signed_txn)

    # Wait for confirmation (~4.5 seconds)
    transaction.wait_for_confirmation(client, tx_id, wait_rounds=4)

    explorer_url = f"https://testnet.algoexplorer.io/tx/{tx_id}"

    print(f"[ALGO] Incident {incident.get('id')} logged on-chain")
    print(f"[ALGO] TX ID:   {tx_id}")
    print(f"[ALGO] Explorer: {explorer_url}")

    return {
        "tx_id": tx_id,
        "explorer_url": explorer_url,
        "success": True,
    }


def get_incident_history(limit=10) -> list:
    """Fetch the last N transactions from the wallet for a Chain Log dashboard."""

    txs = client.account_transactions(address, limit=limit)
    results = []

    for tx in txs.get("transactions", []):
        note_b64 = tx.get("note", "")
        note_data = {}

        if note_b64:
            try:
                note_str = base64.b64decode(note_b64).decode()
                note_data = json.loads(note_str)
            except Exception:
                note_data = {}

        results.append(
            {
                "tx_id": tx["id"],
                "incident_id": note_data.get("id", "unknown"),
                "type": note_data.get("type", "unknown"),
                "risk": note_data.get("risk", 0),
                "timestamp": tx.get("round-time", 0),
                "explorer_url": f"https://testnet.algoexplorer.io/tx/{tx['id']}",
            }
        )

    return results


def get_balance() -> float:
    """Return the wallet balance in ALGO (testnet)."""

    acct = client.account_info(address)
    micro_algos = acct.get("amount", 0)
    return micro_algos / 1_000_000


def print_balance() -> None:
    """Print the wallet address and current balance."""

    balance = get_balance()
    micro_algos = int(balance * 1_000_000)
    print(f"Address: {address}")
    print(f"Balance: {balance:.6f} ALGO ({micro_algos} microAlgos)")

    """ sob thik thk run korche 
    keu chuthiami kore kichu del korbi na """
