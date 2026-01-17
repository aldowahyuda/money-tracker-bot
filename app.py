from fastapi import FastAPI, Request
import json

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "ok"}

@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()

    print("===== RAW UPDATE =====")
    print(json.dumps(data, indent=2))
    print("======================")

    return {"ok": True}
