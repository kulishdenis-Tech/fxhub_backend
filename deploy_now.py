"""
Швидкий деплой - намагається зробити push на GitHub
"""
import subprocess
import sys
import os

GITHUB_USERNAME = "kulishdenis-Tech"
REPO_NAME = "fxhub_backend"

def check_repo_exists():
    """Перевірка чи репозиторій існує"""
    try:
        # Спробуємо зробити fetch для перевірки
        result = subprocess.run(
            ['git', 'ls-remote', f'https://github.com/{GITHUB_USERNAME}/{REPO_NAME}.git'],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except:
        return False

def push_with_credential_helper():
    """Push з використанням credential helper"""
    print("🚀 Спроба push на GitHub...")
    
    # Перевірка незкомічених змін
    result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
    if result.stdout.strip():
        print("📝 Комітимо незбережені зміни...")
        subprocess.run(['git', 'add', '.'], check=False)
        subprocess.run(['git', 'commit', '-m', 'Update: deployment preparation'], check=False)
    
    # Push
    result = subprocess.run(
        ['git', 'push', '-u', 'origin', 'main'],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ УСПІХ! Код завантажено на GitHub!")
        print(f"   🔗 https://github.com/{GITHUB_USERNAME}/{REPO_NAME}")
        return True
    else:
        error = result.stderr if result.stderr else result.stdout
        print(f"⚠️  Помилка push:")
        print(f"   {error[:300]}")
        
        if 'Repository not found' in error:
            print(f"\n💡 Репозиторій не знайдено.")
            print(f"   Створи його: https://github.com/new")
            print(f"   Repository name: {REPO_NAME}")
            return False
        elif 'Authentication' in error or 'permission' in error.lower():
            print(f"\n💡 Потрібна автентифікація.")
            print(f"   Використай Personal Access Token:")
            print(f"   https://github.com/settings/tokens")
            return False
        else:
            return False

def main():
    print("=" * 70)
    print("🚀 Швидкий деплой на GitHub")
    print("=" * 70)
    
    # Перевірка чи remote налаштовано
    result = subprocess.run(['git', 'remote', '-v'], capture_output=True, text=True)
    if 'origin' not in result.stdout:
        print("❌ Remote origin не налаштовано!")
        print(f"   Виконай: git remote add origin https://github.com/{GITHUB_USERNAME}/{REPO_NAME}.git")
        sys.exit(1)
    
    print(f"✅ Remote origin налаштовано")
    
    # Перевірка чи репозиторій існує
    repo_exists = check_repo_exists()
    if not repo_exists:
        print(f"\n⚠️  Репозиторій {REPO_NAME} ще не створено на GitHub")
        print(f"   Створи його: https://github.com/new")
        print(f"   Після створення запусти цей скрипт знову")
        print(f"\n   Або натисни Enter для спроби push (може не спрацювати)...")
        input()
    
    # Спроба push
    if push_with_credential_helper():
        print("\n" + "=" * 70)
        print("✅ КРОК 1 ЗАВЕРШЕНО!")
        print("=" * 70)
        print("\n📝 Наступний крок: Деплой на Render")
        print("   Див. DEPLOY_INSTRUCTIONS.md або QUICK_START.md")
    else:
        print("\n" + "=" * 70)
        print("⚠️  Потрібна ручна дія")
        print("=" * 70)

if __name__ == "__main__":
    main()
