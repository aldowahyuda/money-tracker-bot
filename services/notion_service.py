from datetime import datetime
import os
from notion_client import Client

notion = Client(auth=os.getenv("NOTION_TOKEN"))
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")


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
