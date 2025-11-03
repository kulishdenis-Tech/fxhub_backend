# 🚀 Інструкції для деплою на Render

## ✅ Крок 1: Створити репозиторій на GitHub

### Якщо репозиторій ще не створений:

1. Відкрий https://github.com/new
2. Заповни форму:
   - **Repository name**: `fxhub_backend`
   - **Description**: `FastAPI backend for FX Hub with Supabase integration`
   - **Visibility**: Public або Private (на ваш вибір)
   - **НЕ** додавай README, .gitignore або license (вони вже є в проєкті)
3. Натисни **"Create repository"**

### Після створення репозиторію виконай:

```bash
cd "C:\Users\kulis\Documents\Google drive\Exchange\FastAPI\fxhub_backend"
git remote add origin https://github.com/kulishdenis-Tech/fxhub_backend.git
git branch -M main
git push -u origin main
```

> **Примітка**: Якщо Git запитує credentials, використай:
> - Username: `kulishdenis-Tech`
> - Password: Personal Access Token (створений в GitHub Settings → Developer settings → Personal access tokens)

---

## ✅ Крок 2: Деплой на Render

### 2.1 Створити Web Service на Render

1. Відкрий https://dashboard.render.com
2. Натисни **"New +"** → **"Web Service"**
3. Підключи GitHub:
   - Натисни **"Connect account"** (якщо ще не підключений)
   - Дозволь Render доступ до твоїх репозиторіїв
   - Вибери репозиторій: **`kulishdenis-Tech/fxhub_backend`**

### 2.2 Налаштування сервісу

Render автоматично використає `render.yaml`, але перевір наступне:

- **Name**: `fxhub-backend` (або інша назва)
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### 2.3 Додати Environment Variables

В розділі **"Environment Variables"** додай:

1. **SUPABASE_URL**
   - **Key**: `SUPABASE_URL`
   - **Value**: `https://gtuibuzglapqlzsqruol.supabase.co`
   - **Sync**: ❌ (не синхронізувати)

2. **SUPABASE_KEY**
   - **Key**: `SUPABASE_KEY`
   - **Value**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` (повний ключ з .env)
   - **Sync**: ❌ (не синхронізувати)

> ⚠️ **ВАЖЛИВО**: Використай **Service Role Key**, а не Anon Key!
> 
> Щоб знайти Service Role Key:
> 1. Відкрий Supabase Dashboard → Settings → API
> 2. Знайди розділ "Project API keys"
> 3. Скопіюй **"service_role"** key (secret)

### 2.4 Запустити деплой

1. Натисни **"Create Web Service"**
2. Render почне:
   - Клонувати репозиторій
   - Встановлювати залежності
   - Запускати сервер
3. Чекай 1-2 хвилини на завершення деплою

### 2.5 Перевірити роботу

Після успішного деплою Render надасть URL, наприклад:
```
https://fxhub-backend.onrender.com
```

Тестуй ендпоінти:
- **Root**: https://fxhub-backend.onrender.com/
- **Best Rates**: https://fxhub-backend.onrender.com/rates/bestrate
- **Exchangers**: https://fxhub-backend.onrender.com/exchangers/list
- **Currencies**: https://fxhub-backend.onrender.com/currencies/list

### 2.6 Автоматичний деплой

Render автоматично деплоїть при кожному push в `main` гілку.

---

## 🔧 Troubleshooting

### Помилка: "Module not found"
- Перевір, чи `requirements.txt` містить всі залежності
- Перевір логи build процесу в Render Dashboard

### Помилка: "Supabase connection failed"
- Перевір, чи Environment Variables додано правильно
- Перевір, чи використано Service Role Key, а не Anon Key
- Перевір, чи Supabase проект активний

### Помилка: "Port already in use"
- Render автоматично використовує змінну `$PORT`
- Перевір, чи start command містить `--port $PORT`

### Service не запускається
- Перевір логи в Render Dashboard → Logs
- Перевір, чи всі Environment Variables встановлені
- Перевір, чи Python версія підтримується (рекомендовано 3.8+)

---

## 📊 Моніторинг

Render Dashboard показує:
- **Logs**: Реальний час логів сервера
- **Metrics**: CPU, Memory, Network
- **Events**: Історія деплоїв

---

## 🔄 Оновлення

Для оновлення сервісу:
1. Зроби зміни локально
2. Commit та Push в GitHub:
   ```bash
   git add .
   git commit -m "Update: description of changes"
   git push origin main
   ```
3. Render автоматично виявить зміни та запустить новий деплой

---

## ✅ Готово!

Тепер твій FastAPI backend доступний публічно на Render! 🎉
