"""
image_generator.py — postlar uchun rasm yaratadi.

ASOSIY REJIM — QAT'IY BREND SHABLONI:
Barcha posterlar `assets/poster_template.png` faylidagi (siz bir marta bergan
namunaviy dizayn) FON USTIGA matn chizish orqali yaratiladi. Fon — logotip,
yorug'lik effektlari, umumiy uslub — HECH QACHON o'zgarmaydi. Faqat sarlavha
matni (va belgi/badge matni) har safar yangilanadi.

Agar `assets/poster_template.png` topilmasa, tizim eski (oddiy rangli
kartochka) rejimiga avtomatik o'tadi — botning ishlashi to'xtamaydi.
"""

import os
import time
import textwrap
from PIL import Image, ImageDraw, ImageFont

import config
import design_profile

os.makedirs(config.GENERATED_DIR, exist_ok=True)

CANVAS_SIZE = (1080, 1080)
POSTER_TEMPLATE_PATH = "assets/poster_template.png"

# Namuna dizayndagi hududlar (1024x1280 asl rasm o'lchamiga nisbatan aniqlangan,
# boshqa o'lchamdagi shablon yuklasangiz, bu koordinatalarni moslashtirish kerak bo'ladi)
BADGE_BOX = (300, 330, 724, 390)      # (x1, y1, x2, y2) — kichik "belgi" maydoni
HEADLINE_BOX = (40, 400, 984, 705)    # katta sarlavha matni maydoni


def _load_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def _wrap_to_width(draw, text, font, max_width):
    words = text.split()
    lines, current = [], ""
    for word in words:
        trial = f"{current} {word}".strip()
        bbox = draw.textbbox((0, 0), trial, font=font)
        if bbox[2] - bbox[0] <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _fit_headline(draw, text, box_width, box_height, font_path, max_size=76, min_size=34):
    """Matn box ichiga sig'guncha shrift o'lchamini kamaytirib boradi."""
    size = max_size
    while size >= min_size:
        font = _load_font(font_path, size)
        lines = _wrap_to_width(draw, text, font, box_width)
        line_height = int(size * 1.18)
        total_height = line_height * len(lines)
        if total_height <= box_height:
            return font, lines, line_height
        size -= 4
    font = _load_font(font_path, min_size)
    lines = _wrap_to_width(draw, text, font, box_width)
    return font, lines, int(min_size * 1.18)


def generate_branded_poster(headline: str, badge_text: str = "") -> str:
    """
    Qat'iy brend shabloni (assets/poster_template.png) ustiga sarlavha va
    belgi matnini chizadi. Fon HECH QACHON o'zgarmaydi.
    """
    base = Image.open(POSTER_TEMPLATE_PATH).convert("RGBA")
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # --- Belgi (badge) matni ---
    if badge_text:
        bx1, by1, bx2, by2 = BADGE_BOX
        draw.rounded_rectangle([bx1, by1, bx2, by2], radius=22, fill=(4, 10, 40, 190))
        badge_font = _load_font(config.FONT_BOLD, 26)
        bbox = draw.textbbox((0, 0), badge_text.upper(), font=badge_font)
        tw = bbox[2] - bbox[0]
        tx = bx1 + ((bx2 - bx1) - tw) // 2
        ty = by1 + ((by2 - by1) - (bbox[3] - bbox[1])) // 2 - bbox[1]
        draw.text((tx, ty), badge_text.upper(), font=badge_font, fill=(255, 255, 255, 255))

    # --- Sarlavha matni ---
    hx1, hy1, hx2, hy2 = HEADLINE_BOX
    box_w, box_h = hx2 - hx1, hy2 - hy1
    draw.rounded_rectangle([hx1, hy1, hx2, hy2], radius=28, fill=(2, 8, 45, 165))

    font, lines, line_height = _fit_headline(draw, headline, box_w - 40, box_h - 30, config.FONT_BOLD)
    total_h = line_height * len(lines)
    y = hy1 + ((box_h - total_h) // 2)
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        lw = bbox[2] - bbox[0]
        x = hx1 + ((box_w - lw) // 2)
        draw.text((x, y), line, font=font, fill=(255, 255, 255, 255))
        y += line_height

    result = Image.alpha_composite(base, overlay).convert("RGB")
    filename = f"{config.GENERATED_DIR}/poster_{int(time.time())}.png"
    result.save(filename)
    return filename


# ---------------------------------------------------------------------------
# ZAXIRA REJIM (agar assets/poster_template.png topilmasa)
# ---------------------------------------------------------------------------

def generate_template_image(title: str, subtext: str = "") -> str:
    """Oddiy rangli kartochka (agar brend shabloni yuklanmagan bo'lsa ishlatiladi)."""
    img = Image.new("RGB", CANVAS_SIZE, color=config.BRAND_COLOR_PRIMARY)
    draw = ImageDraw.Draw(img)
    draw.rectangle([(0, CANVAS_SIZE[1] - 24), (CANVAS_SIZE[0], CANVAS_SIZE[1])], fill=config.BRAND_COLOR_SECONDARY)

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

    if os.path.exists(config.LOGO_PATH):
        logo = Image.open(config.LOGO_PATH).convert("RGBA")
        logo.thumbnail((160, 160))
        img.paste(logo, (CANVAS_SIZE[0] - logo.width - 40, 40), logo)

    name_font = _load_font(config.FONT_REGULAR, 30)
    draw.text((40, 40), config.CENTER_NAME, font=name_font, fill=config.BRAND_COLOR_TEXT)

    filename = f"{config.GENERATED_DIR}/template_{int(time.time())}.png"
