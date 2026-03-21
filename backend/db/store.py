import os

from dotenv import load_dotenv

from appwrite.client import Client
from appwrite.services.tables_db import TablesDB
from appwrite.query import Query

# load env
load_dotenv()

# config (MAKE SURE THESE MATCH EXACT APPWRITE IDs)
PROJECT_ID = os.getenv("APPWRITE_PROJECT_ID")
API_KEY = os.getenv("APPWRITE_API_KEY")
DATABASE_ID = os.getenv("APPWRITE_DATABASE_ID")
TABLE_ID = os.getenv("APPWRITE_COLLECTION_ID")  # still using same env name
ENDPOINT = os.getenv("APPWRITE_ENDPOINT")

# client setup
client = Client()
client.set_endpoint(ENDPOINT)
client.set_project(PROJECT_ID)
client.set_key(API_KEY)

db = TablesDB(client)
_active_policies = []

def save_chain_record(record: dict):
    "Called after Algorand confirms TX — saves to Appwrite"

    print(record)

    db.create_row(
        database_id=DATABASE_ID,
        table_id=TABLE_ID,
        row_id="unique()",  # auto ID
        data={
            "incidentId": record["incident_id"],
            "txId": record["tx_id"],
            "explorerUrl": record["explorer_url"],
            "threatType": record.get("threat_type", "unknown"),
            "risk": float(record.get("risk", 0.0)),
            "endpoint": record.get("endpoint", "/"),
        }
    )


def fetch_chain_records(limit=20) -> list:
    "Returns last N chain records for the frontend Chain Log page"

    res = db.list_rows(
        database_id=DATABASE_ID,
        table_id=TABLE_ID,
        queries=[
            Query.order_desc("$createdAt"),
            Query.limit(limit)
        ]
    )

    return [
        {
            "incident_id": d.get("incident_id"),
            "tx_id": d.get("tx_id"),
            "tx_short": (
                d.get("tx_id")[:8] + "..." + d.get("tx_id")[-4:]
                if d.get("tx_id") else ""
            ),
            "explorer_url": d.get("explorer_url"),
            "threat_type": d.get("threat_type"),
            "risk": d.get("risk"),
            "endpoint": d.get("endpoint"),
            "logged_at": d.get("logged_at"),
        }
        for d in res["rows"]
    ]

def add_policy(policy: dict):
    _active_policies.append(policy)

def count_active_policies() -> int:
    return len(_active_policies)

def clear_policies():
    _active_policies.clear()
