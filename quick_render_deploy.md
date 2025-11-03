# ⚡ Швидкий деплой на Render (2 хвилини)

## ✅ Що вже готово:
- ✅ Репозиторій на GitHub: https://github.com/kulishdenis-Tech/fxhub_backend
- ✅ `render.yaml` налаштований
- ✅ Environment variables готові (SUPABASE_URL, SUPABASE_KEY в .env)

## 🚀 Кроки для деплою:

1. **Відкрий Render Dashboard:**
   https://dashboard.render.com

2. **Натисни "New +" → "Web Service"**

3. **Підключи GitHub:**
   - Якщо ще не підключений - натисни "Connect GitHub"
   - Дозволь доступ до репозиторіїв
   - Вибери репозиторій: **fxhub_backend**

4. **Render автоматично:**
   - ✅ Використає `render.yaml` (все налаштовано!)
   - ✅ Визначить Python runtime
   - ✅ Встановить buildCommand та startCommand

5. **Додай Environment Variables:**
   - Перейди в секцію "Environment"
   - Додай:
     - **SUPABASE_URL** = `https://gtuibuzglapqlzsqruol.supabase.co`
     - **SUPABASE_KEY** = (скопіюй з .env - Service Role Key)

6. **Натисни "Create Web Service"**

7. **Чекай 1-2 хвилини** - Render задеплоїть сервіс!

8. **Отримаєш URL:** `https://fxhub-backend.onrender.com`

---

## ✨ Переваги цього підходу:
- ✅ Швидко (2 хвилини)
- ✅ `render.yaml` автоматично використається
- ✅ Не потрібно налаштовувати вручну
- ✅ Всі налаштування вже в коді

---

## 🔗 Корисні посилання:
- **GitHub репо:** https://github.com/kulishdenis-Tech/fxhub_backend
- **Render Dashboard:** https://dashboard.render.com
- **Supabase Dashboard:** https://supabase.com/dashboard
