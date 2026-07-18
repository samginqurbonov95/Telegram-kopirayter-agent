"""
image_generator.py — postlar uchun rasm yaratadi.
Ikki strategiya:
  1) template  -> Pillow yordamida brend ranglari/logotip bilan kartochka
  2) ai        -> OpenAI DALL-E orqali original rasm (OPENAI_API_KEY kerak)
"""

import os
import time
import textwrap
from PIL import Image, ImageDraw, ImageFont

import config
import design_profile

os.makedirs(config.GENERATED_DIR, exist_ok=True)

CANVAS_SIZE = (1080, 1080)  # Telegram/Instagram uchun qulay kvadrat format


def _load_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        # Agar shrift fayli topilmasa, standart shriftga tushamiz
        return ImageFont.load_default()


def generate_template_image(title: str, subtext: str = "") -> str:
    """
    Brend ranglari, logotip va matn bilan Telegram posti uchun kvadrat rasm yaratadi.
    Qaytaradi: yaratilgan faylning yo'li.
    """
    img = Image.new("RGB", CANVAS_SIZE, color=config.BRAND_COLOR_PRIMARY)
    draw = ImageDraw.Draw(img)

    # Pastki urg'u chizig'i (dizayn elementi)
    draw.rectangle(
        [(0, CANVAS_SIZE[1] - 24), (CANVAS_SIZE[0], CANVAS_SIZE[1])],
        fill=config.BRAND_COLOR_SECONDARY,
    )

    # Sarlavha matni (o'rtaga, satrlarga bo'lib)
    title_font = _load_font(config.FONT_BOLD, 72)
    wrapped_title = textwrap.wrap(title, width=18)
    total_h = len(wrapped_title) * 90
    y = (CANVAS_SIZE[1] - total_h) // 2 - 40

    for line in wrapped_title:
        bbox = draw.textbbox((0, 0), line, font=title_font)
        w = bbox[2] - bbox[0]
        x = (CANVAS_SIZE[0] - w) // 2
        draw.text((x, y), line, font=title_font, fill=config.BRAND_COLOR_TEXT)
        y += 90

    # Qo'shimcha matn (subtext), sarlavha ostida
    if subtext:
        sub_font = _load_font(config.FONT_REGULAR, 36)
        wrapped_sub = textwrap.wrap(subtext, width=32)
        y += 30
        for line in wrapped_sub:
            bbox = draw.textbbox((0, 0), line, font=sub_font)
            w = bbox[2] - bbox[0]
            x = (CANVAS_SIZE[0] - w) // 2
            draw.text((x, y), line, font=sub_font, fill=config.BRAND_COLOR_SECONDARY)
            y += 46

    # Logotipni pastki-o'ng burchakka qo'yish (agar mavjud bo'lsa)
    if os.path.exists(config.LOGO_PATH):
        logo = Image.open(config.LOGO_PATH).convert("RGBA")
        logo.thumbnail((160, 160))
        img.paste(logo, (CANVAS_SIZE[0] - logo.width - 40, 40), logo)

    # Markaz nomi yuqori chap burchakda
    name_font = _load_font(config.FONT_REGULAR, 30)
    draw.text((40, 40), config.CENTER_NAME, font=name_font, fill=config.BRAND_COLOR_TEXT)

    filename = f"{config.GENERATED_DIR}/template_{int(time.time())}.png"
    img.save(filename)
    return filename


def generate_ai_image(prompt: str) -> str:
    """
    OpenAI DALL-E orqali original rasm generatsiya qiladi.
    OPENAI_API_KEY sozlanmagan bo'lsa, avtomatik ravishda shablon rasmga tushadi.
    """
    if not config.OPENAI_API_KEY:
        # Kalit yo'q bo'lsa — shablon rasmga fallback
        return generate_template_image(title=prompt[:40])

    from openai import OpenAI
    client = OpenAI(api_key=config.OPENAI_API_KEY)

    style_note = design_profile.get_style_note()
    style_part = f" Follow this brand visual style closely: {style_note}" if style_note else ""

    full_prompt = (
        f"{prompt}. Professional, clean, modern educational branding style, "
        f"primary brand color {config.BRAND_COLOR_PRIMARY}, accent color "
        f"{config.BRAND_COLOR_SECONDARY}.{style_part} "
        f"No readable text in the image, no distorted faces."
    )

    result = client.images.generate(
        model="dall-e-3",
        prompt=full_prompt,
        size="1024x1024",
        n=1,
    )

    import requests
    image_url = result.data[0].url
    image_data = requests.get(image_url).content

    filename = f"{config.GENERATED_DIR}/ai_{int(time.time())}.png"
    with open(filename, "wb") as f:
        f.write(image_data)
    return filename


def generate_image_for_post(post_data: dict) -> str:
    """post_data (content_generator dan) asosida to'g'ri strategiyani tanlab rasm yaratadi."""
    post_type = post_data.get("post_type", "")
    strategy = config.IMAGE_STRATEGY.get(post_type, "template")

    if strategy == "ai":
        return generate_ai_image(post_data.get("image_prompt", post_data["title"]))
    else:
        return generate_template_image(
            title=post_data["title"],
            subtext=post_data.get("hashtags", ""),
        )
