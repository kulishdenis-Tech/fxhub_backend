"""
Автоматичний деплой на Render через Blueprint API (використовує render.yaml)
"""
import requests
import os
import base64
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

RENDER_API_KEY = os.getenv("RENDER_API_KEY")
GITHUB_REPO = "kulishdenis-Tech/fxhub_backend"
SERVICE_NAME = "fxhub-backend"

def get_owner_id(headers):
    """Отримання ownerID"""
    try:
        response = requests.get("https://api.render.com/v1/owners", headers=headers)
        if response.status_code == 200:
            owners = response.json()
            if owners and len(owners) > 0:
                owner = owners[0] if isinstance(owners, list) else owners
                owner_id = owner.get('owner', {}).get('id') if isinstance(owner, dict) else owner.get('id')
                if owner_id:
                    return owner_id
    except:
        pass
    return None

def create_via_blueprint(headers, owner_id):
    """Створення через Blueprint API (використовує render.yaml)"""
    print("   Використовуємо Blueprint API (render.yaml)...")
    
    # Читаємо render.yaml
    render_yaml_path = Path(__file__).parent / "render.yaml"
    if not render_yaml_path.exists():
        print("   ❌ render.yaml не знайдено")
        return False
    
    with open(render_yaml_path, 'r') as f:
        render_yaml_content = f.read()
    
    # Створюємо blueprint через GitHub repo (Render сам підхопить render.yaml)
    data = {
        "ownerId": owner_id,
        "repo": f"https://github.com/{GITHUB_REPO}",
        "branch": "main"
    }
    
    try:
        response = requests.post(
            "https://api.render.com/v1/blueprints",
            headers=headers,
            json=data
        )
        
        if response.status_code == 201:
            blueprint_data = response.json()
            blueprint_id = blueprint_data.get('id')
            print(f"   ✅ Blueprint створено: {blueprint_id}")
            
            # Тепер потрібно задеплоїти blueprint
            deploy_data = {
                "blueprintId": blueprint_id
            }
            
            deploy_response = requests.post(
                f"https://api.render.com/v1/blueprints/{blueprint_id}/deploy",
                headers=headers,
                json=deploy_data
            )
            
            if deploy_response.status_code in [200, 201]:
                print(f"   ✅ Blueprint деплой ініційовано")
                return True
        else:
            print(f"   ❌ Помилка Blueprint API: {response.status_code}")
            print(f"   {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Виняток: {e}")
    
    return False

def create_direct_service(headers, owner_id):
    """Пряме створення сервісу (фінальна спроба з правильною структурою)"""
    print("   Пряме створення сервісу...")
    
    supabase_url = os.getenv("SUPABASE_URL", "")
    supabase_key = os.getenv("SUPABASE_KEY", "")
    
    # Фінальна структура на основі помилок API
    data = {
        "type": "web_service",
        "name": SERVICE_NAME,
        "ownerId": owner_id,
        "repo": f"https://github.com/{GITHUB_REPO}",
        "branch": "main",
        "plan": "free",
        "region": "oregon",
        "serviceDetails": {
            "buildCommand": "pip install -r requirements.txt",
            "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT",
            "envSpecificDetails": {
                "env": "python",
                "runtime": "python"
            }
        },
        "envVars": [
            {"key": "SUPABASE_URL", "value": supabase_url},
            {"key": "SUPABASE_KEY", "value": supabase_key}
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
            service_obj = service_data.get('service', service_data)
            service_id = service_obj.get('id')
            
            print(f"✅ Web Service створено!")
            print(f"   🔗 https://dashboard.render.com/web/{service_id}")
            
            service_details = service_obj.get('serviceDetails', {})
            service_url = service_details.get('url')
            if service_url:
                print(f"   🌐 URL: {service_url}")
            
            return True
        else:
            error = response.text[:300]
            print(f"   ❌ Помилка {response.status_code}: {error}")
            return False
    except Exception as e:
        print(f"   ❌ Виняток: {e}")
        return False

def main():
    print("=" * 70)
    print("🚀 Автоматичний деплой на Render (фінальна версія)")
    print("=" * 70)
    
    if not RENDER_API_KEY:
        print("❌ RENDER_API_KEY не знайдено в .env")
        return
    
    headers = {
        "Authorization": f"Bearer {RENDER_API_KEY}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    # Отримуємо ownerID
    print("   Отримуємо ownerID...")
    owner_id = get_owner_id(headers)
    
    if not owner_id:
        print("❌ Не вдалося отримати ownerID")
        return
    
    print(f"   ✅ OwnerID: {owner_id[:8]}...")
    
    # Перевірка чи сервіс вже існує
    try:
        response = requests.get("https://api.render.com/v1/services", headers=headers)
        if response.status_code == 200:
            services = response.json()
            if isinstance(services, list):
                for service in services:
                    service_data = service.get('service', {}) if isinstance(service, dict) else service
                    if service_data.get('name') == SERVICE_NAME:
                        service_id = service_data.get('id')
                        print(f"ℹ️  Сервіс {SERVICE_NAME} вже існує")
                        print(f"   🔗 https://dashboard.render.com/web/{service_id}")
                        return
    except:
        pass
    
    # Спробуємо Blueprint API
    if not create_via_blueprint(headers, owner_id):
        # Якщо не спрацювало, пробуємо пряме створення
        if create_direct_service(headers, owner_id):
            print("\n✅ Деплой успішний!")
        else:
            print("\n⚠️  Автоматичний деплой не вдався")
            print("\n💡 Рекомендація: Деплой через веб (2 хвилини)")
            print("   Render автоматично використає render.yaml")
    else:
        print("\n✅ Деплой через Blueprint успішний!")

if __name__ == "__main__":
    main()
