"""
Тестування виправленої логіки для PLN
Проблема: для SELL треба порівнювати ТІЛЬКИ sell значення, а не buy і sell разом
"""
from supabase_client import supabase

def test_correct_logic():
    print("=" * 80)
    print("🔧 ТЕСТУВАННЯ ВИПРАВЛЕНОЇ ЛОГІКИ")
    print("=" * 80)
    
    channels_resp = supabase.table("channels").select("id, name").execute()
    channel_map = {ch["name"]: ch["id"] for ch in channels_resp.data}
    mirvaluty_id = channel_map.get("MIRVALUTY")
    
    # Отримуємо записи
    query = supabase.table("rates").select(
        "buy, sell, edited"
    ).eq("channel_id", mirvaluty_id).eq("currency_a", "PLN").eq("currency_b", "UAH").order("edited", desc=True).limit(100)
    
    response = query.execute()
    records = response.data
    
    current_record = records[0]
    current_sell = current_record.get("sell")
    
    print(f"\n📊 Поточний sell: {current_sell}")
    print(f"   Перевіряємо попередні записи ТІЛЬКИ по sell значенню\n")
    
    # ПРАВИЛЬНА ЛОГІКА: порівнюємо ТІЛЬКИ sell
    identical_sell_count = 0
    first_different_sell = None
    
    for i, record in enumerate(records[1:], start=2):
        prev_sell = record.get("sell")
        
        # Порівнюємо ТІЛЬКИ sell!
        sell_different = (current_sell is not None and prev_sell is not None and abs(current_sell - prev_sell) > 0.0001) or \
                        (current_sell is None) != (prev_sell is None)
        
        if sell_different:
            first_different_sell = record
            print(f"✅ ЗНАЙДЕНО ВІДМІННИЙ SELL (№{i}):")
            print(f"   Sell: {prev_sell} (відрізняється від {current_sell})")
            print(f"   Timestamp: {record.get('edited')}")
            break
        else:
            identical_sell_count += 1
            if identical_sell_count <= 5:
                print(f"[{i}] Sell: {prev_sell} - ІДЕНТИЧНИЙ")
    
    print(f"\n📊 Результати:")
    print(f"   Ідентичних sell: {identical_sell_count}")
    
    if first_different_sell:
        baseline_sell = first_different_sell.get("sell")
        change = round(current_sell - baseline_sell, 2)
        trend = "up" if change > 0.0001 else "down" if change < -0.0001 else "stable"
        
        print(f"\n💡 Розрахунок:")
        print(f"   Поточний: {current_sell}")
        print(f"   Baseline: {baseline_sell}")
        print(f"   Зміна: {change}")
        print(f"   Тренд: {trend}")
        
        if identical_sell_count >= 100:
            print(f"\n   ✅ ВСІ 100+ ПОПЕРЕДНІХ SELL ІДЕНТИЧНІ - має бути stable")
        else:
            print(f"\n   ⚠️  Знайдено відмінний sell на записі №{identical_sell_count + 2}")
            print(f"   Має бути: trend={trend}, change={change}")
    else:
        print(f"\n✅ ВСІ {len(records) - 1} ПОПЕРЕДНІХ SELL ІДЕНТИЧНІ!")
        print(f"   Правильний результат: stable, 0.0")

if __name__ == "__main__":
    test_correct_logic()

