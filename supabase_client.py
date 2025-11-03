from supabase import create_client
import os
from dotenv import load_dotenv
from pathlib import Path

# Завантажуємо .env з поточної директорії
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(
        "⚠️  Не знайдено SUPABASE_URL або SUPABASE_KEY у .env файлі. "
        "Перевірте, чи файл .env існує та містить обидва ключі."
    )

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
