# FX Hub Backend

FastAPI backend service for currency exchange rate aggregation and API access.

**🌐 Production URL**: https://fxhub-backend.onrender.com

## 🚀 Features

- **Best Rates API**: Get the best buy/sell rates per currency pair
- **Exchanger List**: Retrieve all available exchangers
- **Currency Pairs**: List all unique currency pairs
- **Supabase Integration**: Fully integrated with Supabase database
- **Render Ready**: Configured for easy deployment on Render.com
- **Automated Testing**: Production testing and deployment automation

## 📁 Project Structure

```
fxhub_backend/
├── main.py                  # FastAPI application with endpoints
├── supabase_client.py       # Supabase client configuration
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
├── render.yaml             # Render deployment configuration
├── test_production.py      # Automated production testing
├── auto_fix_and_deploy.py  # Automated testing and deployment
├── AUTOMATION_GUIDE.md     # Automation guide
└── README.md               # This file
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

Repository is already set up: https://github.com/kulishdenis-Tech/fxhub_backend

### Manual Setup (if needed)

1. **Create a new repository on GitHub:**
   - Go to https://github.com/new
   - Repository name: `fxhub_backend`
   - Description: `FastAPI backend for FX Hub with Supabase integration`
   - Choose public or private
   - **Do NOT** initialize with README, .gitignore, or license (we already have these)

2. **Add remote and push:**
   ```bash
   git remote add origin https://github.com/kulishdenis-Tech/fxhub_backend.git
   git branch -M main
   git push -u origin main
   ```

   > **Note**: If Git asks for credentials, use Personal Access Token instead of password.
   > Create token: GitHub Settings → Developer settings → Personal access tokens → Generate new token (classic) → select `repo` scope

## 🔹 Render Deployment

### Quick Deployment (2 minutes)

1. **Go to Render Dashboard:**
   Visit https://dashboard.render.com and sign in

2. **Create New Web Service:**
   - Click **"New +"** → **"Web Service"**
   - Connect your GitHub account if not already connected
   - Select the repository: `fxhub_backend`

3. **Configure Service:**
   - **Name**: `fxhub-backend` (or your preferred name)
   - Render will automatically detect `render.yaml` and use it

4. **Add Environment Variables:**
   In the Environment Variables section, add:
   - **Key**: `SUPABASE_URL`
     **Value**: `https://your-project.supabase.co`
   - **Key**: `SUPABASE_KEY`
     **Value**: `your_service_role_key`
   
   > ⚠️ **IMPORTANT**: Use **Service Role Key**, not Anon Key!
   > 
   > To find Service Role Key:
   > 1. Supabase Dashboard → Settings → API
   > 2. Find "Project API keys" section
   > 3. Copy **"service_role"** key (secret)

5. **Deploy:**
   - Click **"Create Web Service"**
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

### Automatic Deployment

Render automatically deploys on every push to `main` branch.

### Render Configuration File

The `render.yaml` file automates the deployment configuration. Render will use it automatically when you connect the repository.

## 🤖 Automation

The project includes automation scripts for testing and deployment:

### `test_production.py`
Automated testing of production API endpoints.

```bash
python test_production.py
```

### `auto_fix_and_deploy.py`
Full automation cycle: test → commit → push → wait for deployment → re-test.

```bash
python auto_fix_and_deploy.py
```

For detailed automation guide, see `AUTOMATION_GUIDE.md`.

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

**Issue**: "Port already in use"
- **Solution**: Render automatically uses `$PORT` variable. Ensure start command contains `--port $PORT`

### GitHub Issues

**Issue**: Push fails
- **Solution**: Check if repository exists on GitHub, use Personal Access Token instead of password

## 📊 Monitoring

Render Dashboard shows:
- **Logs**: Real-time server logs
- **Metrics**: CPU, Memory, Network usage
- **Events**: Deployment history

## 🔄 Updates

To update the service:
1. Make changes locally
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Update: description of changes"
   git push origin main
   ```
3. Render will automatically detect changes and trigger new deployment

## 📝 License

This project is part of the FX Hub ecosystem.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 🔗 Links

- **GitHub Repository**: https://github.com/kulishdenis-Tech/fxhub_backend
- **Production API**: https://fxhub-backend.onrender.com
- **API Documentation**: https://fxhub-backend.onrender.com/docs
- **Render Dashboard**: https://dashboard.render.com
- **Supabase Dashboard**: https://supabase.com/dashboard