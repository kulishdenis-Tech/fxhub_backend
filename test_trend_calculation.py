"""
Тестування trend analytics в /rates/bestrate endpoint
"""
import requests

url = "https://fxhub-backend.onrender.com/rates/bestrate"

print("🧪 Тестування Trend Analytics")
print("=" * 70)

for pair in ["USD/UAH", "EUR/UAH"]:
    try:
        print(f"\n📊 Тестування для {pair}...")
        r = requests.get(url, params={"currencies": pair}, timeout=30)
        
        if r.status_code != 200:
            print(f"   ❌ Помилка: HTTP {r.status_code}")
            print(f"   Response: {r.text[:200]}")
            continue
        
        data = r.json()
        
        # Перевіряємо формат відповіді
        if "data" not in data or not data["data"]:
            print(f"   ⚠️  Немає даних для {pair}")
            continue
        
        rate_data = data["data"][0]
        
        print(f"\n   ✅ {pair}:")
        
        # Buy analytics
        if "buy_best" in rate_data:
            print(f"   📈 Buy:")
            print(f"      Курс: {rate_data.get('buy_best')}")
            print(f"      Обмінник: {rate_data.get('buy_exchanger', 'N/A')}")
            print(f"      Тренд: {rate_data.get('buy_trend', 'N/A')}")
            print(f"      Зміна: {rate_data.get('buy_change_abs', 0.0)} ({rate_data.get('buy_change_pct', 0.0)}%)")
        
        # Sell analytics
        if "sell_best" in rate_data:
            print(f"   📉 Sell:")
            print(f"      Курс: {rate_data.get('sell_best')}")
            print(f"      Обмінник: {rate_data.get('sell_exchanger', 'N/A')}")
            print(f"      Тренд: {rate_data.get('sell_trend', 'N/A')}")
            print(f"      Зміна: {rate_data.get('sell_change_abs', 0.0)} ({rate_data.get('sell_change_pct', 0.0)}%)")
        
        # Перевірка наявності всіх полів
        required_fields = ["buy_trend", "buy_change_abs", "buy_change_pct", 
                          "sell_trend", "sell_change_abs", "sell_change_pct"]
        missing = [f for f in required_fields if f not in rate_data]
        if missing:
            print(f"   ⚠️  Відсутні поля: {missing}")
        else:
            print(f"   ✅ Всі поля analytics присутні")
            
    except requests.exceptions.Timeout:
        print(f"   ⏱️  Timeout для {pair} (Render може бути повільним)")
    except Exception as e:
        print(f"   ❌ Помилка для {pair}: {e}")

print("\n" + "=" * 70)
print("✅ Тестування завершено")

