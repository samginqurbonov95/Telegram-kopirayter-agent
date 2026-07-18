"""
content_generator.py — Claude AI orqali "elita" darajadagi, o'zbek adabiy tili
me'yorlariga qat'iy rioya qilingan Telegram kontenti generatsiya qiladi.

Bu faylda 5 ta asosiy funksiya bor:

  1. generate_marketing_post()   — kuniga bir necha marta avtomatik ishlaydigan,
                                    professional marketolog/kopirayter sifatidagi
                                    kreativ reklama-posterlari
  2. generate_news_post()        — haqiqiy RSS yangiliklar asosida ta'lim
                                    yangiliklarini post shakliga keltiradi
  3. generate_from_task()        — admin/xodim bergan erkin topshiriq (yozma
                                    yoki ovozli) asosida maxsus kontent
  4. generate_announcement()     — admin/xodim bergan aniq ma'lumot asosida
                                    E'LON (faktlarga qat'iy sodiq, hech narsa
                                    o'ylab topilmaydi)
  5. classify_intent()           — erkin xabar "topshiriq"mi yoki "e'lon"mi
                                    ekanini aniqlaydi

Barcha ijodiy funksiyalar ikki bosqichli konveyerdan foydalanadi:
  IJODKOR (yuqori kreativlik) -> MUHARRIR (qat'iy til/imlo/punktuatsiya nazorati).
"""

import json
import random
import anthropic

import config
import design_profile

MODEL = "claude-sonnet-4-6"

# ---------------------------------------------------------------------------
# O'ZBEK ADABIY TILI ME'YORLARI — muharrir agent shu qoidalarga qat'iy amal qiladi
# ---------------------------------------------------------------------------
UZBEK_LANGUAGE_RULES = """
O'ZBEK ADABIY TILI, IMLO VA PUNKTUATSIYA QOIDALARI (QAT'IY RIOYA QILINSIN):

1. IMLO:
   - Faqat o'zbek lotin alifbosidagi rasmiy harflardan foydalanilsin: o', g', sh, ch, ng
     harflari to'g'ri va izchil yozilsin.
   - Apostrof (') faqat o' va g' harflarida hamda tutuq belgisi o'rnida ishlatiladi.
   - Qo'shma so'zlar imlo lug'atiga muvofiq qo'shib yoki chiziqcha bilan yozilsin.
   - Chet so'zlar o'zbek tilida qabul qilingan yozilishida ishlatilsin; imkon qadar
     o'zbekcha muqobili afzal ko'rilsin, lekin tushunarsiz arxaik so'zlarga berilmasin.

2. GRAMMATIKA:
   - Gap bo'laklari kelishigi, egalik va shaxs-son qo'shimchalari to'g'ri qo'llanilsin.
   - Fe'l zamonlari matn mazmuniga mos va izchil ishlatilsin.
   - Gaplar grammatik jihatdan to'liq va mantiqan bog'liq bo'lsin.
   - Rus/ingliz tilidan so'zma-so'z tarjima qilingan noqulay iboralar (kalька)
     ishlatilmasin — tabiiy o'zbekcha ifoda uslubi saqlansin.

3. PUNKTUATSIYA:
   - Vergul qo'shma va murakkab qo'shma gaplarda, sanab o'tishlarda, kirish so'z
     va birikmalardan keyin qoidaga muvofiq qo'yilsin.
   - Har bir gap mos tinish belgisi bilan yakunlansin; ortiqcha/takroriy tinish
     belgilariga yo'l qo'yilmasin.
   - Qo'shtirnoq, qavs va tire o'rinli va qoidaga muvofiq ishlatilsin.
   - Emoji tinish belgisi o'rnini bosmaydi — gap baribir grammatik va punktuatsion
     jihatdan to'g'ri tugallangan bo'lsin.

4. USLUB:
   - Matn sof adabiy tilda, ammo jonli va o'quvchiga yaqin ohangda yozilsin.
   - Shablon, sayoz, "Biz sifatli ta'lim beramiz" kabi bayoz iboralardan QATЪIY
     qochilsin — o'rniga aniq, obrazli va yodda qoladigan ifodalar ishlatilsin.
   - Matn diqqatni birinchi jumladanoq tortsin (kuchli "hook").
"""


def _content_brief() -> str:
    return f"""
O'QUV MARKAZI HAQIDA MA'LUMOT:
- Nomi: {config.CENTER_NAME}
- Yo'nalishlar: {config.CENTER_SUBJECTS}
- Auditoriya: {config.CENTER_AUDIENCE}
- Ohang (tone): {config.CENTER_TONE}
- Manzil: {config.CENTER_LOCATION}
"""


def _json_format_instruction() -> str:
    return """
Faqat quyidagi JSON formatda javob ber, boshqa hech narsa yozma (izoh, tushuntirish
yoki markdown belgilarisiz):
{
  "title": "Postning qisqa sarlavhasi (rasm uchun, 3-6 so'z)",
  "body": "Telegram kanaliga chiqadigan to'liq post matni",
  "hashtags": "#tegishli #hashtaglar",
  "image_prompt": "Rasm tavsifi, ingliz tilida, professional, brendga mos, odamlar yuzi aniq bo'lmasin"
}
"""


def _call_claude(system_prompt: str, user_prompt: str, temperature: float, max_tokens: int = 900) -> str:
    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    response = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        temperature=temperature,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    raw = response.content[0].text.strip()
    return raw.replace("```json", "").replace("```", "").strip()


def _safe_json_parse(raw_text: str, fallback_title: str) -> dict:
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        return {
            "title": fallback_title,
            "body": raw_text,
            "hashtags": "",
            "image_prompt": f"{config.CENTER_NAME} education center, professional, modern",
        }


def _run_pipeline(creative_system: str, editor_system: str, user_prompt: str,
                   creative_temp: float = 1.0, editor_temp: float = 0.4,
                   fallback_title: str = "Post") -> dict:
    """Ijodkor -> Muharrir ikki bosqichli konveyer."""
    draft_raw = _call_claude(creative_system, user_prompt, temperature=creative_temp)
    draft = _safe_json_parse(draft_raw, fallback_title=fallback_title)

    editor_user_prompt = (
        "Quyidagi post loyihasini yuqoridagi barcha qoidalarga muvofiq tekshirib, "
        "tahrirlab, yakuniy holatga keltir:\n\n" + json.dumps(draft, ensure_ascii=False)
    )
    final_raw = _call_claude(editor_system, editor_user_prompt, temperature=editor_temp)
    final_data = _safe_json_parse(final_raw, fallback_title=draft.get("title", fallback_title))
    return final_data


def _design_style_hint() -> str:
    note = design_profile.get_style_note()
    if not note:
        return ""
    return f"\n\nBREND DIZAYN USLUBI (avval yuborilgan namunaviy poster asosida): {note}\n"


# ---------------------------------------------------------------------------
# 1. MARKETING POSTI — avtomatik, kuniga bir necha marta
# ---------------------------------------------------------------------------

def _marketing_creative_system() -> str:
    return f"""Sen O'zbekistondagi eng yuqori toifali marketolog va kopirayter-strategsan.
Yirik ta'lim brendlari uchun ijtimoiy tarmoq marketingini yuritishda o'n yillik
tajribaga egasan, AIDA (Attention-Interest-Desire-Action) va PAS
(Problem-Agitate-Solution) kabi kopirayting freymvorklarini mohirona qo'llaysan.

{_content_brief()}
{_design_style_hint()}
VAZIFANG:
"{config.CENTER_NAME}" uchun bugungi kunda ijtimoiy tarmoqda e'lon qilinadigan,
o'ta kreativ va strategik jihatdan kuchli reklama-post g'oyasini yoz. Bu
o'quvchini harakatga undaydigan, hissiyotga ta'sir qiluvchi, aniq bir og'riq
nuqtasi (masalan vaqt yo'qotish, ish topolmaslik, tildan qo'rqish) yoki orzuni
(karyera, yangi imkoniyatlar) nishonga oluvchi post bo'lsin.

QAT'IY TAQIQ: shablon jumlalar ("Biz sifatli ta'lim beramiz", "Bizga qo'shiling"
kabi bayoz iboralar), soxta statistika yoki asossiz va'dalar ishlatilmasin.
Har safar boshqacha uslub, boshqacha kirish jumlasi va boshqacha ijodiy
yondashuv qo'llan — takrorlanish sezilmasin.

{_json_format_instruction()}
"""


def _marketing_editor_system() -> str:
    return f"""Sen o'zbek adabiy tilining eng yetuk bilimdoni va bosh muharririsan,
shuningdek professional marketing-muharrir sifatida ham ishlaysan.

{_content_brief()}
{UZBEK_LANGUAGE_RULES}

VAZIFANG (QAT'IY BAJARILSIN):
1. Berilgan loyihadagi HAR BIR imlo, grammatik va punktuatsion xatoni tuzat.
2. Matnni yanada kreativ, obrazli va ta'sirchan qil, lekin marketing g'oyasini saqla.
3. Kuchli chaqiruv (call-to-action) borligini tekshir, yo'q bo'lsa qo'sh.
4. Soxta statistika yoki tekshirilmagan da'volar bo'lsa — olib tashla.
5. Klishe va sayoz jumlalarni yo'q qil.

{_json_format_instruction()}
"""


def generate_marketing_post(topic: str = None) -> dict:
    user_prompt = "Bugungi marketing postini yarat."
    if topic:
        user_prompt += f" Mavzu/urg'u: {topic}."
    else:
        user_prompt += " Mavzuni o'zing strategik jihatdan tanla."

    result = _run_pipeline(
        _marketing_creative_system(), _marketing_editor_system(), user_prompt,
        creative_temp=1.0, editor_temp=0.4, fallback_title="Marketing post",
    )
    result["post_type"] = "marketing_post"
    return result


# ---------------------------------------------------------------------------
# 2. TA'LIM YANGILIKLARI POSTI — haqiqiy RSS ma'lumot asosida
# ---------------------------------------------------------------------------

def pick_relevant_news(headlines: list) -> dict:
    """Berilgan yangiliklar ro'yxatidan ta'limga eng oid bittasini Claude orqali tanlaydi."""
    if not headlines:
        return None

    listing = "\n".join(
        f"{i+1}. {h['title']} — {h['summary'][:150]}" for i, h in enumerate(headlines)
    )
    prompt = f"""Quyidagi yangiliklar ro'yxatidan FAQAT ta'lim, bilim olish, maktab,
universitet, o'quv dasturlari, stipendiya yoki shu kabi mavzularga oid bo'lganini
tanla. Agar hech biri ta'limga oid bo'lmasa, "yo'q" deb javob ber.

{listing}

Faqat shu formatda javob ber: {{"index": <raqam yoki -1>}}"""

    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    response = client.messages.create(
        model=MODEL, max_tokens=100, temperature=0,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = response.content[0].text.strip().replace("```json", "").replace("```", "")
    try:
        idx = json.loads(raw).get("index", -1)
        if 0 <= idx < len(headlines):
            return headlines[idx]
    except (json.JSONDecodeError, TypeError):
        pass
    return None


def _news_creative_system() -> str:
    return f"""Sen ta'lim sohasi bo'yicha professional jurnalist-kopirayterisan.

{_content_brief()}
{_design_style_hint()}
VAZIFANG:
Senga berilgan HAQIQIY yangilik asosida "{config.CENTER_NAME}" kanali uchun
qiziqarli, o'qishga arzigulik post yoz. Yangilikni o'quvchiga nima uchun
muhimligini tushuntir va, agar tabiiy chiqsa, uni markazning yo'nalishlari bilan
bog'lab, nozik tarzda markazni eslat (lekin bu o'rinli bo'lmasa, majburlama).

QAT'IY QOIDA: FAQAT senga berilgan ma'lumotdan foydalan. Hech qanday yangi fakt,
raqam, sana yoki tafsilot o'ylab topma. Manba nomini matn oxirida qisqacha eslat.

{_json_format_instruction()}
"""


def _news_editor_system() -> str:
    return f"""Sen o'zbek adabiy tilining eng yetuk bilimdoni va bosh muharririsan.

{UZBEK_LANGUAGE_RULES}

VAZIFANG:
1. Imlo, grammatika, punktuatsiya xatolarini to'liq tuzat.
2. Matnni yanada ravon va qiziqarli qil.
3. QAT'IY: hech qanday yangi fakt, raqam yoki da'vo QO'SHMA — faqat berilgan
   ma'lumot doirasida tahrirla.
4. Klişe jumlalarni yo'q qil.

{_json_format_instruction()}
"""


def generate_news_post() -> dict:
    """RSS manbalardan ta'limga oid yangilikni topib, post shakliga keltiradi."""
    import news

    headlines = news.fetch_latest_headlines()
    chosen = pick_relevant_news(headlines)

    if not chosen:
        # Ta'limga oid yangilik topilmasa, marketing postiga fallback qilamiz
        result = generate_marketing_post()
        result["post_type"] = "news_post_fallback"
        return result

    user_prompt = (
        f"Yangilik sarlavhasi: {chosen['title']}\n"
        f"Qisqacha mazmuni: {chosen['summary']}\n"
        f"Manba: {chosen['source']}\n"
        f"Havola: {chosen['link']}"
    )

    result = _run_pipeline(
        _news_creative_system(), _news_editor_system(), user_prompt,
        creative_temp=0.8, editor_temp=0.3, fallback_title=chosen["title"],
    )
    result["post_type"] = "news_post"
    return result


# ---------------------------------------------------------------------------
# 3. ERKIN TOPSHIRIQ ASOSIDA KONTENT (matnli yoki ovozli buyruq)
# ---------------------------------------------------------------------------

def _task_creative_system() -> str:
    return f"""Sen O'zbekistondagi eng yuqori toifali kreativ direktor va kopirayterisan.

{_content_brief()}
{_design_style_hint()}
VAZIFANG:
Admin yoki xodim sizga quyidagi topshiriqni berdi. Shu topshiriq asosida
"{config.CENTER_NAME}" uchun juda kreativ, professional Telegram post yoz.
Topshiriqda aytilgan barcha muhim tafsilotlarni (sana, narx, joy, shartlar va
h.k.) ANIQ saqlab qol — ularni o'zgartirma yoki o'ylab qo'shimcha qilma, faqat
ijodiy taqdimotini yaxshila.

{_json_format_instruction()}
"""


def _task_editor_system() -> str:
    return f"""Sen o'zbek adabiy tilining eng yetuk bilimdoni va bosh muharririsan.

{UZBEK_LANGUAGE_RULES}

VAZIFANG:
1. Imlo, grammatika, punktuatsiya xatolarini to'liq tuzat.
2. Matnni yanada kreativ va ta'sirchan qil.
3. QAT'IY: berilgan topshiriqdagi faktlarni (sana, narx, shart va h.k.) o'zgartirma
   yoki yangi fakt qo'shma.
4. Klişe jumlalarni yo'q qil.

{_json_format_instruction()}
"""


def generate_from_task(task_text: str) -> dict:
    result = _run_pipeline(
        _task_creative_system(), _task_editor_system(),
        f"Topshiriq: {task_text}",
        creative_temp=1.0, editor_temp=0.4, fallback_title="Maxsus post",
    )
    result["post_type"] = "custom_task"
    return result


# ---------------------------------------------------------------------------
# 4. E'LON — faktlarga qat'iy sodiq
# ---------------------------------------------------------------------------

def _announcement_system() -> str:
    return f"""Sen o'zbek adabiy tilining eng yetuk bilimdoni, professional
matbuot-kotib va muharrirsan.

{_content_brief()}
{UZBEK_LANGUAGE_RULES}

VAZIFANG:
Admin yoki xodim sizga quyidagi ma'lumotni berdi. Shu asosda "{config.CENTER_NAME}"
kanali uchun aniq, ishonchli va professional E'LON matnini tayyorla.

QAT'IY QOIDALAR:
- FAQAT berilgan ma'lumotdan foydalan. Hech qanday yangi fakt, sana, narx yoki
  tafsilot O'YLAB TOPMA yoki O'ZGARTIRMA — bu juda muhim, chunki bu haqiqiy e'lon.
- Matn aniq, tushunarli va ishonch uyg'otadigan uslubda bo'lsin — ortiqcha
  bezaklarga berilmasdan, lekin quruq-rasmiy ham bo'lmasdan.
- Imlo, grammatika va punktuatsiyada birorta xato bo'lmasin.

{_json_format_instruction()}
"""


def generate_announcement(info_text: str) -> dict:
    raw = _call_claude(_announcement_system(), f"Ma'lumot: {info_text}", temperature=0.5)
    result = _safe_json_parse(raw, fallback_title="E'lon")
    result["post_type"] = "elon"
    return result


# ---------------------------------------------------------------------------
# 5. INTENT ANIQLASH (erkin xabar: topshiriqmi yoki e'lonmi?)
# ---------------------------------------------------------------------------

def classify_intent(text: str) -> str:
    """
    Berilgan erkin matn "topshiriq" (kreativ kontent so'ralmoqda) yoki
    "elon" (aniq faktik e'lon berilmoqda) ekanini aniqlaydi.
    """
    prompt = f"""Quyidagi xabar o'quv markazi Telegram-botiga yuborilgan buyruq.
Bu xabar quyidagilardan qaysi biriga ko'proq mos kelishini aniqla:
- "elon": xabarda aniq, faktik ma'lumot bor (masalan yangi guruh, sana, narx,
  imtihon natijasi, dam olish kunlari va h.k.) va buni to'g'ridan-to'g'ri e'lon
  qilish so'ralmoqda.
- "topshiriq": xabarda ijodiy kontent yaratish so'ralmoqda (masalan "motivatsion
  post yoz", "yozgi kurslar haqida qiziqarli post tayyorla" kabi ijodiy erkinlik
  bor topshiriq).

Xabar: "{text}"

Faqat shu formatda javob ber: {{"intent": "elon"}} yoki {{"intent": "topshiriq"}}"""

    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    response = client.messages.create(
        model=MODEL, max_tokens=50, temperature=0,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = response.content[0].text.strip().replace("```json", "").replace("```", "")
    try:
        intent = json.loads(raw).get("intent", "topshiriq")
        return intent if intent in ("elon", "topshiriq") else "topshiriq"
    except json.JSONDecodeError:
        return "topshiriq"
