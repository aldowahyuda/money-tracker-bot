from datetime import date
from notion_client import Client
import os

notion = Client(auth=os.getenv("NOTION_API_KEY"))
DATABASE_ID = os.getenv("DATABASE_ID")


def insert_transaction(title: str, amount: int):
    notion.pages.create(
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
            "Type": {
                "select": {"name": "Expense"}
            },
            "Category": {
                "select": {"name": "Food & Dining"}
            },
            "Date": {
                "date": {"start": date.today().isoformat()}
            }
        }
    )
