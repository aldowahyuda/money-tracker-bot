import re
from fastapi import FastAPI, Request
from telegram_service import send_message
from notion_service import insert_transaction

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "ok"}

@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()

    if "message" not in data:
        return {"ok": True}

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "").strip()

    try:
        # ✅ parsing pakai regex (AMAN)
        match = re.match(r"(.+?)\s+(\d+)$", text)
        if not match:
            raise ValueError("Format tidak cocok")

        title = match.group(1)
        amount = int(match.group(2))

        insert_transaction(title, amount)

        await send_message(
            chat_id,
            f"✅ Tercatat!\n📝 {title}\n💸 Rp{amount:,}"
        )

    except Exception as e:
        await send_message(
            chat_id,
            "❌ Format salah.\nContoh: kopi 25000"
        )

    return {"ok": True}
