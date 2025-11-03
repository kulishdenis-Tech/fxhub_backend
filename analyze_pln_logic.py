"""
Детальний аналіз логіки skip-duplicate для PLN/UAH
Перевіряє чи правильно працює логіка коли всі попередні записи ідентичні
"""
import requests
from supabase_client import supabase
import json
from datetime import datetime

def analyze_pln_rates():
    """
    Аналізує PLN/UAH курси та перевіряє логіку skip-duplicate
    """
    print("=" * 80)
    print("🔍 ДЕТАЛЬНИЙ АНАЛІЗ PLN/UAH З ЛОГІКОЮ SKIP-DUPLICATE")
    print("=" * 80)
    
    # 1. Отримуємо поточні дані з API
    print("\n📡 КРОК 1: Отримання поточних даних з API")
    print("-" * 80)
    
    try:
        api_url = "https://fxhub-backend.onrender.com/rates/bestrate"
        response = requests.get(api_url, params={"currencies": "PLN/UAH"}, timeout=60)
        
        if response.status_code != 200:
            print(f"❌ Помилка API: {response.status_code}")
            return
        
        data = response.json()
        
        if "data" not in data or not data["data"]:
            print("❌ Немає даних для PLN/UAH")
            return
        
        pln_data = data["data"][0]
        
        print(f"✅ Отримано дані для PLN/UAH:")
        print(f"   Купівля:  {pln_data.get('buy_best')} (тренд: {pln_data.get('buy_trend')}, зміна: {pln_data.get('buy_change_abs')})")
        print(f"   Обмінник (купівля): {pln_data.get('buy_exchanger')}")
        print(f"   Продаж:  {pln_data.get('sell_best')} (тренд: {pln_data.get('sell_trend')}, зміна: {pln_data.get('sell_change_abs')})")
        print(f"   Обмінник (продаж): {pln_data.get('sell_exchanger')}")
        
        buy_exchanger = pln_data.get('buy_exchanger')
        sell_exchanger = pln_data.get('sell_exchanger')
        current_buy = pln_data.get('buy_best')
        current_sell = pln_data.get('sell_best')
        
    except Exception as e:
        print(f"❌ Помилка отримання даних з API: {e}")
        return
    
    # 2. Отримуємо channel_id для обмінників
    print("\n📡 КРОК 2: Отримання channel_id для обмінників")
    print("-" * 80)
    
    try:
        channels_resp = supabase.table("channels").select("id, name").execute()
        channel_map = {ch["name"]: ch["id"] for ch in channels_resp.data}
        
        buy_channel_id = channel_map.get(buy_exchanger)
        sell_channel_id = channel_map.get(sell_exchanger)
        
        print(f"   Channel ID для {buy_exchanger}: {buy_channel_id}")
        print(f"   Channel ID для {sell_exchanger}: {sell_channel_id}")
        
        if not buy_channel_id or not sell_channel_id:
            print("❌ Не вдалося знайти channel_id")
            return
            
    except Exception as e:
        print(f"❌ Помилка отримання channels: {e}")
        return
    
    # 3. Аналізуємо дані для BUY
    print("\n📈 КРОК 3: АНАЛІЗ КУПІВЛІ (BUY)")
    print("-" * 80)
    print(f"   Обмінник: {buy_exchanger}")
    print(f"   Поточний курс: {current_buy}")
    print(f"   Очікуваний результат: {pln_data.get('buy_trend')} (зміна: {pln_data.get('buy_change_abs')})")
    
    try:
        # Отримуємо останні 100 записів
        query = supabase.table("rates").select(
            "buy, sell, edited"
        ).eq("channel_id", buy_channel_id).eq("currency_a", "PLN").eq("currency_b", "UAH").order("edited", desc=True).limit(100)
        
        response = query.execute()
        
        if not response.data:
            print("❌ Немає даних в БД")
            return
        
        records = response.data
        print(f"\n   📊 Знайдено {len(records)} записів в БД (останні 100)")
        
        # Знаходимо поточний запис (перший)
        if len(records) == 0:
            print("   ❌ Немає записів")
            return
        
        current_record = records[0]
        print(f"\n   🔹 Поточний запис (перший):")
        print(f"      Buy: {current_record.get('buy')}")
        print(f"      Sell: {current_record.get('sell')}")
        print(f"      Timestamp: {current_record.get('edited')}")
        
        # Перевіряємо попередні записи
        identical_count = 0
        different_found = False
        first_different = None
        
        print(f"\n   🔍 Перевірка попередніх записів (пропуск дублікатів):")
        
        for i, record in enumerate(records[1:], start=2):  # Пропускаємо перший (поточний)
            prev_buy = record.get("buy")
            prev_sell = record.get("sell")
            
            # Перевіряємо чи відрізняється
            buy_different = (current_buy is not None and prev_buy is not None and abs(current_buy - prev_buy) > 0.0001) or \
                           (current_buy is None) != (prev_buy is None)
            sell_different = (current_sell is not None and prev_sell is not None and abs(current_sell - prev_sell) > 0.0001) or \
                            (current_sell is None) != (prev_sell is None)
            
            if buy_different or sell_different:
                different_found = True
                first_different = {
                    "index": i,
                    "buy": prev_buy,
                    "sell": prev_sell,
                    "timestamp": record.get("edited"),
                    "buy_different": buy_different,
                    "sell_different": sell_different
                }
                print(f"\n   ✅ ЗНАЙДЕНО ВІДМІННИЙ ЗАПИС (№{i}):")
                print(f"      Buy: {prev_buy} {'(відрізняється)' if buy_different else ''}")
                print(f"      Sell: {prev_sell} {'(відрізняється)' if sell_different else ''}")
                print(f"      Timestamp: {record.get('edited')}")
                break
            else:
                identical_count += 1
                if identical_count <= 5:  # Показуємо перші 5 ідентичних
                    print(f"      [{i}] Buy: {prev_buy}, Sell: {prev_sell} - ІДЕНТИЧНИЙ")
                elif identical_count == 6:
                    print(f"      ... (ще {len(records) - i - 1} ідентичних записів)")
        
        print(f"\n   📊 Результати аналізу:")
        print(f"      • Всього перевірено записів: {len(records) - 1}")
        print(f"      • Ідентичних записів: {identical_count}")
        
        if different_found and first_different:
            print(f"      • Перший відмінний запис: №{first_different['index']}")
            print(f"      • Buy baseline: {first_different['buy']}")
            
            # Розраховуємо зміну
            if first_different['buy_different'] and current_buy and first_different['buy']:
                calculated_change = round(current_buy - first_different['buy'], 2)
                calculated_trend = "up" if calculated_change > 0.0001 else "down" if calculated_change < -0.0001 else "stable"
                
                print(f"\n   💡 Розрахунок:")
                print(f"      Поточний: {current_buy}")
                print(f"      Попередній (baseline): {first_different['buy']}")
                print(f"      Розрахована зміна: {calculated_change}")
                print(f"      Розрахований тренд: {calculated_trend}")
                print(f"      З API: зміна {pln_data.get('buy_change_abs')}, тренд {pln_data.get('buy_trend')}")
                
                if abs(calculated_change - pln_data.get('buy_change_abs', 0)) < 0.01 and calculated_trend == pln_data.get('buy_trend'):
                    print(f"      ✅ РОЗРАХУНОК ЗБІГАЄТЬСЯ З API")
                else:
                    print(f"      ⚠️  РОЗРАХУНОК НЕ ЗБІГАЄТЬСЯ З API")
        else:
            print(f"\n   ⚠️  ВСІ {len(records) - 1} ПОПЕРЕДНІХ ЗАПИСІВ ІДЕНТИЧНІ!")
            print(f"      Очікуваний результат: trend='stable', change_abs=0.0")
            print(f"      Фактичний результат: trend='{pln_data.get('buy_trend')}', change_abs={pln_data.get('buy_change_abs')}")
            
            if pln_data.get('buy_trend') == 'stable' and abs(pln_data.get('buy_change_abs', 0)) < 0.01:
                print(f"      ✅ ЛОГІКА ПРАЦЮЄ ПРАВИЛЬНО - ВСІ ІДЕНТИЧНІ = STABLE")
            else:
                print(f"      ❌ ЛОГІКА ПРАЦЮЄ НЕПРАВИЛЬНО - МАЄ БУТИ STABLE")
    
    except Exception as e:
        print(f"❌ Помилка аналізу buy: {e}")
        import traceback
        traceback.print_exc()
    
    # 4. Аналізуємо дані для SELL
    print("\n\n📉 КРОК 4: АНАЛІЗ ПРОДАЖУ (SELL)")
    print("-" * 80)
    print(f"   Обмінник: {sell_exchanger}")
    print(f"   Поточний курс: {current_sell}")
    print(f"   Очікуваний результат: {pln_data.get('sell_trend')} (зміна: {pln_data.get('sell_change_abs')})")
    
    try:
        # Отримуємо останні 100 записів для sell обмінника
        query = supabase.table("rates").select(
            "buy, sell, edited"
        ).eq("channel_id", sell_channel_id).eq("currency_a", "PLN").eq("currency_b", "UAH").order("edited", desc=True).limit(100)
        
        response = query.execute()
        
        if not response.data:
            print("❌ Немає даних в БД")
            return
        
        records = response.data
        print(f"\n   📊 Знайдено {len(records)} записів в БД (останні 100)")
        
        current_record = records[0]
        print(f"\n   🔹 Поточний запис (перший):")
        print(f"      Buy: {current_record.get('buy')}")
        print(f"      Sell: {current_record.get('sell')}")
        print(f"      Timestamp: {current_record.get('edited')}")
        
        # Отримуємо поточні значення buy для sell обмінника (для правильного skip-duplicate)
        current_sell_rate = records[0]
        current_sell_value = current_sell
        current_buy_value_for_sell = current_sell_rate.get("buy")
        
        # Перевіряємо попередні записи
        identical_count = 0
        different_found = False
        first_different = None
        
        print(f"\n   🔍 Перевірка попередніх записів (пропуск дублікатів):")
        print(f"      Порівнюємо: Buy={current_buy_value_for_sell}, Sell={current_sell_value}")
        
        for i, record in enumerate(records[1:], start=2):
            prev_buy = record.get("buy")
            prev_sell = record.get("sell")
            
            # Перевіряємо чи відрізняється (порівнюємо ОБИДВА значення!)
            buy_different = (current_buy_value_for_sell is not None and prev_buy is not None and abs(current_buy_value_for_sell - prev_buy) > 0.0001) or \
                           (current_buy_value_for_sell is None) != (prev_buy is None)
            sell_different = (current_sell_value is not None and prev_sell is not None and abs(current_sell_value - prev_sell) > 0.0001) or \
                            (current_sell_value is None) != (prev_sell is None)
            
            if buy_different or sell_different:
                different_found = True
                first_different = {
                    "index": i,
                    "buy": prev_buy,
                    "sell": prev_sell,
                    "timestamp": record.get("edited"),
                    "buy_different": buy_different,
                    "sell_different": sell_different
                }
                print(f"\n   ✅ ЗНАЙДЕНО ВІДМІННИЙ ЗАПИС (№{i}):")
                print(f"      Buy: {prev_buy} {'(відрізняється)' if buy_different else ''}")
                print(f"      Sell: {prev_sell} {'(відрізняється)' if sell_different else ''}")
                print(f"      Timestamp: {record.get('edited')}")
                break
            else:
                identical_count += 1
                if identical_count <= 5:
                    print(f"      [{i}] Buy: {prev_buy}, Sell: {prev_sell} - ІДЕНТИЧНИЙ")
                elif identical_count == 6:
                    print(f"      ... (ще {len(records) - i - 1} ідентичних записів)")
        
        print(f"\n   📊 Результати аналізу:")
        print(f"      • Всього перевірено записів: {len(records) - 1}")
        print(f"      • Ідентичних записів: {identical_count}")
        
        if different_found and first_different:
            print(f"      • Перший відмінний запис: №{first_different['index']}")
            print(f"      • Sell baseline: {first_different['sell']}")
            
            # Розраховуємо зміну
            if first_different['sell_different'] and current_sell and first_different['sell']:
                calculated_change = round(current_sell - first_different['sell'], 2)
                calculated_trend = "up" if calculated_change > 0.0001 else "down" if calculated_change < -0.0001 else "stable"
                
                print(f"\n   💡 Розрахунок:")
                print(f"      Поточний: {current_sell}")
                print(f"      Попередній (baseline): {first_different['sell']}")
                print(f"      Розрахована зміна: {calculated_change}")
                print(f"      Розрахований тренд: {calculated_trend}")
                print(f"      З API: зміна {pln_data.get('sell_change_abs')}, тренд {pln_data.get('sell_trend')}")
                
                if abs(calculated_change - pln_data.get('sell_change_abs', 0)) < 0.01 and calculated_trend == pln_data.get('sell_trend'):
                    print(f"      ✅ РОЗРАХУНОК ЗБІГАЄТЬСЯ З API")
                else:
                    print(f"      ⚠️  РОЗРАХУНОК НЕ ЗБІГАЄТЬСЯ З API")
        else:
            print(f"\n   ⚠️  ВСІ {len(records) - 1} ПОПЕРЕДНІХ ЗАПИСІВ ІДЕНТИЧНІ!")
            print(f"      Очікуваний результат: trend='stable', change_abs=0.0")
            print(f"      Фактичний результат: trend='{pln_data.get('sell_trend')}', change_abs={pln_data.get('sell_change_abs')}")
            
            if pln_data.get('sell_trend') == 'stable' and abs(pln_data.get('sell_change_abs', 0)) < 0.01:
                print(f"      ✅ ЛОГІКА ПРАЦЮЄ ПРАВИЛЬНО - ВСІ ІДЕНТИЧНІ = STABLE")
            else:
                print(f"      ❌ ЛОГІКА ПРАЦЮЄ НЕПРАВИЛЬНО - МАЄ БУТИ STABLE")
    
    except Exception as e:
        print(f"❌ Помилка аналізу sell: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("✅ АНАЛІЗ ЗАВЕРШЕНО")
    print("=" * 80)

if __name__ == "__main__":
    analyze_pln_rates()

