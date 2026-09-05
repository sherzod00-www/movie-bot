import asyncio
import logging
import sys

# Windows konsolida emojilarni xatosiz chiqarish uchun UTF-8 reconfigure
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN, ADMIN_IDS
import database as db
from handlers import user_router, admin_router

# Logging sozlash
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot.log", encoding="utf-8")
    ]
)
logger = logging.getLogger("MovieHub")

async def setup_commands(bot: Bot):
    """Bot menyusi uchun buyruqlarni xavfsiz sozlash."""
    # Barcha oddiy foydalanuvchilar uchun faqat 2 ta buyruq
    user_commands = [
        BotCommand(command="start", description="🚀 Botni ishga tushirish"),
        BotCommand(command="help", description="ℹ️ Qo'llanma")
    ]
    await bot.set_my_commands(user_commands, scope=BotCommandScopeDefault())

    # Faqat adminlar uchun to'liq buyruqlar menyusi
    admin_commands = [
        BotCommand(command="start", description="🚀 Botni ishga tushirish"),
        BotCommand(command="admin", description="👑 Admin paneli"),
        BotCommand(command="del", description="🗑 Kinoni o'chirish (/del [kod])"),
        BotCommand(command="delall", description="⚠️ Barcha kinolarni tozalash"),
        BotCommand(command="help", description="ℹ️ Qo'llanma")
    ]
    for admin_id in ADMIN_IDS:
        try:
            await bot.set_my_commands(admin_commands, scope=BotCommandScopeChat(chat_id=admin_id))
        except Exception:
            pass

import os
from aiohttp import web

async def ping_handler(request):
    return web.Response(text="🎬 MovieHub Bot is running 24/7!")

async def start_web_server():
    """Render.com va boshqa bulutli serverlar uchun veb-server."""
    port = int(os.getenv("PORT", 8080))
    app = web.Application()
    app.router.add_get("/", ping_handler)
    app.router.add_get("/ping", ping_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

async def main():
    logger.info("Bot ishga tushirilmoqda...")

    # Mini veb-serverni ishga tushirish (Render.com uchun)
    try:
        await start_web_server()
    except Exception as e:
        logger.warning(f"Veb-server xatosi (lokal rejimda muhim emas): {e}")

    # Ma'lumotlar bazasini ishga tushirish
    await db.init_db()

    # Bot va Dispatcher yaratish
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
    )
    dp = Dispatcher()

    # Routerlarni qo'shish (Admin va User)
    dp.include_router(admin_router)
    dp.include_router(user_router)

    # Bot menyu buyruqlarini o'rnatish
    await setup_commands(bot)

    # Bot ma'lumotlarini olish
    bot_info = await bot.get_me()
    print("\n" + "=" * 50)
    print("🎬 MovieHub Bot muvaffaqiyatli ishga tushdi!")
    print(f"🤖 Bot Username: @{bot_info.username}")
    print("💾 Saqlash rejimi: To'g'ridan-to'g'ri Bot bazasi (Kanalsiz)")
    print("=" * 50 + "\n")

    # Pollingni boshlash
    await dp.start_polling(
        bot,
        allowed_updates=["message", "callback_query"]
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")
