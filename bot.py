"""
bot.py — Agentning asosiy fayli.

QOBILIYATLAR:
1. /vazifa <matn> yoki ovozli xabar — erkin topshiriq asosida kreativ kontent
2. /elon <matn> yoki ovozli xabar — aniq ma'lumot asosida e'lon
3. Oddiy matn/ovozli xabar (buyruqsiz) — bot o'zi "topshiriq"mi, "e'lon"mi
   ekanini aniqlab, mos ravishda ishlaydi
4. /post — darhol marketing-post generatsiya qilish
5. /setdesign — namunaviy poster rasmini (caption yoki reply bilan) yuborsangiz,
   bot uni tahlil qilib, keyingi barcha AI-rasmlarni shu uslubga moslaydi
6. Kuniga bir necha marta (config.SCHEDULE_SLOTS) avtomatik marketing/yangilik
   postlarini taklif qiladi

Har qanday post avval ADMIN_CHAT_ID ga preview + tasdiqlash tugmalari bilan
yuboriladi. Faqat ✅ bosilgandan keyin kanalga chiqadi.

Ishga tushirish: python bot.py
"""

import os
import logging
import datetime
import time as time_module
from zoneinfo import ZoneInfo

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

import config
import design_profile
import voice
from content_generator import (
    generate_marketing_post,
    generate_news_post,
    generate_from_task,
    generate_announcement,
    classify_intent,
)
from image_generator import generate_image_for_post, generate_template_image

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

os.makedirs(config.VOICE_TMP_DIR, exist_ok=True)

# Tasdiqlanishi kutilayotgan postlar: {key: {"text": str, "image": str, "post_type": str}}
PENDING_POSTS = {}


def _authorized_ids() -> set:
    ids = set(config.STAFF_CHAT_IDS)
    if config.ADMIN_CHAT_ID:
        ids.add(str(config.ADMIN_CHAT_ID))
    return ids


def _is_authorized(update: Update) -> bool:
    return str(update.effective_chat.id) in _authorized_ids()


def _format_post_text(post_data: dict) -> str:
    body = post_data["body"].strip()
    hashtags = post_data.get("hashtags", "").strip()
    if hashtags:
        return f"{body}\n\n{hashtags}"
    return body


async def _send_preview(context: ContextTypes.DEFAULT_TYPE, post_data: dict, chat_id=None):
    """Tayyor post_data asosida rasm yaratadi va tasdiqlash uchun yuboradi."""
    image_path = generate_image_for_post(post_data)
    final_text = _format_post_text(post_data)

    key = f"{len(PENDING_POSTS) + 1}_{int(time_module.time())}"
    PENDING_POSTS[key] = {"text": final_text, "image": image_path, "post_type": post_data.get("post_type", "post")}

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Kanalga chiqarish", callback_data=f"approve:{key}"),
            InlineKeyboardButton("🔁 Qayta generatsiya", callback_data=f"regen:{key}"),
        ],
        [InlineKeyboardButton("❌ Bekor qilish", callback_data=f"reject:{key}")],
    ])

    target_chat = chat_id or config.ADMIN_CHAT_ID
    with open(image_path, "rb") as photo:
        await context.bot.send_photo(
            chat_id=target_chat,
            photo=photo,
            caption=f"👀 PREVIEW ({post_data.get('post_type', 'post')})\n\n{final_text}",
            reply_markup=keyboard,
        )


async def _handle_free_text(context: ContextTypes.DEFAULT_TYPE, requester_chat_id, text: str):
    """Buyruqsiz kelgan matn (yoki ovozdan o'girilgan matn) uchun intent aniqlab, kontent yaratadi.
    Post har doim ADMIN_CHAT_ID ga tasdiqlash uchun yuboriladi (kim so'ragan bo'lishidan qat'i nazar)."""
    intent = classify_intent(text)
    if intent == "elon":
        post_data = generate_announcement(text)
    else:
        post_data = generate_from_task(text)
    await _send_preview(context, post_data)
    if str(requester_chat_id) != str(config.ADMIN_CHAT_ID):
        await context.bot.send_message(chat_id=requester_chat_id, text="✅ So'rovingiz tayyorlandi va tasdiqlash uchun adminga yuborildi.")


# ---------------------------------------------------------------------------
# BUYRUQLAR
# ---------------------------------------------------------------------------

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Salom! Men {config.CENTER_NAME} uchun kontent-agentman.\n\n"
        "Buyruqlar:\n"
        "/post — marketing post generatsiya qilish\n"
        "/vazifa <matn> — erkin topshiriq asosida kreativ post\n"
        "/elon <matn> — aniq ma'lumot asosida e'lon\n"
        "/setdesign — namunaviy poster yuborib, dizayn uslubini o'rnatish\n\n"
        "Shuningdek, menga oddiy matn yoki ovozli xabar yuborsangiz ham, men "
        "o'zim buni topshiriqmi yoki e'lonmi ekanini aniqlab, kontent tayyorlayman."
    )


async def cmd_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_authorized(update):
        await update.message.reply_text("Kechirasiz, bu buyruq faqat admin/xodimlar uchun.")
        return
    await update.message.reply_text("⏳ Marketing post tayyorlanmoqda...")
    post_data = generate_marketing_post()
    await _send_preview(context, post_data)
    if str(update.effective_chat.id) != str(config.ADMIN_CHAT_ID):
        await update.message.reply_text("✅ Tayyor, tasdiqlash uchun adminga yuborildi.")


async def cmd_vazifa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_authorized(update):
        await update.message.reply_text("Kechirasiz, bu buyruq faqat admin/xodimlar uchun.")
        return
    task_text = " ".join(context.args)
    if not task_text:
        await update.message.reply_text("Iltimos, topshiriqni yozing. Masalan:\n/vazifa yozgi IT kurslar haqida qiziqarli post")
        return
    await update.message.reply_text("⏳ Topshiriq asosida kontent tayyorlanmoqda...")
    post_data = generate_from_task(task_text)
    await _send_preview(context, post_data)
    if str(update.effective_chat.id) != str(config.ADMIN_CHAT_ID):
        await update.message.reply_text("✅ Tayyor, tasdiqlash uchun adminga yuborildi.")


async def cmd_elon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_authorized(update):
        await update.message.reply_text("Kechirasiz, bu buyruq faqat admin/xodimlar uchun.")
        return
    info_text = " ".join(context.args)
    if not info_text:
        await update.message.reply_text("Iltimos, e'lon ma'lumotini yozing. Masalan:\n/elon 20-avgustdan yangi ingliz tili guruhi ochiladi, dars kunlari dush-chor-juma")
        return
    await update.message.reply_text("⏳ E'lon tayyorlanmoqda...")
    post_data = generate_announcement(info_text)
    await _send_preview(context, post_data)
    if str(update.effective_chat.id) != str(config.ADMIN_CHAT_ID):
        await update.message.reply_text("✅ Tayyor, tasdiqlash uchun adminga yuborildi.")


async def cmd_setdesign(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_authorized(update):
        await update.message.reply_text("Kechirasiz, bu buyruq faqat admin/xodimlar uchun.")
        return
    await update.message.reply_text(
        "Namunaviy poster rasmingizni shu chatga yuboring (rasm sifatida, fayl "
        "emas), keyin men uni tahlil qilib, brend dizayn uslubi sifatida saqlayman."
    )


# ---------------------------------------------------------------------------
# ERKIN XABARLAR (matn, ovoz, rasm)
# ---------------------------------------------------------------------------

async def on_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin/xodim rasm yuborsa — buni namunaviy dizayn sifatida saqlaymiz."""
    if not _is_authorized(update):
        return

    await update.message.reply_text("🎨 Dizayn tahlil qilinmoqda...")
    photo_file = await update.message.photo[-1].get_file()
    local_path = f"{config.GENERATED_DIR}/reference_{int(time_module.time())}.jpg"
    os.makedirs(config.GENERATED_DIR, exist_ok=True)
    await photo_file.download_to_drive(local_path)

    style_note = design_profile.analyze_reference_image(local_path)
    await update.message.reply_text(
        f"✅ Dizayn uslubi saqlandi. Bundan buyon AI-rasmlar shu uslubga moslashadi:\n\n{style_note}"
    )


async def on_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ovozli xabarni matnga o'girib, topshiriq/e'lon sifatida qayta ishlaydi."""
    if not _is_authorized(update):
        return

    await update.message.reply_text("🎙 Ovozli xabar tinglanmoqda...")
    voice_file = await update.message.voice.get_file()
    local_path = f"{config.VOICE_TMP_DIR}/voice_{int(time_module.time())}.ogg"
    await voice_file.download_to_drive(local_path)

    try:
        text = voice.transcribe_voice(local_path)
    except RuntimeError as e:
        await update.message.reply_text(f"⚠️ {e}")
        return
    finally:
        if os.path.exists(local_path):
            os.remove(local_path)

    await update.message.reply_text(f"📝 Tushundim: \"{text}\"\n\n⏳ Kontent tayyorlanmoqda...")
    await _handle_free_text(context, update.effective_chat.id, text)


async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Buyruqsiz oddiy matnni topshiriq/e'lon sifatida qayta ishlaydi."""
    if not _is_authorized(update):
        return
    text = update.message.text.strip()
    if not text:
        return
    await update.message.reply_text("⏳ Kontent tayyorlanmoqda...")
    await _handle_free_text(context, update.effective_chat.id, text)


# ---------------------------------------------------------------------------
# TASDIQLASH TUGMALARI
# ---------------------------------------------------------------------------

async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    if str(update.effective_chat.id) != str(config.ADMIN_CHAT_ID):
        await query.answer("Faqat admin tasdiqlashi mumkin.", show_alert=True)
        return

    await query.answer()

    action, key = query.data.split(":", 1)
    post = PENDING_POSTS.get(key)

    if not post:
        await query.edit_message_caption(caption="⚠️ Bu post muddati o'tgan yoki allaqachon ishlov berilgan.")
        return

    if action == "approve":
        with open(post["image"], "rb") as photo:
            await context.bot.send_photo(chat_id=config.CHANNEL_ID, photo=photo, caption=post["text"])
        await query.edit_message_caption(caption=f"✅ KANALGA CHIQARILDI\n\n{post['text']}")
        del PENDING_POSTS[key]

    elif action == "reject":
        await query.edit_message_caption(caption="❌ Bekor qilindi.")
        del PENDING_POSTS[key]

    elif action == "regen":
        await query.edit_message_caption(caption="🔁 Qayta generatsiya qilinmoqda...")
        post_type = post["post_type"]
        del PENDING_POSTS[key]

        if post_type == "marketing_post":
            new_data = generate_marketing_post()
        elif post_type in ("news_post", "news_post_fallback"):
            new_data = generate_news_post()
        else:
            new_data = generate_marketing_post()  # umumiy fallback

        await _send_preview(context, new_data)


# ---------------------------------------------------------------------------
# AVTOMATIK REJALASHTIRISH
# ---------------------------------------------------------------------------

async def scheduled_job(context: ContextTypes.DEFAULT_TYPE):
    slot_type = context.job.data
    logger.info(f"Rejalashtirilgan post generatsiyasi boshlandi: {slot_type}")
    if slot_type == "news":
        post_data = generate_news_post()
    else:
        post_data = generate_marketing_post()
    await _send_preview(context, post_data)


def main():
    if not config.TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN sozlanmagan. .env faylini tekshiring.")

    app = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("post", cmd_post))
    app.add_handler(CommandHandler("vazifa", cmd_vazifa))
    app.add_handler(CommandHandler("elon", cmd_elon))
    app.add_handler(CommandHandler("setdesign", cmd_setdesign))
    app.add_handler(CallbackQueryHandler(on_callback))
    app.add_handler(MessageHandler(filters.PHOTO, on_photo))
    app.add_handler(MessageHandler(filters.VOICE, on_voice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))

    tz = ZoneInfo(config.TIMEZONE)
    for hour, minute, slot_type in config.SCHEDULE_SLOTS:
        app.job_queue.run_daily(
            scheduled_job,
            time=datetime.time(hour=hour, minute=minute, tzinfo=tz),
            data=slot_type,
        )
    logger.info(f"Rejalashtirilgan vaqtlar ({config.TIMEZONE}): {config.SCHEDULE_SLOTS}")

    logger.info("Bot ishga tushdi...")
    app.run_polling()


if __name__ == "__main__":
    main()
