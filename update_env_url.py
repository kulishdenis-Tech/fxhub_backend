"""Додавання RENDER_URL в .env"""
from pathlib import Path

env_file = Path('.env')
if env_file.exists():
    content = env_file.read_text(encoding='utf-8')
    if 'RENDER_URL' not in content:
        env_file.write_text(content + '\nRENDER_URL=https://fxhub-backend.onrender.com\n', encoding='utf-8')
        print('✅ RENDER_URL додано в .env')
    else:
        print('ℹ️  RENDER_URL вже є в .env')
else:
    print('❌ .env файл не знайдено')

