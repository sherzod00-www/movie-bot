import re
from typing import Optional, Dict, Any

def extract_code_from_user_input(text: str) -> Optional[str]:
    """
    Foydalanuvchi yuborgan xabardan kino kodini ajratib olish va tozalash.
    """
    if not text:
        return None
    
    clean_text = text.strip()
    
    # 1. Aniq kalit so'zlar bilan qidirish (kod, kodi, kino, 🔑, #, №)
    prefix_match = re.search(
        r'(?:🔑|kod[ia]?|code|kino|№|#)\s*[:=\-]?\s*([\d\s]+)',
        clean_text,
        re.IGNORECASE
    )
    if prefix_match:
        digits = re.sub(r'\s+', '', prefix_match.group(1))
        if digits.isdigit():
            return digits

    # 2. Agar butun matndan probellarni olib tashlaganda to'liq raqam qolsa (masalan: "2 34", " 234 ")
    no_spaces = re.sub(r'\s+', '', clean_text)
    if no_spaces.isdigit():
        return no_spaces

    # 3. Agar matnda faqat bitta raqamlar to'plami bo'lsa (masalan "12-kino" yoki "kino: 12")
    digits_list = re.findall(r'\d+', clean_text)
    if len(digits_list) == 1:
        return digits_list[0]
    elif len(digits_list) > 1 and re.fullmatch(r'[\d\s]+', clean_text):
        # Agar faqat raqamlar va probellardan iborat bo'lsa: "1 2 3" -> "123"
        return ''.join(digits_list)

    return None

def extract_movie_info_from_caption(caption: str) -> Optional[Dict[str, Any]]:
    """
    Telegram kanaldagi kino posti tavsifidan (caption) ma'lumotlarni o'qib olish.
    """
    if not caption:
        return None

    clean_caption = caption.strip()
    code = None

    # 1-variant: 🔑 Kod: 1, Kod: 1, Kodi: 1, kod 1, Code: 1, №1, #1
    code_match = re.search(r'(?:🔑|kod[ia]?|code|№|#)\s*[:=\-]?\s*(\d+)', clean_caption, re.IGNORECASE)
    if code_match:
        code = code_match.group(1).strip()
    
    # 2-variant: Agar shunchaki bitta raqam yozilgan bo'lsa (masalan "1" yoki " 12 ")
    if not code and clean_caption.isdigit():
        code = clean_caption

    # 3-variant: "1-kino" yoki "1 kino"
    if not code:
        alt_match = re.search(r'(\d+)\s*(?:-?\s*kino|-?\s*qism)', clean_caption, re.IGNORECASE)
        if alt_match:
            code = alt_match.group(1).strip()

    # 4-variant: Matn ichidagi yagona raqam bo'lsa
    if not code:
        all_digits = re.findall(r'\b\d+\b', clean_caption)
        if len(all_digits) == 1:
            code = all_digits[0]

    if not code:
        return None

    # Kino nomini aniqlash (ixtiyoriy)
    title = None
    title_match = re.search(r'🎬\s*(?:Kino\s*nomi\s*[:=\-]?\s*)?([^\n\r]+)', caption, re.IGNORECASE)
    if title_match:
        title = title_match.group(1).strip()
    
    if not title:
        title = f"Kino #{code}"

    return {
        "code": code,
        "title": title,
        "raw_caption": caption
    }
