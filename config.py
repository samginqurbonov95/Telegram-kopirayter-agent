"""
config.py — Agentning barcha sozlamalari shu yerda.
Haqiqiy qiymatlarni .env fayliga yozasiz (.env.example dan nusxa oling).
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ---------- TELEGRAM ----------
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# Kanal username (masalan "@mening_kanalim") yoki raqamli ID (masalan -1001234567890)
CHANNEL_ID = os.getenv("CHANNEL_ID", "")

# Postlarni tasdiqlash uchun sizga (yoki admin guruhga) yuboriladigan chat ID
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "")

# Xodimlar ham buyruq bera olishi uchun ularning chat ID'larini shu yerga qo'shing.
# Bo'sh qoldirsangiz, faqat ADMIN_CHAT_ID buyruq bera oladi.
# Misol: STAFF_CHAT_IDS = ["111111111", "222222222"]
STAFF_CHAT_IDS = [x.strip() for x in os.getenv("STAFF_CHAT_IDS", "").split(",") if x.strip()]

# ---------- AI KALITLARI ----------
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# OpenAI kaliti endi ikki narsa uchun ishlatiladi:
#  1) AI-rasm generatsiyasi (DALL-E)
#  2) Ovozli xabarlarni matnga o'girish (Whisper)
# Ovozli buyruqlardan foydalanmoqchi bo'lsangiz, bu SHART.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# ---------- O'QUV MARKAZI PROFILI ----------
CENTER_NAME = "Samarqand til maktabi (STM)"          # <-- shu yerga nomini yozing
CENTER_SUBJECTS = "Ingliz tili (IELTS/CEFR), Ona tili va adabiyot, Tarix, Huquqshunoslik, Matematika, SAT, Rus tili, Turk tili, Biologiya, Kimyo, Fizika, Geografiya"  # <-- yo'nalishlaringiz
CENTER_AUDIENCE = "15-30 yoshdagi o'quvchi va talabalar"
CENTER_TONE = "professional, ishonchli, do'stona, motivatsion — lekin haddan tashqari rasmiy emas"
CENTER_LOCATION = "Samarqand"

# Postlarda ishlatiladigan brend ranglari (HEX)
BRAND_COLOR_PRIMARY = "#1B4DA0"     # asosiy rang (fon)
BRAND_COLOR_SECONDARY = "#E31E24"   # urg'u rangi (matn/chiziqlar)
BRAND_COLOR_TEXT = "#FFFFFF"        # matn rangi

LOGO_PATH = "assets/logo.png"
FONT_BOLD = "fonts/DejaVuSans-Bold.ttf"
FONT_REGULAR = "fonts/DejaVuSans.ttf"

# ---------- KONTENT TURLARI (qo'lda /post buyrug'i uchun) ----------
POST_TYPES = [
    "motivatsion_post",
    "foydali_maslahat",
    "kurs_reklamasi",
    "oquvchi_yutugi",
    "qiziqarli_fakt",
]

IMAGE_STRATEGY = {
    "motivatsion_post": "ai",
    "foydali_maslahat": "template",
    "kurs_reklamasi": "template",
    "oquvchi_yutugi": "template",
    "qiziqarli_fakt": "ai",
}

# ---------- BREND DIZAYN PROFILI ----------
# Admin /setdesign orqali namunaviy poster yuborganda, uning tavsifi shu faylga yoziladi
# va keyingi barcha AI-rasmlar shu uslubga moslashtiriladi.
DESIGN_PROFILE_PATH = "design_profile.json"

# ---------- TA'LIM YANGILIKLARI (RSS MANBALARI) ----------
# Bot shu manbalardan so'nggi yangiliklarni olib, ta'limga oid bo'lganini tanlab,
# ijodiy post shaklida qayta ishlaydi. Xohlagancha manba qo'shishingiz/o'chirishingiz mumkin.
# Eslatma: manzillarni vaqti-vaqti bilan tekshirib turing — saytlar RSS manzilini o'zgartirishi mumkin.
NEWS_RSS_FEEDS = [
    "https://www.gazeta.uz/oz/rss/",
    "https://www.gazeta.uz/oz/rss/?section=society",
]

# ---------- FAYLLAR ----------
GENERATED_DIR = "generated"
VOICE_TMP_DIR = "voice_tmp"

# ---------- AVTOMATIK REJALASHTIRISH ----------
# Bot shu vaqtlarda avtomatik post taklif qilib, ADMIN_CHAT_ID ga yuboradi
# (to'g'ridan kanalga CHIQMAYDI — baribir sizning tasdig'ingiz kerak).
# Har bir yozuv: (soat, daqiqa, tur) — tur "marketing" yoki "news" bo'lishi mumkin.
# Vaqt zonasi: Osiyo/Toshkent (UTC+5).
TIMEZONE = "Asia/Tashkent"
SCHEDULE_SLOTS = [
    (9, 0, "marketing"),
    (13, 0, "news"),
    (16, 0, "marketing"),
    (19, 30, "news"),
]
