import os
import requests
from fastapi import FastAPI, Request, Response
import uvicorn
import google.generativeai as genai

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

# ----------------- GEMINI SOZLAMALARI -----------------
# PASTGA O'ZINGIZNING GEMINI API KALITINGIZNI YOZING:
# DIQQAT: KALITNI BU YERGA YOZMANG! GITHUBGA CHIQIB KETSA GOOGLE BLOKLAYDI.
# KALITNI RENDER.COM SAYTIDAGI "ENVIRONMENT VARIABLES" BO'LIMIGA KIRITAMIZ!
import os
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    # Ushbu kalitda 100% kafolatli ishlaydigan model
    model = genai.GenerativeModel('gemini-pro')
else:
    model = None

# ======================================================
# BOTNING MIYASI (SHU YERNI O'Z BIZNESINGIZGA MOSLAB O'ZGARTIRASIZ)
# ======================================================
BOT_QOIDALARI = """
Sen AI Artist va vizual kontent kreatori Xusan Djemilovning shaxsiy blogida kuzatuvchilarga javob beruvchi xushmuomala yordamchisan.
Sening vazifang - kelgan xabarlarga samimiy, do'stona va xuddi inson yozgandek tabiiy javob berish.

Asosiy qoidalar:
1. Har doim o'zbek tilida chiroyli va xatosiz yoz.
2. Kuzatuvchi salom bersa, alik ol va: "Khusan AI artis shaxsiy blogiga xush kelibsiz! Sizga qanday yordam bera olaman?" deb so'ra.
3. Agar foydalanuvchi sun'iy intellekt (Seedance, Kling va hokazo), promtlar yozish sirlari, dizayn xizmatlari narxi yoki hamkorlik haqida so'rasa: batafsil yoz bilganingcha tushunarli qilib Suniy intelektni o'rganmoqchiman desa "Qiziqishingiz uchun rahmat! Xabaringizni Xusanga AI artist yetkazdim, u hozir biroz bandroq, lekin tez orada sizga o'zi batafsil javob yozadi. Ungacha blogdagi AI ijod namunalari bilan tanishib turing!" deb javob ber.
4. Javoblaring juda qisqa, lo'nda va samimiy bo'lsin. Ortiqcha rasmiyatchilikka berilma.
5. Smayliklardan (😊, ✌️, ✨, 🎨) me'yorida foydalan.
"""
def get_ai_reply(text: str, is_comment: bool = False) -> str:
    """ Foydalanuvchi xabariga Gemini orqali javob olish """
    if not model:
        return "Bot tayyor, lekin Gemini API kaliti kiritilmagan! (Iltimos kodga kalitni qo'ying)"
    
    try:
        if is_comment:
            prompt = f"{BOT_QOIDALARI}\n\nVAZIFA: Foydalanuvchi sening postingga shunday izoh (kommentariya) qoldirdi: '{text}'. Unga o'zbek tilida juda qisqa (maksimum 1 ta gap) va chiroyli javob qaytar."
        else:
            prompt = f"{BOT_QOIDALARI}\n\nVAZIFA: Mijoz senga direct'da shunday xabar yozdi: '{text}'. Unga yuqoridagi qoidalarga to'liq amal qilgan holda javob qaytar."
            
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini xatoligi: {e}")
        # Xatolik bo'lsa hech narsa yubormaymiz, aks holda siklga tushib qoladi
        return ""
# ------------------------------------------------------

def send_message(recipient_id: str, message_text: str):
    """ Foydalanuvchiga Instagram orqali javob xabarini yuborish """
    url = "https://graph.instagram.com/v25.0/me/messages"
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

def reply_to_comment(comment_id: str, message_text: str):
    """ Postdagi izohga (kommentga) ommaviy javob qaytarish """
    url = f"https://graph.instagram.com/v25.0/{comment_id}/replies"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "message": message_text
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        print(f"✅ Izohga javob yozildi: {message_text}")
    else:
        print(f"❌ Izohga javob yozishda xatolik: {response.text}")




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
                
                # 1. Direct xabarlarni (DM) o'qish
                for webhook_event in entry.get("messaging", []):
                    if "message" in webhook_event:
                        sender_id = webhook_event["sender"]["id"]
                        message_text = webhook_event["message"].get("text", "")
                        
                        # O'zimiz (bot) yozgan xabarga tsikl bo'lib qaytarmaslik uchun
                        if webhook_event["message"].get("is_echo") or str(sender_id) == str(entry.get("id")):
                            continue
                        
                        print(f"📨 Yangi xabar: {message_text} (Kimdan: {sender_id})")
                        
                        # GEMINI ORQALI AVTOMATIK JAVOB (DIRECTGA)
                        ai_reply = get_ai_reply(message_text, is_comment=False)
                        if ai_reply:
                            send_message(sender_id, ai_reply)

                # 2. Kommentariyalarni (Izohlarni) o'qish
                for change in entry.get("changes", []):
                    if change.get("field") == "comments":
                        comment_value = change.get("value", {})
                        comment_id = comment_value.get("id")
                        comment_text = comment_value.get("text", "")
                        from_id = comment_value.get("from", {}).get("id", "")
                        username = comment_value.get("from", {}).get("username", "Foydalanuvchi")
                        
                        # Bot yoki akkaunt egasi o'zi yozgan izohga tsikl bo'lib qayta javob yozmasligi uchun
                        if str(from_id) == str(entry.get("id")):
                            continue
                        
                        print(f"💬 Yangi kommentariya: {comment_text} (Kimdan: {username})")
                        
                        # GEMINI ORQALI AVTOMATIK JAVOB (POST TAGIGA OCHIQ JAVOB)
                        ai_reply = get_ai_reply(comment_text, is_comment=True)
                        if ai_reply:
                            reply_text = f"@{username}, {ai_reply}"
                            reply_to_comment(comment_id, reply_text)
                        
        return Response(content="EVENT_RECEIVED", status_code=200)
    except Exception as e:
        print(f"Xatolik yuz berdi: {e}")
        return Response(status_code=500)

if __name__ == "__main__":
    # Serverni 8000-portda ishga tushirish
    print("Bot serveri ishga tushmoqda... (Port: 8000)")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
