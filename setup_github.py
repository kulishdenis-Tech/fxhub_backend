"""
Скрипт для створення GitHub репозиторію та push коду
Потребує GitHub Personal Access Token з правами repo
"""
import subprocess
import sys
import os
from pathlib import Path

def check_git_status():
    """Перевірка статусу Git репозиторію"""
    try:
        result = subprocess.run(['git', 'status'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Помилка: Не вдалося виконати git status")
            return False
        return True
    except FileNotFoundError:
        print("❌ Git не встановлений або не в PATH")
        return False

def check_remote():
    """Перевірка, чи налаштовано remote"""
    try:
        result = subprocess.run(['git', 'remote', '-v'], capture_output=True, text=True)
        if 'origin' in result.stdout:
            print("✅ Remote origin налаштовано")
            return True
        else:
            print("⚠️  Remote origin не налаштовано")
            return False
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return False

def push_to_github():
    """Спроба push на GitHub"""
    print("\n🚀 Спроба push на GitHub...")
    try:
        result = subprocess.run(
            ['git', 'push', '-u', 'origin', 'main'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Код успішно завантажено на GitHub!")
            return True
        else:
            print(f"❌ Помилка push: {result.stderr}")
            if 'Repository not found' in result.stderr:
                print("\n💡 Репозиторій не існує на GitHub!")
                print("\n📝 Інструкції:")
                print("1. Відкрий https://github.com/new")
                print("2. Repository name: fxhub_backend")
                print("3. Створи репозиторій (БЕЗ README, .gitignore, license)")
                print("4. Після створення запусти цей скрипт знову")
            return False
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return False

def main():
    print("=" * 60)
    print("🔧 Налаштування GitHub репозиторію для fxhub_backend")
    print("=" * 60)
    
    # Перевірка Git
    if not check_git_status():
        sys.exit(1)
    
    # Перевірка remote
    if not check_remote():
        print("\n⚠️  Спочатку потрібно створити репозиторій на GitHub")
        print("\n📝 Інструкції:")
        print("1. Відкрий https://github.com/new")
        print("2. Repository name: fxhub_backend")
        print("3. Visibility: Public або Private")
        print("4. НЕ додавай README, .gitignore, license")
        print("5. Натисни 'Create repository'")
        print("\n6. Після створення запусти:")
        print("   git remote add origin https://github.com/kulishdenis-Tech/fxhub_backend.git")
        print("   python setup_github.py")
        sys.exit(1)
    
    # Спроба push
    if push_to_github():
        print("\n✅ Все готово! Код на GitHub!")
        print("\n📊 Наступний крок: Деплой на Render")
        print("   Див. DEPLOY_INSTRUCTIONS.md")
    else:
        print("\n⚠️  Push не вдався. Перевір інструкції вище.")
        sys.exit(1)

if __name__ == "__main__":
    main()
