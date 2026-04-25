import requests
import sys

# main.py dan token ni olamiz
try:
    from main import ACCESS_TOKEN
except ImportError:
    print("Xatolik: main.py faylidan ACCESS_TOKEN topilmadi.")
    sys.exit(1)

print(f"Token uzunligi: {len(ACCESS_TOKEN)}")

# Webhook ni Instagram profilga ulash (Subscribe qilish) API si
url = "https://graph.instagram.com/v25.0/me/subscribed_apps"

payload = {
    "subscribed_fields": "messages"
}

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

print("Instagramga ulanish (Subscribe) so'rovi yuborilyapti...")
response = requests.post(url, data=payload, headers=headers)

if response.status_code == 200:
    print("✅ TABRIKLAYMIZ! Botingiz Instagram profilingizga muvaffaqiyatli ulandi!")
    print(response.json())
else:
    print(f"❌ Xatolik yuz berdi ({response.status_code}):")
    print(response.text)
