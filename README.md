# FX Hub Backend

FastAPI backend service for currency exchange rate aggregation and API access.

## 🚀 Features

- **Best Rates API**: Get the best buy/sell rates per currency pair
- **Exchanger List**: Retrieve all available exchangers
- **Currency Pairs**: List all available currency pairs
- **Supabase Integration**: Fully integrated with Supabase database
- **Render Ready**: Configured for easy deployment on Render.com

## 📁 Project Structure

```
fxhub_backend/
├── main.py              # FastAPI application with endpoints
├── supabase_client.py   # Supabase client configuration
├── requirements.txt     # Python dependencies
├── .env.example        # Environment variables template
├── .gitignore          # Git ignore rules
├── render.yaml         # Render deployment configuration
└── README.md           # This file
```

## 🔹 Local Development

### Prerequisites

- Python 3.8 or higher
- Supabase account and project
- pip (Python package manager)

### Setup Steps

1. **Clone and navigate to the project:**
   ```bash
   cd Exchange/FastAPI/fxhub_backend
   ```

2. **Copy environment variables:**
   ```bash
   cp .env.example .env
   ```

3. **Edit `.env` file:**
   Open `.env` and insert your Supabase credentials:
   ```
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your_service_role_key
   ```
   
   > **Note**: Get your Supabase URL and Service Role Key from your Supabase project dashboard (Settings → API).

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the development server:**
   ```bash
   uvicorn main:app --reload --port 8000
   ```

6. **Test the API:**
   
   Open your browser and visit:
   - **Root**: http://127.0.0.1:8000
   - **Best Rates**: http://127.0.0.1:8000/rates/bestrate
   - **Exchangers List**: http://127.0.0.1:8000/exchangers/list
   - **Currencies List**: http://127.0.0.1:8000/currencies/list
   
   Or use curl:
   ```bash
   curl http://127.0.0.1:8000/rates/bestrate
   curl http://127.0.0.1:8000/exchangers/list
   curl http://127.0.0.1:8000/currencies/list
   ```

7. **API Documentation:**
   
   FastAPI provides automatic interactive API documentation:
   - Swagger UI: http://127.0.0.1:8000/docs
   - ReDoc: http://127.0.0.1:8000/redoc

## 📡 API Endpoints

### `/rates/bestrate`

Returns the best buy/sell rates per currency pair.

**Query Parameters:**
- `currencies` (optional): Comma-separated currency pairs (e.g., `USD/UAH,EUR/UAH`)
- `exchangers` (optional): Comma-separated exchanger names (e.g., `Garant,Mirvalut`)
- `city` (optional): City filter (for future use)

**Example Request:**
```bash
GET http://127.0.0.1:8000/rates/bestrate?currencies=USD/UAH,EUR/UAH&exchangers=Garant,Mirvalut
```

**Example Response:**
```json
[
  {
    "currency": "USD/UAH",
    "buy_best": 41.55,
    "buy_exchanger": "Garant Money",
    "buy_timestamp": "2025-11-03T15:10:00Z",
    "sell_best": 41.45,
    "sell_exchanger": "Mirvalut",
    "sell_timestamp": "2025-11-03T14:55:00Z"
  }
]
```

### `/exchangers/list`

Returns a list of all unique exchanger names from the rates table.

**Example Request:**
```bash
GET http://127.0.0.1:8000/exchangers/list
```

**Example Response:**
```json
{
  "exchangers": ["Garant Money", "Mirvalut", "KytGroup", "Obmen24", "FinanceUA"]
}
```

### `/currencies/list`

Returns all unique currency pairs.

**Example Request:**
```bash
GET http://127.0.0.1:8000/currencies/list
```

**Example Response:**
```json
{
  "currencies_a": ["USD", "EUR", "PLN", "GBP"],
  "currencies_b": ["UAH", "USD"],
  "pairs": [
    {"base": "EUR", "quote": "UAH"},
    {"base": "USD", "quote": "EUR"},
    {"base": "USD", "quote": "UAH"}
  ]
}
```

## 🔹 GitHub Integration

### Quick Setup (Автоматично)

Якщо Git репозиторій вже ініціалізовано, просто запусти:

```bash
python setup_github.py
```

Скрипт перевірить налаштування та допоможе з push на GitHub.

### Manual Setup

1. **Create a new repository on GitHub:**
   - Go to https://github.com/new
   - Repository name: `fxhub_backend`
   - Description: `FastAPI backend for FX Hub with Supabase integration`
   - Choose public or private
   - **Do NOT** initialize with README, .gitignore, or license (we already have these)
   - Click **"Create repository"**

2. **Add remote and push:**
   ```bash
   git remote add origin https://github.com/kulishdenis-Tech/fxhub_backend.git
   git branch -M main
   git push -u origin main
   ```

   > **Note**: Якщо Git запитує credentials, використай Personal Access Token замість пароля.
   > Створити токен: GitHub Settings → Developer settings → Personal access tokens → Generate new token (classic) → вибери scope `repo`

### Verify `.gitignore`

Before pushing, ensure `.env` is listed in `.gitignore`:
```bash
cat .gitignore
```

The `.gitignore` file should contain:
```
.env
__pycache__/
*.pyc
...
```

## 🔹 Render Deployment

### Prerequisites

- GitHub account
- Render.com account (free tier available)
- Repository pushed to GitHub

### Deployment Steps

1. **Go to Render Dashboard:**
   Visit https://render.com and sign in

2. **Create New Web Service:**
   - Click **"New +"** → **"Web Service"**
   - Connect your GitHub account if not already connected
   - Select the repository: `fxhub_backend`

3. **Configure Service:**
   - **Name**: `fxhub-backend` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   
   > **Note**: Render will auto-detect `render.yaml` if present, which simplifies this step.

4. **Add Environment Variables:**
   In the Environment Variables section, add:
   - **Key**: `SUPABASE_URL`
     **Value**: `https://your-project.supabase.co`
   - **Key**: `SUPABASE_KEY`
     **Value**: `your_service_role_key`
   
   > **Note**: Make sure to use your actual Supabase credentials (not the example values).

5. **Deploy:**
   - Click **"Create Web Service"**
   - Render will automatically:
     - Clone your repository
     - Install dependencies from `requirements.txt`
     - Start the application using the start command
   
   - Wait for deployment to complete (usually 1-2 minutes)

6. **Access Your API:**
   After successful deployment, Render will provide a URL like:
   ```
   https://fxhub-backend.onrender.com
   ```

7. **Test Endpoints:**
   ```bash
   # Root
   curl https://fxhub-backend.onrender.com/
   
   # Best rates
   curl https://fxhub-backend.onrender.com/rates/bestrate
   
   # Exchangers list
   curl https://fxhub-backend.onrender.com/exchangers/list
   
   # Currencies list
   curl https://fxhub-backend.onrender.com/currencies/list
   ```

### Render Configuration File

The `render.yaml` file automates the deployment configuration. Render will use it automatically when you connect the repository.

## 🔧 Troubleshooting

### Local Development Issues

**Issue**: `ModuleNotFoundError: No module named 'supabase'`
- **Solution**: Run `pip install -r requirements.txt`

**Issue**: `ValueError: ⚠️ Не знайдено ключі Supabase у .env`
- **Solution**: Ensure `.env` file exists and contains valid `SUPABASE_URL` and `SUPABASE_KEY`

**Issue**: Connection errors to Supabase
- **Solution**: Verify your Supabase URL and Service Role Key are correct

### Render Deployment Issues

**Issue**: Build fails with dependency errors
- **Solution**: Ensure `requirements.txt` is in the repository root and contains all dependencies

**Issue**: Service crashes on startup
- **Solution**: Check Render logs for error messages, verify environment variables are set correctly

**Issue**: API returns 500 errors
- **Solution**: Verify Supabase credentials in Render environment variables, check database connection

## 📝 License

This project is part of the FX Hub ecosystem.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
