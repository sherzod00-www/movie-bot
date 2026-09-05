import os
from pathlib import Path
from dotenv import load_dotenv

# Papka yo'llari
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "movies.db"

# .env yuklash (agar mavjud bo'lsa)
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)

# Asosiy Bot Tokeni (Doimiy)
DEFAULT_BOT_TOKEN = "8621462566:AAGraRkhmsCcW8WwImtr3mSY-98qQBLjOkI"
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip() or DEFAULT_BOT_TOKEN

# Admin ID lar
DEFAULT_ADMIN_IDS = [1220090530]
_admin_ids_env = os.getenv("ADMIN_IDS", "").strip()
parsed_admins = [int(i.strip()) for i in _admin_ids_env.split(",") if i.strip().isdigit()]
ADMIN_IDS = parsed_admins if parsed_admins else DEFAULT_ADMIN_IDS
