"""
Перевірка коректності відображення трендів у застосунку
Порівнює дані з API зі скріншотом мобільного додатку
"""
import requests
import json
from datetime import datetime

# Дані зі скріншоту для порівняння
SCREENSHOT_DATA = {
    "USD/UAH": {"buy": 41.97, "buy_change": -0.01, "sell": 42.00, "sell_change": -0.10},
    "EUR/UAH": {"buy": 48.65, "buy_change": 0.0, "sell": 48.75, "sell_change": -0.05},
    "CAD/UAH": {"buy": 29.60, "buy_change": 0.0, "sell": 29.80, "sell_change": -0.20},
    "CHF/UAH": {"buy": 52.60, "buy_change": -0.20, "sell": 53.00, "sell_change": -0.10},
    "GBP/UAH": {"buy": 55.15, "buy_change": -0.25, "sell": 55.60, "sell_change": -0.20},
}

def verify_trends():
    url = "https://fxhub-backend.onrender.com/rates/bestrate"
    
    print("🔍 Перевірка трендів з API vs Скріншот")
    print("=" * 80)
    print(f"📅 Час перевірки: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Отримуємо дані для всіх пар зі скріншоту
    currencies = ",".join(SCREENSHOT_DATA.keys())
    
    try:
        print(f"\n📡 Запит до API: {url}")
        print(f"   Валютні пари: {currencies}\n")
        
        response = requests.get(url, params={"currencies": currencies}, timeout=60)
        
        if response.status_code != 200:
            print(f"❌ Помилка API: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return
        
        data = response.json()
        
        if "data" not in data:
            print("❌ Невірний формат відповіді")
            print(f"   Response: {json.dumps(data, indent=2)[:500]}")
            return
        
        print(f"✅ Отримано {len(data['data'])} валютних пар з API\n")
        
        matches = {"buy": 0, "sell": 0}
        mismatches = {"buy": 0, "sell": 0}
        
        # Порівнюємо кожну пару
        for api_rate in data["data"]:
            currency = api_rate.get("currency")
            screenshot = SCREENSHOT_DATA.get(currency)
            
            if not screenshot:
                print(f"⚠️  Валюта {currency} не знайдена в даних скріншоту")
                continue
            
            print(f"\n{'='*80}")
            print(f"💰 {currency}")
            print(f"{'='*80}")
            
            # Перевірка Buy
            if "buy_best" in api_rate:
                api_buy = api_rate["buy_best"]
                api_buy_change = api_rate.get("buy_change_abs", 0.0)
                api_buy_trend = api_rate.get("buy_trend", "stable")
                api_buy_exchanger = api_rate.get("buy_exchanger", "N/A")
                
                screen_buy = screenshot["buy"]
                screen_buy_change = screenshot["buy_change"]
                
                print(f"\n📈 Купівля:")
                print(f"   Скріншот:  {screen_buy:>6} (зміна: {screen_buy_change:>6.2f})")
                print(f"   API:       {api_buy:>6} (зміна: {api_buy_change:>6.2f}, тренд: {api_buy_trend})")
                print(f"   Обмінник:  {api_buy_exchanger}")
                
                # Порівняння курсів (можуть трохи відрізнятись через час)
                buy_match_price = abs(api_buy - screen_buy) < 0.5  # Допустима різниця через час
                buy_match_change = abs(api_buy_change - screen_buy_change) < 0.01
                buy_trend_expected = "down" if screen_buy_change < 0 else "stable" if screen_buy_change == 0 else "up"
                buy_match_trend = api_buy_trend == buy_trend_expected
                
                if buy_match_price and buy_match_change and buy_match_trend:
                    print(f"   ✅ ВСЕ ЗБІГАЄТЬСЯ")
                    matches["buy"] += 1
                else:
                    print(f"   ⚠️  РОЗБІЖНОСТІ:")
                    if not buy_match_price:
                        print(f"      • Курс: різниця {abs(api_buy - screen_buy):.2f} (може бути через час)")
                    if not buy_match_change:
                        print(f"      • Зміна: очікувано {screen_buy_change:.2f}, отримано {api_buy_change:.2f}, різниця {abs(api_buy_change - screen_buy_change):.2f}")
                    if not buy_match_trend:
                        print(f"      • Тренд: очікувано '{buy_trend_expected}', отримано '{api_buy_trend}'")
                    mismatches["buy"] += 1
                
                # Додаткова інформація
                if api_buy_change != 0:
                    api_buy_pct = api_rate.get("buy_change_pct", 0.0)
                    print(f"   📊 Відсоткова зміна: {api_buy_pct:.2f}%")
            
            # Перевірка Sell
            if "sell_best" in api_rate:
                api_sell = api_rate["sell_best"]
                api_sell_change = api_rate.get("sell_change_abs", 0.0)
                api_sell_trend = api_rate.get("sell_trend", "stable")
                api_sell_exchanger = api_rate.get("sell_exchanger", "N/A")
                
                screen_sell = screenshot["sell"]
                screen_sell_change = screenshot["sell_change"]
                
                print(f"\n📉 Продаж:")
                print(f"   Скріншот:  {screen_sell:>6} (зміна: {screen_sell_change:>6.2f})")
                print(f"   API:       {api_sell:>6} (зміна: {api_sell_change:>6.2f}, тренд: {api_sell_trend})")
                print(f"   Обмінник:  {api_sell_exchanger}")
                
                sell_match_price = abs(api_sell - screen_sell) < 0.5
                sell_match_change = abs(api_sell_change - screen_sell_change) < 0.01
                sell_trend_expected = "down" if screen_sell_change < 0 else "stable" if screen_sell_change == 0 else "up"
                sell_match_trend = api_sell_trend == sell_trend_expected
                
                if sell_match_price and sell_match_change and sell_match_trend:
                    print(f"   ✅ ВСЕ ЗБІГАЄТЬСЯ")
                    matches["sell"] += 1
                else:
                    print(f"   ⚠️  РОЗБІЖНОСТІ:")
                    if not sell_match_price:
                        print(f"      • Курс: різниця {abs(api_sell - screen_sell):.2f} (може бути через час)")
                    if not sell_match_change:
                        print(f"      • Зміна: очікувано {screen_sell_change:.2f}, отримано {api_sell_change:.2f}, різниця {abs(api_sell_change - screen_sell_change):.2f}")
                    if not sell_match_trend:
                        print(f"      • Тренд: очікувано '{sell_trend_expected}', отримано '{api_sell_trend}'")
                    mismatches["sell"] += 1
                
                # Додаткова інформація
                if api_sell_change != 0:
                    api_sell_pct = api_rate.get("sell_change_pct", 0.0)
                    print(f"   📊 Відсоткова зміна: {api_sell_pct:.2f}%")
        
        # Підсумок
        print(f"\n{'='*80}")
        print("📊 ПІДСУМОК ПЕРЕВІРКИ")
        print(f"{'='*80}")
        print(f"✅ Збігається (купівля): {matches['buy']}/{len(SCREENSHOT_DATA)}")
        print(f"✅ Збігається (продаж):  {matches['sell']}/{len(SCREENSHOT_DATA)}")
        print(f"⚠️  Розбіжності (купівля): {mismatches['buy']}")
        print(f"⚠️  Розбіжності (продаж):  {mismatches['sell']}")
        
        total_checks = len(SCREENSHOT_DATA) * 2
        total_matches = matches['buy'] + matches['sell']
        accuracy = (total_matches / total_checks * 100) if total_checks > 0 else 0
        
        print(f"\n📈 Точність: {total_matches}/{total_checks} ({accuracy:.1f}%)")
        
        if mismatches['buy'] == 0 and mismatches['sell'] == 0:
            print("\n🎉 ВІДМІННО! Всі дані збігаються!")
        elif accuracy >= 80:
            print("\n✅ Добре! Більшість даних збігається. Невеликі розбіжності можуть бути через:")
            print("   • Час між скріншотом і перевіркою (курси міняються)")
            print("   • Різні обмінники для найкращих курсів")
        else:
            print("\n⚠️  Є значні розбіжності. Перевір логіку розрахунку трендів.")
        
        print(f"\n{'='*80}")
        
    except requests.exceptions.Timeout:
        print("⏱️  Timeout - Render сервіс може бути повільним")
        print("   Спробуй запустити ще раз")
    except Exception as e:
        print(f"❌ Помилка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_trends()

