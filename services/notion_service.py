from datetime import datetime
import os
from notion_client import Client

notion = Client(auth=os.getenv("NOTION_TOKEN"))
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")


def get_today_transactions():
    today = datetime.now().date().isoformat()

    response = notion.search(
        filter={
            "property": "object",
            "value": "page"
        }
    )

    results = []

    for page in response["results"]:
        props = page["properties"]

        if "Date" not in props:
            continue

        date_prop = props["Date"].get("date")
        if not date_prop:
            continue

        if date_prop["start"] == today:
            results.append(page)

    return results
