import os
from notion_client import Client
from datetime import datetime

notion = Client(auth=os.getenv("NOTION_TOKEN"))
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")


def insert_transaction(title: str, amount: int):
    response = notion.pages.create(
        parent={"database_id": DATABASE_ID},
        properties={
            "Transaction": {
                "title": [
                    {"text": {"content": title}}
                ]
            },
            "Amount": {
                "number": amount
            },
            "Date": {
                "date": {"start": datetime.now().isoformat()}
            }
        }
    )
    return response
