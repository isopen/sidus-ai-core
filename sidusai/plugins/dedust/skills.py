import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any

class DedustSkills:
    def __init__(self, components):
        self.components = components
        self._prices_cache = None
        self._prices_cache_time = None
        self._pools_cache = None
        self._pools_cache_time = None
        self._address_to_symbol = {}

    def _parse_amount(self, amount) -> float:
        try:
            if amount is None:
                return 0.0
            if isinstance(amount, (int, float)):
                return float(amount)
            if isinstance(amount, str):
                amount_str = amount.strip(' "\'\t\n\r')
                if not amount_str or amount_str.lower() in ['null', 'none', 'nan']:
                    return 0.0
                amount_str = amount_str.replace(',', '')
                return float(amount_str)
            return 0.0
        except (ValueError, TypeError):
            return 0.0

    def _safe_get(self, data, key, default=None):
        try:
            if isinstance(data, dict):
                if key in data:
                    value = data[key]
                    if isinstance(value, (dict, list)):
                        return value
                    return self._parse_amount(value) if isinstance(value, (str, int, float)) else value

                if '.' in str(key):
                    parts = str(key).split('.')
                    current = data
                    for part in parts:
                        if isinstance(current, dict) and part in current:
                            current = current[part]
                        else:
                            return default
                    return current
                return default

            elif isinstance(data, list) and isinstance(key, int) and 0 <= key < len(data):
                return data[key]

            return default
        except:
            return default

    def _get_cached_prices(self, force_refresh: bool = False) -> Dict[str, float]:
        current_time = datetime.now()

        if (force_refresh or 
            self._prices_cache is None or 
            self._prices_cache_time is None or 
            (current_time - self._prices_cache_time).total_seconds() > 60):

            try:
                print("Updating price cache...")
                prices_result = self.components.get_prices()

                prices_list = []
                if isinstance(prices_result, dict):
                    prices_list = self._safe_get(prices_result, "prices", [])
                elif isinstance(prices_result, list):
                    prices_list = prices_result

                prices_dict = {}
                for item in prices_list:
                    if isinstance(item, dict):
                        symbol = item.get("symbol")
                        price = item.get("price")
                        if symbol and price is not None:
                            symbol_str = str(symbol).strip()
                            price_val = self._parse_amount(price)
                            if price_val > 0:
                                prices_dict[symbol_str] = price_val

                self._prices_cache = prices_dict
                self._prices_cache_time = current_time
                print(f"Price cache updated: {len(prices_dict)} assets")

            except Exception as e:
                print(f"Price cache update error: {e}")
                if self._prices_cache is None:
                    self._prices_cache = {}

        return self._prices_cache

    def _get_cached_pools(self, force_refresh: bool = False) -> List[Dict]:
        current_time = datetime.now()

        if (force_refresh or 
            self._pools_cache is None or 
            self._pools_cache_time is None or 
            (current_time - self._pools_cache_time).total_seconds() > 120):

            try:
                print("Updating pools cache...")
                pools_result = self.components.get_pools()

                pools_list = []
                if isinstance(pools_result, dict):
                    pools_list = self._safe_get(pools_result, "pool_list", [])
                elif isinstance(pools_result, list):
                    pools_list = pools_result

                self._pools_cache = pools_list
                self._pools_cache_time = current_time
                print(f"Pools cache updated: {len(pools_list)} pools")

            except Exception as e:
                print(f"Pools cache update error: {e}")
                if self._pools_cache is None:
                    self._pools_cache = []

        return self._pools_cache

    def _get_token_price(self, symbol: str) -> float:
        if not symbol or str(symbol).strip() in ['', 'Unknown', 'None']:
            return 0.0

        prices = self._get_cached_prices()
        return prices.get(str(symbol).strip(), 0.0)

    def _parse_decimal_amount(self, amount, decimals=9) -> float:
        try:
            amount_float = self._parse_amount(amount)
            return amount_float / (10 ** decimals)
        except:
            return 0.0

    def analyze_asset(self, symbol: str) -> Dict[str, Any]:
        try:
            print(f"Analyzing asset {symbol}...")

            details_result = self.components.get_asset_details(symbol)

            details = {}
            if isinstance(details_result, dict):
                details = self._safe_get(details_result, "asset", {})
                if not details:
                    details = details_result
            elif isinstance(details_result, list) and len(details_result) > 0:
                details = details_result[0]

            price_usd = self._get_token_price(symbol)

            market_cap = self._parse_amount(details.get("market_cap"))
            volume_24h = self._parse_amount(details.get("volume_24h"))
            total_supply = self._parse_amount(details.get("total_supply"))
            circulating_supply = self._parse_amount(details.get("circulating_supply"))

            health_score = 0

            if price_usd > 0:
                health_score += 25

            if market_cap > 10000000:
                health_score += 25
            elif market_cap > 1000000:
                health_score += 20
            elif market_cap > 100000:
                health_score += 15
            elif market_cap > 0:
                health_score += 10

            if volume_24h > 0:
                if market_cap > 0:
                    volume_ratio = volume_24h / market_cap
                    if volume_ratio > 0.1:
                        health_score += 25
                    elif volume_ratio > 0.01:
                        health_score += 20
                    elif volume_ratio > 0:
                        health_score += 15
                else:
                    health_score += 15

            if details.get("is_verified", False):
                health_score += 25

            if circulating_supply > 0 and total_supply > 0:
                circulation_rate = circulating_supply / total_supply
                if circulation_rate > 0.9:
                    health_score += 10
                elif circulation_rate > 0.5:
                    health_score += 7
                elif circulation_rate > 0:
                    health_score += 5

            liquidity_analysis = self.get_liquidity_analysis(symbol)
            if liquidity_analysis.get("success"):
                liquidity_score = liquidity_analysis.get("depth_score", 0)
                health_score += liquidity_score * 0.1

            return {
                "success": True,
                "asset": {
                    "symbol": symbol,
                    "name": details.get("name", symbol),
                    "address": details.get("address", ""),
                    "description": details.get("description", "")
                },
                "price": {
                    "usd": round(price_usd, 6),
                    "updated_at": datetime.now().isoformat()
                },
                "market_data": {
                    "market_cap_usd": round(market_cap, 2),
                    "volume_24h_usd": round(volume_24h, 2),
                    "total_supply": round(total_supply, 0),
                    "circulating_supply": round(circulating_supply, 0),
                    "circulation_rate": round(circulating_supply / total_supply * 100, 2) if total_supply > 0 else 0
                },
                "metadata": {
                    "decimals": details.get("decimals", 9),
                    "is_verified": details.get("is_verified", False),
                    "is_scam": details.get("is_scam", False),
                    "website": details.get("website", ""),
                    "socials": details.get("socials", {})
                },
                "health": {
                    "score": min(health_score, 100),
                    "level": "Excellent" if health_score >= 80 else 
                             "Good" if health_score >= 60 else 
                             "Fair" if health_score >= 40 else 
                             "Poor" if health_score >= 20 else "Critical",
                    "factors": {
                        "has_price": price_usd > 0,
                        "has_market_cap": market_cap > 0,
                        "has_volume": volume_24h > 0,
                        "is_verified": details.get("is_verified", False)
                    }
                },
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            print(f"Asset analysis error: {e}")
            return {"success": False, "error": str(e), "symbol": symbol}

    def find_arbitrage_opportunities(self, 
                                   min_profit_usd: float = 5.0, 
                                   min_tvl: float = 1000.0, 
                                   max_price_diff: float = 0.05,
                                   max_pools_to_check: int = 50) -> Dict[str, Any]:
        try:
            print(f"Searching for arbitrage opportunities...")

            pools = self._get_cached_pools()

            if not pools or len(pools) < 2:
                return {
                    "success": True,
                    "opportunities": [],
                    "message": "Not enough pools for arbitrage analysis"
                }

            pools_to_check = pools[:max_pools_to_check]

            pools_by_pair = {}

            for pool in pools_to_check:
                if not isinstance(pool, dict):
                    continue

                address = pool.get("address")
                if not address:
                    continue

                asset0 = self._safe_get(pool, "asset0", {})
                asset1 = self._safe_get(pool, "asset1", {})

                token0_symbol = self._safe_get(asset0, "symbol", "Unknown")
                token1_symbol = self._safe_get(asset1, "symbol", "Unknown")

                if token0_symbol == "Unknown" or token1_symbol == "Unknown":
                    continue

                sorted_symbols = tuple(sorted([str(token0_symbol), str(token1_symbol)]))

                pool_tvl = self._calculate_pool_tvl(pool)

                if pool_tvl < min_tvl:
                    continue

                reserve0 = self._parse_amount(self._safe_get(pool, "reserve0"))
                reserve1 = self._parse_amount(self._safe_get(pool, "reserve1"))

                if reserve0 <= 0 or reserve1 <= 0:
                    continue

                price_0_to_1 = reserve1 / reserve0
                price_1_to_0 = reserve0 / reserve1

                pool_data = {
                    "address": address,
                    "tokens": [token0_symbol, token1_symbol],
                    "reserves": [reserve0, reserve1],
                    "price_0_to_1": price_0_to_1,
                    "price_1_to_0": price_1_to_0,
                    "tvl_usd": pool_tvl,
                    "is_disabled": pool.get("is_disabled", False)
                }

                if sorted_symbols not in pools_by_pair:
                    pools_by_pair[sorted_symbols] = []

                pools_by_pair[sorted_symbols].append(pool_data)

            opportunities = []

            for pair_symbols, pair_pools in pools_by_pair.items():
                if len(pair_pools) < 2:
                    continue

                for i in range(len(pair_pools)):
                    for j in range(i + 1, len(pair_pools)):
                        pool1 = pair_pools[i]
                        pool2 = pair_pools[j]

                        if pool1["is_disabled"] or pool2["is_disabled"]:
                            continue

                        tokenA, tokenB = pair_symbols

                        price1 = pool1["price_0_to_1"]
                        price2 = pool2["price_0_to_1"]

                        if price1 > 0 and price2 > 0:
                            price_diff = abs(price1 - price2) / min(price1, price2)

                            if price_diff <= max_price_diff:
                                min_tvl = min(pool1["tvl_usd"], pool2["tvl_usd"])
                                trade_amount_usd = min_tvl * 0.01

                                estimated_profit = trade_amount_usd * price_diff

                                if estimated_profit >= min_profit_usd:
                                    if price1 > price2:
                                        direction = f"Buy in {pool2['address'][:8]}, sell in {pool1['address'][:8]}"
                                        buy_price = price2
                                        sell_price = price1
                                    else:
                                        direction = f"Buy in {pool1['address'][:8]}, sell in {pool2['address'][:8]}"
                                        buy_price = price1
                                        sell_price = price2

                                    opportunities.append({
                                        "token_pair": f"{tokenA}/{tokenB}",
                                        "pool1": {
                                            "address": pool1["address"],
                                            "price": round(price1, 6),
                                            "tvl_usd": round(pool1["tvl_usd"], 2)
                                        },
                                        "pool2": {
                                            "address": pool2["address"],
                                            "price": round(price2, 6),
                                            "tvl_usd": round(pool2["tvl_usd"], 2)
                                        },
                                        "arbitrage": {
                                            "price_difference_pct": round(price_diff * 100, 2),
                                            "estimated_profit_usd": round(estimated_profit, 2),
                                            "recommended_trade_amount_usd": round(trade_amount_usd, 2),
                                            "direction": direction,
                                            "buy_price": round(buy_price, 6),
                                            "sell_price": round(sell_price, 6),
                                            "profit_margin_pct": round((sell_price / buy_price - 1) * 100, 2)
                                        },
                                        "risk_assessment": "Low" if min_tvl > 10000 else 
                                                          "Medium" if min_tvl > 1000 else "High"
                                    })

            opportunities.sort(key=lambda x: x["arbitrage"]["estimated_profit_usd"], reverse=True)

            return {
                "success": True,
                "search_parameters": {
                    "min_profit_usd": min_profit_usd,
                    "min_tvl_usd": min_tvl,
                    "max_price_diff_pct": max_price_diff * 100,
                    "max_pools_checked": max_pools_to_check
                },
                "statistics": {
                    "total_pools_analyzed": len(pools_to_check),
                    "unique_token_pairs": len(pools_by_pair),
                    "opportunities_found": len(opportunities)
                },
                "opportunities": opportunities[:10],
                "timestamp": datetime.now().isoformat(),
                "note": "This is theoretical estimation. Actual profit may differ due to fees, slippage, and execution delays."
            }

        except Exception as e:
            print(f"Arbitrage search error: {e}")
            return {"success": False, "error": str(e)}

    def compare_pools(self, pool_addresses: List[str]) -> Dict[str, Any]:
        try:
            print(f"Comparing {len(pool_addresses)} pools...")

            if len(pool_addresses) < 2:
                return {
                    "success": False,
                    "error": "Minimum 2 pools required for comparison",
                    "pools_provided": len(pool_addresses)
                }

            pool_analyses = {}
            failed_pools = []

            for address in pool_addresses:
                analysis = self.analyze_pool(address)
                if analysis.get("success"):
                    pool_analyses[address] = analysis
                else:
                    failed_pools.append({
                        "address": address,
                        "error": analysis.get("error", "Unknown error")
                    })

            if len(pool_analyses) < 2:
                return {
                    "success": False,
                    "error": "Successfully analyzed less than 2 pools",
                    "successful": len(pool_analyses),
                    "failed": failed_pools
                }

            comparison_data = []
            all_metrics = {}

            for address, analysis in pool_analyses.items():
                metrics = analysis.get("metrics", {})
                health = analysis.get("health", {})
                tokens = analysis.get("tokens", {})

                pool_data = {
                    "address": address,
                    "tokens": {
                        "token0": tokens.get("token0", {}).get("symbol", "Unknown"),
                        "token1": tokens.get("token1", {}).get("symbol", "Unknown")
                    },
                    "tvl_usd": metrics.get("tvl_usd", 0),
                    "volume_24h_usd": metrics.get("volume_24h_usd", 0),
                    "fee_percent": metrics.get("fee_percent", 0.3),
                    "health_score": health.get("score", 0),
                    "health_level": health.get("level", "Unknown"),
                    "liquidity_depth_usd": metrics.get("liquidity_depth_usd", 0),
                    "price_ratio": metrics.get("price_ratio", 0),
                    "is_disabled": analysis.get("status", {}).get("is_disabled", False)
                }

                comparison_data.append(pool_data)

                for key, value in pool_data.items():
                    if isinstance(value, (int, float)):
                        if key not in all_metrics:
                            all_metrics[key] = []
                        all_metrics[key].append(value)

            best_by_metric = {}

            for metric in ["tvl_usd", "volume_24h_usd", "health_score", "liquidity_depth_usd"]:
                if metric in all_metrics and all_metrics[metric]:
                    best_index = all_metrics[metric].index(max(all_metrics[metric]))
                    best_by_metric[metric] = {
                        "address": comparison_data[best_index]["address"],
                        "value": max(all_metrics[metric])
                    }

            averages = {}
            for metric, values in all_metrics.items():
                if isinstance(values, list) and values:
                    averages[metric] = sum(values) / len(values)

            recommendations = []

            tvl_values = all_metrics.get("tvl_usd", [])
            if tvl_values:
                max_tvl = max(tvl_values)
                min_tvl = min(tvl_values)
                if max_tvl > min_tvl * 10:
                    recommendations.append("Large TVL difference between pools. Consider pools with higher TVL for less slippage.")

            fee_values = all_metrics.get("fee_percent", [])
            if fee_values:
                min_fee = min(fee_values)
                max_fee = max(fee_values)
                if max_fee > min_fee * 2:
                    recommendations.append(f"Pool fees differ. Lowest fee: {min_fee}%, highest: {max_fee}%")

            health_values = all_metrics.get("health_score", [])
            if health_values:
                avg_health = sum(health_values) / len(health_values)
                if avg_health < 50:
                    recommendations.append("Average health score is low. Consider more reliable pools.")

            return {
                "success": True,
                "pools_compared": len(pool_analyses),
                "failed_pools": failed_pools,
                "comparison": comparison_data,
                "best_performers": best_by_metric,
                "averages": {k: round(v, 2) for k, v in averages.items() if isinstance(v, (int, float))},
                "statistics": {
                    "total_tvl_usd": round(sum(all_metrics.get("tvl_usd", [])), 2),
                    "total_volume_24h_usd": round(sum(all_metrics.get("volume_24h_usd", [])), 2),
                    "avg_health_score": round(sum(health_values) / len(health_values), 1) if health_values else 0,
                    "disabled_pools": sum(1 for p in comparison_data if p.get("is_disabled", False))
                },
                "recommendations": recommendations,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            print(f"Pool comparison error: {e}")
            return {"success": False, "error": str(e)}

    def get_liquidity_analysis(self, token_symbol: str) -> Dict[str, Any]:
        try:
            print(f"Analyzing liquidity for {token_symbol}...")

            pools = self._get_cached_pools()

            if not pools:
                return {
                    "success": False,
                    "error": "Failed to get pool data",
                    "token_symbol": token_symbol
                }

            token_pools = []

            for pool in pools:
                if not isinstance(pool, dict):
                    continue

                asset0 = self._safe_get(pool, "asset0", {})
                asset1 = self._safe_get(pool, "asset1", {})

                token0_symbol = self._safe_get(asset0, "symbol", "Unknown")
                token1_symbol = self._safe_get(asset1, "symbol", "Unknown")

                if token_symbol not in [token0_symbol, token1_symbol]:
                    continue

                address = pool.get("address")
                if not address:
                    continue

                pool_tvl = self._calculate_pool_tvl(pool)

                reserve0 = self._parse_amount(self._safe_get(pool, "reserve0"))
                reserve1 = self._parse_amount(self._safe_get(pool, "reserve1"))

                if token0_symbol == token_symbol:
                    paired_token = token1_symbol
                    token_reserve = reserve0
                    paired_reserve = reserve1
                    token_price = self._get_token_price(token_symbol)
                    paired_price = self._get_token_price(token1_symbol)
                else:
                    paired_token = token0_symbol
                    token_reserve = reserve1
                    paired_reserve = reserve0
                    token_price = self._get_token_price(token_symbol)
                    paired_price = self._get_token_price(token0_symbol)

                token_liquidity_usd = token_reserve * token_price
                paired_liquidity_usd = paired_reserve * paired_price

                liquidity_balance = min(token_liquidity_usd, paired_liquidity_usd) / max(token_liquidity_usd, paired_liquidity_usd) if max(token_liquidity_usd, paired_liquidity_usd) > 0 else 0

                token_pools.append({
                    "pool_address": address,
                    "paired_token": paired_token,
                    "reserves": {
                        "token": round(token_reserve, 6),
                        "paired": round(paired_reserve, 6)
                    },
                    "liquidity_usd": {
                        "token": round(token_liquidity_usd, 2),
                        "paired": round(paired_liquidity_usd, 2),
                        "total": round(pool_tvl, 2)
                    },
                    "metrics": {
                        "liquidity_balance": round(liquidity_balance, 3),
                        "depth_score": min(liquidity_balance * 100, 100)
                    },
                    "tvl_usd": round(pool_tvl, 2),
                    "is_disabled": pool.get("is_disabled", False)
                })

            if not token_pools:
                return {
                    "success": True,
                    "token_symbol": token_symbol,
                    "message": "Token not found in active pools",
                    "total_pools": 0,
                    "total_liquidity_usd": 0,
                    "timestamp": datetime.now().isoformat()
                }

            token_pools.sort(key=lambda x: x["tvl_usd"], reverse=True)

            total_liquidity_usd = sum(p["tvl_usd"] for p in token_pools)
            active_pools = sum(1 for p in token_pools if not p["is_disabled"])

            concentration_index = 0
            if total_liquidity_usd > 0:
                for pool in token_pools:
                    share = pool["tvl_usd"] / total_liquidity_usd
                    concentration_index += share ** 2

            paired_tokens = {}
            for pool in token_pools:
                paired_token = pool["paired_token"]
                if paired_token not in paired_tokens:
                    paired_tokens[paired_token] = 0
                paired_tokens[paired_token] += pool["tvl_usd"]

            top_paired_tokens = sorted(paired_tokens.items(), key=lambda x: x[1], reverse=True)[:5]

            depth_score = 0

            if len(token_pools) >= 5:
                depth_score += 30
            elif len(token_pools) >= 3:
                depth_score += 20
            elif len(token_pools) >= 1:
                depth_score += 10

            if total_liquidity_usd > 1000000:
                depth_score += 40
            elif total_liquidity_usd > 100000:
                depth_score += 30
            elif total_liquidity_usd > 10000:
                depth_score += 20
            elif total_liquidity_usd > 1000:
                depth_score += 10

            if concentration_index < 0.3:
                depth_score += 30
            elif concentration_index < 0.5:
                depth_score += 20
            elif concentration_index < 0.7:
                depth_score += 10

            avg_liquidity_balance = sum(p["metrics"]["liquidity_balance"] for p in token_pools) / len(token_pools)
            if avg_liquidity_balance > 0.8:
                depth_score += 20
            elif avg_liquidity_balance > 0.5:
                depth_score += 15
            elif avg_liquidity_balance > 0.2:
                depth_score += 10

            return {
                "success": True,
                "token_symbol": token_symbol,
                "overview": {
                    "total_pools": len(token_pools),
                    "active_pools": active_pools,
                    "disabled_pools": len(token_pools) - active_pools,
                    "total_liquidity_usd": round(total_liquidity_usd, 2),
                    "average_pool_liquidity_usd": round(total_liquidity_usd / len(token_pools), 2) if token_pools else 0,
                    "concentration_index": round(concentration_index, 3)
                },
                "depth_analysis": {
                    "score": min(depth_score, 100),
                    "level": "Excellent" if depth_score >= 80 else 
                             "Good" if depth_score >= 60 else 
                             "Fair" if depth_score >= 40 else 
                             "Poor" if depth_score >= 20 else "Critical",
                    "factors": {
                        "pool_count": len(token_pools),
                        "total_liquidity_usd": total_liquidity_usd,
                        "concentration": concentration_index,
                        "avg_liquidity_balance": round(avg_liquidity_balance, 3)
                    }
                },
                "paired_tokens": [
                    {
                        "token": token,
                        "liquidity_usd": round(liquidity, 2),
                        "share_pct": round(liquidity / total_liquidity_usd * 100, 1) if total_liquidity_usd > 0 else 0
                    }
                    for token, liquidity in top_paired_tokens
                ],
                "top_pools": token_pools[:10],
                "recommendations": self._generate_liquidity_recommendations(
                    len(token_pools), total_liquidity_usd, concentration_index, avg_liquidity_balance
                ),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            print(f"Liquidity analysis error: {e}")
            return {"success": False, "error": str(e), "token_symbol": token_symbol}

    def _generate_liquidity_recommendations(self, pool_count: int, total_liquidity: float, 
                                          concentration: float, balance: float) -> List[str]:
        recommendations = []

        if pool_count == 0:
            recommendations.append("Token not represented in liquidity pools. Consider creating LP.")
        elif pool_count == 1:
            recommendations.append("Token represented in only one pool. Liquidity diversification reduces risks.")

        if total_liquidity < 10000:
            recommendations.append("Low total liquidity. High slippage risk for large trades.")

        if concentration > 0.7:
            recommendations.append("High liquidity concentration in one/few pools. Consider distributing liquidity.")

        if balance < 0.3:
            recommendations.append("Low liquidity balance in pools. May lead to inefficient pricing.")

        if not recommendations and pool_count > 2 and total_liquidity > 50000 and concentration < 0.5:
            recommendations.append("Token liquidity is in good condition.")

        return recommendations

    def get_top_performing_pools(self, period: str = "24h", limit: int = 10, 
                               min_tvl: float = 1000.0) -> Dict[str, Any]:
        try:
            print(f"Getting top {limit} pools for {period}...")

            pools = self._get_cached_pools()

            if not pools:
                return {
                    "success": False,
                    "error": "Failed to get pool data",
                    "period": period,
                    "limit": limit
                }

            analyzed_pools = []
            pools_to_analyze = pools[:100]

            for pool in pools_to_analyze:
                if not isinstance(pool, dict):
                    continue

                address = pool.get("address")
                if not address:
                    continue

                if pool.get("is_disabled", False):
                    continue

                pool_tvl = self._calculate_pool_tvl(pool)

                if pool_tvl < min_tvl:
                    continue

                try:
                    trades_result = self.components.get_pool_trades(address, limit=30)
                    trades = []
                    if isinstance(trades_result, dict):
                        trades = self._safe_get(trades_result, "trades", [])
                    elif isinstance(trades_result, list):
                        trades = trades_result
                except:
                    trades = []

                volume = 0
                if trades:
                    current_time = datetime.now()
                    for trade in trades:
                        if isinstance(trade, dict):
                            amount_usd = self._parse_amount(trade.get("amount_usd"))
                            volume += amount_usd

                asset0 = self._safe_get(pool, "asset0", {})
                asset1 = self._safe_get(pool, "asset1", {})

                token0_symbol = self._safe_get(asset0, "symbol", "Unknown")
                token1_symbol = self._safe_get(asset1, "symbol", "Unknown")

                performance_score = 0

                if pool_tvl > 100000:
                    performance_score += 35
                elif pool_tvl > 10000:
                    performance_score += 25
                elif pool_tvl > 1000:
                    performance_score += 15

                if volume > 0:
                    volume_tvl_ratio = volume / pool_tvl if pool_tvl > 0 else 0
                    if volume_tvl_ratio > 0.5:
                        performance_score += 40
                    elif volume_tvl_ratio > 0.1:
                        performance_score += 30
                    elif volume_tvl_ratio > 0.01:
                        performance_score += 20
                    elif volume > 0:
                        performance_score += 10

                reserve0 = self._parse_amount(self._safe_get(pool, "reserve0"))
                reserve1 = self._parse_amount(self._safe_get(pool, "reserve1"))

                if reserve0 > 0 and reserve1 > 0:
                    price0 = self._get_token_price(token0_symbol)
                    price1 = self._get_token_price(token1_symbol)

                    if price0 > 0 and price1 > 0:
                        value0 = reserve0 * price0
                        value1 = reserve1 * price1
                        balance_ratio = min(value0, value1) / max(value0, value1) if max(value0, value1) > 0 else 0

                        if balance_ratio > 0.8:
                            performance_score += 25
                        elif balance_ratio > 0.5:
                            performance_score += 20
                        elif balance_ratio > 0.2:
                            performance_score += 15

                analyzed_pools.append({
                    "pool_address": address,
                    "tokens": [token0_symbol, token1_symbol],
                    "metrics": {
                        "tvl_usd": round(pool_tvl, 2),
                        "volume_usd": round(volume, 2),
                        "volume_tvl_ratio": round(volume / pool_tvl, 4) if pool_tvl > 0 else 0,
                        "performance_score": round(performance_score, 1)
                    },
                    "reserves": {
                        "token0": round(reserve0, 6),
                        "token1": round(reserve1, 6)
                    }
                })

            analyzed_pools.sort(key=lambda x: x["metrics"]["performance_score"], reverse=True)

            return {
                "success": True,
                "period": period,
                "limit": limit,
                "min_tvl_usd": min_tvl,
                "statistics": {
                    "total_pools_analyzed": len(analyzed_pools),
                    "total_tvl_usd": round(sum(p["metrics"]["tvl_usd"] for p in analyzed_pools), 2),
                    "total_volume_usd": round(sum(p["metrics"]["volume_usd"] for p in analyzed_pools), 2),
                    "avg_performance_score": round(sum(p["metrics"]["performance_score"] for p in analyzed_pools) / len(analyzed_pools), 1) if analyzed_pools else 0
                },
                "top_pools": analyzed_pools[:limit],
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            print(f"Top pools error: {e}")
            return {"success": False, "error": str(e)}

    def generate_pool_report(self, pool_address: str) -> str:
        try:
            print(f"Generating report for pool {pool_address[:16]}...")

            analysis = self.analyze_pool(pool_address)

            if not analysis.get("success"):
                return f"Error: {analysis.get('error', 'Unknown error')}"

            try:
                liquidity_providers = self.components.get_liquidity_providers(pool_address)
                lp_count = len(liquidity_providers) if isinstance(liquidity_providers, list) else 0
            except:
                lp_count = 0

            tokens = analysis.get("tokens", {})
            metrics = analysis.get("metrics", {})
            health = analysis.get("health", {})
            status = analysis.get("status", {})

            report_lines = []
            report_lines.append("=" * 80)
            report_lines.append("LIQUIDITY POOL ANALYTICAL REPORT")
            report_lines.append("=" * 80)
            report_lines.append(f"Pool address: {pool_address}")
            report_lines.append(f"Report time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report_lines.append(f"Data source: DeDust API v2")
            report_lines.append("=" * 80)

            report_lines.append("GENERAL INFORMATION")
            report_lines.append("-" * 40)
            report_lines.append(f"Tokens: {tokens.get('token0', {}).get('symbol', 'Unknown')} / {tokens.get('token1', {}).get('symbol', 'Unknown')}")
            report_lines.append(f"Names: {tokens.get('token0', {}).get('name', 'N/A')} / {tokens.get('token1', {}).get('name', 'N/A')}")
            report_lines.append(f"TVL: ${metrics.get('tvl_usd', 0):,.2f}")
            report_lines.append(f"24h trading volume: ${metrics.get('volume_24h_usd', 0):,.2f}")
            report_lines.append(f"Liquidity depth: ${metrics.get('liquidity_depth_usd', 0):,.2f}")
            report_lines.append(f"Liquidity providers: {lp_count}")
            report_lines.append(f"Pool fee: {metrics.get('fee_percent', 0.3)}%")
            report_lines.append(f"Pool status: {'Disabled' if status.get('is_disabled', False) else 'Active'}")

            report_lines.append("")
            report_lines.append("POOL METRICS")
            report_lines.append("-" * 40)
            report_lines.append(f"Health Score: {health.get('score', 0)}/100 ({health.get('level', 'Unknown')})")
            report_lines.append(f"Price: 1 {tokens.get('token0', {}).get('symbol', 'A')} = {metrics.get('token1_per_token0', 0):.6f} {tokens.get('token1', {}).get('symbol', 'B')}")
            report_lines.append(f"Price: 1 {tokens.get('token1', {}).get('symbol', 'B')} = {metrics.get('token0_per_token1', 0):.6f} {tokens.get('token0', {}).get('symbol', 'A')}")
            report_lines.append(f"Reserve {tokens.get('token0', {}).get('symbol', 'A')}: {tokens.get('token0', {}).get('reserve', 0):,.2f} (${tokens.get('token0', {}).get('value_usd', 0):,.2f})")
            report_lines.append(f"Reserve {tokens.get('token1', {}).get('symbol', 'B')}: {tokens.get('token1', {}).get('reserve', 0):,.2f} (${tokens.get('token1', {}).get('value_usd', 0):,.2f})")
            report_lines.append(f"24h trades: {status.get('trade_count_24h', 0)}")

            report_lines.append("")
            report_lines.append("RISK ANALYSIS")
            report_lines.append("-" * 40)

            risks = []
            recommendations = []

            if health.get("score", 0) < 50:
                risks.append("Low health score indicates increased risks")
                recommendations.append("Consider more reliable pools with higher health score")

            if metrics.get("tvl_usd", 0) < 10000:
                risks.append("Low TVL may lead to high slippage")
                recommendations.append("For large trades use pools with TVL > $10,000")

            if status.get("is_disabled", False):
                risks.append("Pool disabled - adding liquidity not possible")
                recommendations.append("Do not add liquidity to disabled pools")

            if not risks:
                risks.append("Pool shows good performance")
                recommendations.append("Can be considered for adding liquidity")

            for i, risk in enumerate(risks, 1):
                report_lines.append(f"{i}. {risk}")

            report_lines.append("")
            report_lines.append("RECOMMENDATIONS")
            report_lines.append("-" * 40)

            for i, rec in enumerate(recommendations, 1):
                report_lines.append(f"{i}. {rec}")

            report_lines.append("")
            report_lines.append("ADDITIONAL INFORMATION")
            report_lines.append("-" * 40)
            report_lines.append(f"Decimals {tokens.get('token0', {}).get('symbol', 'A')}: {tokens.get('token0', {}).get('decimals', 9)}")
            report_lines.append(f"Decimals {tokens.get('token1', {}).get('symbol', 'B')}: {tokens.get('token1', {}).get('decimals', 9)}")
            report_lines.append(f"Price {tokens.get('token0', {}).get('symbol', 'A')}: ${tokens.get('token0', {}).get('price_usd', 0):.6f}")
            report_lines.append(f"Price {tokens.get('token1', {}).get('symbol', 'B')}: ${tokens.get('token1', {}).get('price_usd', 0):.6f}")

            report_lines.append("")
            report_lines.append("=" * 80)
            report_lines.append("IMPORTANT NOTICE")
            report_lines.append("=" * 80)
            report_lines.append("This report provides analytical information only.")
            report_lines.append("Not financial advice.")
            report_lines.append("Make all investment decisions independently.")
            report_lines.append("Report author is not responsible for your decisions.")
            report_lines.append("=" * 80)

            return "\n".join(report_lines)

        except Exception as e:
            return f"Report generation error: {str(e)}"

    def calculate_impermanent_loss(self, pool_address: str, 
                                 token_a_change: float, 
                                 token_b_change: float) -> Dict[str, Any]:
        try:
            print(f"Calculating impermanent loss for pool {pool_address[:16]}...")

            analysis = self.analyze_pool(pool_address)

            if not analysis.get("success"):
                return {
                    "success": False,
                    "error": analysis.get("error", "Failed to analyze pool"),
                    "pool_address": pool_address
                }

            tokens = analysis.get("tokens", {})
            metrics = analysis.get("metrics", {})

            current_price_ratio = metrics.get("price_ratio", 1)
            reserve0_value = tokens.get("token0", {}).get("value_usd", 0)
            reserve1_value = tokens.get("token1", {}).get("value_usd", 0)

            if reserve0_value <= 0 or reserve1_value <= 0:
                return {
                    "success": False,
                    "error": "Cannot calculate IL for pool with zero reserves",
                    "pool_address": pool_address
                }

            new_price_ratio = current_price_ratio * (1 + token_b_change) / (1 + token_a_change)

            price_ratio_change = new_price_ratio / current_price_ratio

            if price_ratio_change > 0:
                impermanent_loss_pct = (2 * np.sqrt(price_ratio_change) / (1 + price_ratio_change) - 1) * 100
            else:
                impermanent_loss_pct = -100

            total_value_now = reserve0_value + reserve1_value

            held_value = reserve0_value * (1 + token_a_change) + reserve1_value * (1 + token_b_change)

            pooled_value = total_value_now * (1 + impermanent_loss_pct / 100)

            absolute_loss = held_value - pooled_value

            if impermanent_loss_pct < -5:
                risk_level = "High"
                interpretation = "Significant impermanent loss expected with such price changes"
            elif impermanent_loss_pct < -2:
                risk_level = "Medium"
                interpretation = "Moderate impermanent loss possible"
            elif impermanent_loss_pct < 0:
                risk_level = "Low"
                interpretation = "Minor impermanent loss"
            else:
                risk_level = "Minimal"
                interpretation = "No impermanent loss expected or profit expected"

            return {
                "success": True,
                "pool_address": pool_address,
                "tokens": [
                    tokens.get("token0", {}).get("symbol", "Token A"),
                    tokens.get("token1", {}).get("symbol", "Token B")
                ],
                "current_state": {
                    "price_ratio": round(current_price_ratio, 6),
                    "token0_value_usd": round(reserve0_value, 2),
                    "token1_value_usd": round(reserve1_value, 2),
                    "total_value_usd": round(total_value_now, 2)
                },
                "price_changes": {
                    "token_a_pct": round(token_a_change * 100, 1),
                    "token_b_pct": round(token_b_change * 100, 1),
                    "new_price_ratio": round(new_price_ratio, 6),
                    "price_ratio_change_pct": round((new_price_ratio / current_price_ratio - 1) * 100, 2)
                },
                "impermanent_loss": {
                    "percentage": round(impermanent_loss_pct, 2),
                    "absolute_usd": round(absolute_loss, 2),
                    "held_value_usd": round(held_value, 2),
                    "pooled_value_usd": round(pooled_value, 2),
                    "difference_usd": round(held_value - pooled_value, 2)
                },
                "risk_assessment": {
                    "level": risk_level,
                    "impermanent_loss_pct": round(abs(impermanent_loss_pct), 2),
                    "interpretation": interpretation
                },
                "recommendation": "Consider holding tokens instead of providing liquidity" if impermanent_loss_pct < -3 else 
                               "Providing liquidity may be appropriate" if impermanent_loss_pct < -1 else 
                               "Low impermanent loss risk",
                "formula_used": "IL = 2 * sqrt(new_price/old_price) / (1 + new_price/old_price) - 1",
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            print(f"Impermanent loss calculation error: {e}")
            return {"success": False, "error": str(e), "pool_address": pool_address}

    def analyze_wallet_portfolio(self, wallet_address: str) -> Dict[str, Any]:
        try:
            print(f"Analyzing wallet portfolio {wallet_address[:16]}...")

            assets_result = self.components.get_account_assets(wallet_address)

            assets = []
            if isinstance(assets_result, dict):
                assets = self._safe_get(assets_result, "asset_list", [])
            elif isinstance(assets_result, list):
                assets = assets_result

            if not isinstance(assets, list):
                return {
                    "success": False,
                    "error": "Failed to get asset data",
                    "wallet_address": wallet_address
                }

            analyzed_assets = []
            total_value_usd = 0

            for asset in assets:
                if not isinstance(asset, dict):
                    continue

                symbol = asset.get("symbol")
                if not symbol:
                    continue

                balance = self._parse_amount(asset.get("balance"))
                if balance <= 0:
                    continue

                price_usd = self._get_token_price(symbol)
                value_usd = balance * price_usd

                try:
                    asset_details = self.components.get_asset_details(symbol)
                    details = {}
                    if isinstance(asset_details, dict):
                        details = self._safe_get(asset_details, "asset", {})
                        if not details:
                            details = asset_details

                    asset_name = details.get("name", symbol)
                    decimals = details.get("decimals", 9)
                    is_verified = details.get("is_verified", False)
                    is_scam = details.get("is_scam", False)
                except:
                    asset_name = symbol
                    decimals = 9
                    is_verified = False
                    is_scam = False

                if value_usd > 0.01:
                    analyzed_assets.append({
                        "symbol": symbol,
                        "name": asset_name,
                        "balance": round(balance, 6),
                        "price_usd": round(price_usd, 6),
                        "value_usd": round(value_usd, 2),
                        "decimals": decimals,
                        "is_verified": is_verified,
                        "is_scam": is_scam,
                        "share_pct": 0
                    })
                    total_value_usd += value_usd

            for asset in analyzed_assets:
                if total_value_usd > 0:
                    asset["share_pct"] = round(asset["value_usd"] / total_value_usd * 100, 2)

            analyzed_assets.sort(key=lambda x: x["value_usd"], reverse=True)

            try:
                trades_result = self.components.get_account_trades(wallet_address)
                trades = []
                if isinstance(trades_result, dict):
                    trades = self._safe_get(trades_result, "trade_list", [])
                elif isinstance(trades_result, list):
                    trades = trades_result

                recent_trades = []
                trade_volume_24h = 0

                for trade in trades[:20]:
                    if isinstance(trade, dict):
                        amount_usd = self._parse_amount(trade.get("amount_usd"))
                        trade_type = trade.get("type", "unknown")
                        timestamp = trade.get("timestamp", "")

                        recent_trades.append({
                            "type": trade_type,
                            "amount_usd": round(amount_usd, 2),
                            "timestamp": timestamp
                        })

                        try:
                            if timestamp:
                                trade_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                                if (datetime.now() - trade_time) <= timedelta(hours=24):
                                    trade_volume_24h += amount_usd
                        except:
                            trade_volume_24h += amount_usd
            except:
                recent_trades = []
                trade_volume_24h = 0

            diversification_score = 0

            asset_count = len(analyzed_assets)
            if asset_count >= 5:
                diversification_score += 30
            elif asset_count >= 3:
                diversification_score += 20
            elif asset_count >= 1:
                diversification_score += 10

            if asset_count > 1:
                top_asset_share = analyzed_assets[0]["share_pct"] if analyzed_assets else 0
                if top_asset_share < 50:
                    diversification_score += 30
                elif top_asset_share < 70:
                    diversification_score += 20
                elif top_asset_share < 90:
                    diversification_score += 10

            if total_value_usd > 10000:
                diversification_score += 20
            elif total_value_usd > 1000:
                diversification_score += 15
            elif total_value_usd > 100:
                diversification_score += 10

            if trade_volume_24h > 0:
                diversification_score += 20

            risky_assets = [a for a in analyzed_assets if a.get("is_scam", False)]
            unverified_assets = [a for a in analyzed_assets if not a.get("is_verified", False) and not a.get("is_scam", False)]

            risk_assessment = "Low"
            if len(risky_assets) > 0:
                risk_assessment = "Critical"
            elif len(unverified_assets) > asset_count * 0.5:
                risk_assessment = "High"
            elif len(unverified_assets) > 0:
                risk_assessment = "Medium"

            recommendations = []

            if len(risky_assets) > 0:
                recommendations.append(f"Potential scam tokens detected ({len(risky_assets)}): consider withdrawing funds")

            if len(unverified_assets) > asset_count * 0.3:
                recommendations.append(f"High proportion of unverified tokens ({len(unverified_assets)} of {asset_count})")

            if asset_count == 1:
                recommendations.append("Portfolio consists of one token - high concentration risk")
            elif analyzed_assets and analyzed_assets[0]["share_pct"] > 70:
                recommendations.append(f"High concentration in one token ({analyzed_assets[0]['symbol']}: {analyzed_assets[0]['share_pct']}%)")

            if not recommendations:
                recommendations.append("Portfolio shows good diversification and risk management")

            return {
                "success": True,
                "wallet_address": wallet_address,
                "portfolio_summary": {
                    "total_value_usd": round(total_value_usd, 2),
                    "asset_count": asset_count,
                    "verified_assets": sum(1 for a in analyzed_assets if a.get("is_verified", False)),
                    "unverified_assets": len(unverified_assets),
                    "risky_assets": len(risky_assets),
                    "trade_volume_24h_usd": round(trade_volume_24h, 2)
                },
                "diversification": {
                    "score": min(diversification_score, 100),
                    "level": "Excellent" if diversification_score >= 80 else 
                             "Good" if diversification_score >= 60 else 
                             "Fair" if diversification_score >= 40 else 
                             "Poor" if diversification_score >= 20 else "Critical"
                },
                "risk_assessment": {
                    "level": risk_assessment,
                    "risky_assets": [{"symbol": a["symbol"], "value_usd": a["value_usd"]} for a in risky_assets],
                    "unverified_assets": [{"symbol": a["symbol"], "value_usd": a["value_usd"]} for a in unverified_assets]
                },
                "assets": analyzed_assets[:10],
                "recent_activity": {
                    "trade_count": len(recent_trades),
                    "trades": recent_trades[:5],
                    "volume_24h_usd": round(trade_volume_24h, 2)
                },
                "recommendations": recommendations,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            print(f"Portfolio analysis error: {e}")
            return {"success": False, "error": str(e), "wallet_address": wallet_address}

    def get_swap_recommendations(self, offer_token: str, ask_token: str, 
                               amount: float) -> Dict[str, Any]:
        try:
            print(f"Finding best swap route {offer_token} -> {ask_token}...")

            if offer_token == ask_token:
                return {
                    "success": False,
                    "error": "Swap tokens are identical",
                    "offer_token": offer_token,
                    "ask_token": ask_token,
                    "amount": amount
                }

            if amount <= 0:
                return {
                    "success": False,
                    "error": "Swap amount must be positive",
                    "amount": amount
                }

            pools = self._get_cached_pools()

            direct_pools = []

            for pool in pools:
                if not isinstance(pool, dict):
                    continue

                address = pool.get("address")
                if not address:
                    continue

                asset0 = self._safe_get(pool, "asset0", {})
                asset1 = self._safe_get(pool, "asset1", {})

                token0_symbol = self._safe_get(asset0, "symbol", "Unknown")
                token1_symbol = self._safe_get(asset1, "symbol", "Unknown")

                if (token0_symbol == offer_token and token1_symbol == ask_token) or \
                   (token1_symbol == offer_token and token0_symbol == ask_token):

                    pool_tvl = self._calculate_pool_tvl(pool)

                    reserve0 = self._parse_amount(self._safe_get(pool, "reserve0"))
                    reserve1 = self._parse_amount(self._safe_get(pool, "reserve1"))

                    if token0_symbol == offer_token:
                        input_reserve = reserve0
                        output_reserve = reserve1
                        price = output_reserve / input_reserve if input_reserve > 0 else 0
                    else:
                        input_reserve = reserve1
                        output_reserve = reserve0
                        price = output_reserve / input_reserve if input_reserve > 0 else 0

                    if input_reserve > 0 and output_reserve > 0:
                        k = input_reserve * output_reserve
                        new_input_reserve = input_reserve + amount
                        new_output_reserve = k / new_input_reserve
                        output_amount = output_reserve - new_output_reserve

                        fee = self._parse_amount(pool.get("fee", "0.3")) / 100
                        output_amount_after_fee = output_amount * (1 - fee)

                        price_impact = (amount / input_reserve) * 100 if input_reserve > 0 else 100

                        direct_pools.append({
                            "pool_address": address,
                            "type": "direct",
                            "estimated_output": round(output_amount_after_fee, 6),
                            "price": round(price, 6),
                            "price_impact_pct": round(price_impact, 2),
                            "tvl_usd": round(pool_tvl, 2),
                            "fee_pct": fee * 100,
                            "route": f"{offer_token} → {ask_token}"
                        })

            direct_pools.sort(key=lambda x: x["estimated_output"], reverse=True)

            complex_routes = []

            intermediate_tokens = ["TON", "USDT", "USDC"]

            for intermediate in intermediate_tokens:
                if intermediate in [offer_token, ask_token]:
                    continue

                first_pool = None
                second_pool = None

                for pool in pools:
                    if not isinstance(pool, dict):
                        continue

                    address = pool.get("address")
                    if not address:
                        continue

                    asset0 = self._safe_get(pool, "asset0", {})
                    asset1 = self._safe_get(pool, "asset1", {})

                    token0_symbol = self._safe_get(asset0, "symbol", "Unknown")
                    token1_symbol = self._safe_get(asset1, "symbol", "Unknown")

                    if not first_pool and (
                        (token0_symbol == offer_token and token1_symbol == intermediate) or
                        (token1_symbol == offer_token and token0_symbol == intermediate)
                    ):
                        first_pool = pool

                    if not second_pool and (
                        (token0_symbol == intermediate and token1_symbol == ask_token) or
                        (token1_symbol == intermediate and token0_symbol == ask_token)
                    ):
                        second_pool = pool

                if first_pool and second_pool:
                    try:
                        reserve0_1 = self._parse_amount(self._safe_get(first_pool, "reserve0"))
                        reserve1_1 = self._parse_amount(self._safe_get(first_pool, "reserve1"))

                        asset0_1 = self._safe_get(first_pool, "asset0", {})
                        asset1_1 = self._safe_get(first_pool, "asset1", {})
                        token0_1 = self._safe_get(asset0_1, "symbol", "Unknown")
                        token1_1 = self._safe_get(asset1_1, "symbol", "Unknown")

                        if token0_1 == offer_token:
                            input_reserve_1 = reserve0_1
                            output_reserve_1 = reserve1_1
                        else:
                            input_reserve_1 = reserve1_1
                            output_reserve_1 = reserve0_1

                        if input_reserve_1 > 0 and output_reserve_1 > 0:
                            k1 = input_reserve_1 * output_reserve_1
                            new_input_reserve_1 = input_reserve_1 + amount
                            new_output_reserve_1 = k1 / new_input_reserve_1
                            intermediate_amount = output_reserve_1 - new_output_reserve_1

                            fee1 = self._parse_amount(first_pool.get("fee", "0.3")) / 100
                            intermediate_amount_after_fee1 = intermediate_amount * (1 - fee1)

                            reserve0_2 = self._parse_amount(self._safe_get(second_pool, "reserve0"))
                            reserve1_2 = self._parse_amount(self._safe_get(second_pool, "reserve1"))

                            asset0_2 = self._safe_get(second_pool, "asset0", {})
                            asset1_2 = self._safe_get(second_pool, "asset1", {})
                            token0_2 = self._safe_get(asset0_2, "symbol", "Unknown")
                            token1_2 = self._safe_get(asset1_2, "symbol", "Unknown")

                            if token0_2 == intermediate:
                                input_reserve_2 = reserve0_2
                                output_reserve_2 = reserve1_2
                            else:
                                input_reserve_2 = reserve1_2
                                output_reserve_2 = reserve0_2

                            if input_reserve_2 > 0 and output_reserve_2 > 0:
                                k2 = input_reserve_2 * output_reserve_2
                                new_input_reserve_2 = input_reserve_2 + intermediate_amount_after_fee1
                                new_output_reserve_2 = k2 / new_input_reserve_2
                                final_amount = output_reserve_2 - new_output_reserve_2

                                fee2 = self._parse_amount(second_pool.get("fee", "0.3")) / 100
                                final_amount_after_fee = final_amount * (1 - fee2)

                                total_fee_pct = (fee1 + fee2) * 100

                                price_impact_1 = (amount / input_reserve_1) * 100 if input_reserve_1 > 0 else 100
                                price_impact_2 = (intermediate_amount_after_fee1 / input_reserve_2) * 100 if input_reserve_2 > 0 else 100
                                total_price_impact = price_impact_1 + price_impact_2

                                complex_routes.append({
                                    "pool1_address": first_pool.get("address"),
                                    "pool2_address": second_pool.get("address"),
                                    "type": "complex",
                                    "intermediate_token": intermediate,
                                    "estimated_output": round(final_amount_after_fee, 6),
                                    "total_fee_pct": round(total_fee_pct, 2),
                                    "total_price_impact_pct": round(total_price_impact, 2),
                                    "route": f"{offer_token} → {intermediate} → {ask_token}",
                                    "steps": [
                                        {
                                            "from": offer_token,
                                            "to": intermediate,
                                            "pool": first_pool.get("address"),
                                            "fee_pct": fee1 * 100
                                        },
                                        {
                                            "from": intermediate,
                                            "to": ask_token,
                                            "pool": second_pool.get("address"),
                                            "fee_pct": fee2 * 100
                                        }
                                    ]
                                })
                    except:
                        continue

            complex_routes.sort(key=lambda x: x["estimated_output"], reverse=True)

            all_routes = direct_pools + complex_routes
            all_routes.sort(key=lambda x: x["estimated_output"], reverse=True)

            if not all_routes:
                return {
                    "success": False,
                    "error": "No suitable pools found for swap",
                    "offer_token": offer_token,
                    "ask_token": ask_token,
                    "amount": amount
                }

            best_route = all_routes[0]

            ask_token_price = self._get_token_price(ask_token)
            output_value_usd = best_route["estimated_output"] * ask_token_price
            input_value_usd = amount * self._get_token_price(offer_token)

            efficiency = (output_value_usd / input_value_usd - 1) * 100 if input_value_usd > 0 else 0

            return {
                "success": True,
                "swap_request": {
                    "offer_token": offer_token,
                    "ask_token": ask_token,
                    "amount": amount,
                    "input_value_usd": round(input_value_usd, 2)
                },
                "best_route": best_route,
                "output_value_usd": round(output_value_usd, 2),
                "efficiency_pct": round(efficiency, 2),
                "alternative_routes": all_routes[1:4] if len(all_routes) > 1 else [],
                "statistics": {
                    "direct_pools_found": len(direct_pools),
                    "complex_routes_found": len(complex_routes),
                    "total_routes_evaluated": len(all_routes)
                },
                "recommendation": {
                    "route_type": best_route.get("type", "unknown"),
                    "estimated_output": best_route["estimated_output"],
                    "efficiency": "High" if efficiency > -1 else "Medium" if efficiency > -3 else "Low",
                    "suggestion": "Use this route" if best_route["type"] == "direct" else 
                                  "Consider direct route if available" if direct_pools else 
                                  "This is the best available route"
                },
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            print(f"Swap route search error: {e}")
            return {"success": False, "error": str(e)}

    def calculate_apy_breakdown(self, jetton_address: str) -> Dict[str, Any]:
        try:
            print(f"Calculating APY for jetton {jetton_address[:16]}...")

            metadata = self.components.get_jetton_metadata(jetton_address)

            holders_result = self.components.get_jetton_holders(jetton_address)
            holders = []
            if isinstance(holders_result, dict):
                holders = self._safe_get(holders_result, "holders", [])
            elif isinstance(holders_result, list):
                holders = holders_result

            total_supply_result = self.components.get_jetton_total_supply(jetton_address)
            total_supply = self._parse_amount(total_supply_result.get("total_supply")) if isinstance(total_supply_result, dict) else 0

            circulating_supply_result = self.components.get_jetton_circulating_supply(jetton_address)
            circulating_supply = self._parse_amount(circulating_supply_result.get("circulating_supply")) if isinstance(circulating_supply_result, dict) else 0

            holder_distribution = []
            total_analyzed_balance = 0

            for holder in holders[:20]:
                if isinstance(holder, dict):
                    address = holder.get("address", "")
                    balance = self._parse_amount(holder.get("balance"))

                    if balance > 0:
                        percentage = (balance / total_supply * 100) if total_supply > 0 else 0
                        holder_distribution.append({
                            "address": address[:16] + "..." if len(address) > 16 else address,
                            "balance": round(balance, 2),
                            "percentage": round(percentage, 2)
                        })
                        total_analyzed_balance += balance

            concentration_index = 0
            if total_analyzed_balance > 0:
                for holder in holder_distribution:
                    share = holder["balance"] / total_analyzed_balance
                    concentration_index += share ** 2

            try:
                top_buys = self.components.get_jetton_top_buys(jetton_address)
                top_traders = self.components.get_jetton_top_traders(jetton_address)

                buy_count = len(top_buys) if isinstance(top_buys, list) else 0
                trader_count = len(top_traders) if isinstance(top_traders, list) else 0
            except:
                buy_count = 0
                trader_count = 0

            apy_score = 0

            if len(holder_distribution) >= 100:
                apy_score += 30
            elif len(holder_distribution) >= 50:
                apy_score += 20
            elif len(holder_distribution) >= 20:
                apy_score += 10

            if concentration_index < 0.2:
                apy_score += 25
            elif concentration_index < 0.4:
                apy_score += 20
            elif concentration_index < 0.6:
                apy_score += 15
            elif concentration_index < 0.8:
                apy_score += 10

            if buy_count > 50:
                apy_score += 25
            elif buy_count > 20:
                apy_score += 20
            elif buy_count > 10:
                apy_score += 15
            elif buy_count > 0:
                apy_score += 10

            if total_supply > 0:
                circulation_rate = circulating_supply / total_supply
                if circulation_rate > 0.8:
                    apy_score += 20
                elif circulation_rate > 0.5:
                    apy_score += 15
                elif circulation_rate > 0.2:
                    apy_score += 10

            if apy_score >= 80:
                apy_range = "15-30%"
                apy_potential = "High"
            elif apy_score >= 60:
                apy_range = "8-15%"
                apy_potential = "Medium"
            elif apy_score >= 40:
                apy_range = "3-8%"
                apy_potential = "Moderate"
            elif apy_score >= 20:
                apy_range = "1-3%"
                apy_potential = "Low"
            else:
                apy_range = "0-1%"
                apy_potential = "Minimal"

            return {
                "success": True,
                "jetton_address": jetton_address,
                "metadata": {
                    "name": metadata.get("name", "Unknown"),
                    "symbol": metadata.get("symbol", "Unknown"),
                    "description": metadata.get("description", "")
                } if isinstance(metadata, dict) else {},
                "supply_metrics": {
                    "total_supply": round(total_supply, 2),
                    "circulating_supply": round(circulating_supply, 2),
                    "circulation_rate_pct": round(circulating_supply / total_supply * 100, 2) if total_supply > 0 else 0,
                    "locked_supply": round(total_supply - circulating_supply, 2)
                },
                "holder_analysis": {
                    "total_holders": len(holders),
                    "top_holders_analyzed": len(holder_distribution),
                    "concentration_index": round(concentration_index, 3),
                    "distribution": "Decentralized" if concentration_index < 0.3 else 
                                   "Moderately centralized" if concentration_index < 0.6 else 
                                   "Highly centralized",
                    "top_holders": holder_distribution[:10]
                },
                "trading_activity": {
                    "recent_buyers": buy_count,
                    "active_traders": trader_count,
                    "activity_level": "High" if buy_count > 50 else 
                                     "Medium" if buy_count > 20 else 
                                     "Low" if buy_count > 0 else "None"
                },
                "apy_assessment": {
                    "score": min(apy_score, 100),
                    "estimated_apy_range": apy_range,
                    "potential": apy_potential,
                    "factors": {
                        "holder_distribution": len(holder_distribution),
                        "concentration_index": round(concentration_index, 3),
                        "trading_activity": buy_count,
                        "circulation_rate": round(circulating_supply / total_supply * 100, 2) if total_supply > 0 else 0
                    }
                },
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            print(f"APY calculation error: {e}")
            return {"success": False, "error": str(e), "jetton_address": jetton_address}

    def analyze_jetton(self, jetton_address: str) -> Dict[str, Any]:
        try:
            print(f"Comprehensive jetton analysis {jetton_address[:16]}...")

            apy_analysis = self.calculate_apy_breakdown(jetton_address)

            if not apy_analysis.get("success"):
                return apy_analysis

            try:
                metadata = self.components.get_jetton_metadata(jetton_address)
                symbol = "Unknown"
                if isinstance(metadata, dict):
                    symbol = metadata.get("symbol", "Unknown")

                asset_analysis = None
                if symbol != "Unknown":
                    try:
                        asset_analysis = self.analyze_asset(symbol)
                    except:
                        asset_analysis = None
            except:
                asset_analysis = None

            liquidity_analysis = None
            if symbol != "Unknown":
                try:
                    liquidity_analysis = self.get_liquidity_analysis(symbol)
                except:
                    liquidity_analysis = None

            health_score = 0

            apy_score = apy_analysis.get("apy_assessment", {}).get("score", 0)
            health_score += apy_score * 0.4

            if asset_analysis and asset_analysis.get("success"):
                asset_health = asset_analysis.get("health", {}).get("score", 0)
                health_score += asset_health * 0.3
            else:
                health_score += apy_score * 0.15

            if liquidity_analysis and liquidity_analysis.get("success"):
                liquidity_score = liquidity_analysis.get("depth_analysis", {}).get("score", 0)
                health_score += liquidity_score * 0.3
            else:
                holder_distribution = apy_analysis.get("holder_analysis", {}).get("distribution", "")
                if "Decentralized" in holder_distribution:
                    health_score += 25
                elif "Moderately" in holder_distribution:
                    health_score += 15
                elif "Highly" in holder_distribution:
                    health_score += 5

            health_score = min(health_score, 100)

            recommendations = []

            apy_potential = apy_analysis.get("apy_assessment", {}).get("potential", "Low")
            if apy_potential in ["High", "Medium"]:
                recommendations.append(f"APY potential: {apy_potential} - may be interesting for staking/liquidity")
            else:
                recommendations.append(f"APY potential: {apy_potential} - low expected yield")

            concentration = apy_analysis.get("holder_analysis", {}).get("concentration_index", 1)
            if concentration > 0.7:
                recommendations.append("High concentration among top holders - increased risk")
            elif concentration > 0.4:
                recommendations.append("Moderate concentration - standard risk")
            else:
                recommendations.append("Good distribution among holders - low concentration risk")

            if liquidity_analysis and liquidity_analysis.get("success"):
                liquidity_score = liquidity_analysis.get("depth_analysis", {}).get("score", 0)
                if liquidity_score < 40:
                    recommendations.append("Low liquidity - possible withdrawal issues")
                elif liquidity_score < 70:
                    recommendations.append("Moderate liquidity - consider for large trades")
                else:
                    recommendations.append("Good liquidity - low slippage risk")

            activity = apy_analysis.get("trading_activity", {}).get("activity_level", "None")
            if activity == "None":
                recommendations.append("No trading activity - token may be illiquid")
            elif activity == "Low":
                recommendations.append("Low trading activity - limited market")

            return {
                "success": True,
                "jetton_address": jetton_address,
                "overview": {
                    "name": apy_analysis.get("metadata", {}).get("name", "Unknown"),
                    "symbol": apy_analysis.get("metadata", {}).get("symbol", "Unknown"),
                    "total_supply": apy_analysis.get("supply_metrics", {}).get("total_supply", 0),
                    "circulating_supply": apy_analysis.get("supply_metrics", {}).get("circulating_supply", 0)
                },
                "health_analysis": {
                    "score": round(health_score, 1),
                    "level": "Excellent" if health_score >= 80 else 
                             "Good" if health_score >= 60 else 
                             "Fair" if health_score >= 40 else 
                             "Poor" if health_score >= 20 else "Critical",
                    "components": {
                        "apy_score": round(apy_score, 1),
                        "asset_health": round(asset_analysis.get("health", {}).get("score", 0), 1) if asset_analysis and asset_analysis.get("success") else "N/A",
                        "liquidity_score": round(liquidity_analysis.get("depth_analysis", {}).get("score", 0), 1) if liquidity_analysis and liquidity_analysis.get("success") else "N/A"
                    }
                },
                "detailed_analyses": {
                    "apy_breakdown": apy_analysis,
                    "asset_analysis": asset_analysis if asset_analysis and asset_analysis.get("success") else None,
                    "liquidity_analysis": liquidity_analysis if liquidity_analysis and liquidity_analysis.get("success") else None
                },
                "key_metrics": {
                    "holder_concentration": round(concentration, 3),
                    "trading_activity": activity,
                    "circulation_rate_pct": apy_analysis.get("supply_metrics", {}).get("circulation_rate_pct", 0),
                    "estimated_apy_range": apy_analysis.get("apy_assessment", {}).get("estimated_apy_range", "N/A")
                },
                "risk_assessment": {
                    "concentration_risk": "High" if concentration > 0.7 else "Medium" if concentration > 0.4 else "Low",
                    "liquidity_risk": "High" if liquidity_score < 40 else "Medium" if liquidity_score < 70 else "Low" if liquidity_analysis else "Unknown",
                    "market_risk": "High" if activity in ["None", "Low"] else "Medium" if activity == "Medium" else "Low"
                },
                "recommendations": recommendations,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            print(f"Jetton analysis error: {e}")
            return {"success": False, "error": str(e), "jetton_address": jetton_address}

    def _calculate_pool_tvl_simple(self, pool: Dict, prices_dict: Dict[str, float]) -> float:
        try:
            if not isinstance(pool, dict):
                return 0.0

            asset0 = pool.get("asset0", {})
            asset1 = pool.get("asset1", {})

            if not isinstance(asset0, dict) or not isinstance(asset1, dict):
                return 0.0

            token0_symbol = asset0.get("symbol", "")
            token1_symbol = asset1.get("symbol", "")

            if not token0_symbol or not token1_symbol:
                return 0.0

            price0 = prices_dict.get(token0_symbol, 0.0)
            price1 = prices_dict.get(token1_symbol, 0.0)

            if price0 <= 0 and price1 <= 0:
                return 0.0

            reserve0_raw = pool.get("reserve0") or pool.get("token0_reserve") or "0"
            reserve1_raw = pool.get("reserve1") or pool.get("token1_reserve") or "0"

            try:
                reserve0 = float(str(reserve0_raw).replace(',', ''))
                reserve1 = float(str(reserve1_raw).replace(',', ''))
            except:
                reserve0 = 0.0
                reserve1 = 0.0

            decimals0 = asset0.get("decimals")
            decimals1 = asset1.get("decimals")

            if decimals0 and isinstance(decimals0, (int, str)):
                try:
                    reserve0 = reserve0 / (10 ** int(decimals0))
                except:
                    pass

            if decimals1 and isinstance(decimals1, (int, str)):
                try:
                    reserve1 = reserve1 / (10 ** int(decimals1))
                except:
                    pass

            tvl = (reserve0 * price0) + (reserve1 * price1)
            return max(0.0, tvl)

        except Exception as e:
            return 0.0

    def _parse_amount(self, amount) -> float:
        try:
            if amount is None:
                return 0.0
            if isinstance(amount, (int, float)):
                return float(amount)
            if isinstance(amount, str):
                amount = str(amount).strip(' "\'\t\n\r')
                if not amount or amount.lower() in ['null', 'none', 'nan']:
                    return 0.0
                return float(amount)
            return 0.0
        except (ValueError, TypeError):
            return 0.0

    def _parse_with_decimals(self, amount_str: str, decimals: int = 9) -> float:
        try:
            amount = self._parse_amount(amount_str)
            if amount == 0:
                return 0.0
            return amount / (10 ** decimals)
        except:
            return 0.0

    def _get_cached_prices(self, force_refresh: bool = False) -> Dict[str, float]:
        current_time = datetime.now()

        if (force_refresh or self._prices_cache is None or 
            self._prices_cache_time is None or 
            (current_time - self._prices_cache_time).total_seconds() > 60):

            try:
                print("Updating price cache...")
                prices_result = self.components.get_prices()

                prices_list = []
                if isinstance(prices_result, list):
                    prices_list = prices_result
                elif isinstance(prices_result, dict) and "prices" in prices_result:
                    prices_list = prices_result["prices"]

                prices_dict = {}
                for item in prices_list:
                    if isinstance(item, dict):
                        symbol = item.get("symbol")
                        price = item.get("price")
                        if symbol and price is not None:
                            symbol_str = str(symbol).strip()
                            price_val = self._parse_amount(price)
                            if price_val > 0:
                                prices_dict[symbol_str] = price_val

                self._prices_cache = prices_dict
                self._prices_cache_time = current_time
                print(f"Price cache updated: {len(prices_dict)} assets")

            except Exception as e:
                print(f"Price cache update error: {e}")
                if self._prices_cache is None:
                    self._prices_cache = {}

        return self._prices_cache

    def _get_cached_pools(self, force_refresh: bool = False) -> List[Dict]:
        current_time = datetime.now()

        if (force_refresh or self._pools_cache is None or 
            self._pools_cache_time is None or 
            (current_time - self._pools_cache_time).total_seconds() > 120):

            try:
                print("Updating pools cache...")
                pools_result = self.components.get_pools()

                pools_list = []
                if isinstance(pools_result, list):
                    pools_list = pools_result
                elif isinstance(pools_result, dict) and "pool_list" in pools_result:
                    pools_list = pools_result["pool_list"]

                self._pools_cache = pools_list
                self._pools_cache_time = current_time
                print(f"Pools cache updated: {len(pools_list)} pools")

            except Exception as e:
                print(f"Pools cache update error: {e}")
                if self._pools_cache is None:
                    self._pools_cache = []

        return self._pools_cache

    def _get_token_symbol_from_asset(self, asset: Dict) -> str:
        try:
            if not isinstance(asset, dict):
                return "UNKNOWN"

            asset_type = asset.get("type", "")

            if asset_type == "native":
                metadata = asset.get("metadata", {})
                if metadata and isinstance(metadata, dict):
                    symbol = metadata.get("symbol")
                    if symbol:
                        return str(symbol)
                return "TON"

            elif asset_type == "jetton":
                metadata = asset.get("metadata", {})
                if metadata and isinstance(metadata, dict):
                    symbol = metadata.get("symbol")
                    if symbol:
                        return str(symbol)

                address = asset.get("address", "")
                if address and address.startswith("EQ"):
                    if address in self._address_to_symbol:
                        return self._address_to_symbol[address]

                    return f"JETTON_{address[:8]}"

            return "UNKNOWN"

        except Exception as e:
            print(f"Symbol retrieval error: {e}")
            return "UNKNOWN"

    def _get_token_decimals(self, asset: Dict) -> int:
        try:
            if not isinstance(asset, dict):
                return 9

            metadata = asset.get("metadata", {})
            if metadata and isinstance(metadata, dict):
                decimals = metadata.get("decimals")
                if decimals is not None:
                    return int(decimals)

            asset_type = asset.get("type", "")
            if asset_type == "native":
                return 9
            elif asset_type == "jetton":
                return 9

            return 9

        except:
            return 9

    def _calculate_pool_tvl(self, pool: Dict) -> float:
        try:
            if not isinstance(pool, dict):
                print(f"Pool is not dict: {type(pool)}")
                return 0.0

            assets = pool.get("assets", [])
            reserves = pool.get("reserves", [])

            if not isinstance(assets, list) or len(assets) < 2:
                print(f"Invalid assets format: {assets}")
                return 0.0

            if not isinstance(reserves, list) or len(reserves) < 2:
                print(f"Invalid reserves format: {reserves}")
                return 0.0

            asset0 = assets[0] if isinstance(assets[0], dict) else {}
            asset1 = assets[1] if isinstance(assets[1], dict) else {}

            symbol0 = self._get_token_symbol_from_asset(asset0)
            symbol1 = self._get_token_symbol_from_asset(asset1)

            decimals0 = self._get_token_decimals(asset0)
            decimals1 = self._get_token_decimals(asset1)

            reserve0_raw = reserves[0]
            reserve1_raw = reserves[1]

            reserve0 = self._parse_with_decimals(reserve0_raw, decimals0)
            reserve1 = self._parse_with_decimals(reserve1_raw, decimals1)

            prices = self._get_cached_prices()
            price0 = prices.get(symbol0, 0.0)
            price1 = prices.get(symbol1, 0.0)

            tvl = (reserve0 * price0) + (reserve1 * price1)

            if "debug_printed" not in pool:
                pool["debug_printed"] = True
                print(f"\nPOOL DEBUG {pool.get('address', '')[:16]}...:")
                print(f"   Tokens: {symbol0}/{symbol1}")
                print(f"   Reserves: {reserve0_raw} → {reserve0:.6f} {symbol0}")
                print(f"           {reserve1_raw} → {reserve1:.6f} {symbol1}")
                print(f"   Decimals: {decimals0}/{decimals1}")
                print(f"   Prices: ${price0}/{price1}")
                print(f"   TVL: ${tvl:.2f}")

            return max(0.0, tvl)

        except Exception as e:
            print(f"TVL v2 calculation error: {e}")
            import traceback
            traceback.print_exc()
            return 0.0

    def analyze_pool(self, pool_address: str) -> Dict[str, Any]:
        try:
            print(f"Analyzing pool v2 {pool_address[:16]}...")

            pools = self._get_cached_pools()
            target_pool = None

            for pool in pools:
                if isinstance(pool, dict) and pool.get("address") == pool_address:
                    target_pool = pool
                    break

            if not target_pool:
                return {
                    "success": False,
                    "error": "Pool not found",
                    "pool_address": pool_address
                }

            assets = target_pool.get("assets", [])
            reserves = target_pool.get("reserves", [])

            if len(assets) < 2 or len(reserves) < 2:
                return {
                    "success": False,
                    "error": "Invalid pool data format",
                    "pool_address": pool_address
                }

            asset0 = assets[0] if isinstance(assets[0], dict) else {}
            asset1 = assets[1] if isinstance(assets[1], dict) else {}

            symbol0 = self._get_token_symbol_from_asset(asset0)
            symbol1 = self._get_token_symbol_from_asset(asset1)
            decimals0 = self._get_token_decimals(asset0)
            decimals1 = self._get_token_decimals(asset1)

            reserve0 = self._parse_with_decimals(reserves[0], decimals0)
            reserve1 = self._parse_with_decimals(reserves[1], decimals1)

            prices = self._get_cached_prices()
            price0 = prices.get(symbol0, 0.0)
            price1 = prices.get(symbol1, 0.0)

            tvl_usd = (reserve0 * price0) + (reserve1 * price1)

            if reserve0 > 0:
                price_ratio = reserve1 / reserve0
                token0_per_token1 = price_ratio
                token1_per_token0 = 1 / price_ratio if price_ratio > 0 else 0
            else:
                price_ratio = 0
                token0_per_token1 = 0
                token1_per_token0 = 0

            metadata0 = asset0.get("metadata", {}) if isinstance(asset0.get("metadata"), dict) else {}
            metadata1 = asset1.get("metadata", {}) if isinstance(asset1.get("metadata"), dict) else {}

            return {
                "success": True,
                "pool_address": pool_address,
                "tokens": {
                    "token0": {
                        "symbol": symbol0,
                        "name": metadata0.get("name", symbol0),
                        "type": asset0.get("type", "unknown"),
                        "address": asset0.get("address", ""),
                        "reserve": round(reserve0, 6),
                        "reserve_raw": reserves[0],
                        "decimals": decimals0,
                        "price_usd": round(price0, 6),
                        "value_usd": round(reserve0 * price0, 2)
                    },
                    "token1": {
                        "symbol": symbol1,
                        "name": metadata1.get("name", symbol1),
                        "type": asset1.get("type", "unknown"),
                        "address": asset1.get("address", ""),
                        "reserve": round(reserve1, 6),
                        "reserve_raw": reserves[1],
                        "decimals": decimals1,
                        "price_usd": round(price1, 6),
                        "value_usd": round(reserve1 * price1, 2)
                    }
                },
                "metrics": {
                    "tvl_usd": round(tvl_usd, 2),
                    "total_supply": target_pool.get("totalSupply", "0"),
                    "trade_fee_percent": target_pool.get("tradeFee", "0.25"),
                    "pool_type": target_pool.get("type", "volatile"),
                    "price_ratio": round(price_ratio, 6),
                    "token0_per_token1": round(token0_per_token1, 6),
                    "token1_per_token0": round(token1_per_token0, 6),
                    "liquidity_depth_usd": round(min(reserve0 * price0, reserve1 * price1) * 2, 2)
                },
                "raw_data_sample": {
                    "reserves": reserves[:2],
                    "assets_types": [asset0.get("type"), asset1.get("type")]
                },
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            print(f"Pool v2 analysis error: {e}")
            return {
                "success": False,
                "error": str(e),
                "pool_address": pool_address
            }

    def get_market_overview(self) -> Dict[str, Any]:
        try:
            print("Getting DeDust v2 market overview...")

            pools = self._get_cached_pools(force_refresh=True)
            prices = self._get_cached_prices(force_refresh=True)

            print(f"Pools received: {len(pools)}")
            print(f"Prices received: {len(prices)}")

            if not pools:
                return {
                    "success": False,
                    "error": "Failed to get pool data"
                }

            total_pools = len(pools)
            max_to_analyze = min(50, total_pools)

            print(f"Analyzing {max_to_analyze} pools of {total_pools}...")

            active_pools = 0
            total_tvl_usd = 0.0
            pool_tvls = []

            for i, pool in enumerate(pools[:max_to_analyze]):
                if not isinstance(pool, dict):
                    continue

                try:
                    reserves = pool.get("reserves", [])
                    if len(reserves) >= 2:
                        reserve0 = self._parse_amount(reserves[0])
                        reserve1 = self._parse_amount(reserves[1])

                        if reserve0 > 0 and reserve1 > 0:
                            active_pools += 1

                            pool_tvl = self._calculate_pool_tvl(pool)
                            total_tvl_usd += pool_tvl
                            pool_tvls.append(pool_tvl)

                            if i < 3:
                                assets = pool.get("assets", [])
                                if len(assets) >= 2:
                                    symbol0 = self._get_token_symbol_from_asset(assets[0])
                                    symbol1 = self._get_token_symbol_from_asset(assets[1])
                                    print(f"   Pool {i+1}: {symbol0}/{symbol1} - TVL: ${pool_tvl:.2f}")

                except Exception as e:
                    continue

            disabled_pools = total_pools - active_pools
            active_pool_ratio = active_pools / total_pools if total_pools > 0 else 0

            try:
                coingecko_pairs = self.components.get_coingecko_pairs()
                cg_pair_count = len(coingecko_pairs) if isinstance(coingecko_pairs, list) else 0
            except:
                cg_pair_count = 0

            avg_tvl = total_tvl_usd / len(pool_tvls) if pool_tvls else 0

            estimated_total_tvl = avg_tvl * total_pools if avg_tvl > 0 else total_tvl_usd

            print(f"\nTOTAL:")
            print(f"   • Total pools: {total_pools}")
            print(f"   • Active pools: {active_pools}")
            print(f"   • TVL (analyzed): ${total_tvl_usd:,.2f}")
            print(f"   • TVL (estimated all): ${estimated_total_tvl:,.2f}")

            return {
                "success": True,
                "market_overview": {
                    "total_pools": total_pools,
                    "active_pools": active_pools,
                    "disabled_pools": disabled_pools,
                    "active_pool_ratio_pct": round(active_pool_ratio * 100, 1),
                    "analyzed_pools": max_to_analyze,
                    "total_tvl_usd": round(total_tvl_usd, 2),
                    "estimated_total_tvl_usd": round(estimated_total_tvl, 2),
                    "avg_tvl_per_pool": round(avg_tvl, 2),
                    "tracked_assets": len(prices),
                    "coingecko_integrated_pairs": cg_pair_count
                },
                "analysis_details": {
                    "pools_analyzed": max_to_analyze,
                    "pools_with_tvl": len(pool_tvls),
                    "min_tvl": round(min(pool_tvls), 2) if pool_tvls else 0,
                    "max_tvl": round(max(pool_tvls), 2) if pool_tvls else 0
                },
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            print(f"Market overview v2 error: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}

    def get_analyze_pool_skill(context: Dict[str, Any]) -> Dict[str, Any]:
        client = context.get('dedust_client')
        if not client or not hasattr(client, 'skills'):
            return {"success": False, "error": "Dedust client not available"}

        pool_address = context.get('pool_address')
        if not pool_address:
            return {"success": False, "error": "Pool address is required"}

        return client.skills.analyze_pool(pool_address)

    def get_analyze_asset_skill(context: Dict[str, Any]) -> Dict[str, Any]:
        client = context.get('dedust_client')
        if not client or not hasattr(client, 'skills'):
            return {"success": False, "error": "Dedust client not available"}

        symbol = context.get('symbol')
        if not symbol:
            return {"success": False, "error": "Symbol is required"}

        return client.skills.analyze_asset(symbol)

    def get_find_arbitrage_skill(context: Dict[str, Any]) -> Dict[str, Any]:
        client = context.get('dedust_client')
        if not client or not hasattr(client, 'skills'):
            return {"success": False, "error": "Dedust client not available"}

        min_profit_usd = context.get('min_profit_usd', 10.0)
        min_tvl = context.get('min_tvl', 1000.0)
        max_price_diff = context.get('max_price_diff', 0.10)

        return client.skills.find_arbitrage_opportunities(
            min_profit_usd, min_tvl, max_price_diff
        )

    def get_compare_pools_skill(context: Dict[str, Any]) -> Dict[str, Any]:
        client = context.get('dedust_client')
        if not client or not hasattr(client, 'skills'):
            return {"success": False, "error": "Dedust client not available"}

        pool_addresses = context.get('pool_addresses', [])
        if not pool_addresses or len(pool_addresses) < 2:
            return {"success": False, "error": "At least 2 pool addresses required"}

        return client.skills.compare_pools(pool_addresses)

    def get_analyze_liquidity_skill(context: Dict[str, Any]) -> Dict[str, Any]:
        client = context.get('dedust_client')
        if not client or not hasattr(client, 'skills'):
            return {"success": False, "error": "Dedust client not available"}

        token_address = context.get('token_address')
        if not token_address:
            return {"success": False, "error": "Token address is required"}

        return client.skills.get_liquidity_analysis(token_address)

    def get_top_performing_pools_skill(context: Dict[str, Any]) -> Dict[str, Any]:
        client = context.get('dedust_client')
        if not client or not hasattr(client, 'skills'):
            return {"success": False, "error": "Dedust client not available"}

        period = context.get('period', '24h')
        limit = context.get('limit', 10)

        return client.skills.get_top_performing_pools(period, limit)

    def get_generate_pool_report_skill(context: Dict[str, Any]) -> Dict[str, Any]:
        client = context.get('dedust_client')
        if not client or not hasattr(client, 'skills'):
            return {"success": False, "error": "Dedust client not available"}

        pool_address = context.get('pool_address')
        if not pool_address:
            return {"success": False, "error": "Pool address is required"}

        result = client.skills.generate_pool_report(pool_address)
        return {"success": True, "report": result}

    def get_calculate_impermanent_loss_skill(context: Dict[str, Any]) -> Dict[str, Any]:
        client = context.get('dedust_client')
        if not client or not hasattr(client, 'skills'):
            return {"success": False, "error": "Dedust client not available"}

        pool_address = context.get('pool_address')
        token_a_change = context.get('token_a_change', 0.0)
        token_b_change = context.get('token_b_change', 0.0)

        if not pool_address:
            return {"success": False, "error": "Pool address is required"}

        return client.skills.calculate_impermanent_loss(
            pool_address, token_a_change, token_b_change
        )

    def get_analyze_wallet_portfolio_skill(context: Dict[str, Any]) -> Dict[str, Any]:
        client = context.get('dedust_client')
        if not client or not hasattr(client, 'skills'):
            return {"success": False, "error": "Dedust client not available"}

        wallet_address = context.get('wallet_address')
        if not wallet_address:
            return {"success": False, "error": "Wallet address is required"}

        return client.skills.analyze_wallet_portfolio(wallet_address)

    def get_swap_recommendations_skill(context: Dict[str, Any]) -> Dict[str, Any]:
        client = context.get('dedust_client')
        if not client or not hasattr(client, 'skills'):
            return {"success": False, "error": "Dedust client not available"}

        offer_token = context.get('offer_token')
        ask_token = context.get('ask_token')
        amount = context.get('amount', 1.0)

        if not offer_token or not ask_token:
            return {"success": False, "error": "Offer token and ask token are required"}

        if amount <= 0:
            return {"success": False, "error": "Amount must be positive"}

        return client.skills.get_swap_recommendations(
            offer_token, ask_token, amount
        )

    def get_calculate_apy_breakdown_skill(context: Dict[str, Any]) -> Dict[str, Any]:
        client = context.get('dedust_client')
        if not client or not hasattr(client, 'skills'):
            return {"success": False, "error": "Dedust client not available"}

        jetton_address = context.get('jetton_address')
        if not jetton_address:
            return {"success": False, "error": "Jetton address is required"}

        return client.skills.calculate_apy_breakdown(jetton_address)

    def get_analyze_jetton_skill(context: Dict[str, Any]) -> Dict[str, Any]:
        client = context.get('dedust_client')
        if not client or not hasattr(client, 'skills'):
            return {"success": False, "error": "Dedust client not available"}

        jetton_address = context.get('jetton_address')
        if not jetton_address:
            return {"success": False, "error": "Jetton address is required"}

        return client.skills.analyze_jetton(jetton_address)

    def get_market_overview_skill(context: Dict[str, Any]) -> Dict[str, Any]:
        client = context.get('dedust_client')
        if not client or not hasattr(client, 'skills'):
            return {"success": False, "error": "Dedust client not available"}

        return client.skills.get_market_overview()
