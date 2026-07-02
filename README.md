# Nafas fiziologiyasi test boti — o'rnatish va ishga tushirish

## 1-qadam: BotFather orqali bot yaratish
1. Telegram'da @BotFather'ni oching
2. `/newbot` buyrug'ini yuboring
3. Bot uchun nom bering (masalan: "Nafas Fiziologiyasi Test")
4. Username bering — oxiri "bot" bilan tugashi kerak (masalan: nafas_fiziologiya_bot)
5. BotFather sizga TOKEN beradi (masalan: `123456789:AAExampleTokenHere`) — buni saqlab qo'ying, hech kimga bermang

## 2-qadam: Kompyuteringizga kerakli dasturlarni o'rnatish
Python 3.10 yoki undan yuqori versiyasi kerak. Terminalda:

```bash
pip install -r requirements.txt
```

## 3-qadam: Tokenni o'rnatish
Terminalda (Linux/Mac):
```bash
export TELEGRAM_TOKEN="sizning_tokeningiz"
```

Windows (PowerShell):
```powershell
$env:TELEGRAM_TOKEN="sizning_tokeningiz"
```

## 4-qadam: Botni ishga tushirish
```bash
python bot.py
```

Terminal oynasi ochiq turishi kerak — bot shu vaqt davomida ishlaydi.

## 5-qadam: Botni sinab ko'rish
Telegram'da o'z botingizni toping (username orqali), `/start` yuboring, keyin `/quiz` yuboring — test avtomatik boshlanadi. Har bir savol uchun 30 soniya vaqt beriladi (buni bot.py faylidagi `QUIZ_TIME_LIMIT` qiymatini o'zgartirib sozlash mumkin).

## Fayllar tuzilishi
- `bot.py` — botning asosiy kodi
- `questions.json` — 80 ta savol (savol, variantlar, to'g'ri javob)
- `requirements.txt` — kerakli kutubxonalar ro'yxati

## Botni doimiy ishlashini xohlasangiz
Yuqoridagi usul kompyuteringiz yoqilib turgandagina ishlaydi. Agar bot 24/7 ishlab tursin desangiz, uni bepul serverga (masalan Render, Railway yoki PythonAnywhere) joylashtirish kerak bo'ladi — buni ham istasangiz qadam-baqadam ko'rsatib beraman.

## Savollarni o'zgartirish
`questions.json` faylini istalgan matn muharriri bilan ochib, savol/variant/to'g'ri javobni tahrirlashingiz mumkin. Format:
```json
{
  "question": "Savol matni",
  "options": ["variant1", "variant2", "variant3", "variant4"],
  "correct_option_id": 0
}
```
`correct_option_id` — to'g'ri javobning `options` ro'yxatidagi tartib raqami (0 dan boshlanadi).
