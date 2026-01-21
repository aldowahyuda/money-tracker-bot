import os
from datetime import datetime
from notion_client import Client

notion = Client(auth=os.getenv("NOTION_TOKEN"))
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")


# =========================
# INSERT TRANSACTION
# =========================
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
            "Category": {
                "select": {"name": category}
            },
            "Date": {
                "date": {"start": datetime.now().isoformat()}
            }
        }
    )


# =========================
# INTERNAL SEARCH HELPER
# =========================
def _get_pages_by_date_prefix(prefix: str):
    results = []
    cursor = None

    while True:
        response = notion.search(
            filter={"property": "object", "value": "page"},
            start_cursor=cursor
        )

        for page in response["results"]:
            props = page.get("properties", {})
            date_prop = props.get("Date", {}).get("date")

            if not date_prop:
                continue

            if date_prop["start"].startswith(prefix):
                results.append(page)

        if not response.get("has_more"):
            break

        cursor = response.get("next_cursor")

    return results


# =========================
# TODAY / MONTH / YEAR
# =========================
def get_today_transactions():
    return _get_pages_by_date_prefix(datetime.now().strftime("%Y-%m-%d"))


def get_month_transactions():
    return _get_pages_by_date_prefix(datetime.now().strftime("%Y-%m"))


def get_year_transactions():
    return _get_pages_by_date_prefix(datetime.now().strftime("%Y"))
