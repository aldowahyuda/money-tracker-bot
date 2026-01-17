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

    # ========= 1. VALIDASI UPDATE =========
    if "message" not in data:
        return {"ok": True}

    message = data["message"]
    chat_id = message["chat"]["id"]
    text = message.get("text")

    if not text:
        await safe_reply(chat_id, "❌ Kirim teks ya bro")
        return {"ok": True}

    text = text.strip()

    # ========= 2. PARSING INPUT =========
    match = re.search(r"(.+?)\s+(\d+)\s*$", text)
    if not match:
        await safe_reply(
            chat_id,
            "❌ Format salah.\nContoh: kopi 25000"
        )
        return {"ok": True}

    title = match.group(1)
    amount = int(match.group(2))

    # ========= 3. INSERT KE NOTION =========
    try:
        insert_transaction(title, amount)
    except Exception as e:
        print("NOTION ERROR:", e)
        await safe_reply(
            chat_id,
            "⚠️ Gagal simpan ke Notion. Coba lagi ya."
        )
        return {"ok": True}

    # ========= 4. BALAS KE TELEGRAM =========
    await safe_reply(
        chat_id,
        f"✅ Tercatat!\n📝 {title}\n💸 Rp{amount:,}"
    )

    return {"ok": True}

async def safe_reply(chat_id: int, text: str):
    try:
        await send_message(chat_id, text)
    except Exception as e:
        print("TELEGRAM ERROR:", e)