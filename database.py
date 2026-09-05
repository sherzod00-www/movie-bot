import aiosqlite
import logging
from typing import Optional, Dict, Any, List
from config import DB_PATH

logger = logging.getLogger(__name__)

async def init_db():
    """Ma'lumotlar bazasi va jadvallarni ishga tushirish hamda sxemani yangilash."""
    async with aiosqlite.connect(DB_PATH) as db:
        # Agar eski bazada channel_id NOT NULL bo'lsa, uni toza yangi sxemaga o'tkazish
        cursor = await db.execute("PRAGMA table_info(movies)")
        columns = await cursor.fetchall()
        
        # Ustunlar orasida channel_id NOT NULL bormi tekshirish
        needs_migration = False
        if columns:
            for col in columns:
                # col[1] ustun nomi, col[3] notnull bayrog'i
                if col[1] in ("channel_id", "message_id") and col[3] == 1:
                    needs_migration = True
                    break

        if needs_migration:
            logger.info("Bazaning eski sxemasi aniqlandi. Yangi kanalsiz sxemaga o'tkazilmoqda...")
            await db.execute("""
                CREATE TABLE IF NOT EXISTS movies_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT UNIQUE NOT NULL,
                    file_id TEXT NOT NULL,
                    file_type TEXT NOT NULL,
                    title TEXT,
                    caption TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Agar eski ma'lumotlar bo'lsa ko'chirish (file_id borlarini)
            try:
                await db.execute("""
                    INSERT OR IGNORE INTO movies_new (code, file_id, file_type, title, caption, created_at)
                    SELECT code, file_id, file_type, title, caption, created_at FROM movies WHERE file_id IS NOT NULL
                """)
            except Exception:
                pass
            await db.execute("DROP TABLE movies")
            await db.execute("ALTER TABLE movies_new RENAME TO movies")
            logger.info("Baza muvaffaqiyatli yangilandi!")
        else:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS movies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT UNIQUE NOT NULL,
                    file_id TEXT NOT NULL,
                    file_type TEXT NOT NULL,
                    title TEXT,
                    caption TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await db.commit()
    logger.info("Ma'lumotlar bazasi muvaffaqiyatli ishga tushirildi.")

async def add_or_update_movie(
    code: str,
    file_id: str,
    file_type: str,
    title: Optional[str] = None,
    caption: Optional[str] = None
) -> bool:
    """Kino ma'lumotlarini bazaga qo'shish yoki yangilash."""
    async with aiosqlite.connect(DB_PATH) as db:
        try:
            await db.execute("""
                INSERT INTO movies (code, file_id, file_type, title, caption)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(code) DO UPDATE SET
                    file_id = excluded.file_id,
                    file_type = excluded.file_type,
                    title = excluded.title,
                    caption = excluded.caption,
                    created_at = CURRENT_TIMESTAMP
            """, (str(code).strip(), str(file_id), str(file_type), title, caption))
            await db.commit()
            return True
        except Exception as e:
            logger.error(f"Kinoni saqlashda xatolik: {e}")
            return False

async def get_movie(code: str) -> Optional[Dict[str, Any]]:
    """Kodni to'liq yoki tozalangan holda qidirish."""
    code_str = str(code).strip()
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM movies WHERE code = ? LIMIT 1", (code_str,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return dict(row)
    return None

async def delete_movie(code: str) -> bool:
    """Kinoni bazadan o'chirish."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("DELETE FROM movies WHERE code = ?", (str(code).strip(),))
        await db.commit()
        return cursor.rowcount > 0

async def clear_all_movies() -> int:
    """Bazadagi barcha kinolarni tozalash."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("DELETE FROM movies")
        await db.commit()
        return cursor.rowcount

async def count_movies() -> int:
    """Jami kinolar soni."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM movies") as cursor:
            res = await cursor.fetchone()
            return res[0] if res else 0

async def get_movies_list(limit: int = 15, offset: int = 0) -> List[Dict[str, Any]]:
    """Kinolar ro'yxatini olish."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM movies ORDER BY id DESC LIMIT ? OFFSET ?", (limit, offset)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

async def add_user(user_id: int, username: Optional[str], first_name: Optional[str], last_name: Optional[str]):
    """Foydalanuvchini ro'yxatga olish."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO users (user_id, username, first_name, last_name)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username = excluded.username,
                first_name = excluded.first_name,
                last_name = excluded.last_name
        """, (user_id, username, first_name, last_name))
        await db.commit()

async def count_users() -> int:
    """Jami foydalanuvchilar soni."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cursor:
            res = await cursor.fetchone()
            return res[0] if res else 0
