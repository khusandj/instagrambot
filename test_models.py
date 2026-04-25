import google.generativeai as genai

API_KEY = "AIzaSyDHV76hHRxbV2LzBtpbCvb3u-hOW_FPD0Y"
genai.configure(api_key=API_KEY)

print("\n=== SIZNING KALITINGIZDA ISHLAYDIGAN MODELLAR RO'YXATI ===")
try:
    models = genai.list_models()
    for m in models:
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
    print("========================================================\n")
except Exception as e:
    print("XATOLIK:", e)
