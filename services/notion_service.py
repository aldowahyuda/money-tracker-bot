import os
from datetime import datetime
from notion_client import Client

notion = Client(auth=os.getenv("NOTION_TOKEN"))
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")


def insert_transaction(title: str, amount: int, tx_type: str):
    return notion.pages.create(
        parent={"database_id": DATABASE_ID},
        properties={
            "Transaction": {
                "title": [{"text": {"content": title}}]
            },
            "Amount": {
                "number": amount
            },
            "Type": {
                "select": {"name": tx_type.capitalize()}
            },
            "Date": {
                "date": {"start": datetime.now().isoformat()}
            }
        }
    )


def get_today_transactions():
    today = datetime.now().date().isoformat()

    return notion.databases.query(
        database_id=DATABASE_ID,
        filter={
            "property": "Date",
            "date": {"equals": today}
        }
    )["results"]
