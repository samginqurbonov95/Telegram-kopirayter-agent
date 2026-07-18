"""
voice.py — ovozli (voice) xabarlarni matnga o'giradi (OpenAI Whisper API orqali).
Admin yoki xodim botga ovozli xabar yuborsa, shu modul uni matnga aylantiradi,
so'ng oddiy matnli buyruq kabi qayta ishlanadi.
"""

import os
from openai import OpenAI

import config


def transcribe_voice(file_path: str) -> str:
    """
    Berilgan audio faylni (ogg/mp3/wav) matnga o'giradi.
    OPENAI_API_KEY sozlanmagan bo'lsa, xato haqida tushunarli xabar qaytaradi.
    """
    if not config.OPENAI_API_KEY:
        raise RuntimeError(
            "Ovozli buyruqlardan foydalanish uchun OPENAI_API_KEY sozlanishi kerak "
            "(.env fayliga qo'shing)."
        )

    client = OpenAI(api_key=config.OPENAI_API_KEY)

    with open(file_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="uz",  # Whisper o'zbek tilini ham qoniqarli tanib oladi
        )

    return transcript.text.strip()
