"""
Детальний дебаг проблеми з PLN/UAH
Перевіряє чому для sell показується stable замість down
"""
from supabase_client import supabase
import json

def debug_pln_sell():
    print("=" * 80)
    print("🐛 ДЕБАГ ПРОБЛЕМИ З PLN/UAH SELL")
    print("=" * 80)
    
    # Отримуємо channel_id для MIRVALUTY
    channels_resp = supabase.table("channels").select("id, name").execute()
    channel_map = {ch["name"]: ch["id"] for ch in channels_resp.data}
    mirvaluty_id = channel_map.get("MIRVALUTY")
    
    print(f"\n📡 Channel ID для MIRVALUTY: {mirvaluty_id}")
    
    # Отримуємо останні 100 записів
    query = supabase.table("rates").select(
        "buy, sell, edited"
    ).eq("channel_id", mirvaluty_id).eq("currency_a", "PLN").eq("currency_b", "UAH").order("edited", desc=True).limit(100)
    
    response = query.execute()
    records = response.data
    
    print(f"\n📊 Останні 10 записів (з {len(records)}):")
    print("-" * 80)
    
    current_record = records[0]
    current_buy = current_record.get("buy")
    current_sell = current_record.get("sell")
    
    print(f"Поточний запис (№1):")
    print(f"  Buy: {current_buy}, Sell: {current_sell}, Timestamp: {current_record.get('edited')}")
    
    print(f"\nПопередні 9 записів:")
    identical_count = 0
    
    for i, record in enumerate(records[1:10], start=2):
        prev_buy = record.get("buy")
        prev_sell = record.get("sell")
        
        buy_match = abs(current_buy - prev_buy) < 0.0001 if (current_buy and prev_buy) else current_buy == prev_buy
        sell_match = abs(current_sell - prev_sell) < 0.0001 if (current_sell and prev_sell) else current_sell == prev_sell
        
        if buy_match and sell_match:
            identical_count += 1
            status = "✅ ІДЕНТИЧНИЙ"
        else:
            status = f"⚠️ ВІДРІЗНЯЄТЬСЯ (buy: {buy_match}, sell: {sell_match})"
        
        print(f"[{i}] Buy: {prev_buy}, Sell: {prev_sell} - {status}")
        print(f"    Timestamp: {record.get('edited')}")
    
    print(f"\n📊 Аналіз:")
    print(f"  Ідентичних серед перших 9: {identical_count}")
    
    # Перевіряємо всю логіку як в коді
    print(f"\n🔍 ПОВНА ПЕРЕВІРКА ЛОГІКИ (як в find_previous_rate):")
    print("-" * 80)
    
    found_different = False
    first_different = None
    
    for i, record in enumerate(records[1:], start=2):
        prev_buy = record.get("buy")
        prev_sell = record.get("sell")
        
        # ТАКА Ж ЛОГІКА ЯК В КОДІ
        buy_different = (current_buy is not None and prev_buy is not None and abs(current_buy - prev_buy) > 0.0001) or \
                       (current_buy is None) != (prev_buy is None)
        sell_different = (current_sell is not None and prev_sell is not None and abs(current_sell - prev_sell) > 0.0001) or \
                        (current_sell is None) != (prev_sell is None)
        
        if buy_different or sell_different:
            found_different = True
            first_different = record
            print(f"\n✅ Знайдено перший відмінний запис (№{i}):")
            print(f"   Buy: {prev_buy} {'(відрізняється)' if buy_different else ''}")
            print(f"   Sell: {prev_sell} {'(відрізняється)' if sell_different else ''}")
            print(f"   Timestamp: {record.get('edited')}")
            break
        else:
            if i <= 10:
                print(f"[{i}] Ідентичний")
    
    if found_different:
        print(f"\n💡 Розрахунок для SELL:")
        print(f"   Поточний sell: {current_sell}")
        print(f"   Baseline sell: {first_different.get('sell')}")
        
        if first_different.get('sell') and current_sell:
            change = round(current_sell - first_different.get('sell'), 2)
            trend = "up" if change > 0.0001 else "down" if change < -0.0001 else "stable"
            
            print(f"   Зміна: {change}")
            print(f"   Тренд: {trend}")
            print(f"\n   ⚠️  АЛЕ API ПОКАЗУЄ: stable, 0.0")
            print(f"   Це означає що логіка працює неправильно!")
    else:
        print(f"\n✅ Всі записи ідентичні - має бути stable")
    
    # Тепер перевіримо що передається в find_previous_rate для sell
    print(f"\n\n🔍 ЧОГО ОЧІКУЄТЬСЯ:")
    print("-" * 80)
    print(f"Для обмінника MIRVALUTY і PLN/UAH:")
    print(f"  При виклику find_previous_rate для SELL передається:")
    print(f"  - channel_id: {mirvaluty_id}")
    print(f"  - currency_a: PLN")
    print(f"  - currency_b: UAH")
    print(f"  - current_buy: {current_buy} (buy значення з поточного запису MIRVALUTY)")
    print(f"  - current_sell: {current_sell} (sell значення яке ми шукаємо)")
    
    print(f"\n  Логіка: порівнюємо ОБИДВА buy і sell разом!")
    print(f"  Якщо buy або sell відрізняються - знайдено baseline")
    print(f"  Але для розрахунку тренду використовуємо тільки sell з baseline")

if __name__ == "__main__":
    debug_pln_sell()

