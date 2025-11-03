"""Тестування health endpoint"""
import requests
import time

PRODUCTION_URL = "https://fxhub-backend.onrender.com"

def test_health():
    """Тестування health endpoint"""
    print(f"🔍 Тестування {PRODUCTION_URL}/health...")
    
    max_attempts = 6
    for i in range(max_attempts):
        try:
            response = requests.get(f"{PRODUCTION_URL}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check OK!")
                print(f"   Status: {data.get('status')}")
                print(f"   Database: {data.get('database')}")
                print(f"   Version: {data.get('version')}")
                print(f"   Timestamp: {data.get('timestamp')}")
                return True
        except Exception as e:
            if i < max_attempts - 1:
                print(f"   Спроба {i+1}/{max_attempts}: чекаю... ({e})")
                time.sleep(10)
            else:
                print(f"   ❌ Не вдалося підключитись після {max_attempts} спроб")
    return False

if __name__ == "__main__":
    test_health()

