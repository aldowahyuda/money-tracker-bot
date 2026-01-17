from fastapi import FastAPI, Request
from services.telegram_service import send_message
from services.notion_service import insert_transaction, get_today_transactions
from services.parser_service import parse_transaction

app = FastAPI()


@app.get("/")
async def root():
    return {"status": "ok"}


@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()

    if "message" not in data:
        return {"ok": True}

    message = data["message"]
    chat_id = message["chat"]["id"]
    text = message.get("text", "").strip()

    if not text:
        await safe_reply(chat_id, "❌ Kirim teks ya bro")
        return {"ok": True}

    # ===== COMMAND =====
    if text == "/today":
        return await handle_today(chat_id)

    # ===== TRANSACTION =====
    try:
        tx = parse_transaction(text)
    except ValueError:
        await safe_reply(
            chat_id,
            "❌ Format salah.\nContoh:\n- kopi 25k\n- gaji 5jt"
        )
        return {"ok": True}

    try:
        insert_transaction(
            tx["title"],
            tx["amount"],
            tx["type"]
        )
    except Exception as e:
        print("NOTION ERROR:", e)
        await safe_reply(chat_id, "⚠️ Gagal simpan ke Notion")
        return {"ok": True}

    emoji = "💰" if tx["type"] == "income" else "💸"

    await safe_reply(
        chat_id,
        f"✅ Tercatat!\n"
        f"📝 {tx['title']}\n"
        f"{emoji} Rp{tx['amount']:,}\n"
        f"📌 {tx['type'].capitalize()}"
    )

    return {"ok": True}


async def handle_today(chat_id: int):
    rows = get_today_transactions()

    if not rows:
        await safe_reply(chat_id, "📭 Belum ada transaksi hari ini")
        return {"ok": True}

    total = 0
    lines = []

    for row in rows:
        title = row["properties"]["Transaction"]["title"][0]["text"]["content"]
        amount = row["properties"]["Amount"]["number"]
        tx_type = row["properties"]["Type"]["select"]["name"]

        sign = "+" if tx_type == "Income" else "-"
        total += amount if sign == "+" else -amount

        lines.append(f"{sign} {title}: Rp{amount:,}")

    msg = "📅 Transaksi Hari Ini\n\n" + "\n".join(lines)
    msg += f"\n\n💡 Total: Rp{total:,}"

    await safe_reply(chat_id, msg)
    return {"ok": True}


async def safe_reply(chat_id: int, text: str):
    try:
        await send_message(chat_id, text)
    except Exception as e:
        print("TELEGRAM ERROR:", e)
