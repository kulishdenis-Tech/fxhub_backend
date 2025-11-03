# ⚡ Швидкий старт для деплою

## Крок 1: Створити GitHub репозиторій (2 хвилини)

### Варіант A: Через браузер (рекомендовано)

1. Відкрий: https://github.com/new
2. Заповни форму:
   - **Repository name**: `fxhub_backend`
   - **Description**: `FastAPI backend for FX Hub`
   - **Visibility**: Public або Private
   - ⚠️ **НЕ** додавай README, .gitignore, license
3. Натисни **"Create repository"**

### Варіант B: Автоматично через скрипт

Якщо маєш GitHub Personal Access Token:

```bash
# Зміни TOKEN на свій токен
python -c "
import requests
headers = {'Authorization': 'token YOUR_TOKEN_HERE'}
data = {'name': 'fxhub_backend', 'description': 'FastAPI backend for FX Hub'}
r = requests.post('https://api.github.com/user/repos', json=data, headers=headers)
print('✅ Репозиторій створено!' if r.status_code == 201 else f'❌ Помилка: {r.text}')
"
```

---

## Крок 2: Push код на GitHub (30 секунд)

Після створення репозиторію виконай:

```bash
cd "C:\Users\kulis\Documents\Google drive\Exchange\FastAPI\fxhub_backend"

# Якщо remote ще не додано:
git remote add origin https://github.com/kulishdenis-Tech/fxhub_backend.git

# Push на GitHub:
git push -u origin main
```

**Якщо Git запитує credentials:**
- **Username**: `kulishdenis-Tech`
- **Password**: GitHub Personal Access Token (НЕ пароль від акаунту!)

> 💡 Створити токен: https://github.com/settings/tokens → Generate new token (classic) → вибери `repo` scope

**Або використай скрипт:**
```bash
python setup_github.py
```

---

## Крок 3: Деплой на Render (5 хвилин)

### 3.1 Створити Web Service

1. Відкрий: https://dashboard.render.com
2. Натисни **"New +"** → **"Web Service"**
3. Підключи GitHub:
   - Натисни **"Connect GitHub"** (якщо ще не підключений)
   - Дозволь доступ до `fxhub_backend`
   - Вибери репозиторій: **`kulishdenis-Tech/fxhub_backend`**

### 3.2 Налаштування (Render використає `render.yaml` автоматично)

- **Name**: `fxhub-backend`
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt` ✅ (вже в render.yaml)
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT` ✅ (вже в render.yaml)

### 3.3 Додати Environment Variables

В розділі **"Environment"** додай:

| Key | Value | Де знайти |
|-----|-------|-----------|
| `SUPABASE_URL` | `https://gtuibuzglapqlzsqruol.supabase.co` | З твого `.env` файлу |
| `SUPABASE_KEY` | `eyJhbGci...` (повний ключ) | З твого `.env` файлу (Service Role Key!) |

> ⚠️ **ВАЖЛИВО**: Використай **Service Role Key**!
> 
> Як знайти:
> 1. Supabase Dashboard → Settings → API
> 2. Розділ "Project API keys"
> 3. Скопіюй **"service_role"** key (secret, починається з `eyJhbG...`)

### 3.4 Запустити деплой

1. Натисни **"Create Web Service"**
2. Чекай 1-2 хвилини
3. Render надасть URL: `https://fxhub-backend.onrender.com`

---

## Крок 4: Перевірка ✅

Тестуй ендпоінти:

```bash
# Root
curl https://fxhub-backend.onrender.com/

# Best rates
curl https://fxhub-backend.onrender.com/rates/bestrate

# Exchangers
curl https://fxhub-backend.onrender.com/exchangers/list

# Currencies
curl https://fxhub-backend.onrender.com/currencies/list
```

Або відкрий в браузері:
- **Swagger UI**: `https://fxhub-backend.onrender.com/docs`
- **ReDoc**: `https://fxhub-backend.onrender.com/redoc`

---

## 🎉 Готово!

Тепер твій FastAPI backend працює публічно на Render!

### Автоматичні оновлення

При кожному `git push origin main` Render автоматично:
1. Виявить зміни
2. Запустить новий build
3. Задеплоїть оновлену версію

---

## 📚 Детальні інструкції

Див. `DEPLOY_INSTRUCTIONS.md` для повної документації з troubleshooting та моніторингом.

---

## ❓ Troubleshooting

### Push не працює
- Перевір, чи репозиторій створено на GitHub
- Перевір, чи правильний username (`kulishdenis-Tech`)
- Використай Personal Access Token замість пароля

### Render деплой не працює
- Перевір логи в Render Dashboard
- Перевір, чи Environment Variables додано правильно
- Перевір, чи Service Role Key (не Anon Key!)

### API повертає помилки
- Перевір, чи Supabase проект активний
- Перевір, чи таблиці `channels` та `rates` існують
- Перевір логи сервера в Render Dashboard
