from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from typing import Optional, List
from supabase_client import supabase
from datetime import datetime

app = FastAPI(title="FX Hub Backend", version="1.0.0")


@app.get("/")
async def root():
    return {"message": "FX Hub Backend API", "version": "1.0.0"}


@app.get("/rates/bestrate")
async def get_best_rates(
    currencies: Optional[str] = Query(None, description="Comma-separated currency pairs (e.g., USD/UAH,EUR/UAH)"),
    exchangers: Optional[str] = Query(None, description="Comma-separated exchanger names"),
    city: Optional[str] = Query(None, description="Optional city filter")
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
        
        # If no filters, return top global best rates (all results)
        # If filters applied, return filtered results
        return JSONResponse(status_code=200, content=final_results)
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
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
            content={"exchangers": exchanger_names}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
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
        
        return JSONResponse(
            status_code=200,
            content={
                "currencies_a": sorted(list(currencies_a)),
                "currencies_b": sorted(list(currencies_b)),
                "pairs": sorted(pairs, key=lambda x: (x["base"], x["quote"]))
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
