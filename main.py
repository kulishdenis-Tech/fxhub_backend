from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from supabase_client import supabase
from datetime import datetime, timedelta
import logging
import threading

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import and start keep-alive background thread (before app initialization)
try:
    from keep_alive import keep_alive
    keep_alive_thread = threading.Thread(target=keep_alive, daemon=True)
    keep_alive_thread.start()
    logger.info("🚀 Keep-alive background thread started")
except Exception as e:
    logger.warning(f"⚠️  Could not start keep-alive thread: {e}")

app = FastAPI(title="FX Hub Backend", version="1.0.0")


def find_previous_rate(channel_id: int, currency_a: str, currency_b: str, current_buy: Optional[float], current_sell: Optional[float], channel_name: str, compare_value_type: str = "both"):
    """
    Знаходить попередній запис курсу для конкретного обмінника та валютної пари.
    
    Логіка skip-duplicate:
    1. Запитуємо останні 100 записів для цього обмінника та пари (відсортовані за timestamp DESC)
    2. Пропускаємо дублікати залежно від compare_value_type:
       - "buy": порівнюємо тільки buy значення (для розрахунку buy тренду)
       - "sell": порівнюємо тільки sell значення (для розрахунку sell тренду)
       - "both": порівнюємо обидва buy і sell (застарілий режим)
    3. Зупиняємося при першому записі, де значення відрізняється
    4. Якщо всі попередні значення ідентичні → повертаємо None (trend = "stable")
    
    Args:
        channel_id: ID обмінника (channel_id в таблиці rates)
        currency_a: Перша валюта пари (напр. "USD")
        currency_b: Друга валюта пари (напр. "UAH")
        current_buy: Поточне значення buy
        current_sell: Поточне значення sell
        channel_name: Назва обмінника (для логування)
        compare_value_type: Що порівнювати для skip-duplicate: "buy", "sell", або "both"
    
    Returns:
        dict з полями "buy" та "sell" (попередні значення) або None якщо всі однакові
    """
    try:
        # Запитуємо останні 100 записів для цього обмінника та валютної пари
        query = supabase.table("rates").select(
            "buy, sell, edited"
        ).eq("channel_id", channel_id).eq("currency_a", currency_a).eq("currency_b", currency_b).order("edited", desc=True).limit(100)
        
        response = query.execute()
        
        if not response.data or len(response.data) < 2:
            # Немає попередніх записів або лише один запис
            return None
        
        # Пропускаємо перший запис (це поточний, він має бути першим через DESC order)
        # Ітеруємо починаючи з другого запису
        for record in response.data[1:]:  # Пропускаємо перший (поточний)
            prev_buy = record.get("buy")
            prev_sell = record.get("sell")
            
            # Порівнюємо залежно від типу
            if compare_value_type == "buy":
                # Для BUY: порівнюємо тільки buy значення для skip-duplicate
                buy_different = (current_buy is not None and prev_buy is not None and abs(current_buy - prev_buy) > 0.0001) or \
                               (current_buy is None) != (prev_buy is None)
                if buy_different:
                    return {
                        "buy": prev_buy,
                        "sell": prev_sell
                    }
            elif compare_value_type == "sell":
                # Для SELL: порівнюємо тільки sell значення для skip-duplicate
                sell_different = (current_sell is not None and prev_sell is not None and abs(current_sell - prev_sell) > 0.0001) or \
                                (current_sell is None) != (prev_sell is None)
                if sell_different:
                    return {
                        "buy": prev_buy,
                        "sell": prev_sell
                    }
            else:
                # Старий режим "both": порівнюємо обидва значення
                buy_different = (current_buy is not None and prev_buy is not None and abs(current_buy - prev_buy) > 0.0001) or \
                               (current_buy is None) != (prev_buy is None)
                sell_different = (current_sell is not None and prev_sell is not None and abs(current_sell - prev_sell) > 0.0001) or \
                                (current_sell is None) != (prev_sell is None)
                
                # Якщо хоча б одне значення відрізняється - знайшли baseline для порівняння
                if buy_different or sell_different:
                    return {
                        "buy": prev_buy,
                        "sell": prev_sell
                    }
        
        # Якщо всі попередні значення ідентичні - тренд стабільний
        return None
        
    except Exception as e:
        logger.warning(f"Error finding previous rate for {channel_name} {currency_a}/{currency_b}: {e}")
        return None


def calculate_trend_and_changes(current_value: Optional[float], previous_value: Optional[float]) -> dict:
    """
    Розраховує тренд та зміни для одного значення (buy або sell).
    
    Args:
        current_value: Поточне значення
        previous_value: Попереднє значення
    
    Returns:
        dict з полями:
        - trend: "up", "down", або "stable"
        - change_abs: Абсолютна зміна (округлена до 2 знаків)
        - change_pct: Відсоткова зміна (округлена до 2 знаків)
    """
    # Якщо немає попереднього значення або поточне значення None → стабільний
    if previous_value is None or current_value is None:
        return {
            "trend": "stable",
            "change_abs": 0.0,
            "change_pct": 0.0
        }
    
    # Розраховуємо абсолютну зміну
    change_abs = round(current_value - previous_value, 2)
    
    # Розраховуємо відсоткову зміну
    if previous_value != 0:
        change_pct = round((change_abs / previous_value) * 100, 2)
    else:
        change_pct = 0.0
    
    # Визначаємо тренд
    if change_abs > 0.0001:  # Невеликий поріг для уникнення floating point помилок
        trend = "up"
    elif change_abs < -0.0001:
        trend = "down"
    else:
        trend = "stable"
        change_abs = 0.0  # Округлюємо до 0 якщо зміна мінімальна
        change_pct = 0.0
    
    return {
        "trend": trend,
        "change_abs": change_abs,
        "change_pct": change_pct
    }

app = FastAPI(title="FX Hub Backend", version="1.0.0")

# CORS middleware для Flutter мобільного додатку
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: обмежити на fxhub.app для production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {"message": "FX Hub Backend API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring and Flutter app status.
    Returns API status and database connection status.
    """
    try:
        # Перевірка підключення до Supabase
        test_query = supabase.table("channels").select("id").limit(1).execute()
        db_status = "connected" if test_query.data is not None else "error"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "error"
    
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "database": db_status,
        "version": "1.0.0"
    }


@app.get("/rates/bestrate")
async def get_best_rates(
    currencies: Optional[str] = Query(None, description="Comma-separated currency pairs (e.g., USD/UAH,EUR/UAH)"),
    exchangers: Optional[str] = Query(None, description="Comma-separated exchanger names"),
    city: Optional[str] = Query(None, description="Optional city filter"),
    limit: Optional[int] = Query(None, ge=1, le=100, description="Limit number of results (for pagination)"),
    offset: Optional[int] = Query(0, ge=0, description="Offset for pagination")
):
    """
    Returns best buy/sell rates per currency pair.
    
    Logic:
    - Fetches latest record per exchanger_id, currency_a, currency_b (ordered by timestamp DESC)
    - Computes buy_best = max(buy), sell_best = min(sell)
    """
    try:
        # Parse filters
        currency_pairs = []
        if currencies:
            currency_pairs = [pair.strip() for pair in currencies.split(",")]
        
        exchanger_names = []
        if exchangers:
            exchanger_names = [ex.strip() for ex in exchangers.split(",")]
        
        # Get channel mapping (id -> name)
        channels_resp = supabase.table("channels").select("id, name").execute()
        channel_map = {ch["id"]: ch["name"] for ch in channels_resp.data}
        
        # Build query to get rates
        query = supabase.table("rates").select(
            "currency_a, currency_b, buy, sell, edited, channel_id"
        )
        
        # Apply exchanger filter if provided
        if exchanger_names:
            # Get channel IDs for these exchangers
            filtered_channel_ids = [
                ch_id for ch_id, name in channel_map.items() if name in exchanger_names
            ]
            if filtered_channel_ids:
                query = query.in_("channel_id", filtered_channel_ids)
            else:
                # No matching exchangers found
                return JSONResponse(status_code=200, content=[])
        
        # Execute query - order by edited timestamp DESC to get latest first
        response = query.order("edited", desc=True).execute()
        
        if not response.data:
            return JSONResponse(
                status_code=200,
                content=[]
            )
        
        # Group by currency pair and exchanger, keeping only the latest record per combination
        latest_rates = {}
        
        for rate in response.data:
            channel_id = rate.get("channel_id")
            channel_name = channel_map.get(channel_id, "Unknown")
            
            # Skip if exchanger filter doesn't match
            if exchanger_names and channel_name not in exchanger_names:
                continue
            
            pair_key = f"{rate['currency_a']}/{rate['currency_b']}"
            
            # Apply currency filter if provided
            if currency_pairs:
                pair_formatted = f"{rate['currency_a']}/{rate['currency_b']}"
                if pair_formatted not in currency_pairs:
                    continue
            
            # Create unique key: pair + channel
            unique_key = f"{pair_key}_{channel_id}"
            
            # Only keep the latest record per exchanger and currency pair
            if unique_key not in latest_rates:
                latest_rates[unique_key] = {
                    **rate,
                    "channel_name": channel_name
                }
            else:
                # Compare timestamps to keep the latest
                current_time = latest_rates[unique_key].get("edited")
                new_time = rate.get("edited")
                if new_time and (not current_time or new_time > current_time):
                    latest_rates[unique_key] = {
                        **rate,
                        "channel_name": channel_name
                    }
        
        # Group by currency pair and calculate best rates
        results = {}
        # Store full rate records for trend calculation
        rate_records_map = {}  # Maps (pair_key, exchanger) -> full rate record
        
        for unique_key, rate in latest_rates.items():
            pair_key = f"{rate['currency_a']}/{rate['currency_b']}"
            channel_name = rate.get("channel_name", "Unknown")
            
            # Store full rate record for later trend calculation
            rate_records_map[(pair_key, channel_name)] = rate
            
            if pair_key not in results:
                results[pair_key] = {
                    "currency": pair_key,
                    "buy_records": [],
                    "sell_records": []
                }
            
            if rate.get("buy") is not None:
                results[pair_key]["buy_records"].append({
                    "value": rate["buy"],
                    "exchanger": channel_name,
                    "timestamp": rate.get("edited")
                })
            
            if rate.get("sell") is not None:
                results[pair_key]["sell_records"].append({
                    "value": rate["sell"],
                    "exchanger": channel_name,
                    "timestamp": rate.get("edited")
                })
        
        # Calculate best rates and trend analytics
        final_results = []
        for pair_key, data in results.items():
            buy_records = data["buy_records"]
            sell_records = data["sell_records"]
            
            if not buy_records and not sell_records:
                continue
            
            # Parse currency pair
            currency_a, currency_b = pair_key.split("/")
            
            result = {
                "currency": pair_key
            }
            
            # Process buy rates
            if buy_records:
                best_buy = max(buy_records, key=lambda x: x["value"])
                result["buy_best"] = best_buy["value"]
                result["buy_exchanger"] = best_buy["exchanger"]
                result["buy_timestamp"] = best_buy["timestamp"]
                
                # Find channel_id for best buy exchanger
                buy_channel_id = None
                for ch_id, name in channel_map.items():
                    if name == best_buy["exchanger"]:
                        buy_channel_id = ch_id
                        break
                
                # Get full rate record for best buy (to get both buy and sell for duplicate skipping)
                current_buy_rate = rate_records_map.get((pair_key, best_buy["exchanger"]))
                current_buy_value = best_buy["value"]
                current_sell_value = current_buy_rate.get("sell") if current_buy_rate else None
                
                # Find previous rate for buy (skip duplicates)
                # Для BUY порівнюємо тільки buy значення при skip-duplicate
                if buy_channel_id:
                    prev_buy_rate = find_previous_rate(
                        buy_channel_id, currency_a, currency_b,
                        current_buy_value, current_sell_value, best_buy["exchanger"],
                        compare_value_type="buy"
                    )
                    
                    # Calculate trend and changes for buy
                    if prev_buy_rate and prev_buy_rate.get("buy") is not None:
                        buy_analytics = calculate_trend_and_changes(
                            best_buy["value"], prev_buy_rate["buy"]
                        )
                    else:
                        # All previous rates identical or no previous record
                        buy_analytics = {
                            "trend": "stable",
                            "change_abs": 0.0,
                            "change_pct": 0.0
                        }
                    
                    result["buy_trend"] = buy_analytics["trend"]
                    result["buy_change_abs"] = buy_analytics["change_abs"]
                    result["buy_change_pct"] = buy_analytics["change_pct"]
                else:
                    # Channel not found - set defaults
                    result["buy_trend"] = "stable"
                    result["buy_change_abs"] = 0.0
                    result["buy_change_pct"] = 0.0
            
            # Process sell rates
            if sell_records:
                best_sell = min(sell_records, key=lambda x: x["value"])
                result["sell_best"] = best_sell["value"]
                result["sell_exchanger"] = best_sell["exchanger"]
                result["sell_timestamp"] = best_sell["timestamp"]
                
                # Find channel_id for best sell exchanger
                sell_channel_id = None
                for ch_id, name in channel_map.items():
                    if name == best_sell["exchanger"]:
                        sell_channel_id = ch_id
                        break
                
                # Get full rate record for best sell (to get both buy and sell for duplicate skipping)
                current_sell_rate = rate_records_map.get((pair_key, best_sell["exchanger"]))
                current_sell_value = best_sell["value"]
                current_buy_value_for_sell = current_sell_rate.get("buy") if current_sell_rate else None
                
                # Find previous rate for sell (skip duplicates)
                # Для SELL порівнюємо тільки sell значення при skip-duplicate
                if sell_channel_id:
                    prev_sell_rate = find_previous_rate(
                        sell_channel_id, currency_a, currency_b,
                        current_buy_value_for_sell, current_sell_value, best_sell["exchanger"],
                        compare_value_type="sell"
                    )
                    
                    # Calculate trend and changes for sell
                    if prev_sell_rate and prev_sell_rate.get("sell") is not None:
                        sell_analytics = calculate_trend_and_changes(
                            best_sell["value"], prev_sell_rate["sell"]
                        )
                    else:
                        # All previous rates identical or no previous record
                        sell_analytics = {
                            "trend": "stable",
                            "change_abs": 0.0,
                            "change_pct": 0.0
                        }
                    
                    result["sell_trend"] = sell_analytics["trend"]
                    result["sell_change_abs"] = sell_analytics["change_abs"]
                    result["sell_change_pct"] = sell_analytics["change_pct"]
                else:
                    # Channel not found - set defaults
                    result["sell_trend"] = "stable"
                    result["sell_change_abs"] = 0.0
                    result["sell_change_pct"] = 0.0
            
            final_results.append(result)
        
        # Apply pagination if requested
        total_count = len(final_results)
        if limit:
            start = offset or 0
            end = start + limit
            paginated_results = final_results[start:end]
        else:
            paginated_results = final_results
            start = 0
            end = total_count
        
        # Return with metadata for Flutter
        return JSONResponse(status_code=200, content={
            "success": True,
            "data": paginated_results,
            "meta": {
                "total": total_count,
                "limit": limit,
                "offset": start,
                "returned": len(paginated_results)
            }
        })
        
    except Exception as e:
        logger.error(f"Error in get_best_rates: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Internal server error",
                "message": str(e)
            }
        )


@app.get("/exchangers/list")
async def get_exchangers_list():
    """
    Returns a list of all unique exchanger names from the rates table.
    """
    try:
        # Get all unique channel names that have rates
        response = supabase.table("channels").select("name").execute()

        exchanger_names = sorted(set([ch["name"] for ch in response.data]))     

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": {"exchangers": exchanger_names},
                "meta": {"count": len(exchanger_names)}
            }
        )
    except Exception as e:
        logger.error(f"Error in get_exchangers_list: {e}", exc_info=True)       
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Internal server error",
                "message": str(e)
            }
        )


@app.get("/exchangers/pairs")
async def get_exchangers_pairs():
    """
    Returns a mapping of all exchangers and the currency pairs they support.
    
    This endpoint is useful for dependent filtering logic in Flutter History Screen.
    Each exchanger entry contains the list of currency pairs available for that exchanger.
    """
    try:
        # Get channel mapping (id -> name)
        channels_resp = supabase.table("channels").select("id, name").execute() 
        channel_map = {ch["id"]: ch["name"] for ch in channels_resp.data}
        
        # Initialize mapping for ALL exchangers (even if they have no rates)
        exchanger_pairs_map = {name: set() for name in channel_map.values()}
        all_pairs_set = set()
        
        # For each exchanger, get the latest rates (last record per currency pair)
        # Strategy: Get all rates, group by (channel_id, currency_a, currency_b), keep only latest per group
        
        # Get all rates ordered by edited DESC (latest first)
        response = supabase.table("rates").select(
            "channel_id, currency_a, currency_b, edited"
        ).order("edited", desc=True).execute()
        
        # Track which (channel_id, currency_a, currency_b) combinations we've already seen
        # This way we keep only the LATEST record for each combination
        seen_combinations = set()
        
        # Build mapping: add currency pairs from LATEST records only
        for rate in response.data:
            channel_id = rate.get("channel_id")
            currency_a = rate.get("currency_a")
            currency_b = rate.get("currency_b")
            
            # Skip null or empty values
            if not channel_id or not currency_a or not currency_b:
                continue
            
            exchanger_name = channel_map.get(channel_id)
            if not exchanger_name:
                continue
            
            # Create unique key: (channel_id, currency_a, currency_b)
            combination_key = (channel_id, currency_a, currency_b)
            
            # Skip if we've already processed this combination (we have the latest record)
            if combination_key in seen_combinations:
                continue
            
            # Mark this combination as seen
            seen_combinations.add(combination_key)
            
            # Create currency pair string
            pair = f"{currency_a}/{currency_b}"
            
            # Add to exchanger's set of pairs
            exchanger_pairs_map[exchanger_name].add(pair)
            all_pairs_set.add(pair)
        
        # Convert to list format and sort
        result_data = []
        for exchanger_name in sorted(exchanger_pairs_map.keys()):
            pairs_list = sorted(list(exchanger_pairs_map[exchanger_name]))
            result_data.append({
                "exchanger": exchanger_name,
                "pairs": pairs_list
            })
        
        # Return with metadata
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": result_data,
                "meta": {
                    "total_exchangers": len(result_data),
                    "total_pairs": len(all_pairs_set),
                    "generated_at": datetime.utcnow().isoformat() + "Z"
                }
            }
        )
    except Exception as e:
        logger.error(f"Error in get_exchangers_pairs: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Database query failed",
                "details": str(e)
            }
        )


@app.get("/rates/history")
async def get_rates_history(
    currency_pair: str = Query(..., description="Currency pair (e.g., USD/UAH)"),
    exchanger: Optional[str] = Query(None, description="Optional exchanger name filter"),
    days: int = Query(7, ge=1, le=90, description="Number of days of history (1-90)"),
    interval: Optional[str] = Query("hour", regex="^(hour|day)$", description="Data aggregation interval")
):
    """
    Returns historical rates data for charts/graphs.
    
    Returns data points with buy/sell rates over time for a specific currency pair.
    """
    try:
        # Parse currency pair
        if "/" not in currency_pair:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": "Invalid currency pair format",
                    "message": "Use format: USD/UAH"
                }
            )
        
        currency_a, currency_b = currency_pair.split("/")
        currency_a = currency_a.strip().upper()
        currency_b = currency_b.strip().upper()
        
        # Get channel mapping
        channels_resp = supabase.table("channels").select("id, name").execute()
        channel_map = {ch["id"]: ch["name"] for ch in channels_resp.data}
        
        # Build query
        query = supabase.table("rates").select(
            "currency_a, currency_b, buy, sell, edited, channel_id"
        ).eq("currency_a", currency_a).eq("currency_b", currency_b)
        
        # Apply exchanger filter if provided
        if exchanger:
            filtered_channel_ids = [
                ch_id for ch_id, name in channel_map.items() if name == exchanger.strip()
            ]
            if filtered_channel_ids:
                query = query.in_("channel_id", filtered_channel_ids)
            else:
                return JSONResponse(status_code=200, content={
                    "success": True,
                    "data": {
                        "currency": currency_pair,
                        "period_days": days,
                        "interval": interval,
                        "data_points": []
                    },
                    "meta": {"count": 0}
                })
        
        # Calculate date range
        from_date = datetime.utcnow()
        # Supabase PostgREST uses ISO format for date filtering
        # We'll filter in Python for simplicity, or use Supabase's date functions
        
        # Execute query - get all records for the period
        response = query.order("edited", desc=True).execute()
        
        if not response.data:
            return JSONResponse(status_code=200, content={
                "success": True,
                "data": {
                    "currency": currency_pair,
                    "period_days": days,
                    "interval": interval,
                    "data_points": []
                },
                "meta": {"count": 0}
            })
        
        # Filter by date range and group by interval
        cutoff_date = datetime.utcnow()
        if days > 0:
            from datetime import timedelta
            cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        data_points = []
        seen_times = set()  # Для дедуплікації
        
        for rate in response.data:
            edited_str = rate.get("edited")
            if not edited_str:
                continue
            
            # Parse timestamp
            try:
                if isinstance(edited_str, str):
                    if "T" in edited_str:
                        rate_time = datetime.fromisoformat(edited_str.replace("Z", "+00:00"))
                    else:
                        rate_time = datetime.strptime(edited_str, "%Y-%m-%d %H:%M:%S")
                else:
                    rate_time = edited_str
                
                # Convert to UTC if timezone-aware
                if rate_time.tzinfo:
                    rate_time = rate_time.replace(tzinfo=None)
                
                # Filter by date range
                if rate_time < cutoff_date:
                    continue
                
                # Group by interval
                if interval == "hour":
                    time_key = rate_time.replace(minute=0, second=0, microsecond=0)
                else:  # day
                    time_key = rate_time.replace(hour=0, minute=0, second=0, microsecond=0)
                
                # Deduplicate and aggregate
                time_iso = time_key.isoformat() + "Z"
                
                if time_iso not in seen_times:
                    channel_id = rate.get("channel_id")
                    channel_name = channel_map.get(channel_id, "Unknown")
                    
                    data_points.append({
                        "timestamp": time_iso,
                        "buy": rate.get("buy"),
                        "sell": rate.get("sell"),
                        "exchanger": channel_name
                    })
                    seen_times.add(time_iso)
                else:
                    # If multiple records for same interval, keep best rates
                    for dp in data_points:
                        if dp["timestamp"] == time_iso:
                            if rate.get("buy") and (dp["buy"] is None or rate.get("buy") > dp["buy"]):
                                dp["buy"] = rate.get("buy")
                                dp["exchanger"] = channel_map.get(rate.get("channel_id"), "Unknown")
                            if rate.get("sell") and (dp["sell"] is None or rate.get("sell") < dp["sell"]):
                                dp["sell"] = rate.get("sell")
                            break
            except Exception as e:
                logger.warning(f"Error parsing timestamp {edited_str}: {e}")
                continue
        
        # Sort by timestamp
        data_points.sort(key=lambda x: x["timestamp"])
        
        return JSONResponse(status_code=200, content={
            "success": True,
            "data": {
                "currency": currency_pair,
                "period_days": days,
                "interval": interval,
                "data_points": data_points
            },
            "meta": {
                "count": len(data_points),
                "from_date": cutoff_date.isoformat() + "Z",
                "to_date": datetime.utcnow().isoformat() + "Z"
            }
        })
        
    except Exception as e:
        logger.error(f"Error in get_rates_history: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Internal server error",
                "message": str(e)
            }
        )


@app.get("/currencies/list")
async def get_currencies_list():
    """
    Returns all unique currency pairs.
    """
    try:
        # Get all unique currency combinations
        response = supabase.table("rates").select("currency_a, currency_b").execute()
        
        currencies_a = set()
        currencies_b = set()
        pairs = []
        seen_pairs = set()
        
        for rate in response.data:
            if rate.get("currency_a"):
                currencies_a.add(rate["currency_a"])
            if rate.get("currency_b"):
                currencies_b.add(rate["currency_b"])
            
            # Create unique pair
            pair_key = (rate.get("currency_a"), rate.get("currency_b"))
            if pair_key not in seen_pairs and pair_key[0] and pair_key[1]:
                pairs.append({
                    "base": pair_key[0],
                    "quote": pair_key[1]
                })
                seen_pairs.add(pair_key)
        
        sorted_pairs = sorted(pairs, key=lambda x: (x["base"], x["quote"]))
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": {
                    "currencies_a": sorted(list(currencies_a)),
                    "currencies_b": sorted(list(currencies_b)),
                    "pairs": sorted_pairs
                },
                "meta": {
                    "currencies_a_count": len(currencies_a),
                    "currencies_b_count": len(currencies_b),
                    "pairs_count": len(sorted_pairs)
                }
            }
        )
    except Exception as e:
        logger.error(f"Error in get_currencies_list: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Internal server error",
                "message": str(e)
            }
        )
