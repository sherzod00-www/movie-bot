import os
from pathlib import Path
from dotenv import load_dotenv

# Papka yo'llari
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "movies.db"

# .env yuklash
load_dotenv(dotenv_path=ENV_PATH)

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

# Admin ID lar
_admin_ids_env = os.getenv("ADMIN_IDS", "").strip()
ADMIN_IDS = [int(i.strip()) for i in _admin_ids_env.split(",") if i.strip().isdigit()]

if not BOT_TOKEN:
    raise ValueError("DIQQAT: .env faylida BOT_TOKEN ko'rsatilmagan!")
