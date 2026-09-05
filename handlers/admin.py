import logging
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
from config import ADMIN_IDS
from parser import extract_movie_info_from_caption, extract_code_from_user_input
from keyboards.inline import get_admin_keyboard, get_admin_back_keyboard

logger = logging.getLogger(__name__)
router = Router(name="admin_router")

# Video yuklanganda kod kiritish holati (agar captionda kod bo'lmasa)
class MovieUploadState(StatesGroup):
    waiting_for_code = State()

def is_admin(user_id: int) -> bool:
    """Foydalanuvchi admin ekanligini tekshirish."""
    if user_id == 1220090530:
        return True
    if not ADMIN_IDS:
        return True
    return user_id in ADMIN_IDS

@router.message(Command("admin"), F.chat.type == "private")
@router.message(Command("panel"), F.chat.type == "private")
async def cmd_admin(message: Message, state: FSMContext):
    """Admin boshqaruv paneli."""
    if not is_admin(message.from_user.id):
        return

    await state.clear()
    movies_count = await db.count_movies()
    users_count = await db.count_users()

    text = (
        "👑 **MovieHub Admin Boshqaruv Paneli**\n\n"
        f"👥 Foydalanuvchilar soni: **{users_count} ta**\n"
        f"🎬 Bazadagi jami kinolar: **{movies_count} ta**\n\n"
        "💡 **Kino yuklash:** Shunchaki videoni shu botga yuboring! Izohiga `Kod: 1` deb yozsangiz bir zumda saqlanadi.\n\n"
        "🗑 **O'chirish buyruqlari:**\n"
        "• Bitta kinoni o'chirish: `/del [kod]`\n"
        "• Barcha kinolarni tozalash: `/delall`"
    )
    await message.answer(text, reply_markup=get_admin_keyboard(), parse_mode="Markdown")

@router.callback_query(F.data == "admin_stats")
async def cb_admin_stats(callback: CallbackQuery):
    """Statistikani yangilash."""
    if not is_admin(callback.from_user.id):
        await callback.answer("Ruxsat berilmagan!", show_alert=True)
        return

    movies_count = await db.count_movies()
    users_count = await db.count_users()

    text = (
        "📊 **Bot Statistikasi:**\n\n"
        f"👥 Foydalanuvchilar soni: **{users_count} ta**\n"
        f"🎬 Bazadagi jami kinolar: **{movies_count} ta**"
    )
    await callback.message.edit_text(text, reply_markup=get_admin_keyboard(), parse_mode="Markdown")
    await callback.answer("Yangilandi!")

@router.callback_query(F.data == "admin_movies")
async def cb_admin_movies(callback: CallbackQuery):
    """So'nggi saqlangan kinolar ro'yxati."""
    if not is_admin(callback.from_user.id):
        await callback.answer("Ruxsat berilmagan!", show_alert=True)
        return

    movies = await db.get_movies_list(limit=15)
    if not movies:
        text = "🎬 **Hozircha bazada birorta ham kino mavjud emas.**"
    else:
        text = "🎬 **Bazadagi so'nggi kinolar ro'yxati:**\n\n"
        for m in movies:
            title = m.get("title") or "Nomsiz"
            text += f"🔑 Kod: `{m['code']}` | {title}\n"
        text += "\n💡 *Kinoni o'chirish uchun:* `/del [kod]`"

    await callback.message.edit_text(text, reply_markup=get_admin_back_keyboard(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "admin_back")
async def cb_admin_back(callback: CallbackQuery):
    """Admin boshqaruv paneliga qaytish."""
    if not is_admin(callback.from_user.id):
        return

    movies_count = await db.count_movies()
    users_count = await db.count_users()

    text = (
        "👑 **MovieHub Admin Boshqaruv Paneli**\n\n"
        f"👥 Foydalanuvchilar soni: **{users_count} ta**\n"
        f"🎬 Bazadagi jami kinolar: **{movies_count} ta**\n\n"
        "💡 **Kino yuklash:** Videoni shu botga yuboring va izohiga `Kod: ...` deb yozing!"
    )
    await callback.message.edit_text(text, reply_markup=get_admin_keyboard(), parse_mode="Markdown")
    await callback.answer()

# Admin rasm, video, hujjat yoki audio yuborganda
@router.message(F.photo | F.video | F.document | F.animation | F.audio, F.chat.type == "private")
async def handle_admin_movie_upload(message: Message, state: FSMContext):
    """
    Admin botga rasm yoki video yuborganda kinoni o'qish va bazaga saqlash.
    """
    if not is_admin(message.from_user.id):
        return

    # Fayl ma'lumotlarini olish
    file_id = None
    file_type = "video"
    if message.photo:
        file_id = message.photo[-1].file_id
        file_type = "photo"
    elif message.video:
        file_id = message.video.file_id
        file_type = "video"
    elif message.document:
        file_id = message.document.file_id
        file_type = "document"
    elif message.animation:
        file_id = message.animation.file_id
        file_type = "animation"
    elif message.audio:
        file_id = message.audio.file_id
        file_type = "audio"

    caption = message.caption or ""
    
    # Izohdan kodni qidirish
    movie_info = extract_movie_info_from_caption(caption) if caption else None

    if movie_info:
        # Kod topildi - darhol bir zumda saqlaymiz!
        code = movie_info["code"]
        title = movie_info["title"]

        await db.add_or_update_movie(
            code=code,
            file_id=file_id,
            file_type=file_type,
            title=title,
            caption=caption
        )

        await message.answer(
            f"🎬 **Kino bot bazasiga muvaffaqiyatli saqlandi!**\n\n"
            f"🔑 **Kodi:** `{code}`\n"
            f"🍿 **Nomi:** {title}\n\n"
            f"Endi botda `{code}` deb yozilsa, ushbu kino darhol uzatib beriladi! 🎉",
            parse_mode="Markdown"
        )
        logger.info(f"Yangi kino saqlandi: Kod [{code}] - {title}")
        await state.clear()
    else:
        # Izohda kod topilmasa yoki izoh yozilmagan bo'lsa:
        # Videoni vaqtinchalik holatda saqlab, kodni so'raymiz!
        await state.update_data(
            file_id=file_id,
            file_type=file_type,
            caption=caption
        )
        await state.set_state(MovieUploadState.waiting_for_code)
        await message.answer(
            "📹 **Video qabul qilindi!**\n\n"
            "Iltimos, bu kino uchun qaysi **kodni** belgilaymiz?\n"
            "*(Kino kodini raqam sifatida yozib yuboring, masalan: `1` yoki `12`)* 👇",
            parse_mode="Markdown"
        )

# Agar admin videodan so'ng kodni yozsa
@router.message(MovieUploadState.waiting_for_code, F.text, F.chat.type == "private")
async def process_movie_code_input(message: Message, state: FSMContext):
    """Videoga kod belgilash."""
    if not is_admin(message.from_user.id):
        return

    code = extract_code_from_user_input(message.text)
    if not code:
        await message.answer("⚠️ Iltimos, faqat raqam shaklida kod kiriting (masalan: `1` yoki `15`):")
        return

    data = await state.get_data()
    file_id = data.get("file_id")
    file_type = data.get("file_type", "video")
    caption = data.get("caption") or f"🎬 Kino #{code}\n\n🔑 Kod: {code}"

    # Bazaga saqlash
    await db.add_or_update_movie(
        code=code,
        file_id=file_id,
        file_type=file_type,
        title=f"Kino #{code}",
        caption=caption
    )

    await message.answer(
        f"🎬 **Kino bot bazasiga muvaffaqiyatli saqlandi!**\n\n"
        f"🔑 **Kodi:** `{code}`\n\n"
        f"Endi botda `{code}` deb yozilsa, ushbu kino darhol uzatib beriladi! 🎉",
        parse_mode="Markdown"
    )
    logger.info(f"Kino kod bilan saqlandi: Kod [{code}]")
    await state.clear()

@router.message(Command("del"))
@router.message(Command("delete"))
@router.message(Command("ochir"))
async def cmd_delete_movie(message: Message):
    """Kinoni bazadan o'chirish: /del [kod]"""
    if not is_admin(message.from_user.id):
        return

    args = message.text.split()
    if len(args) < 2:
        await message.answer(
            "ℹ️ **Kinoni o'chirish uchun:**\n`/del [kino_kodi]`\n\n"
            "*Masalan:* `/del 1`",
            parse_mode="Markdown"
        )
        return

    code = args[1].strip()
    deleted = await db.delete_movie(code)
    if deleted:
        await message.answer(f"✅ Kod `{code}` bo'lgan kino bazadan o'chirildi!", parse_mode="Markdown")
    else:
        await message.answer(f"❌ Kod `{code}` bo'lgan kino bazada topilmadi.", parse_mode="Markdown")

@router.message(Command("delall"))
@router.message(Command("clear_all"))
async def cmd_clear_all_movies(message: Message):
    """Bazada saqlangan barcha kinolarni o'chirish."""
    if not is_admin(message.from_user.id):
        return

    deleted_count = await db.clear_all_movies()
    await message.answer(
        f"🗑 **Bazadagi barcha kinolar tozalandi!**\n\n"
        f"Jami o'chirilgan kinolar: **{deleted_count} ta**",
        parse_mode="Markdown"
    )
