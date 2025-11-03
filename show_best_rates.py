"""
Відображення найкращих курсів у вигляді таблиці
"""
import requests
from datetime import datetime

PRODUCTION_URL = "https://fxhub-backend.onrender.com"

def get_best_rates():
    """Отримання найкращих курсів з API"""
    try:
        response = requests.get(f"{PRODUCTION_URL}/rates/bestrate", timeout=10)
        if response.status_code == 200:
            data = response.json()
            # Адаптація до нового формату (success/data/meta)
            if isinstance(data, dict) and "data" in data:
                return data.get("data", [])
            return data if isinstance(data, list) else []
        else:
            print(f"❌ Помилка API: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Помилка запиту: {e}")
        return None

def format_table(rates_data):
    """Форматування даних у таблицю"""
    if not rates_data:
        print("❌ Немає даних")
        return
    
    print("\n" + "=" * 100)
    print("💰 НАЙКРАЩІ КУРСИ ВАЛЮТ")
    print("=" * 100)
    print(f"📅 Оновлено: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 100)
    
    # Заголовок таблиці
    print(f"{'Валютна пара':<15} │ {'Купівля':<10} │ {'Обмінник (куп)':<18} │ {'Продаж':<10} │ {'Обмінник (прод)':<18} │ {'Оновлено':<16}")
    print("─" * 100)
    
    # Сортуємо по валютній парі
    sorted_rates = sorted(rates_data, key=lambda x: x.get('currency', ''))
    
    for rate in sorted_rates:
        currency = rate.get('currency', 'N/A')
        
        # Купівля
        buy_best = rate.get('buy_best')
        buy_exchanger = rate.get('buy_exchanger', 'N/A')
        buy_timestamp = rate.get('buy_timestamp', '')
        if buy_timestamp:
            try:
                dt = datetime.fromisoformat(buy_timestamp.replace('Z', '+00:00'))
                buy_time = dt.strftime('%Y-%m-%d %H:%M')
            except:
                buy_time = buy_timestamp[:16]
        else:
            buy_time = 'N/A'
        
        # Продаж
        sell_best = rate.get('sell_best')
        sell_exchanger = rate.get('sell_exchanger', 'N/A')
        sell_timestamp = rate.get('sell_timestamp', '')
        if sell_timestamp:
            try:
                dt = datetime.fromisoformat(sell_timestamp.replace('Z', '+00:00'))
                sell_time = dt.strftime('%Y-%m-%d %H:%M')
            except:
                sell_time = sell_timestamp[:16]
        else:
            sell_time = 'N/A'
        
        # Форматуємо рядок
        buy_str = f"{buy_best:.4f}" if buy_best is not None else "N/A"
        sell_str = f"{sell_best:.4f}" if sell_best is not None else "N/A"
        
        # Скорочуємо час до HH:MM (якщо формат YYYY-MM-DD HH:MM)
        if ' ' in buy_time:
            buy_time_short = buy_time.split()[1][:5]  # Беремо HH:MM
        else:
            buy_time_short = buy_time[11:16] if len(buy_time) >= 16 else buy_time[:5]
        
        if ' ' in sell_time:
            sell_time_short = sell_time.split()[1][:5]
        else:
            sell_time_short = sell_time[11:16] if len(sell_time) >= 16 else sell_time[:5]
        
        # Об'єднуємо timestamp якщо однакові
        if buy_time == sell_time or (buy_time_short == sell_time_short and buy_time != 'N/A'):
            time_display = buy_time_short
        else:
            time_display = f"{buy_time_short}/{sell_time_short}"
        
        # Форматуємо рядок з правильними відступами
        row = f"{currency:<15} │ {buy_str:<10} │ {buy_exchanger:<18} │ {sell_str:<10} │ {sell_exchanger:<18} │ {time_display:<16}"
        print(row)
    
    print("=" * 100)
    
    # Статистика
    print(f"\n📊 Статистика:")
    print(f"   Всього валютних пар: {len(rates_data)}")
    
    # Підрахунок обмінників
    exchangers_buy = set()
    exchangers_sell = set()
    for rate in rates_data:
        if rate.get('buy_exchanger'):
            exchangers_buy.add(rate.get('buy_exchanger'))
        if rate.get('sell_exchanger'):
            exchangers_sell.add(rate.get('sell_exchanger'))
    
    print(f"   Унікальних обмінників (купівля): {len(exchangers_buy)}")
    print(f"   Унікальних обмінників (продаж): {len(exchangers_sell)}")
    
    print("\n" + "=" * 100)

def main():
    print("🔍 Отримання найкращих курсів з production API...")
    
    rates_data = get_best_rates()
    
    if rates_data:
        format_table(rates_data)
    else:
        print("❌ Не вдалося отримати дані")

if __name__ == "__main__":
    main()

