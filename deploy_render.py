"""
Автоматичний деплой на Render через API
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
        # Отримуємо інформацію про користувача
        response = requests.get("https://api.render.com/v1/owners", headers=headers)
        if response.status_code == 200:
            owners = response.json()
            if owners and len(owners) > 0:
                # Беремо першого owner (зазвичай це користувач)
                owner_id = owners[0].get('owner', {}).get('id') if isinstance(owners[0], dict) else owners[0].get('id')
                return owner_id
    except:
        pass
    
    # Альтернативний метод - отримуємо з сервісів
    try:
        response = requests.get("https://api.render.com/v1/services", headers=headers)
        if response.status_code == 200:
            services = response.json()
            if services and len(services) > 0:
                owner_id = services[0].get('service', {}).get('ownerId')
                if owner_id:
                    return owner_id
    except:
        pass
    
    return None

def create_render_service():
    """Створення Web Service на Render через API"""
    if not RENDER_API_KEY:
        print("⚠️  RENDER_API_KEY не знайдено в .env")
        print("\n💡 Щоб автоматично задеплоїти на Render:")
        print("1. Відкрий: https://dashboard.render.com/account/api-keys")
        print("2. Створи API ключ")
        print("3. Додай в .env: RENDER_API_KEY=твій_ключ")
        print("4. Запусти цей скрипт знову")
        return False
    
    print(f"🔧 Створення Web Service на Render...")
    
    headers = {
        "Authorization": f"Bearer {RENDER_API_KEY}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    # Отримуємо ownerID
    print("   Отримуємо ownerID...")
    owner_id = get_owner_id(headers)
    
    if not owner_id:
        # Остання спроба - через user endpoint
        try:
            response = requests.get("https://api.render.com/v1/users/me", headers=headers)
            if response.status_code == 200:
                user_data = response.json()
                owner_id = user_data.get('user', {}).get('id')
        except:
            pass
    
    if not owner_id:
        print("❌ Не вдалося отримати ownerID")
        print("   Спробуй створити сервіс вручну через Dashboard")
        return False
    
    print(f"   ✅ OwnerID: {owner_id[:8]}...")
    
    # Отримуємо список сервісів для перевірки
    response = requests.get("https://api.render.com/v1/services", headers=headers)
    
    if response.status_code == 401:
        print("❌ Невалідний RENDER_API_KEY")
        return False
    
    # Перевірка чи сервіс вже існує
    services = response.json() if response.status_code == 200 else []
    for service in services:
        service_data = service.get('service', {}) if isinstance(service, dict) else service
        if service_data.get('name') == SERVICE_NAME:
            service_id = service_data.get('id')
            print(f"ℹ️  Сервіс {SERVICE_NAME} вже існує на Render")
            print(f"   🔗 https://dashboard.render.com/web/{service_id}")
            return True
    
    # Створення нового сервісу
    supabase_url = os.getenv("SUPABASE_URL", "")
    supabase_key = os.getenv("SUPABASE_KEY", "")
    
    if not supabase_url or not supabase_key:
        print("⚠️  SUPABASE_URL або SUPABASE_KEY не знайдено в .env")
        print("   Додай їх перед деплоєм")
        return False
    
    data = {
        "type": "web_service",
        "name": SERVICE_NAME,
        "ownerId": owner_id,
        "repo": f"https://github.com/{GITHUB_REPO}",
        "branch": "main",
        "plan": "free",
        "region": "oregon",
        "buildCommand": "pip install -r requirements.txt",
        "serviceDetails": {
            "runtime": "python",
            "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT",
            "envSpecificDetails": {
                "env": "python"
            }
        },
        "envVars": [
            {
                "key": "SUPABASE_URL",
                "value": supabase_url
            },
            {
                "key": "SUPABASE_KEY",
                "value": supabase_key
            }
        ]
    }
    
    try:
        response = requests.post(
            "https://api.render.com/v1/services",
            headers=headers,
            json=data
        )
        
        if response.status_code == 201:
            service_data = response.json()
            service_id = service_data.get('service', {}).get('id')
            service_url = service_data.get('service', {}).get('serviceDetails', {}).get('url')
            
            print(f"✅ Web Service створено на Render!")
            print(f"   🔗 Dashboard: https://dashboard.render.com/web/{service_id}")
            if service_url:
                print(f"   🌐 URL: {service_url}")
            return True
        else:
            print(f"❌ Помилка API: {response.status_code}")
            print(f"   Відповідь: {response.text[:300]}")
            return False
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return False

def main():
    print("=" * 70)
    print("🚀 Автоматичний деплой на Render")
    print("=" * 70)
    
    if create_render_service():
        print("\n" + "=" * 70)
        print("✅ Деплой ініційовано!")
        print("=" * 70)
        print("\n⏳ Чекай 1-2 хвилини поки Render задеплоїть сервіс")
        print("   Перевір статус в Render Dashboard")
    else:
        print("\n" + "=" * 70)
        print("💡 Інструкції для ручного деплою:")
        print("=" * 70)
        print("\n1. Відкрий: https://dashboard.render.com")
        print("2. New + → Web Service")
        print("3. Підключи GitHub репозиторій: fxhub_backend")
        print("4. Render автоматично використає render.yaml")
        print("5. Додай Environment Variables:")
        print(f"   - SUPABASE_URL = {os.getenv('SUPABASE_URL', 'your_url')}")
        print(f"   - SUPABASE_KEY = {os.getenv('SUPABASE_KEY', 'your_key')[:20]}...")
        print("6. Create Web Service")
        print("\nДетальніше: DEPLOY_INSTRUCTIONS.md")

if __name__ == "__main__":
    main()
