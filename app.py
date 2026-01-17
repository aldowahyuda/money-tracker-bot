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

    # ✅ Telegram standard
    if "message" not in data:
        return {"ok": True}

    message = data["message"]

    if "text" not in message:
        return {"ok": True}

    chat_id = message["chat"]["id"]
    text = message["text"].strip()

    try:
        # ✅ regex robust
        match = re.search(r"(.+?)\s+(\d+)\s*$", text)
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
            f"❌ ERROR DEBUG\ntext={repr(text)}\nerror={str(e)}"
        )


    return {"ok": True}
