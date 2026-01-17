from fastapi import FastAPI, Request
from dotenv import load_dotenv
from telegram_service import send_message

load_dotenv()

app = FastAPI()

# 🔥 WAJIB ADA (HEALTHCHECK)
@app.get("/")
async def root():
    return {"status": "ok"}

@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    chat_id = data["message"]["chat"]["id"]
    await send_message(chat_id, "👋 Bot hidup bro")
    return {"ok": True}
