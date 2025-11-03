"""
Автоматичний скрипт для створення GitHub репозиторію та підготовки до Render деплою
"""
import subprocess
import sys
import os
import requests
import json
from pathlib import Path

GITHUB_USERNAME = "kulishdenis-Tech"
REPO_NAME = "fxhub_backend"
REPO_DESCRIPTION = "FastAPI backend for FX Hub with Supabase integration"

def check_git_config():
    """Перевірка Git конфігурації"""
    try:
        result = subprocess.run(['git', 'config', '--get', 'remote.origin.url'], 
                              capture_output=True, text=True)
        if result.returncode == 0 and 'github.com' in result.stdout:
            print(f"✅ Remote налаштовано: {result.stdout.strip()}")
            return True
        return False
    except:
        return False

def create_repo_with_api(token):
    """Створення репозиторію через GitHub API"""
    print(f"\n🔧 Створення репозиторію {GITHUB_USERNAME}/{REPO_NAME} через GitHub API...")
    
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
            print(f"✅ Репозиторій {REPO_NAME} успішно створено на GitHub!")
            return True
        elif response.status_code == 422:
            error_msg = response.json().get('errors', [{}])[0].get('message', '')
            if 'already exists' in error_msg.lower():
                print(f"ℹ️  Репозиторій {REPO_NAME} вже існує на GitHub")
                return True
            else:
                print(f"❌ Помилка 422: {error_msg}")
                return False
        else:
            print(f"❌ Помилка API: {response.status_code}")
            print(f"   Відповідь: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ Помилка при створенні репозиторію: {e}")
        return False

def setup_remote():
    """Налаштування remote origin"""
    remote_url = f"https://github.com/{GITHUB_USERNAME}/{REPO_NAME}.git"
    
    # Перевірка, чи remote вже налаштовано
    result = subprocess.run(['git', 'remote', 'get-url', 'origin'], 
                          capture_output=True, text=True)
    if result.returncode == 0:
        current_url = result.stdout.strip()
        if REPO_NAME in current_url:
            print(f"✅ Remote origin вже налаштовано: {current_url}")
            return True
    
    # Додавання remote
    print(f"\n🔧 Налаштування remote origin: {remote_url}")
    result = subprocess.run(['git', 'remote', 'add', 'origin', remote_url],
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ Remote origin додано")
        return True
    else:
        # Можливо remote вже існує, спробуємо оновити
        result = subprocess.run(['git', 'remote', 'set-url', 'origin', remote_url],
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Remote origin оновлено")
            return True
        else:
            print(f"❌ Помилка налаштування remote: {result.stderr}")
            return False

def push_to_github():
    """Push коду на GitHub"""
    print(f"\n🚀 Push коду на GitHub...")
    
    # Перевірка, чи є зміни для push
    result = subprocess.run(['git', 'status', '--porcelain'], 
                          capture_output=True, text=True)
    if result.stdout.strip():
        print("⚠️  Є незкомічені зміни. Робимо commit...")
        subprocess.run(['git', 'add', '.'], capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Update: prepare for deployment'], 
                      capture_output=True)
    
    # Перевірка, чи потрібен push
    result = subprocess.run(['git', 'ls-remote', '--heads', 'origin', 'main'],
                          capture_output=True, text=True)
    
    if result.returncode == 0 and result.stdout.strip():
        print("ℹ️  Гілка main вже існує на GitHub. Перевіряємо статус...")
        result = subprocess.run(['git', 'fetch', 'origin'], capture_output=True)
    
    # Push
    result = subprocess.run(['git', 'push', '-u', 'origin', 'main'],
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ Код успішно завантажено на GitHub!")
        print(f"   🔗 https://github.com/{GITHUB_USERNAME}/{REPO_NAME}")
        return True
    else:
        error = result.stderr if result.stderr else result.stdout
        if 'Repository not found' in error:
            print(f"❌ Репозиторій не знайдено. Потрібно створити його спочатку.")
        elif 'Authentication failed' in error or 'permission denied' in error.lower():
            print(f"❌ Помилка автентифікації.")
            print(f"   Потрібен Personal Access Token для push.")
            print(f"   Створити: https://github.com/settings/tokens")
        else:
            print(f"⚠️  Помилка push: {error[:200]}")
        return False

def main():
    print("=" * 70)
    print("🚀 Автоматичний деплой: GitHub + Render")
    print("=" * 70)
    
    # Крок 1: Створення репозиторію через API (якщо є токен)
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    
    if token:
        print(f"\n📝 Знайдено GitHub токен. Використовуємо API...")
        if not create_repo_with_api(token):
            print("\n⚠️  Не вдалося створити через API. Спробуй створити вручну:")
            print(f"   https://github.com/new")
            print(f"   Repository name: {REPO_NAME}")
    else:
        print(f"\n⚠️  GitHub токен не знайдено в змінних оточення (GITHUB_TOKEN або GH_TOKEN)")
        print(f"   Створи репозиторій вручну: https://github.com/new")
        print(f"   Repository name: {REPO_NAME}")
        print(f"   Після створення натисни Enter для продовження...")
        input()
    
    # Крок 2: Налаштування remote
    if not setup_remote():
        print("\n❌ Не вдалося налаштувати remote. Перевір налаштування.")
        sys.exit(1)
    
    # Крок 3: Push на GitHub
    if push_to_github():
        print("\n" + "=" * 70)
        print("✅ КРОК 1 ЗАВЕРШЕНО: Код на GitHub!")
        print("=" * 70)
        print(f"\n📊 Репозиторій: https://github.com/{GITHUB_USERNAME}/{REPO_NAME}")
        
        print("\n" + "=" * 70)
        print("📝 КРОК 2: Деплой на Render")
        print("=" * 70)
        print("\nТепер виконай наступні кроки:")
        print("1. Відкрий: https://dashboard.render.com")
        print("2. New + → Web Service")
        print("3. Підключи GitHub репозиторій: fxhub_backend")
        print("4. Додай Environment Variables:")
        print("   - SUPABASE_URL (з твого .env)")
        print("   - SUPABASE_KEY (з твого .env)")
        print("5. Натисни 'Create Web Service'")
        print("\nДетальні інструкції: DEPLOY_INSTRUCTIONS.md")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("⚠️  Push не вдався")
        print("=" * 70)
        print("\nМожливі причини:")
        print("1. Репозиторій не створено на GitHub")
        print("2. Немає доступу (потрібен Personal Access Token)")
        print("3. Проблеми з мережею")
        print("\nСпробуй вручну:")
        print(f"   git push -u origin main")
        print("\nАбо див. QUICK_START.md для інструкцій")

if __name__ == "__main__":
    main()
