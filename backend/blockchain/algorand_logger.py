import json
import os
import threading

from algosdk import mnemonic, transaction
from algosdk.error import WrongMnemonicLengthError
from algosdk.v2client import algod
from dotenv import load_dotenv
from pathlib import Path

from db.store import save_chain_record

DOTENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=DOTENV_PATH)
load_dotenv()

ALGOD_ADDRESS = "https://testnet-api.algonode.cloud"
ALGOD_TOKEN   = ""
client        = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)

mn = os.getenv("ALGO_MNEMONIC")
if not mn:
    raise RuntimeError(f"ALGO_MNEMONIC is not set in {DOTENV_PATH}")

try:
    private_key = mnemonic.to_private_key(mn)
except WrongMnemonicLengthError as e:
    raise RuntimeError(f"ALGO_MNEMONIC invalid (must be 25 words): {e}") from e

address = os.getenv("ALGO_ADDRESS")
if not address:
    raise RuntimeError(f"ALGO_ADDRESS is not set in {DOTENV_PATH}")


# ── Batch window config ───────────────────────────────────────
# Wait this long after the FIRST incident before chaining.
# By then the model has seen enough traffic → correct classification.
BATCH_WINDOW_SECONDS = 8


# ── Internal state ────────────────────────────────────────────
_lock        = threading.Lock()
_pending     : list[dict] = []
_flush_timer : threading.Timer | None = None


def _submit_to_chain(incident: dict, batch_size: int) -> None:
    """Chain a single tx representing the last (correctly classified) incident."""
    try:
        note = json.dumps({
            "id"         : incident.get("id"),
            "type"       : incident.get("type"),   # correct type, not cold-start anomaly
            "endpoint"   : incident.get("endpoint"),
            "ip"         : incident.get("ip"),
            "risk"       : incident.get("risk"),
            "policy"     : incident.get("policy", "none"),
            "batch_size" : batch_size,             # how many incidents this tx represents
            "source"     : "ZION_DEFENSE_SYSTEM",
        }).encode()

        params     = client.suggested_params()
        txn        = transaction.PaymentTxn(
            sender=address, sp=params,
            receiver=address, amt=0, note=note,
        )
        signed_txn = txn.sign(private_key)
        tx_id      = client.send_transaction(signed_txn)
        transaction.wait_for_confirmation(client, tx_id, wait_rounds=6)

        explorer_url = f"https://testnet.algoexplorer.io/tx/{tx_id}"

        save_chain_record({
            "incident_id" : incident.get("id"),
            "tx_id"       : tx_id,
            "explorer_url": explorer_url,
            "threat_type" : incident.get("type"),
            "risk"        : incident.get("risk"),
            "endpoint"    : incident.get("endpoint"),
        })

        print(
            f"[ALGO] ✓ chained LAST of {batch_size} incident(s) "
            f"| type={incident.get('type')} "
            f"| tx={tx_id[:16]}..."
        )

    except Exception as e:
        print(f"[ALGO] ✗ Failed to submit chain record: {e}")


def _flush() -> None:
    """Timer fires → grab the last buffered incident and chain it."""
    global _flush_timer

    with _lock:
        _flush_timer = None
        if not _pending:
            return
        last       = _pending[-1]   # last = most context = correct type
        batch_size = len(_pending)
        _pending.clear()

    print(
        f"[ALGO] Window closed — {batch_size} incident(s) buffered, "
        f"chaining last (type={last.get('type')})"
    )

    threading.Thread(
        target=_submit_to_chain, args=(last, batch_size), daemon=True
    ).start()


def log_incident_async(incident: dict) -> None:
    """
    Non-blocking. Buffers the incident.

    First incident in a burst arms the timer.
    Subsequent incidents just update the buffer.
    When the window closes, ONLY the last incident is chained —
    ensuring the cold-start generic 'anomaly' label never makes it on-chain.
    """
    global _flush_timer

    with _lock:
        _pending.append(incident)
        n = len(_pending)

        if _flush_timer is None:
            _flush_timer = threading.Timer(BATCH_WINDOW_SECONDS, _flush)
            _flush_timer.daemon = True
            _flush_timer.start()
            print(
                f"[ALGO] Window opened ({incident.get('endpoint')}) "
                f"— chaining last incident in {BATCH_WINDOW_SECONDS}s"
            )
        else:
            print(
                f"[ALGO] Buffered {incident.get('id')} "
                f"type={incident.get('type')} (buffer={n})"
            )


def get_chain_history(limit: int = 20) -> list:
    from db.store import fetch_chain_records
    return fetch_chain_records(limit)


def log_incident(incident: dict) -> dict:
    """Legacy sync — bypasses batching, submits immediately."""
    _submit_to_chain(incident, batch_size=1)
    return {"success": True}


def get_balance() -> float:
    return client.account_info(address).get("amount", 0) / 1_000_000


def print_balance() -> None:
    balance = get_balance()
    print(f"Address: {address}")
    print(f"Balance: {balance:.6f} ALGO ({int(balance * 1_000_000)} microAlgos)")