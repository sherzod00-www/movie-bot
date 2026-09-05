# 🎬 MovieHub Telegram Kino Boti

Professional, tezkor va mutlaqo **mustaqil** Telegram kino boti.
Telegram kanallarsiz, to'g'ridan-to'g'ri botning o'ziga kinolarni yuklash orqali ishlaydi.

---

## 🌟 Asosiy Imkoniyatlar

1. **Mustaqil Baza (Kanalsiz):**
   - Endi hech qanday kanal yaratish yoki sozlash shart emas!
   - Admin shunchaki kinoni (videoni) to'g'ridan-to'g'ri botga yuboradi va uning izohiga (caption) kodini yozadi (masalan: `Kod: 1`).
   - Bot kinoni o'zining SQLite bazasiga saqlaydi va bir zumda kod orqali tarqatishga tayyor bo'ladi.

2. **Aqlli Kod Qidiruvi (Fuzzy Matching):**
   - Foydalanuvchi kodni probellar bilan yozsa ham (`2 34`, ` 12 `, `kod: 5`) bot ortiqcha belgilarni tozalab aniq kinoni topib beradi.
   - Mavjud bo'lmagan kod kiritilganda chiroyli xabar chiqadi.

3. **To'liq Xavfsizlik:**
   - Botga faqat **Siz (Admin - `1220090530`)** kino yuklashingiz yoki o'chirishingiz mumkin.
   - Boshqa foydalanuvchilar video yuborsa yoki `/admin`, `/del` buyrug'ini yozsa, bot hech qanday ruxsat bermaydi.

---

## 📥 Kino Yuklash Qo'llanmasi (Juda Oson!)

1. Telegramda **`@mov1ehubbot`** ga kiring.
2. Kinoning video faylini botga yuboring.
3. Yuborishdan oldin uning izohiga (caption) kino ma'lumotlarini va kodini yozing:

```text
🎬 Kino nomi: Forsaj 10
🌍 Davlat: AQSH
🎭 Janr: Jangari
⏱ Davomiyligi: 2:10:00
🎙 Til: O'zbekcha
📅 Yili: 2023

🔑 Kod: 1
```

*(Yoki shunchaki `Kod: 1` deb yozib yuborsangiz ham bo'ladi)*

4. Bot darhol sizga:
   > 🎬 **Kino bot bazasiga muvaffaqiyatli saqlandi!**
   > 🔑 **Kodi:** `1`
   > 🍿 **Nomi:** Forsaj 10
   
   deb tasdiq beradi!

---

## 🗑 Kinolarni O'chirish (Faqat Siz Uchun)

* **Bitta kinoni o'chirish:** `/del [kod]` *(Masalan: `/del 1`)*
* **Barcha kinolarni tozalash:** `/delall`
* **Admin paneli:** `/admin`

---

## 🚀 Botni Ishga Tushirish

1. `movie_bot` papkasidagi **`run.bat`** faylini ikki marta bosing.
2. Bot faol bo'ladi va kinolarni uzatishga tayyor turadi!
