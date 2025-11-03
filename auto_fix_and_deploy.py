"""
Автоматичне виявлення проблем, виправлення та деплой
"""
import subprocess
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

def test_production():
    """Запуск тестів production"""
    print("🧪 Запуск тестів production...")
    result = subprocess.run(['python', 'test_production.py'], 
                          capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("Помилки:", result.stderr)
    return result.returncode == 0

def commit_and_push(message="Auto-fix: improvements"):
    """Commit та push на GitHub"""
    print(f"\n📤 Commit та push: {message}")
    
    # Add всіх змін
    subprocess.run(['git', 'add', '.'], check=False)
    
    # Commit
    result = subprocess.run(['git', 'commit', '-m', message], 
                          capture_output=True, text=True)
    if 'nothing to commit' in result.stdout:
        print("   ℹ️  Немає змін для commit")
        return False
    
    print(f"   ✅ Commit створено")
    
    # Push
    result = subprocess.run(['git', 'push'], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"   ✅ Push на GitHub успішний")
        print(f"   ⏳ Render автоматично передеплоїть (чекай 1-2 хв)")
        return True
    else:
        print(f"   ❌ Помилка push: {result.stderr}")
        return False

def wait_for_deployment(url, max_wait=120):
    """Очікування завершення деплою"""
    import time
    import requests
    
    print(f"\n⏳ Очікування деплою (до {max_wait} сек)...")
    
    for i in range(0, max_wait, 10):
        try:
            response = requests.get(f"{url}/", timeout=5)
            if response.status_code == 200:
                print(f"   ✅ Сервер доступний після {i} сек")
                return True
        except:
            pass
        
        if i % 30 == 0:
            print(f"   ⏳ Чекаю... ({i}/{max_wait} сек)")
        time.sleep(10)
    
    print(f"   ⚠️  Деплой триває довше ніж очікувалось")
    return False

def main():
    print("=" * 70)
    print("🔄 Автоматичний цикл: Тест → Виправлення → Деплой")
    print("=" * 70)
    
    # Крок 1: Тестування
    if not test_production():
        print("\n⚠️  Тести не пройдені - можливо потрібні виправлення")
        print("   Виправ помилки в коді та запусти знову")
        return False
    
    # Крок 2: Перевірка чи є зміни
    result = subprocess.run(['git', 'status', '--porcelain'], 
                          capture_output=True, text=True)
    
    if not result.stdout.strip():
        print("\n✅ Немає змін для деплою - все актуально")
        return True
    
    # Крок 3: Commit та Push
    if commit_and_push():
        print("\n✅ Код завантажено на GitHub")
        print("   Render автоматично перезапустить сервіс")
        
        # Опціонально: очікування деплою
        url = os.getenv("RENDER_URL", "https://fxhub-backend.onrender.com")
        wait_for_deployment(url)
        
        # Повторне тестування
        print("\n🧪 Повторне тестування після деплою...")
        test_production()
        
        return True
    
    return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
