from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_start_keyboard() -> InlineKeyboardMarkup:
    """Start xabari uchun inline tugmalar."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="ℹ️ Yo'riqnoma", callback_data="help_info"),
                InlineKeyboardButton(text="🔎 Qidirish", callback_data="how_to_search")
            ]
        ]
    )
    return keyboard

def get_movie_keyboard() -> InlineKeyboardMarkup:
    """Kino uzatilganda chiqadigan inline tugmalar."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔄 Boshqa kino qidirish", callback_data="search_again")
            ]
        ]
    )
    return keyboard

def get_back_keyboard() -> InlineKeyboardMarkup:
    """Orqaga qaytish tugmasi."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="◀️ Asosiy menyu", callback_data="back_to_main")
            ]
        ]
    )
    return keyboard

def get_admin_keyboard() -> InlineKeyboardMarkup:
    """Admin paneli uchun tugmalar (to'liq kanalsiz)."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats"),
                InlineKeyboardButton(text="🎬 So'nggi kinolar", callback_data="admin_movies")
            ]
        ]
    )
    return keyboard

def get_admin_back_keyboard() -> InlineKeyboardMarkup:
    """Admin paneli ichidan orqaga qaytish tugmasi."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="◀️ Admin panelga qaytish", callback_data="admin_back")
            ]
        ]
    )
    return keyboard
