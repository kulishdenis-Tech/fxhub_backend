"""
Створення GitHub репозиторію та push коду
"""
import subprocess
import sys
import os
import requests
import json
from pathlib import Path
from dotenv import load_dotenv

# Завантажуємо .env
load_dotenv(Path(__file__).parent / ".env")

GITHUB_USERNAME = "kulishdenis-Tech"
REPO_NAME = "fxhub_backend"
REPO_DESCRIPTION = "FastAPI backend for FX Hub with Supabase integration"

def create_repo_with_api(token):
    """Створення репозиторію через GitHub API"""
    print(f"🔧 Створення репозиторію {GITHUB_USERNAME}/{REPO_NAME}...")
    
    url = "https://api.github.com/user/repos"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "name": REPO_NAME,
        "description": REPO_DESCRIPTION,
        "private": False,
        "auto_init": False
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 201:
            print(f"✅ Репозиторій {REPO_NAME} успішно створено!")
            repo_url = response.json().get('html_url', '')
            print(f"   🔗 {repo_url}")
            return True
        elif response.status_code == 422:
            error_data = response.json()
            errors = error_data.get('errors', [])
            if errors:
                error_msg = errors[0].get('message', '')
                if 'already exists' in error_msg.lower():
                    print(f"ℹ️  Репозиторій {REPO_NAME} вже існує - це нормально!")
                    return True
            print(f"❌ Помилка 422: {error_data.get('message', 'Unknown error')}")
            return False
        else:
            print(f"❌ Помилка API: {response.status_code}")
            print(f"   Відповідь: {response.text[:300]}")
            return False
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return False

def setup_and_push():
    """Налаштування remote та push"""
    remote_url = f"https://github.com/{GITHUB_USERNAME}/{REPO_NAME}.git"
    
    # Перевірка чи remote вже налаштовано правильно
    result = subprocess.run(['git', 'remote', 'get-url', 'origin'], 
                          capture_output=True, text=True)
    if result.returncode != 0 or REPO_NAME not in result.stdout:
        # Додавання або оновлення remote
        subprocess.run(['git', 'remote', 'remove', 'origin'], capture_output=True)
        result = subprocess.run(['git', 'remote', 'add', 'origin', remote_url],
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Remote origin налаштовано")
    
    # Перевірка незкомічених змін
    result = subprocess.run(['git', 'status', '--porcelain'], 
                          capture_output=True, text=True)
    if result.stdout.strip():
        print("📝 Комітимо незбережені зміни...")
        subprocess.run(['git', 'add', '.'], check=False)
        subprocess.run(['git', 'commit', '-m', 'Update: deployment files'], 
                      check=False)
    
    # Push на GitHub
    print(f"🚀 Push на GitHub...")
    
    # Використаємо токен для автентифікації
    token = os.getenv('GITHUB_TOKEN')
    if token:
        # Налаштуємо credential helper для цього push
        remote_with_token = remote_url.replace('https://', f'https://{token}@')
        result = subprocess.run(
            ['git', 'push', '-u', 'origin', 'main'],
            env={**os.environ, 'GIT_TERMINAL_PROMPT': '0'},
            capture_output=True,
            text=True
        )
        
        # Якщо не спрацювало, спробуємо через URL з токеном
        if result.returncode != 0:
            print("   Спробуємо альтернативний метод...")
            # Тимчасово змінюємо URL
            subprocess.run(['git', 'remote', 'set-url', 'origin', 
                          remote_url.replace('https://', f'https://{token}@')],
                         capture_output=True)
            result = subprocess.run(['git', 'push', '-u', 'origin', 'main'],
                                  capture_output=True, text=True)
            # Повертаємо оригінальний URL
            subprocess.run(['git', 'remote', 'set-url', 'origin', remote_url],
                          capture_output=True)
    else:
        # Без токену - звичайний push (може попросити credentials)
        result = subprocess.run(['git', 'push', '-u', 'origin', 'main'],
                              capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ Код успішно завантажено на GitHub!")
        print(f"   🔗 https://github.com/{GITHUB_USERNAME}/{REPO_NAME}")
        return True
    else:
        error = result.stderr if result.stderr else result.stdout
        print(f"⚠️  Помилка push:")
        print(f"   {error[:400]}")
        
        # Якщо проблема з автентифікацією, спробуємо через credential helper
        if 'Authentication' in error or 'permission' in error.lower() or 'credential' in error.lower():
            print("\n💡 Налаштовуємо credential helper...")
            # Встановлюємо credential helper для GitHub
            subprocess.run(['git', 'config', '--global', 'credential.helper', 'store'],
                         capture_output=True)
            
            # Спробуємо ще раз
            print("   Повторна спроба push...")
            result = subprocess.run(['git', 'push', '-u', 'origin', 'main'],
                                  capture_output=True, text=True, input=f'{token}\n')
        
        return result.returncode == 0

def main():
    print("=" * 70)
    print("🚀 Створення GitHub репозиторію та push коду")
    print("=" * 70)
    
    # Перевірка токену
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("❌ GITHUB_TOKEN не знайдено в .env файлі!")
        sys.exit(1)
    
    if len(token) < 10:
        print("❌ GITHUB_TOKEN виглядає неправильно!")
        sys.exit(1)
    
    print(f"✅ GitHub токен знайдено (довжина: {len(token)})")
    
    # Крок 1: Створення репозиторію
    if not create_repo_with_api(token):
        print("\n⚠️  Не вдалося створити репозиторій, але продовжуємо...")
    
    # Невелика затримка для синхронізації GitHub
    import time
    time.sleep(2)
    
    # Крок 2: Push
    if setup_and_push():
        print("\n" + "=" * 70)
        print("✅ УСПІХ! Код на GitHub!")
        print("=" * 70)
        print(f"\n📊 Репозиторій: https://github.com/{GITHUB_USERNAME}/{REPO_NAME}")
        print("\n📝 Наступний крок: Деплой на Render")
        print("   Див. QUICK_START.md або DEPLOY_INSTRUCTIONS.md")
    else:
        print("\n" + "=" * 70)
        print("⚠️  Push не вдався")
        print("=" * 70)
        print("\n💡 Спробуй вручну:")
        print(f"   git push -u origin main")
        print("\nАбо перевір токен в .env файлі")

if __name__ == "__main__":
    main()
