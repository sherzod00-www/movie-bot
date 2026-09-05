import logging
from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramAPIError

import database as db
from parser import extract_code_from_user_input
from keyboards.inline import (
    get_start_keyboard,
    get_movie_keyboard,
    get_back_keyboard
)

logger = logging.getLogger(__name__)
router = Router(name="user_router")

@router.message(CommandStart())
async def cmd_start(message: Message):
    """
    Foydalanuvchi /start buyrug'ini bosganda xush kelibsiz xabari.
    """
    # Foydalanuvchini bazaga kiritish
    await db.add_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )

    user_name = message.from_user.first_name or "Foydalanuvchi"
    
    text = (
        f"🎬 **Assalomu alaykum, {user_name}!**\n\n"
        "🍿 **MovieHub** kino botiga xush kelibsiz!\n\n"
        "✨ **Kino kodini kiriting** va sevimli kinongizni darhol tomosha qiling!\n\n"
        "💡 *Masalan:* `1`, `12` yoki `234`"
    )

    await message.answer(
        text=text,
        reply_markup=get_start_keyboard(),
        parse_mode="Markdown"
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    """Botdan foydalanish bo'yicha yordam xabari."""
    help_text = (
        "📖 **Botdan qanday foydalaniladi?**\n\n"
        "1️⃣ O'zingiz qidirayotgan kinoning kodini oling (masalan: `12`).\n"
        "2️⃣ Botga shu kodni oddiy xabar sifatida yuboring.\n"
        "3️⃣ Bot sizga kinoni to'g'ridan-to'g'ri yetkazib beradi!\n\n"
        "⚠️ *Agar xato bilan `1 2` yoki `  12  ` deb yozsangiz ham bot buni to'g'ri tushunadi.*"
    )
    await message.answer(help_text, reply_markup=get_start_keyboard(), parse_mode="Markdown")

@router.callback_query(F.data == "help_info")
async def cb_help_info(callback: CallbackQuery):
    """Inline tugma orqali yo'riqnoma."""
    help_text = (
        "ℹ️ **Botdan foydalanish yo'riqnomasi:**\n\n"
        "1. Kino kodini botga oddiy xabar sifatida yuboring (masalan: `1`, `15`, `256`).\n"
        "2. Bot bir necha soniyada kinoni sizga yetkazib beradi!\n\n"
        "🔢 **Hozir kodni yozib yuborishingiz mumkin!**"
    )
    await callback.message.edit_text(help_text, reply_markup=get_back_keyboard(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "how_to_search")
@router.callback_query(F.data == "search_again")
async def cb_search_prompt(callback: CallbackQuery):
    """Kino qidirish bo'yicha taklif."""
    await callback.message.answer(
        "🔢 **Marhamat, kino kodini kiriting:**\n\n*(Masalan: `1`, `12`, `234`)*",
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "back_to_main")
async def cb_back_to_main(callback: CallbackQuery):
    """Asosiy menyuga qaytish."""
    user_name = callback.from_user.first_name or "Foydalanuvchi"
    text = (
        f"🎬 **Assalomu alaykum, {user_name}!**\n\n"
        "✨ **Kino kodini kiriting** va tomosha qilishni boshlang!\n\n"
        "💡 *Masalan:* `1`, `12` yoki `234`"
    )
    await callback.message.edit_text(
        text=text,
        reply_markup=get_start_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.message(F.text)
async def handle_user_message(message: Message, bot: Bot):
    """
    Foydalanuvchi yuborgan barcha matnli xabarlarni tekshirish va kino kodini topish.
    """
    # Agar xabar buyruq (command) bo'lsa o'tkazib yuborish
    if message.text.startswith("/"):
        return

    raw_text = message.text
    
    # Probel va boshqa xatoliklarni tozalab kodni ajratib olish
    code = extract_code_from_user_input(raw_text)

    if not code:
        await message.answer(
            "⚠️ **Iltimos, faqat kino kodini kiriting!**\n\n"
            "💡 *Masalan:* `1`, `12` yoki `234`",
            parse_mode="Markdown"
        )
        return

    # Bazadan qidirish
    movie = await db.get_movie(code)

    if not movie:
        # Kino topilmadi: kanal havolasisiz toza xabar
        await message.answer(
            "😔 **Kechirasiz, kino mavjud emas!**\n\n"
            f"🔍 Siz kiritgan kod: `{code}`\n\n"
            "Iltimos, kodni to'g'ri kiritganingizga ishonch hosil qiling.",
            parse_mode="Markdown"
        )
        return

    # Kino topildi - bot bazasidagi file_id orqali yuborish
    file_id = movie["file_id"]
    file_type = movie.get("file_type", "video")
    caption = movie.get("caption")

    try:
        if file_type == "photo":
            await bot.send_photo(
                chat_id=message.chat.id,
                photo=file_id,
                caption=caption,
                reply_markup=get_movie_keyboard()
            )
        elif file_type == "document":
            await bot.send_document(
                chat_id=message.chat.id,
                document=file_id,
                caption=caption,
                reply_markup=get_movie_keyboard()
            )
        elif file_type == "animation":
            await bot.send_animation(
                chat_id=message.chat.id,
                animation=file_id,
                caption=caption,
                reply_markup=get_movie_keyboard()
            )
        elif file_type == "audio":
            await bot.send_audio(
                chat_id=message.chat.id,
                audio=file_id,
                caption=caption,
                reply_markup=get_movie_keyboard()
            )
        else: # video
            await bot.send_video(
                chat_id=message.chat.id,
                video=file_id,
                caption=caption,
                reply_markup=get_movie_keyboard()
            )
    except TelegramAPIError as e:
        logger.error(f"Kinoni yuborishda xatolik (Kod {code}): {e}")
        await message.answer(
            "⚠️ **Kechirasiz, kinoni uzatishda texnik xatolik yuz berdi!**",
            parse_mode="Markdown"
        )
