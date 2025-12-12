import numpy as np
from datetime import datetime
from typing import Dict, List, Any

class StonFiSkills:
    def __init__(self, components):
        self.components = components

    def _parse_amount(self, amount_str: str) -> float:
        try:
            return float(amount_str)
        except:
            return 0.0

    def analyze_pool(self, pool_address: str) -> Dict[str, Any]:
        try:
            pool_data = self.components.get_pool(pool_address)

            if "pool" not in pool_data:
                return {"success": False, "error": "Invalid pool data"}

            pool = pool_data["pool"]

            reserve0 = self._parse_amount(pool.get("reserve0", "0"))
            reserve1 = self._parse_amount(pool.get("reserve1", "0"))
            volume_24h = self._parse_amount(pool.get("volume_24h_usd", "0"))
            lp_total_supply = self._parse_amount(pool.get("lp_total_supply", "0"))
            lp_price = self._parse_amount(pool.get("lp_price_usd", "0"))

            tvl_usd = reserve0 + reserve1
            if lp_total_supply > 0:
                lp_value = tvl_usd / lp_total_supply
            else:
                lp_value = 0

            lp_fee = self._parse_amount(pool.get("lp_fee", "0"))
            protocol_fee = self._parse_amount(pool.get("protocol_fee", "0"))
            ref_fee = self._parse_amount(pool.get("ref_fee", "0"))
            total_fee = lp_fee + protocol_fee + ref_fee

            apy_1d = self._parse_amount(pool.get("apy_1d", "0"))
            apy_7d = self._parse_amount(pool.get("apy_7d", "0"))
            apy_30d = self._parse_amount(pool.get("apy_30d", "0"))

            token0 = pool.get("token0_address", "")
            token1 = pool.get("token1_address", "")

            price_ratio = reserve1 / reserve0 if reserve0 > 0 else 0

            health_score = 0
            if tvl_usd > 10000:
                health_score += 30

            if volume_24h > tvl_usd * 0.1:
                health_score += 30

            if apy_30d > 0.05:
                health_score += 20

            if not pool.get("deprecated", False):
                health_score += 20

            return {
                "success": True,
                "pool_address": pool_address,
                "tokens": [token0, token1],
                "tvl_usd": round(tvl_usd, 2),
                "volume_24h_usd": round(volume_24h, 2),
                "liquidity": {
                    "token0": round(reserve0, 2),
                    "token1": round(reserve1, 2),
                    "total": round(tvl_usd, 2)
                },
                "fees": {
                    "lp_fee": lp_fee,
                    "protocol_fee": protocol_fee,
                    "ref_fee": ref_fee,
                    "total_fee": total_fee
                },
                "apy": {
                    "1d": round(apy_1d * 100, 2),
                    "7d": round(apy_7d * 100, 2),
                    "30d": round(apy_30d * 100, 2)
                },
                "lp_metrics": {
                    "total_supply": lp_total_supply,
                    "price_usd": round(lp_price, 4),
                    "value": round(lp_value, 4)
                },
                "health_score": min(health_score, 100),
                "deprecated": pool.get("deprecated", False),
                "price_ratio": round(price_ratio, 6),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def analyze_asset(self, asset_address: str) -> Dict[str, Any]:
        try:
            asset_data = self.components.get_asset(asset_address)

            if "asset" not in asset_data:
                return {"success": False, "error": "Invalid asset data"}

            asset = asset_data["asset"]

            dex_price = self._parse_amount(asset.get("dex_price_usd", "0"))
            third_party_price = self._parse_amount(asset.get("third_party_price_usd", "0"))
            dex_usd_price = self._parse_amount(asset.get("dex_usd_price", "0"))
            third_party_usd_price = self._parse_amount(asset.get("third_party_usd_price", "0"))

            if dex_price > 0:
                price = dex_price
                price_source = "dex"
            elif third_party_price > 0:
                price = third_party_price
                price_source = "third_party"
            elif dex_usd_price > 0:
                price = dex_usd_price
                price_source = "dex_usd"
            elif third_party_usd_price > 0:
                price = third_party_usd_price
                price_source = "third_party_usd"
            else:
                price = 0
                price_source = "unknown"

            balance = self._parse_amount(asset.get("balance", "0"))

            decimals = asset.get("decimals", 9)
            scale = self._parse_amount(asset.get("scale", "1"))
            total_supply = balance * (10 ** (decimals - 9))

            if scale > 0:
                total_supply *= scale

            market_cap = price * total_supply

            health_score = 0

            if price > 0:
                health_score += 20

            if not asset.get("blacklisted", False):
                health_score += 20

            if not asset.get("deprecated", False):
                health_score += 20

            if asset.get("community", False):
                health_score += 10

            if asset.get("taxable", False):
                health_score += 10

            popularity = asset.get("popularity_index", 0)
            health_score += min(popularity, 20)

            return {
                "success": True,
                "asset_address": asset_address,
                "name": asset.get("display_name", "Unknown"),
                "symbol": asset.get("symbol", "UNKNOWN"),
                "kind": asset.get("kind", "Unknown"),
                "price": {
                    "value": round(price, 6),
                    "source": price_source,
                    "dex": round(dex_price, 6),
                    "third_party": round(third_party_price, 6)
                },
                "metrics": {
                    "decimals": decimals,
                    "balance": balance,
                    "total_supply": total_supply,
                    "market_cap": round(market_cap, 2),
                    "popularity": popularity
                },
                "flags": {
                    "blacklisted": asset.get("blacklisted", False),
                    "community": asset.get("community", False),
                    "deprecated": asset.get("deprecated", False),
                    "taxable": asset.get("taxable", False),
                    "default_symbol": asset.get("default_symbol", False)
                },
                "health_score": min(health_score, 100),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def find_arbitrage_opportunities(self, min_profit_usd: float = 10.0, 
                               min_tvl: float = 1000.0, 
                               max_price_diff: float = 0.10) -> List[Dict[str, Any]]:
        try:
            pools_data = self.components.get_pools()

            if "pool_list" not in pools_data:
                return []

            opportunities = []
            pools = pools_data["pool_list"]

            valid_pools = []
            for pool in pools:
                try:
                    reserve0 = self._parse_amount(pool.get("reserve0", "0"))
                    reserve1 = self._parse_amount(pool.get("reserve1", "0"))
                    tvl = reserve0 + reserve1

                    if (tvl >= min_tvl and 
                        reserve0 > 0 and 
                        reserve1 > 0 and 
                        not pool.get("deprecated", False)):

                        valid_pools.append({
                            "address": pool.get("address"),
                            "token0": pool.get("token0_address"),
                            "token1": pool.get("token1_address"),
                            "reserve0": reserve0,
                            "reserve1": reserve1,
                            "tvl": tvl,
                            "volume_24h": self._parse_amount(pool.get("volume_24h_usd", "0"))
                        })

                except:
                    continue

            print(f"   ℹ️  Valid pools for analysis: {len(valid_pools)}/{len(pools)}")

            token_pools = {}
            for pool in valid_pools:
                token0 = pool.get("token0")
                token1 = pool.get("token1")

                if token0 and token1:
                    pair = tuple(sorted([token0, token1]))
                    if pair not in token_pools:
                        token_pools[pair] = []
                    token_pools[pair].append(pool)

            for pair, pool_list in token_pools.items():
                if len(pool_list) >= 2:
                    prices = []
                    for pool in pool_list:
                        reserve0 = pool.get("reserve0", 0)
                        reserve1 = pool.get("reserve1", 0)

                        if reserve0 > 0 and reserve1 > 0:
                            price = reserve1 / reserve0

                            if 0.000001 < price < 1000000:
                                prices.append({
                                    "pool": pool.get("address"),
                                    "price": price,
                                    "reserve0": reserve0,
                                    "reserve1": reserve1,
                                    "tvl": pool.get("tvl", 0),
                                    "volume_24h": pool.get("volume_24h", 0)
                                })

                    if len(prices) >= 2:
                        min_price = min(p['price'] for p in prices)
                        max_price = max(p['price'] for p in prices)

                        if min_price > 0:
                            price_diff_pct = (max_price - min_price) / min_price

                            if 0.01 <= price_diff_pct <= max_price_diff:
                                min_pool = next(p for p in prices if p['price'] == min_price)
                                max_pool = next(p for p in prices if p['price'] == max_price)

                                trade_size_token0 = min(
                                    min_pool['reserve0'] * 0.01,
                                    max_pool['reserve1'] / max_price * 0.01
                                )

                                if trade_size_token0 > 1:
                                    estimated_profit = trade_size_token0 * (max_price - min_price)

                                    fee_percentage = 0.003 * 2
                                    fee_amount = trade_size_token0 * max_price * fee_percentage
                                    net_profit = estimated_profit - fee_amount

                                    if net_profit >= min_profit_usd:
                                        try:
                                            token0_info = self.components.get_asset(pair[0])
                                            token1_info = self.components.get_asset(pair[1])

                                            symbol0 = token0_info.get("asset", {}).get("symbol", pair[0][:8])
                                            symbol1 = token1_info.get("asset", {}).get("symbol", pair[1][:8])
                                        except:
                                            symbol0 = pair[0][:8]
                                            symbol1 = pair[1][:8]

                                        opportunities.append({
                                            "token_pair": list(pair),
                                            "symbol_pair": f"{symbol0}/{symbol1}",
                                            "price_difference_pct": round(price_diff_pct * 100, 2),
                                            "estimated_profit_usd": round(estimated_profit, 2),
                                            "net_profit_usd": round(net_profit, 2),
                                            "trade_size_estimate": round(trade_size_token0, 2),
                                            "trade_size_usd": round(trade_size_token0 * ((min_price + max_price) / 2), 2),
                                            "cheap_pool": min_pool['pool'],
                                            "cheap_price": round(min_price, 6),
                                            "expensive_pool": max_pool['pool'],
                                            "expensive_price": round(max_price, 6),
                                            "cheap_pool_tvl": round(min_pool['tvl'], 2),
                                            "expensive_pool_tvl": round(max_pool['tvl'], 2),
                                            "timestamp": datetime.now().isoformat()
                                        })

            opportunities.sort(key=lambda x: x['net_profit_usd'], reverse=True)

            return opportunities

        except Exception as e:
            print(f"Error finding arbitrage opportunities: {e}")
            return []

    def compare_pools(self, pool_addresses: List[str]) -> Dict[str, Any]:
        try:
            comparison = {}

            for address in pool_addresses:
                analysis = self.analyze_pool(address)
                if analysis["success"]:
                    comparison[address] = analysis
                else:
                    comparison[address] = {"success": False, "error": analysis.get("error", "Unknown error")}

            successful = {k: v for k, v in comparison.items() if v.get("success", False)}

            if len(successful) >= 2:
                best_by_tvl = max(successful.items(), key=lambda x: x[1].get("tvl_usd", 0))
                best_by_volume = max(successful.items(), key=lambda x: x[1].get("volume_24h_usd", 0))
                best_by_apy = max(successful.items(), key=lambda x: x[1].get("apy", {}).get("30d", 0))
                best_by_health = max(successful.items(), key=lambda x: x[1].get("health_score", 0))

                comparison["summary"] = {
                    "total_pools": len(pool_addresses),
                    "successful_analyses": len(successful),
                    "best_by_tvl": best_by_tvl[0],
                    "best_by_volume": best_by_volume[0],
                    "best_by_apy": best_by_apy[0],
                    "best_by_health": best_by_health[0],
                    "average_tvl": sum(v.get("tvl_usd", 0) for v in successful.values()) / len(successful),
                    "average_apy": sum(v.get("apy", {}).get("30d", 0) for v in successful.values()) / len(successful)
                }

            return comparison

        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_liquidity_analysis(self, token_address: str) -> Dict[str, Any]:
        try:
            pools_data = self.components.get_pools()

            if "pool_list" not in pools_data:
                return {"success": False, "error": "No pools data"}

            token_pools = []
            total_liquidity = 0

            for pool in pools_data["pool_list"]:
                token0 = pool.get("token0_address")
                token1 = pool.get("token1_address")

                if token0 == token_address or token1 == token_address:
                    reserve0 = self._parse_amount(pool.get("reserve0", "0"))
                    reserve1 = self._parse_amount(pool.get("reserve1", "0"))
                    tvl = reserve0 + reserve1

                    token_pools.append({
                        "pool_address": pool.get("address"),
                        "paired_token": token1 if token0 == token_address else token0,
                        "token_reserve": reserve0 if token0 == token_address else reserve1,
                        "paired_reserve": reserve1 if token0 == token_address else reserve0,
                        "tvl": tvl,
                        "price": paired_reserve / token_reserve if token_reserve > 0 else 0
                    })

                    total_liquidity += tvl

            concentration = 0
            if total_liquidity > 0:
                for pool in token_pools:
                    share = pool["tvl"] / total_liquidity
                    concentration += share ** 2

            token_pools.sort(key=lambda x: x["tvl"], reverse=True)
            top_pools = token_pools[:5] if len(token_pools) > 5 else token_pools

            depth_score = 0
            if len(token_pools) >= 3:
                depth_score += 30
            if total_liquidity > 100000:
                depth_score += 40
            if concentration < 0.5:
                depth_score += 30

            return {
                "success": True,
                "token_address": token_address,
                "total_pools": len(token_pools),
                "total_liquidity_usd": round(total_liquidity, 2),
                "concentration_index": round(concentration, 3),
                "depth_score": min(depth_score, 100),
                "top_pools": top_pools,
                "pool_count_by_size": {
                    "large": len([p for p in token_pools if p["tvl"] > 100000]),
                    "medium": len([p for p in token_pools if 10000 <= p["tvl"] <= 100000]),
                    "small": len([p for p in token_pools if p["tvl"] < 10000])
                },
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_top_performing_pools(self, period: str = "24h", limit: int = 10) -> List[Dict[str, Any]]:
        try:
            pools_data = self.components.get_pools()

            if "pool_list" not in pools_data:
                return []

            pools = pools_data["pool_list"]

            scored_pools = []

            for pool in pools:
                volume = self._parse_amount(pool.get("volume_24h_usd", "0"))
                tvl = self._parse_amount(pool.get("reserve0", "0")) + self._parse_amount(pool.get("reserve1", "0"))
                apy_30d = self._parse_amount(pool.get("apy_30d", "0"))

                if tvl > 0:
                    volume_ratio = volume / tvl
                    performance_score = (volume_ratio * 50) + (apy_30d * 5000)

                    scored_pools.append({
                        "pool_address": pool.get("address"),
                        "tokens": [pool.get("token0_address"), pool.get("token1_address")],
                        "tvl": round(tvl, 2),
                        "volume_24h": round(volume, 2),
                        "volume_ratio": round(volume_ratio, 4),
                        "apy_30d": round(apy_30d * 100, 2),
                        "performance_score": round(performance_score, 2),
                        "deprecated": pool.get("deprecated", False)
                    })

            scored_pools.sort(key=lambda x: x["performance_score"], reverse=True)

            filtered_pools = [p for p in scored_pools if not p["deprecated"]]
            return filtered_pools[:limit]

        except Exception as e:
            print(f"Error getting top pools: {e}")
            return []

    def generate_pool_report(self, pool_address: str) -> str:
        try:
            analysis = self.analyze_pool(pool_address)

            if not analysis["success"]:
                return f"Error: {analysis.get('error', 'Unknown error')}"

            pool = analysis

            farms_data = self.components.get_farms_by_pool(pool_address)
            farms = farms_data.get("farm_list", [])

            report = f"""
{'='*80}
STON.FI POOL ANALYSIS REPORT
{'='*80}

POOL: {pool_address}
REPORT TIME: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
DATA SOURCE: STON.fi API

{'='*80}
OVERVIEW
{'='*80}
Tokens: {pool['tokens'][0]} / {pool['tokens'][1]}
TVL: ${pool['tvl_usd']:,.2f}
24h Volume: ${pool['volume_24h_usd']:,.2f}
Volume/TVL Ratio: {pool['volume_24h_usd']/pool['tvl_usd']*100 if pool['tvl_usd'] > 0 else 0:.2f}%
Health Score: {pool['health_score']}/100
Deprecated: {'Yes' if pool['deprecated'] else 'No'}

{'='*80}
LIQUIDITY DETAILS
{'='*80}
Token 0 Reserve: ${pool['liquidity']['token0']:,.2f}
Token 1 Reserve: ${pool['liquidity']['token1']:,.2f}
Total Liquidity: ${pool['liquidity']['total']:,.2f}
Price Ratio: {pool['price_ratio']:.6f}

{'='*80}
FEE STRUCTURE
{'='*80}
LP Fee: {pool['fees']['lp_fee']:.4f}%
Protocol Fee: {pool['fees']['protocol_fee']:.4f}%
Referral Fee: {pool['fees']['ref_fee']:.4f}%
Total Fee: {pool['fees']['total_fee']:.4f}%

{'='*80}
YIELD METRICS
{'='*80}
APY (24h): {pool['apy']['1d']:.2f}%
APY (7d): {pool['apy']['7d']:.2f}%
APY (30d): {pool['apy']['30d']:.2f}%

{'='*80}
LP TOKEN METRICS
{'='*80}
Total Supply: {pool['lp_metrics']['total_supply']:,.2f}
Price: ${pool['lp_metrics']['price_usd']:.6f}
Value per LP: ${pool['lp_metrics']['value']:.6f}
            """

            if farms:
                report += f"""
{'='*80}
FARMS ({len(farms)})
{'='*80}
"""
                for i, farm in enumerate(farms[:5], 1):
                    status = farm.get("status", "Unknown")
                    apy = farm.get("apy", "0")
                    report += f"{i}. Status: {status}, APY: {apy}\n"

            report += f"""
{'='*80}
RECOMMENDATIONS
{'='*80}
"""

            recommendations = []

            if pool['health_score'] < 50:
                recommendations.append("Low health score - consider higher quality pools")

            if pool['deprecated']:
                recommendations.append("Pool is deprecated - avoid adding liquidity")

            if pool['tvl_usd'] < 10000:
                recommendations.append("Low TVL - higher risk of slippage")

            if pool['apy']['30d'] > 20:
                recommendations.append("High APY - attractive for yield farming")

            if pool['volume_24h_usd'] / pool['tvl_usd'] > 0.5:
                recommendations.append("High volume/TVL ratio - good fee generation")

            if recommendations:
                for i, rec in enumerate(recommendations, 1):
                    report += f"{i}. {rec}\n"
            else:
                report += "No specific recommendations\n"

            report += f"""
{'='*80}
RISK FACTORS
{'='*80}
1. Impermanent loss risk
2. Smart contract risk
3. Market volatility risk
4. Liquidity provider risk
5. Protocol upgrade risk

{'='*80}
DISCLAIMER
{'='*80}
This report is for informational purposes only.
Not financial advice. Always do your own research.
Past performance is not indicative of future results.
{'='*80}
"""

            return report

        except Exception as e:
            return f"Error generating report: {str(e)}"

    def calculate_impermanent_loss(self, pool_address: str, token_a_change: float, token_b_change: float) -> Dict[str, Any]:
        try:
            pool_data = self.components.get_pool(pool_address)

            if "pool" not in pool_data:
                return {"success": False, "error": "Invalid pool data"}

            pool = pool_data["pool"]

            reserve0 = self._parse_amount(pool.get("reserve0", "1"))
            reserve1 = self._parse_amount(pool.get("reserve1", "1"))

            current_price = reserve1 / reserve0 if reserve0 > 0 else 1

            new_reserve0 = reserve0 * (1 + token_a_change)
            new_reserve1 = reserve1 * (1 + token_b_change)
            new_price = new_reserve1 / new_reserve0 if new_reserve0 > 0 else current_price

            price_ratio_change = new_price / current_price if current_price > 0 else 1

            if price_ratio_change > 0:
                impermanent_loss = (2 * np.sqrt(price_ratio_change) / (1 + price_ratio_change) - 1) * 100
            else:
                impermanent_loss = 0

            return {
                "success": True,
                "pool_address": pool_address,
                "current_price": round(current_price, 6),
                "new_price": round(new_price, 6),
                "price_change_pct": round((new_price / current_price - 1) * 100, 2),
                "impermanent_loss_pct": round(impermanent_loss, 2),
                "token_changes": {
                    "token_a": round(token_a_change * 100, 1),
                    "token_b": round(token_b_change * 100, 1)
                },
                "reserves": {
                    "current": [round(reserve0, 2), round(reserve1, 2)],
                    "new": [round(new_reserve0, 2), round(new_reserve1, 2)]
                },
                "interpretation": "Negative value means loss relative to holding" if impermanent_loss < 0 else "Positive value means gain"
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def analyze_wallet_portfolio(self, wallet_address: str) -> Dict[str, Any]:
        try:
            assets_data = self.components.get_wallet_assets(wallet_address)
            pools_data = self.components.get_wallet_pools(wallet_address, dex_v2=True)
            farms_data = self.components.get_wallet_farms(wallet_address, dex_v2=True, only_active=False)

            assets = assets_data.get("asset_list", [])
            pools = pools_data.get("pool_list", [])
            farms = farms_data.get("farm_list", [])

            asset_values = []
            total_value = 0

            for asset in assets:
                balance = self._parse_amount(asset.get("balance", "0"))
                dex_price = self._parse_amount(asset.get("dex_price_usd", "0"))

                if dex_price > 0 and balance > 0:
                    value = balance * dex_price
                    asset_values.append({
                        "address": asset.get("contract_address"),
                        "symbol": asset.get("symbol", "UNKNOWN"),
                        "balance": balance,
                        "price": dex_price,
                        "value": value
                    })
                    total_value += value

            lp_positions = []
            lp_value = 0

            for pool in pools:
                lp_balance = self._parse_amount(pool.get("lp_balance", "0"))
                lp_price = self._parse_amount(pool.get("lp_price_usd", "0"))

                if lp_price > 0 and lp_balance > 0:
                    value = lp_balance * lp_price
                    lp_positions.append({
                        "pool_address": pool.get("address"),
                        "tokens": [pool.get("token0_address"), pool.get("token1_address")],
                        "lp_balance": lp_balance,
                        "lp_price": lp_price,
                        "value": value
                    })
                    lp_value += value

            farm_positions = []
            farm_value = 0

            for farm in farms:
                locked_lp = self._parse_amount(farm.get("locked_total_lp", "0"))
                locked_lp_usd = self._parse_amount(farm.get("locked_total_lp_usd", "0"))

                if locked_lp_usd > 0:
                    farm_positions.append({
                        "farm_address": farm.get("address"),
                        "pool_address": farm.get("pool_address"),
                        "locked_lp": locked_lp,
                        "value": locked_lp_usd
                    })
                    farm_value += locked_lp_usd

            total_portfolio = total_value + lp_value + farm_value

            if total_portfolio > 0:
                asset_allocation = (total_value / total_portfolio) * 100
                lp_allocation = (lp_value / total_portfolio) * 100
                farm_allocation = (farm_value / total_portfolio) * 100
            else:
                asset_allocation = lp_allocation = farm_allocation = 0

            diversification_score = 0

            if len(asset_values) >= 3:
                diversification_score += 30

            if len(lp_positions) >= 2:
                diversification_score += 30

            if len(farm_positions) >= 1:
                diversification_score += 20

            if total_portfolio > 1000:
                diversification_score += 20

            asset_values.sort(key=lambda x: x["value"], reverse=True)
            lp_positions.sort(key=lambda x: x["value"], reverse=True)
            farm_positions.sort(key=lambda x: x["value"], reverse=True)

            return {
                "success": True,
                "wallet_address": wallet_address,
                "portfolio_summary": {
                    "total_value": round(total_portfolio, 2),
                    "asset_value": round(total_value, 2),
                    "lp_value": round(lp_value, 2),
                    "farm_value": round(farm_value, 2),
                    "asset_allocation": round(asset_allocation, 1),
                    "lp_allocation": round(lp_allocation, 1),
                    "farm_allocation": round(farm_allocation, 1)
                },
                "diversification_score": min(diversification_score, 100),
                "holdings": {
                    "assets_count": len(asset_values),
                    "lp_positions_count": len(lp_positions),
                    "farm_positions_count": len(farm_positions),
                    "top_assets": asset_values[:5],
                    "top_lp_positions": lp_positions[:3],
                    "top_farm_positions": farm_positions[:3]
                },
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_swap_recommendations(self, offer_token: str, ask_token: str, amount: float) -> Dict[str, Any]:
        try:
            swap_data = self.components.simulate_swap(
                offer_token, ask_token, str(amount), "0.005"
            )

            if "swap_rate" not in swap_data:
                return {"success": False, "error": "Swap simulation failed"}

            pools_data = self.components.get_pools_by_market(offer_token, ask_token)

            alternative_pools = []
            if "pool_list" in pools_data:
                for pool in pools_data["pool_list"][:3]:
                    pool_addr = pool.get("address")

                    try:
                        alt_swap = self.components.simulate_swap(
                            offer_token, ask_token, str(amount), "0.005",
                            pool_address=pool_addr
                        )

                        if "swap_rate" in alt_swap:
                            swap_rate = self._parse_amount(alt_swap.get("swap_rate", "0"))
                            price_impact = self._parse_amount(alt_swap.get("price_impact", "0"))

                            alternative_pools.append({
                                "pool_address": pool_addr,
                                "swap_rate": swap_rate,
                                "price_impact": price_impact,
                                "router": alt_swap.get("router", {}).get("address")
                            })
                    except:
                        continue

            alternative_pools.sort(key=lambda x: x["swap_rate"], reverse=True)

            return {
                "success": True,
                "offer_token": offer_token,
                "ask_token": ask_token,
                "amount": amount,
                "recommended_swap": {
                    "pool_address": swap_data.get("pool_address"),
                    "router_address": swap_data.get("router_address"),
                    "swap_rate": self._parse_amount(swap_data.get("swap_rate", "0")),
                    "price_impact": self._parse_amount(swap_data.get("price_impact", "0")),
                    "estimated_output": self._parse_amount(swap_data.get("ask_units", "0"))
                },
                "alternative_routes": alternative_pools,
                "slippage_tolerance": swap_data.get("slippage_tolerance", "0.005"),
                "recommended_slippage": swap_data.get("recommended_slippage_tolerance", "0.005"),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def calculate_apy_breakdown(self, farm_address: str) -> Dict[str, Any]:
        try:
            farm_data = self.components.get_farm(farm_address)

            if "farm" not in farm_data:
                return {"success": False, "error": "Invalid farm data"}

            farm = farm_data["farm"]
            rewards = farm.get("rewards", [])

            apy_str = farm.get("apy", "0")
            try:
                apy = float(apy_str)
            except:
                apy = 0

            rewards_breakdown = []
            total_rewards_value = 0

            for reward in rewards:
                token_address = reward.get("token_address")
                daily_reward = self._parse_amount(reward.get("daily_reward", "0"))

                try:
                    asset_data = self.components.get_asset(token_address)
                    if "asset" in asset_data:
                        token_price = self._parse_amount(asset_data["asset"].get("dex_price_usd", "0"))
                        reward_value = daily_reward * token_price * 365
                        total_rewards_value += reward_value

                        rewards_breakdown.append({
                            "token_address": token_address,
                            "daily_reward": daily_reward,
                            "token_price": token_price,
                            "annual_value": reward_value
                        })
                except:
                    continue

            locked_lp_usd = self._parse_amount(farm.get("locked_total_lp_usd", "0"))

            calculated_apy = 0
            if locked_lp_usd > 0:
                calculated_apy = (total_rewards_value / locked_lp_usd) * 100

            pool_address = farm.get("pool_address")
            pool_apy = 0
            if pool_address:
                try:
                    pool_data = self.components.get_pool(pool_address)
                    if "pool" in pool_data:
                        pool_apy = self._parse_amount(pool_data["pool"].get("apy_30d", "0")) * 100
                except:
                    pass

            total_apy = pool_apy + calculated_apy

            return {
                "success": True,
                "farm_address": farm_address,
                "pool_address": pool_address,
                "apy_breakdown": {
                    "reported_apy": round(apy, 2),
                    "calculated_apy": round(calculated_apy, 2),
                    "pool_apy": round(pool_apy, 2),
                    "total_apy": round(total_apy, 2)
                },
                "rewards": rewards_breakdown,
                "staking_metrics": {
                    "locked_lp_usd": round(locked_lp_usd, 2),
                    "total_rewards_value": round(total_rewards_value, 2),
                    "min_stake_duration": farm.get("min_stake_duration_s", "0")
                },
                "farm_status": farm.get("status", "Unknown"),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {"success": False, "error": str(e)}
