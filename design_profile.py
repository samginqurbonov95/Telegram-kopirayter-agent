"""
design_profile.py — admin bir marta yuborgan namunaviy poster dizaynini Claude'ning
ko'rish (vision) qobiliyati orqali tahlil qilib, uning uslubini yozma tavsif
sifatida saqlaydi. Bu tavsif keyingi barcha AI-rasm generatsiyalarida "uslub
yo'riqnomasi" sifatida ishlatiladi — shunda barcha posterlar bir xil ruhda chiqadi.

MUHIM CHEKLOV: bu haqiqiy dizayn faylini (masalan Figma/PSD) emas, balki uning
tavsifini saqlaydi — ya'ni piksel darajasida aynan bir xil nusxa emas, balki
bir xil uslub/kayfiyat/kompozitsiyaga ega yangi rasmlar yaratishga yordam beradi.
"""

import os
import json
import base64
import anthropic

import config


def _load_profile() -> dict:
    if os.path.exists(config.DESIGN_PROFILE_PATH):
        with open(config.DESIGN_PROFILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_profile(data: dict):
    with open(config.DESIGN_PROFILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_style_note() -> str:
    """Saqlangan uslub tavsifini qaytaradi (agar mavjud bo'lmasa, bo'sh satr)."""
    profile = _load_profile()
    return profile.get("style_note", "")


def analyze_reference_image(image_path: str) -> str:
    """
    Berilgan namunaviy poster rasmini Claude vision orqali tahlil qilib,
    batafsil uslub tavsifini yaratadi va design_profile.json ga saqlaydi.
    Qaytaradi: yaratilgan uslub tavsifi (matn).
    """
    with open(image_path, "rb") as f:
        image_data = base64.standard_b64encode(f.read()).decode("utf-8")

    media_type = "image/png" if image_path.lower().endswith(".png") else "image/jpeg"

    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": (
                            "Bu — o'quv markazining namunaviy Telegram posteri. "
                            "Uning vizual uslubini keyingi AI-rasm generatsiyalarida "
                            "namuna sifatida ishlatish uchun ingliz tilida batafsil "
                            "tavsifla: kompozitsiya, rang sxemasi, tipografiya "
                            "xarakteri, elementlarning joylashuvi, umumiy kayfiyat/uslub "
                            "(masalan minimalist, korporativ, o'yinqaroq va h.k). "
                            "Faqat tavsifni yoz, boshqa hech narsa qo'shma. "
                            "3-5 gapdan iborat bo'lsin."
                        ),
                    },
                ],
            }
        ],
    )

    style_note = response.content[0].text.strip()

    profile = _load_profile()
    profile["style_note"] = style_note
    profile["source_image"] = image_path
    _save_profile(profile)

    return style_note
