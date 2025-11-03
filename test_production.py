"""
Автоматичне тестування production API на Render
"""
import requests
import json
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

# Може бути встановлено в .env або використовуємо за замовчуванням
PRODUCTION_URL = os.getenv("RENDER_URL", "https://fxhub-backend.onrender.com")

def test_endpoint(endpoint, expected_status=200, description=""):
    """Тестування ендпоінту"""
    url = f"{PRODUCTION_URL}{endpoint}"
    print(f"\n🧪 Тест: {description or endpoint}")
    print(f"   URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        status = response.status_code
        
        if status == expected_status:
            print(f"   ✅ Status: {status}")
            try:
                data = response.json()
                print(f"   📊 Response: {json.dumps(data, indent=2, ensure_ascii=False)[:200]}...")
                return True, data
            except:
                print(f"   📄 Response: {response.text[:100]}...")
                return True, response.text
        else:
            print(f"   ❌ Status: {status} (очікувалось {expected_status})")
            print(f"   📄 Response: {response.text[:200]}")
            return False, None
    except requests.exceptions.Timeout:
        print(f"   ⏱️  Timeout (сервер може ще деплоїтись)")
        return None, None
    except requests.exceptions.ConnectionError:
        print(f"   🔌 Connection Error (сервер може бути недоступний)")
        return None, None
    except Exception as e:
        print(f"   ❌ Помилка: {e}")
        return False, None

def main():
    print("=" * 70)
    print("🧪 Автоматичне тестування Production API")
    print("=" * 70)
    print(f"🌐 Production URL: {PRODUCTION_URL}")
    
    results = {}
    
    # Тест 1: Root endpoint
    results['root'] = test_endpoint("/", 200, "Root endpoint")
    
    # Тест 2: Exchangers list
    results['exchangers'] = test_endpoint("/exchangers/list", 200, "Exchangers list")
    
    # Тест 3: Currencies list
    results['currencies'] = test_endpoint("/currencies/list", 200, "Currencies list")
    
    # Тест 4: Best rates (без фільтрів)
    results['bestrates_all'] = test_endpoint("/rates/bestrate", 200, "Best rates (всі)")
    
    # Тест 5: Best rates з фільтром
    results['bestrates_filtered'] = test_endpoint(
        "/rates/bestrate?currencies=USD/UAH", 
        200, 
        "Best rates (USD/UAH)"
    )
    
    # Підсумок
    print("\n" + "=" * 70)
    print("📊 Підсумок тестування")
    print("=" * 70)
    
    passed = sum(1 for r in results.values() if r[0] is True)
    failed = sum(1 for r in results.values() if r[0] is False)
    unknown = sum(1 for r in results.values() if r[0] is None)
    
    print(f"✅ Успішні: {passed}")
    print(f"❌ Помилки: {failed}")
    print(f"⏳ Невідомо: {unknown} (може ще деплоїться)")
    
    if failed == 0 and unknown == 0:
        print("\n🎉 Всі тести пройдені!")
        return True
    elif unknown > 0:
        print("\n⏳ Деякі тести не завершені - можливо сервер ще деплоїться")
        return None
    else:
        print("\n⚠️  Є помилки - потрібні виправлення")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
