import os

from dotenv import load_dotenv

# load env
load_dotenv()

# config (MAKE SURE THESE MATCH EXACT APPWRITE IDs)
PROJECT_ID = os.getenv("APPWRITE_PROJECT_ID")
API_KEY = os.getenv("APPWRITE_API_KEY")
DATABASE_ID = os.getenv("APPWRITE_DATABASE_ID")
TABLE_ID = os.getenv("APPWRITE_COLLECTION_ID")  # still using same env name
ENDPOINT = os.getenv("APPWRITE_ENDPOINT")

_active_policies: list[dict] = []
_chain_records: list[dict] = []


def _appwrite_enabled() -> bool:
    return bool(PROJECT_ID and API_KEY and DATABASE_ID and TABLE_ID and ENDPOINT)


def _get_db():
    """Lazily create Appwrite client only when env vars exist.

    This keeps local demos usable without Appwrite configured.
    """
    if not _appwrite_enabled():
        return None

    from appwrite.client import Client
    from appwrite.services.tables_db import TablesDB

    client = Client()
    client.set_endpoint(ENDPOINT)
    client.set_project(PROJECT_ID)
    client.set_key(API_KEY)
    return TablesDB(client)

def save_chain_record(record: dict):
    """Called after Algorand confirms TX.

    If Appwrite is configured, persists to Appwrite TablesDB.
    Otherwise, stores records in-memory for local demos.
    """

    print(record)

    db = _get_db()
    if db is None:
        _chain_records.append(record)
        return

    db.create_row(
        database_id=DATABASE_ID,
        table_id=TABLE_ID,
        row_id="unique()",  # auto ID
        data={
            "incidentId": record.get("incident_id"),
            "txId": record.get("tx_id"),
            "explorerUrl": record.get("explorer_url"),
            "threatType": record.get("threat_type", "unknown"),
            "risk": float(record.get("risk", 0.0)),
            "endpoint": record.get("endpoint", "/"),
        },
    )


def fetch_chain_records(limit=20) -> list:
    "Returns last N chain records for the frontend Chain Log page"

    db = _get_db()
    if db is None:
        # Return a recent slice of in-memory records.
        return list(reversed(_chain_records[-int(limit):]))

    from appwrite.query import Query

    res = db.list_rows(
        database_id=DATABASE_ID,
        table_id=TABLE_ID,
        queries=[Query.order_desc("$createdAt"), Query.limit(limit)],
    )

    # Appwrite's returned schema may differ by configuration; pass through safe fields.
    out = []
    for d in res.get("rows", []):
        tx_id = d.get("txId") or d.get("tx_id")
        out.append(
            {
                "incident_id": d.get("incidentId") or d.get("incident_id"),
                "tx_id": tx_id,
                "tx_short": (tx_id[:8] + "..." + tx_id[-4:]) if tx_id else "",
                "explorer_url": d.get("explorerUrl") or d.get("explorer_url"),
                "threat_type": d.get("threatType") or d.get("threat_type"),
                "risk": d.get("risk"),
                "endpoint": d.get("endpoint"),
                "logged_at": d.get("$createdAt") or d.get("logged_at"),
            }
        )
    return out

def add_policy(policy: dict):
    _active_policies.append(policy)

def count_active_policies() -> int:
    return len(_active_policies)

def clear_policies():
    _active_policies.clear()
