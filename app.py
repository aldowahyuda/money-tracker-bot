from fastapi import FastAPI, Request
from dotenv import load_dotenv
import re

from notion_service import insert_transaction
from telegram_service import send_message

load_dotenv()

app = FastAPI()


@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()

    # ignore non-message updates
    if "message" not in data:
        return {"ok": True}

    message = data["message"]
    chat_id = message["chat"]["id"]
    text = message.get("text", "").lower()

    # parsing sederhana: cari angka
    match = re.search(r"\d+", text)
    if not match:
        await send_message(chat_id, "❌ Nominal ga ketemu")
        return {"ok": True}

    amount = int(match.group())

    # insert ke Notion
    insert_transaction(title=text, amount=amount)

    # reply ke Telegram
    await send_message(chat_id, f"✅ Tercatat: Rp{amount:,}")

    return {"ok": True}
