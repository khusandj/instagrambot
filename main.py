import os
import requests
from fastapi import FastAPI, Request, Response
import uvicorn

app = FastAPI()

# Buni o'zimiz o'ylab topamiz (ixtiyoriy so'z), Webhook tasdiqlash uchun kerak.
VERIFY_TOKEN = "mening_maxfiy_sozim_123"

# Buni Meta sahifasidan hozir olasiz, olganingizdan keyin shu yerga qo'yamiz
ACCESS_TOKEN = "IGAAVYWn4xgz1BZAGJrUWFTRlZAxVVFaeEYwVUxXSmJTS2UzZAXc5Ukw2TTFEeDFrc25fOFd2UW5pd09HTEF4ZAlQ1NzdJNXZAvUEhmSmlINjlrb3ZAjU2l2cTdETW1EaTNQX0lnWGRXUW1HalJjNF9LeTZAuRnJxbktXaU5IeW9pYUI4UQZDZD"

from fastapi.responses import PlainTextResponse

@app.get("/webhook")
async def verify_webhook(request: Request):
    """ Meta (Instagram) webhookni tasdiqlash uchun shu yerga GET so'rov yuboradi """
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("Webhook muvaffaqiyatli tasdiqlandi! ✅")
        return PlainTextResponse(content=str(challenge), status_code=200)
    else:
        return Response(status_code=403)

def send_message(recipient_id: str, message_text: str):
    """ Foydalanuvchiga Instagram orqali javob xabarini yuborish """
    url = "https://graph.facebook.com/v19.0/me/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        print(f"✅ Xabar yuborildi: {message_text}")
    else:
        print(f"❌ Xabar yuborishda xatolik: {response.text}")


@app.post("/webhook")
async def handle_webhook(request: Request):
    """ Instagramdan kelgan barcha xabarlar va izohlar shu yerga tushadi """
    try:
        body = await request.json()
        print("\n=== 📩 YANGI MA'LUMOT KELDI ===")
        print(body)
        print("=================================\n")
        
        # Xabarlarni tahlil qilish
        if body.get("object") == "instagram":
            for entry in body.get("entry", []):
                for webhook_event in entry.get("messaging", []):
                    if "message" in webhook_event:
                        sender_id = webhook_event["sender"]["id"]
                        message_text = webhook_event["message"].get("text", "")
                        
                        # O'zimiz (bot) yozgan xabarga tsikl bo'lib qaytarmaslik uchun
                        if webhook_event["message"].get("is_echo"):
                            continue
                        
                        print(f"📨 Yangi xabar: {message_text} (Kimdan: {sender_id})")
                        
                        # BIZNING AVTOMATIK JAVOBIMIZ
                        reply_text = f"Salom! Sizning '{message_text}' degan xabaringizni oldim. Men hozircha botman 😊"
                        send_message(sender_id, reply_text)
                        
        return Response(content="EVENT_RECEIVED", status_code=200)
    except Exception as e:
        print(f"Xatolik yuz berdi: {e}")
        return Response(status_code=500)

if __name__ == "__main__":
    # Serverni 8000-portda ishga tushirish
    print("Bot serveri ishga tushmoqda... (Port: 8000)")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
