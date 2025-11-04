"""
Тестування endpoint /exchangers/pairs
Перевіряє структуру відповіді, наявність даних та відсутність дублікатів
"""
import requests
import json

PROD_URL = "https://fxhub-backend.onrender.com"
LOCAL_URL = "http://127.0.0.1:8000"

def test_exchanger_pairs(use_production=True):
    """Тестує endpoint /exchangers/pairs"""
    base_url = PROD_URL if use_production else LOCAL_URL
    url = f"{base_url}/exchangers/pairs"
    
    print("=" * 80)
    print(f"🧪 ТЕСТУВАННЯ /exchangers/pairs")
    print("=" * 80)
    print(f"URL: {url}")
    print("-" * 80)
    
    try:
        response = requests.get(url, timeout=60)
        
        if response.status_code != 200:
            print(f"❌ Помилка: HTTP {response.status_code}")
            print(f"Відповідь: {response.text}")
            return False
        
        data = response.json()
        
        # Перевірка структури відповіді
        if "success" not in data:
            print("❌ Відсутнє поле 'success'")
            return False
        
        if not data["success"]:
            print(f"❌ API повернуло помилку: {data.get('error', 'Unknown error')}")
            return False
        
        if "data" not in data:
            print("❌ Відсутнє поле 'data'")
            return False
        
        if "meta" not in data:
            print("❌ Відсутнє поле 'meta'")
            return False
        
        exchangers_data = data["data"]
        meta = data["meta"]
        
        # Перевірка метаданих
        print(f"\n📊 Метадані:")
        print(f"   total_exchangers: {meta.get('total_exchangers')}")
        print(f"   total_pairs: {meta.get('total_pairs')}")
        print(f"   generated_at: {meta.get('generated_at')}")
        
        # Перевірка даних
        if not isinstance(exchangers_data, list):
            print("❌ 'data' має бути списком")
            return False
        
        if len(exchangers_data) == 0:
            print("⚠️  Немає обмінників в відповіді")
            return False
        
        print(f"\n✅ Знайдено {len(exchangers_data)} обмінників")
        
        # Перевірка структури кожного обмінника
        all_exchangers = set()
        all_pairs = set()
        exchangers_with_no_pairs = []
        
        for i, exchanger_info in enumerate(exchangers_data, 1):
            # Перевірка обов'язкових полів
            if "exchanger" not in exchanger_info:
                print(f"❌ Обмінник #{i}: відсутнє поле 'exchanger'")
                return False
            
            if "pairs" not in exchanger_info:
                print(f"❌ Обмінник #{i}: відсутнє поле 'pairs'")
                return False
            
            exchanger_name = exchanger_info["exchanger"]
            pairs = exchanger_info["pairs"]
            
            # Перевірка на дублікати обмінників
            if exchanger_name in all_exchangers:
                print(f"❌ Знайдено дублікат обмінника: {exchanger_name}")
                return False
            
            all_exchangers.add(exchanger_name)
            
            # Перевірка що pairs є списком
            if not isinstance(pairs, list):
                print(f"❌ Обмінник {exchanger_name}: 'pairs' має бути списком")
                return False
            
            # Перевірка наявності пар
            if len(pairs) == 0:
                exchangers_with_no_pairs.append(exchanger_name)
            
            # Перевірка на дублікати пар в одному обміннику
            pairs_set = set(pairs)
            if len(pairs_set) != len(pairs):
                print(f"❌ Обмінник {exchanger_name}: знайдено дублікати валютних пар")
                return False
            
            # Перевірка на null/empty значення
            for pair in pairs:
                if not pair or not isinstance(pair, str):
                    print(f"❌ Обмінник {exchanger_name}: знайдено невалідну пару: {pair}")
                    return False
                
                # Перевірка формату пари (має містити "/")
                if "/" not in pair:
                    print(f"❌ Обмінник {exchanger_name}: невалідний формат пари: {pair}")
                    return False
                
                all_pairs.add(pair)
        
        # Виведення результатів
        print(f"\n✅ Перевірка структури:")
        print(f"   Унікальних обмінників: {len(all_exchangers)}")
        print(f"   Унікальних валютних пар: {len(all_pairs)}")
        
        if exchangers_with_no_pairs:
            print(f"\n⚠️  Обмінники без валютних пар: {', '.join(exchangers_with_no_pairs)}")
        else:
            print(f"   Всі обмінники мають хоча б одну валютну пару")
        
        # Перевірка сортування
        exchanger_names = [ex["exchanger"] for ex in exchangers_data]
        if exchanger_names != sorted(exchanger_names):
            print(f"❌ Обмінники не відсортовані за алфавітом")
            return False
        
        print(f"   Обмінники відсортовані за алфавітом")
        
        # Перевірка сортування пар для кожного обмінника
        for exchanger_info in exchangers_data:
            pairs = exchanger_info["pairs"]
            if pairs != sorted(pairs):
                print(f"❌ Обмінник {exchanger_info['exchanger']}: пари не відсортовані")
                return False
        
        print(f"   Валютні пари відсортовані для кожного обмінника")
        
        # Виведення перших кількох прикладів
        print(f"\n📋 Приклади (перші 3 обмінники):")
        for exchanger_info in exchangers_data[:3]:
            print(f"   {exchanger_info['exchanger']}: {len(exchanger_info['pairs'])} пар")
            if exchanger_info['pairs']:
                print(f"      Перші пари: {', '.join(exchanger_info['pairs'][:5])}")
        
        print(f"\n{'='*80}")
        print(f"✅ ВСІ ТЕСТИ ПРОЙДЕНО УСПІШНО!")
        print(f"{'='*80}")
        
        return True
        
    except requests.exceptions.Timeout:
        print(f"❌ Таймаут запиту (можливо сервіс спить)")
        return False
    except Exception as e:
        print(f"❌ Помилка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys
    
    use_prod = True
    if len(sys.argv) > 1 and sys.argv[1] == "--local":
        use_prod = False
    
    success = test_exchanger_pairs(use_production=use_prod)
    sys.exit(0 if success else 1)
