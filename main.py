from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from supabase_client import supabase
from datetime import datetime, timedelta
import logging

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        
        for unique_key, rate in latest_rates.items():
            pair_key = f"{rate['currency_a']}/{rate['currency_b']}"
            channel_name = rate.get("channel_name", "Unknown")
            
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
        
        # Calculate best rates
        final_results = []
        for pair_key, data in results.items():
            buy_records = data["buy_records"]
            sell_records = data["sell_records"]
            
            if not buy_records and not sell_records:
                continue
            
            result = {
                "currency": pair_key
            }
            
            if buy_records:
                best_buy = max(buy_records, key=lambda x: x["value"])
                result["buy_best"] = best_buy["value"]
                result["buy_exchanger"] = best_buy["exchanger"]
                result["buy_timestamp"] = best_buy["timestamp"]
            
            if sell_records:
                best_sell = min(sell_records, key=lambda x: x["value"])
                result["sell_best"] = best_sell["value"]
                result["sell_exchanger"] = best_sell["exchanger"]
                result["sell_timestamp"] = best_sell["timestamp"]
            
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


@app.get("/rates/history")
async def get_rates_history(
    currency_pair: str = Query(..., description="Currency pair (e.g., USD/UAH)"),
    exchanger: Optional[str] = Query(None, description="Optional exchanger name filter"),
    days: int = Query(7, ge=1, le=30, description="Number of days of history (1-30)"),
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
