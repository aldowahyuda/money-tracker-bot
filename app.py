from fastapi import FastAPI, Request
from services.telegram_service import send_message
from services.notion_service import insert_transaction, get_today_transactions, get_month_transactions, get_year_transactions
from services.parser_service import parse_transaction
from services.category_service import detect_category


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
    
    if text == "/month":
        return await handle_month(chat_id)
    
    if text == "/year":
        return await handle_year(chat_id)

    # ===== TRANSACTION =====
    try:
        tx = parse_transaction(text)
    except ValueError:
        await safe_reply(
            chat_id,
            "❌ Format salah.\nContoh:\n- kopi 25k\n- gaji 5jt"
        )
        return {"ok": True}
    
    category = detect_category(tx["title"])
    #print("CATEGORY:", category)

    try:
        insert_transaction(
            tx["title"],
            tx["amount"],
            tx["type"],
            category
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
        f"📌 {tx['type'].capitalize()}\n"
        f"🏷️ {category}"
    )

    return {"ok": True}

async def safe_reply(chat_id: int, text: str):
    try:
        await send_message(chat_id, text)
    except Exception as e:
        print("TELEGRAM ERROR:", e)


async def handle_today(chat_id: int):
    rows = get_today_transactions()

    if not rows:
        await safe_reply(chat_id, "📭 Belum ada transaksi hari ini")
        return {"ok": True}

    income = []
    expense = []
    total_income = 0
    total_expense = 0

    for r in rows:
        props = r["properties"]
        title = props["Transaction"]["title"][0]["text"]["content"]
        amount = props["Amount"]["number"]
        tx_type = props["Type"]["select"]["name"].lower()

        if tx_type == "income":
            income.append((title, amount))
            total_income += amount
        else:
            expense.append((title, amount))
            total_expense += amount

    msg = "📅 Ringkasan Hari Ini\n\n"

    if income:
        msg += "💰 Income:\n"
        for t, a in income:
            msg += f"+ {t} : Rp{a:,}\n"

    if expense:
        msg += "\n💸 Expense:\n"
        for t, a in expense:
            msg += f"- {t} : Rp{a:,}\n"

    msg += f"\n💡 Net: Rp{total_income - total_expense:,}"

    await safe_reply(chat_id, msg)
    return {"ok": True}


async def handle_month(chat_id: int):
    rows = get_month_transactions()

    if not rows:
        await safe_reply(chat_id, "📭 Belum ada transaksi bulan ini")
        return {"ok": True}

    income = []
    expense = []
    total_income = 0
    total_expense = 0

    for r in rows:
        props = r["properties"]
        title = props["Transaction"]["title"][0]["text"]["content"]
        amount = props["Amount"]["number"]
        tx_type = props["Type"]["select"]["name"].lower()

        if tx_type == "income":
            income.append((title, amount))
            total_income += amount
        else:
            expense.append((title, amount))
            total_expense += amount

    msg = "📊 Ringkasan Bulan Ini\n\n"

    if income:
        msg += "💰 Income:\n"
        for t, a in income:
            msg += f"+ {t}: Rp{a:,}\n"

    if expense:
        msg += "\n💸 Expense:\n"
        for t, a in expense:
            msg += f"- {t}: Rp{a:,}\n"

    msg += f"\n💡 Net: Rp{total_income - total_expense:,}"

    await safe_reply(chat_id, msg)
    return {"ok": True}


async def handle_year(chat_id: int):
    rows = get_year_transactions()

    if not rows:
        await safe_reply(chat_id, "📭 Belum ada transaksi tahun ini")
        return {"ok": True}

    income = {}
    expense = {}
    total_income = 0
    total_expense = 0

    for r in rows:
        props = r["properties"]
        title = props["Transaction"]["title"][0]["text"]["content"]
        amount = props["Amount"]["number"]
        tx_type = props["Type"]["select"]["name"].lower()

        if tx_type == "income":
            income[title] = income.get(title, 0) + amount
            total_income += amount
        else:
            expense[title] = expense.get(title, 0) + amount
            total_expense += amount

    msg = "📊 Ringkasan Tahun Ini\n\n"

    if income:
        msg += "💰 Income:\n"
        for k, v in income.items():
            msg += f"+ {k}: Rp{v:,}\n"

    if expense:
        msg += "\n💸 Expense:\n"
        for k, v in expense.items():
            msg += f"- {k}: Rp{v:,}\n"

    msg += f"\n💡 Net: Rp{total_income - total_expense:,}"

    await safe_reply(chat_id, msg)
    return {"ok": True}

