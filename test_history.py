"""Тестування /rates/history endpoint"""
import requests
import json

PRODUCTION_URL = "https://fxhub-backend.onrender.com"

def test_history():
    """Тестування history endpoint"""
    print("🧪 Тестування /rates/history endpoint...\n")
    
    # Тест 1: USD/UAH за останні 7 днів
    print("1. Тест: USD/UAH за 7 днів (hour interval)")
    try:
        response = requests.get(
            f"{PRODUCTION_URL}/rates/history",
            params={"currency_pair": "USD/UAH", "days": 7, "interval": "hour"},
            timeout=15
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {response.status_code}")
            print(f"   📊 Data points: {data.get('meta', {}).get('count', 0)}")
            if data.get('data', {}).get('data_points'):
                print(f"   📅 First point: {data['data']['data_points'][0]}")
                print(f"   📅 Last point: {data['data']['data_points'][-1]}")
        else:
            print(f"   ❌ Status: {response.status_code}")
            print(f"   {response.text[:200]}")
    except Exception as e:
        print(f"   ⚠️  Помилка: {e}")
    
    print()
    
    # Тест 2: EUR/UAH за 1 день
    print("2. Тест: EUR/UAH за 1 день (hour interval)")
    try:
        response = requests.get(
            f"{PRODUCTION_URL}/rates/history",
            params={"currency_pair": "EUR/UAH", "days": 1, "interval": "hour"},
            timeout=15
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {response.status_code}")
            print(f"   📊 Data points: {data.get('meta', {}).get('count', 0)}")
    except Exception as e:
        print(f"   ⚠️  Помилка: {e}")
    
    print()
    
    # Тест 3: З фільтром обмінника
    print("3. Тест: USD/UAH для GARANT за 7 днів")
    try:
        response = requests.get(
            f"{PRODUCTION_URL}/rates/history",
            params={"currency_pair": "USD/UAH", "exchanger": "GARANT", "days": 7},
            timeout=15
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {response.status_code}")
            print(f"   📊 Data points: {data.get('meta', {}).get('count', 0)}")
    except Exception as e:
        print(f"   ⚠️  Помилка: {e}")

if __name__ == "__main__":
    test_history()

