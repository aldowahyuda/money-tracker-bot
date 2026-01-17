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
    results = []
    cursor = None

    while True:
        response = notion.search(
            filter={"property": "object", "value": "page"},
            start_cursor=cursor
        )

        for page in response["results"]:
            props = page["properties"]
            date_prop = props.get("Date", {}).get("date")

            if not date_prop:
                continue

            if date_prop["start"].startswith(today):
                results.append(page)

        if not response.get("has_more"):
            break

        cursor = response.get("next_cursor")

    return results

def get_month_transactions():
    now = datetime.now()
    month_prefix = now.strftime("%Y-%m")
    results = []
    cursor = None

    while True:
        response = notion.search(
            filter={"property": "object", "value": "page"},
            start_cursor=cursor
        )

        for page in response["results"]:
            props = page["properties"]
            date_prop = props.get("Date", {}).get("date")

            if not date_prop:
                continue

            if date_prop["start"].startswith(month_prefix):
                results.append(page)

        if not response.get("has_more"):
            break

        cursor = response.get("next_cursor")

    return results
