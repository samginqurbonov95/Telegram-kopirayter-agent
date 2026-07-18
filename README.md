# O'quv Markazi Telegram Kontent-Agenti

Bu agent Telegram kanalingiz uchun professional matn va rasmli postlarni avtomatik
generatsiya qiladi va **siz tasdiqlagandan keyin** kanalga chiqaradi. Bot **bulutda
(server'da) 24/7 ishlaydi** — kompyuteringizni yoqib qo'yish shart emas, hech qanday
kod yozish ham kerak emas.

## Qanday ishlaydi

1. Botga `/post` yozasiz (yoki bot o'zi belgilangan vaqtda avtomatik taklif yuboradi)
2. Bot Claude AI orqali (ijodkor + til muharriri — ikki bosqichli tekshiruv bilan)
   xatosiz, kreativ post matnini yozadi
3. Bot postga mos rasm yaratadi (shablon yoki AI orqali)
4. Tayyor post sizga ✅ / 🔁 / ❌ tugmalari bilan yuboriladi
5. ✅ bossangiz — post darhol kanalga chiqadi

---

## QISM 1 — Telegram va API sozlamalari (5-10 daqiqa)

### 1. Telegram bot yaratish
Telegram'da **@BotFather** ga yozing → `/newbot` → nom bering → sizga beriladigan
**TOKEN**ni saqlab qo'ying (masalan: `123456789:AAExampleToken...`).

### 2. Botni kanalingizga admin qilib qo'shish
Kanal sozlamalari → Administrators → botingizni qidirib toping va qo'shing →
**"Post Messages"** huquqini yoqib qo'ying.

### 3. Kanal ID
- Kanal public bo'lsa: shunchaki `@kanal_username` yetarli
- Private bo'lsa: kanalga bitta post yuboring, so'ng brauzerda quyidagi manzilni
  oching (TOKEN o'rniga o'zingiznikini qo'ying):
  `https://api.telegram.org/bot<TOKEN>/getUpdates`
  U yerda `"chat":{"id":-100...}` ko'rinishidagi raqamni topasiz — shu **CHANNEL_ID**.

### 4. O'zingizning (admin) chat ID
Telegram'da **@userinfobot** ga `/start` yozing — u sizga ID raqamingizni beradi.

### 5. Anthropic API kalit
https://console.anthropic.com — ro'yxatdan o'ting, **API Keys** bo'limidan yangi
kalit yarating va saqlab qo'ying. (Matn generatsiyasi shu orqali ishlaydi;
taxminan oyiga bir necha dollar xarajat bo'ladi, postlar sonига qarab.)

### 6. (Ixtiyoriy) OpenAI API kalit — AI-rasm uchun
https://platform.openai.com — agar rasm turini "AI" qilib tanlagan bo'lsangiz kerak
bo'ladi. Bo'lmasa, tizim avtomatik shablon-rasmlardan foydalanadi (bepul).

---

## QISM 2 — Botni bulutga joylashtirish (kod yozmasdan)

Eng oson yo'l — **Railway.app** xizmati (oyiga ~5$ atrofida, kredit karta kerak,
lekin boshlang'ich bepul limit ham bor). Hammasi brauzerda, sichqoncha bilan bosib
bajariladi.

### A-qadam: Kodni GitHub'ga yuklash
1. https://github.com da bepul hisob oching (agar yo'q bo'lsa)
2. **"New repository"** tugmasini bosing, nom bering (masalan `telegram-content-agent`),
   **Create repository**ni bosing
3. Ochilgan sahifada **"uploading an existing file"** havolasini bosing
4. Menga bergan zip-faylni kompyuteringizda oching (arxivdan chiqaring) va ICHIDAGI
   BARCHA fayl va papkalarni (zip faylning o'zini emas!) shu GitHub sahifasiga
   sudrab tashlang (drag & drop)
5. Pastdagi **"Commit changes"** tugmasini bosing

### B-qadam: Railway'da deploy qilish
1. https://railway.app ga kiring, GitHub hisobingiz orqali ro'yxatdan o'ting
2. **"New Project"** → **"Deploy from GitHub repo"** → yuqorida yaratgan
   repositoryingizni tanlang
3. Railway avtomatik ravishda `requirements.txt` va `Procfile`ni aniqlab, botni
   o'rnatishni boshlaydi
4. **"Variables"** (Environment Variables) bo'limiga o'ting va quyidagilarni
   birma-bir qo'shing (Qism 1'da olgan qiymatlaringiz bilan):
   - `TELEGRAM_BOT_TOKEN`
   - `CHANNEL_ID`
   - `ADMIN_CHAT_ID`
   - `ANTHROPIC_API_KEY`
   - `OPENAI_API_KEY` (agar bo'lsa, bo'lmasa bo'sh qoldiring)
5. **"Deploy"** ni bosing — bir necha daqiqadan so'ng bot ishga tushadi

### C-qadam: Tekshirish
Telegram'da botingizga `/post` deb yozing. Bir necha soniyadan so'ng sizga rasm
va matn bilan preview kelishi kerak. ✅ bossangiz — kanalingizda chiqadi.

Shu bilan bot **doimiy, 24/7, avtomatik** ishlab turadi — kompyuteringiz
o'chirilgan bo'lsa ham hech narsa o'zgarmaydi.

> **Eslatma:** Railway o'rniga Render.com yoki PythonAnywhere kabi boshqa
> xizmatlarni ham ishlatish mumkin — jarayon deyarli bir xil (GitHub'dan ulash,
> environment variable'larni kiritish).

---

## QISM 3 — Markazingizga moslashtirish

`config.py` faylini GitHub'da to'g'ridan-to'g'ri tahrirlashingiz mumkin (fayl
ustiga bosing → qalam belgisi → o'zgartiring → **Commit changes** — Railway
avtomatik qayta deploy qiladi):

- `CENTER_NAME`, `CENTER_SUBJECTS`, `CENTER_AUDIENCE`, `CENTER_TONE`
- `BRAND_COLOR_PRIMARY`, `BRAND_COLOR_SECONDARY` — brend ranglaringiz (HEX)
- `SCHEDULE_TIMES` — bot avtomatik post taklif qiladigan vaqtlar

Logotipni qo'shish uchun `assets/logo.png` faylini GitHub'da **"Add file" →
"Upload files"** orqali yuklang (shaffof fon PNG tavsiya etiladi).

O'zbekcha harflarni (o', g', sh, ch) to'liq qo'llab-quvvatlaydigan shrift
qo'shish uchun `fonts/` papkasiga TTF faylini xuddi shu tarzda yuklang va
`config.py` dagi `FONT_BOLD` / `FONT_REGULAR` yo'lini yangilang.

---

## Botning imkoniyatlari

### 1. Erkin topshiriq asosida kreativ kontent
Botga yozma yoki **ovozli** xabar bilan topshiriq bering — masalan:
> "Kuzgi IT kurslar haqida juda kreativ post tayyorla, o'quvchilarni ilhomlantirsin"

yoki `/vazifa <matn>` buyrug'i orqali. Bot buni tushunib, kreativ post yaratadi
va rasmini ham (brend ranglari va — agar o'rnatilgan bo'lsa — namunaviy dizayn
uslubida) tayyorlaydi.

### 2. E'lonlar
Aniq ma'lumot bering — masalan:
> "20-avgustdan yangi ingliz tili guruhi ochiladi, dars kunlari dushanba-chorshanba-juma, narxi 400 ming so'm"

yoki `/elon <matn>`. Bot **faqat berilgan faktlarga tayangan holda** — hech qanday
sana, narx yoki tafsilotni o'zidan qo'shmasdan — professional e'lon matnini yozadi.

Bot xabaringizni o'zi tahlil qilib, bu "topshiriq"mi (ijodiy erkinlik bor) yoki
"e'lon"mi (aniq faktlar berilgan) ekanini avtomatik aniqlaydi — shuning uchun
buyruqsiz, oddiy yozma yoki ovozli xabar yuborishingiz ham kifoya.

**Ovozli buyruqlar uchun `OPENAI_API_KEY` shart** (Whisper orqali matnga o'giriladi).

### 3. Bir martalik dizaynni namuna sifatida o'rnatish
`/setdesign` buyrug'ini yuboring, so'ng namunaviy poster rasmingizni jo'nating.
Bot uni (Claude ko'rish qobiliyati orqali) tahlil qilib, uslubini — kompozitsiya,
rang, tipografiya xarakteri, kayfiyat — yozma tavsif sifatida saqlaydi va shundan
keyin yaratiladigan barcha AI-rasmlarni shu uslubga moslashtiradi.

> **Muhim cheklov:** bu piksel darajasida aynan bir xil nusxa emas — balki bir xil
> "ruh"da yangi rasmlar yaratishga yordam beradi. Agar rasmlar aynan bitta shablon
> asosida (masalan bir xil logotip joylashuvi, bir xil chegaralar) chiqishi kerak
> bo'lsa, buni `image_generator.py` dagi `generate_template_image()` funksiyasida
> qo'lda sozlash kerak bo'ladi — buni xohlasangiz, keyingi bosqichda siz bergan
> aniq dizaynga moslab tuzataman.

### 4. Kunlik avtomatik postlar (marketolog + yangiliklar)
`config.py` dagi `SCHEDULE_SLOTS` bo'yicha kuniga bir necha marta (standart: 4
marta) bot o'zi:
- **marketing** turida — professional marketolog/kopirayter sifatida, AIDA/PAS
  kabi freymvorklardan foydalanib, o'ta kreativ reklama-poster postini, yoki
- **news** turida — RSS orqali topilgan haqiqiy ta'lim yangiligini ijodiy post
  shaklida

tayyorlab, tasdiqlash uchun yuboradi. Vaqtlarni va turlarini `config.py` da
o'zgartirishingiz mumkin.

### 5. Xodimlarga ruxsat berish
`config.py` dagi (yoki `.env` dagi) `STAFF_CHAT_IDS` ga xodimlaringizning
Telegram chat ID'larini vergul bilan ajratib qo'shsangiz, ular ham botga
topshiriq/e'lon bera oladi (ularning postlari ham avval tasdiqlash uchun sizga
— `ADMIN_CHAT_ID`ga — yuboriladi, chunki `CHANNEL_ID`ga chiqarish faqat ✅
tugmasi orqali amalga oshadi).

Manbalar `config.py` dagi `NEWS_RSS_FEEDS` da sozlangan (hozircha gazeta.uz
asosida). Bot yig'ilgan yangiliklar orasidan ta'limga aloqador bo'lganini o'zi
tanlaydi; agar hech biri mos kelmasa, o'sha vaqt oralig'ida marketing-postga
o'tadi. Boshqa manbalarni (masalan Kun.uz, Daryo.uz, IATF) qo'shmoqchi bo'lsangiz,
avval o'sha saytning haqiqiy RSS-manzilini tekshirib, ro'yxatga qo'shing.

## Kontent sifati: ikki bosqichli AI-konveyer

Har bir post ikki AI-agent zanjiri orqali yaratiladi (`content_generator.py`):

1. **Ijodkor (Kreativ direktor)** — original, kuchli va diqqatni tortadigan
   g'oyani yozadi.
2. **Muharrir (Bosh muharrir)** — o'zbek adabiy tili, imlo, grammatika va
   tinish belgilari qoidalariga qat'iy asosda matnni tekshiradi, tuzatadi va
   yakuniy "elita" darajaga olib chiqadi.

Qoidalar to'plamini (`UZBEK_LANGUAGE_RULES`) GitHub'da fayl ichida o'zingiz
kengaytirishingiz mumkin.

## Xarajatlar haqida (taxminiy)

- **Railway hosting**: ~5$/oy (kichik loyihalar uchun boshlang'ich bepul limit bor)
- **Anthropic API**: har bir post uchun bir necha sent (kunlik 4 avtomatik post +
  qo'shimcha buyruqlar = oyiga taxminan $5-15, hajmga qarab)
- **OpenAI Whisper** (ovozli buyruqlar uchun): daqiqasiga ~$0.006 — juda arzon
- **OpenAI DALL-E** (ixtiyoriy): rasm boshiga ~$0.04
- Shablon-rasmlar (Pillow): **bepul**

## Yordam kerak bo'lsa

Agar GitHub'ga yuklashda, Railway sozlashda yoki boshqa istalgan qadamda
qiynalsangiz — qaysi qadamda ekaningizni va nima ko'rinayotganini yozing,
birga hal qilamiz.
