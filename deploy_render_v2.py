"""
Автоматичний деплой на Render через API (версія 2)
Спробуємо різні структури API
"""
import requests
import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

RENDER_API_KEY = os.getenv("RENDER_API_KEY")
GITHUB_REPO = "kulishdenis-Tech/fxhub_backend"
SERVICE_NAME = "fxhub-backend"

def get_owner_id(headers):
    """Отримання ownerID користувача"""
    try:
        response = requests.get("https://api.render.com/v1/owners", headers=headers)
        if response.status_code == 200:
            owners = response.json()
            if owners and len(owners) > 0:
                owner = owners[0] if isinstance(owners, list) else owners
                owner_id = owner.get('owner', {}).get('id') if isinstance(owner, dict) else owner.get('id')
                if owner_id:
                    return owner_id
    except Exception as e:
        print(f"   Помилка отримання ownerID (owners endpoint): {e}")
    
    try:
        response = requests.get("https://api.render.com/v1/services", headers=headers)
        if response.status_code == 200:
            services = response.json()
            if services and len(services) > 0:
                service = services[0] if isinstance(services, list) else services
                service_data = service.get('service', {}) if isinstance(service, dict) else service
                owner_id = service_data.get('ownerId')
                if owner_id:
                    return owner_id
    except Exception as e:
        print(f"   Помилка отримання ownerID (services endpoint): {e}")
    
    return None

def check_existing_service(headers):
    """Перевірка чи сервіс вже існує"""
    try:
        response = requests.get("https://api.render.com/v1/services", headers=headers)
        if response.status_code == 200:
            services = response.json()
            if isinstance(services, list):
                for service in services:
                    service_data = service.get('service', {}) if isinstance(service, dict) else service
                    if service_data.get('name') == SERVICE_NAME:
                        return service_data.get('id')
            elif isinstance(services, dict):
                if services.get('name') == SERVICE_NAME:
                    return services.get('id')
    except Exception as e:
        print(f"   Помилка перевірки сервісів: {e}")
    return None

def create_render_service():
    """Створення Web Service на Render через API"""
    if not RENDER_API_KEY:
        print("⚠️  RENDER_API_KEY не знайдено в .env")
        return False
    
    print(f"🔧 Створення Web Service на Render...")
    
    headers = {
        "Authorization": f"Bearer {RENDER_API_KEY}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    # Перевірка чи сервіс вже існує
    existing_id = check_existing_service(headers)
    if existing_id:
        print(f"ℹ️  Сервіс {SERVICE_NAME} вже існує на Render")
        print(f"   🔗 https://dashboard.render.com/web/{existing_id}")
        return True
    
    # Отримуємо ownerID
    print("   Отримуємо ownerID...")
    owner_id = get_owner_id(headers)
    
    if not owner_id:
        print("❌ Не вдалося отримати ownerID")
        return False
    
    print(f"   ✅ OwnerID: {owner_id[:8]}...")
    
    supabase_url = os.getenv("SUPABASE_URL", "")
    supabase_key = os.getenv("SUPABASE_KEY", "")
    
    if not supabase_url or not supabase_key:
        print("⚠️  SUPABASE_URL або SUPABASE_KEY не знайдено в .env")
        return False
    
    # Спробуємо кілька варіантів структури
    print("   Спробуємо створення сервісу...")
    
    # Варіант 1: runtime на верхньому рівні + serviceDetails
    data_v1 = {
        "type": "web_service",
        "name": SERVICE_NAME,
        "ownerId": owner_id,
        "repo": f"https://github.com/{GITHUB_REPO}",
        "branch": "main",
        "runtime": "python",
        "plan": "free",
        "region": "oregon",
        "buildCommand": "pip install -r requirements.txt",
        "serviceDetails": {
            "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT",
            "envSpecificDetails": {
                "env": "python"
            }
        },
        "envVars": [
            {"key": "SUPABASE_URL", "value": supabase_url},
            {"key": "SUPABASE_KEY", "value": supabase_key}
        ]
    }
    
    # Варіант 2: Все в serviceDetails
    data_v2 = {
        "type": "web_service",
        "name": SERVICE_NAME,
        "ownerId": owner_id,
        "repo": f"https://github.com/{GITHUB_REPO}",
        "branch": "main",
        "plan": "free",
        "region": "oregon",
        "serviceDetails": {
            "runtime": "python",
            "buildCommand": "pip install -r requirements.txt",
            "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT",
            "envSpecificDetails": {
                "env": "python"
            }
        },
        "envVars": [
            {"key": "SUPABASE_URL", "value": supabase_url},
            {"key": "SUPABASE_KEY", "value": supabase_key}
        ]
    }
    
    # Варіант 3: Мінімальна структура з runtime на верхньому рівні
    data_v3 = {
        "type": "web_service",
        "name": SERVICE_NAME,
        "ownerId": owner_id,
        "repo": f"https://github.com/{GITHUB_REPO}",
        "branch": "main",
        "runtime": "python",
        "plan": "free",
        "region": "oregon",
        "buildCommand": "pip install -r requirements.txt",
        "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT",
        "serviceDetails": {
            "envSpecificDetails": {
                "env": "python"
            }
        },
        "envVars": [
            {"key": "SUPABASE_URL", "value": supabase_url},
            {"key": "SUPABASE_KEY", "value": supabase_key}
        ]
    }
    
    # Пробуємо кожен варіант
    for i, data in enumerate([data_v1, data_v2, data_v3], 1):
        print(f"\n   Спроба {i}/3...")
        try:
            response = requests.post(
                "https://api.render.com/v1/services",
                headers=headers,
                json=data
            )
            
            if response.status_code == 201:
                service_data = response.json()
                service_obj = service_data.get('service', service_data)
                service_id = service_obj.get('id')
                
                print(f"✅ Web Service створено на Render!")
                print(f"   🔗 Dashboard: https://dashboard.render.com/web/{service_id}")
                
                # Отримуємо URL сервісу
                service_details = service_obj.get('serviceDetails', {})
                service_url = service_details.get('url')
                if service_url:
                    print(f"   🌐 URL: {service_url}")
                else:
                    print(f"   ⏳ URL буде доступний після завершення деплою")
                
                return True
            else:
                error_msg = response.text[:200]
                print(f"   ❌ Помилка {response.status_code}: {error_msg}")
                if i < 3:
                    continue
                else:
                    print(f"\n   Детальна відповідь: {response.text[:500]}")
        except Exception as e:
            print(f"   ❌ Виняток: {e}")
            if i < 3:
                continue
    
    return False

def main():
    print("=" * 70)
    print("🚀 Автоматичний деплой на Render (API)")
    print("=" * 70)
    
    if create_render_service():
        print("\n" + "=" * 70)
        print("✅ Деплой ініційовано!")
        print("=" * 70)
        print("\n⏳ Чекай 1-2 хвилини поки Render задеплоїть сервіс")
        print("   Перевір статус в Render Dashboard")
        print("\n💡 Після деплою можна тестувати:")
        print("   - python test_production.py")
    else:
        print("\n" + "=" * 70)
        print("⚠️  Автоматичний деплой через API не вдався")
        print("=" * 70)
        print("\n💡 Альтернатива: Деплой через веб-інтерфейс (2 хвилини)")
        print("   1. https://dashboard.render.com")
        print("   2. New + → Web Service")
        print("   3. Підключи GitHub: fxhub_backend")
        print("   4. Render автоматично використає render.yaml")
        print("   5. Додай Environment Variables")
        print("\nДетальніше: quick_render_deploy.md")

if __name__ == "__main__":
    main()
