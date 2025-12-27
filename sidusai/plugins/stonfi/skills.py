from typing import Dict, Any
from datetime import datetime, timedelta

class StonFiDataValue:
    def __init__(self, data: Dict[str, Any]):
        self.value = data

def token_analysis_skill(context: Dict[str, Any]) -> StonFiDataValue:
    print("Starting token_analysis_skill...")

    token_address = context.get('token_address')

    try:
        client = context.get('stonfi_client')

        if not client:
            result = {"success": False, "error": "StonFi client not available"}
            return StonFiDataValue(result)

        try:
            response = client.get_asset(token_address)

            if isinstance(response, dict) and 'asset' in response:
                token_data = response['asset']

                symbol = token_data.get('symbol', 'N/A')
                name = token_data.get('display_name', 'N/A')
                contract_address = token_data.get('contract_address', token_address)

                price = None
                for price_key in ['dex_price_usd', 'dex_usd_price', 'third_party_price_usd', 'third_party_usd_price']:
                    if price_key in token_data and token_data[price_key]:
                        try:
                            price = float(token_data[price_key])
                            break
                        except:
                            continue

                analysis_result = {
                    "success": True,
                    "symbol": symbol,
                    "name": name,
                    "address": contract_address,
                    "price_usd": price,
                    "price_formatted": f"${price:.6f}" if price else "N/A",
                    "decimals": token_data.get('decimals', 'N/A'),
                    "token_type": token_data.get('kind', 'N/A'),
                    "tags": token_data.get('tags', []),
                    "timestamp": datetime.now().isoformat()
                }

                print(f"✅ Token analysis: {symbol} ({name}) - Price: ${price if price else 'N/A'}")

            else:
                analysis_result = {
                    "success": False,
                    "error": "Invalid response structure from API",
                    "timestamp": datetime.now().isoformat()
                }

        except Exception as e:
            print(f"Error getting token info: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to get token info: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return StonFiDataValue(analysis_result)

        if analysis_result.get('success'):
            try:
                pools_response = client.get_pools()
                related_pools = []

                if isinstance(pools_response, dict) and 'pool_list' in pools_response:
                    pools = pools_response['pool_list']
                    print(f"Found {len(pools)} pools total")

                    processed = 0
                    matched = 0

                    for pool in pools[:500]:
                        processed += 1
                        if not isinstance(pool, dict):
                            continue

                        token0_addr = pool.get('token0_address', '')
                        token1_addr = pool.get('token1_address', '')

                        if token_address in [token0_addr, token1_addr]:
                            matched += 1

                            token0_symbol = 'UNKNOWN'
                            token1_symbol = 'UNKNOWN'

                            try:
                                if token0_addr:
                                    token0_info = client.get_asset(token0_addr)
                                    if isinstance(token0_info, dict) and 'asset' in token0_info:
                                        token0_asset = token0_info['asset']
                                        token0_symbol = token0_asset.get('symbol', token0_addr[:6])
                                    else:
                                        token0_symbol = token0_addr[:6]
                            except:
                                token0_symbol = token0_addr[:6] if token0_addr else 'UNKNOWN'

                            try:
                                if token1_addr:
                                    token1_info = client.get_asset(token1_addr)
                                    if isinstance(token1_info, dict) and 'asset' in token1_info:
                                        token1_asset = token1_info['asset']
                                        token1_symbol = token1_asset.get('symbol', token1_addr[:6])
                                    else:
                                        token1_symbol = token1_addr[:6]
                            except:
                                token1_symbol = token1_addr[:6] if token1_addr else 'UNKNOWN'

                            if token0_addr == token_address:
                                pair = f"{symbol}/{token1_symbol}"
                            else:
                                pair = f"{token0_symbol}/{symbol}"

                            lp_total_supply_usd_str = pool.get('lp_total_supply_usd', '0')
                            try:
                                lp_total_supply_usd = float(lp_total_supply_usd_str)
                            except:
                                lp_total_supply_usd = 0

                            volume_24h_usd_str = pool.get('volume_24h_usd', '0')
                            try:
                                volume_24h_usd = float(volume_24h_usd_str)
                            except:
                                volume_24h_usd = 0

                            reserve0_str = pool.get('reserve0', '0')
                            reserve1_str = pool.get('reserve1', '0')
                            try:
                                reserve0 = float(reserve0_str)
                                reserve1 = float(reserve1_str)
                            except:
                                reserve0 = 0
                                reserve1 = 0

                            apy_30d_str = pool.get('apy_30d', '0')
                            try:
                                apy_30d = float(apy_30d_str) * 100
                            except:
                                apy_30d = 0

                            token_price_in_pool = None
                            if token0_addr == token_address and reserve1 > 0 and reserve0 > 0:
                                token_price_in_pool = reserve1 / reserve0
                            elif token1_addr == token_address and reserve0 > 0 and reserve1 > 0:
                                token_price_in_pool = reserve0 / reserve1

                            pool_info = {
                                "pool_address": pool.get('address', ''),
                                "pair": pair,
                                "liquidity_usd": lp_total_supply_usd,
                                "liquidity_formatted": f"${lp_total_supply_usd:,.2f}",
                                "volume_24h_usd": volume_24h_usd,
                                "volume_24h_formatted": f"${volume_24h_usd:,.2f}",
                                "apy_30d": apy_30d,
                                "apy_formatted": f"{apy_30d:.2f}%",
                                "reserve0": reserve0,
                                "reserve1": reserve1,
                                "token0": {
                                    "symbol": token0_symbol,
                                    "address": token0_addr,
                                    "is_our_token": token0_addr == token_address,
                                    "reserve": reserve0
                                },
                                "token1": {
                                    "symbol": token1_symbol,
                                    "address": token1_addr,
                                    "is_our_token": token1_addr == token_address,
                                    "reserve": reserve1
                                },
                                "token_price_in_pool": token_price_in_pool,
                                "token_price_formatted": f"${token_price_in_pool:.6f}" if token_price_in_pool else "N/A",
                                "lp_price_usd": float(pool.get('lp_price_usd', 0)) if pool.get('lp_price_usd') else 0,
                                "protocol_fee": pool.get('protocol_fee', ''),
                                "lp_fee": pool.get('lp_fee', '')
                            }

                            related_pools.append(pool_info)

                    print(f"Processed {processed} pools, found {matched} matches")

                    active_pools = [p for p in related_pools if p['liquidity_usd'] > 100]

                    if active_pools:
                        active_pools.sort(key=lambda x: x['liquidity_usd'], reverse=True)

                        total_liquidity = sum(p['liquidity_usd'] for p in active_pools)
                        total_volume = sum(p['volume_24h_usd'] for p in active_pools)

                        partner_stats = {}
                        for pool in active_pools:
                            if pool['token0']['is_our_token']:
                                partner = pool['token1']['symbol']
                            else:
                                partner = pool['token0']['symbol']

                            if partner not in partner_stats:
                                partner_stats[partner] = {
                                    'liquidity': 0, 
                                    'volume': 0,
                                    'pools': 0,
                                    'avg_apy': 0
                                }

                            partner_stats[partner]['liquidity'] += pool['liquidity_usd']
                            partner_stats[partner]['volume'] += pool['volume_24h_usd']
                            partner_stats[partner]['pools'] += 1
                            partner_stats[partner]['avg_apy'] += pool['apy_30d']

                        for partner in partner_stats:
                            if partner_stats[partner]['pools'] > 0:
                                partner_stats[partner]['avg_apy'] /= partner_stats[partner]['pools']

                        top_partners = sorted(
                            [(k, v['liquidity'], v['volume'], v['pools'], v['avg_apy']) 
                             for k, v in partner_stats.items()],
                            key=lambda x: x[1],
                            reverse=True
                        )[:5]

                        analysis_result.update({
                            "related_pools": active_pools[:20],
                            "related_pools_count": len(active_pools),
                            "total_pools_found": matched,
                            "total_liquidity_usd": total_liquidity,
                            "total_liquidity_formatted": f"${total_liquidity:,.2f}",
                            "total_volume_24h_usd": total_volume,
                            "total_volume_formatted": f"${total_volume:,.2f}",
                            "avg_liquidity_per_pool": total_liquidity / len(active_pools) if active_pools else 0,
                            "avg_volume_per_pool": total_volume / len(active_pools) if active_pools else 0,
                            "top_partners": [
                                {
                                    "token": token,
                                    "liquidity": liq,
                                    "liquidity_formatted": f"${liq:,.0f}",
                                    "volume": vol,
                                    "pools": pools,
                                    "avg_apy": f"{avg_apy:.2f}%"
                                }
                                for token, liq, vol, pools, avg_apy in top_partners
                            ],
                            "top_pools": [
                                {
                                    "pair": p["pair"],
                                    "liquidity": p["liquidity_formatted"],
                                    "volume": p["volume_24h_formatted"],
                                    "apy": p["apy_formatted"],
                                    "price_in_pool": p["token_price_formatted"]
                                }
                                for p in active_pools[:5]
                            ]
                        })

                        if active_pools:
                            top_pool = active_pools[0]
                            print(f"Top pool: {top_pool['pair']}")
                            print(f"  Liquidity: {top_pool['liquidity_formatted']}")
                            print(f"  Volume 24h: {top_pool['volume_24h_formatted']}")
                            print(f"  APY 30d: {top_pool['apy_formatted']}")
                            print(f"  Price in pool: {top_pool['token_price_formatted']}")

                        print(f"Total liquidity across {len(active_pools)} active pools: ${total_liquidity:,.2f}")
                        print(f"Total volume 24h: ${total_volume:,.2f}")

                    else:
                        print(f"No active pools found (liquidity > $100)")
                        if related_pools:
                            related_pools.sort(key=lambda x: x['liquidity_usd'], reverse=True)
                            analysis_result.update({
                                "related_pools": related_pools[:10],
                                "related_pools_count": len(related_pools),
                                "total_pools_found": matched,
                                "total_liquidity_usd": sum(p['liquidity_usd'] for p in related_pools),
                                "note": "All pools have liquidity < $100"
                            })
                            print(f"Showing {len(related_pools)} pools with low liquidity")
                        else:
                            analysis_result.update({
                                "related_pools": [],
                                "related_pools_count": 0,
                                "total_pools_found": matched
                            })

                else:
                    print(f"No pools data found in response")
                    analysis_result["related_pools"] = []
                    analysis_result["related_pools_count"] = 0

            except Exception as pool_error:
                print(f"Warning: Could not fetch pools: {pool_error}")
                import traceback
                traceback.print_exc()
                analysis_result["related_pools_error"] = str(pool_error)
                analysis_result["related_pools"] = []
                analysis_result["related_pools_count"] = 0

        return StonFiDataValue(analysis_result)

    except Exception as e:
        print(f"Error in advanced_token_analysis_skill: {e}")
        import traceback
        traceback.print_exc()
        result = {
            "success": False, 
            "error": f"Failed to analyze token: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return StonFiDataValue(result)

def swap_simulation_skill(context: Dict[str, Any]) -> StonFiDataValue:
    print("Starting swap_simulation_skill...")

    offer_address = context.get('offer_address')
    ask_address = context.get('ask_address')
    units = context.get('units')
    slippage_tolerance = context.get('slippage_tolerance', 0.01)
    pool_address = context.get('pool_address')

    if not offer_address or not ask_address or not units:
        return StonFiDataValue({
            "success": False, 
            "error": "Missing required parameters",
            "timestamp": datetime.now().isoformat()
        })

    try:
        client = context.get('stonfi_client')
        if not client:
            return StonFiDataValue({
                "success": False, 
                "error": "StonFi client not available",
                "timestamp": datetime.now().isoformat()
            })

        swap_result = client.simulate_swap(
            offer_address=offer_address,
            ask_address=ask_address,
            units=units,
            slippage_tolerance=slippage_tolerance,
            pool_address=pool_address
        )

        if not swap_result or not isinstance(swap_result, dict):
            return StonFiDataValue({
                "success": False, 
                "error": "Empty or invalid swap result",
                "timestamp": datetime.now().isoformat()
            })

        ask_units = swap_result.get('ask_units')
        min_ask_units = swap_result.get('min_ask_units')

        if not ask_units or ask_units == '0':
            return StonFiDataValue({
                "success": False,
                "error": "Swap returned zero amount",
                "swap_raw_response": swap_result,
                "timestamp": datetime.now().isoformat()
            })

        try:
            ask_units_float = float(ask_units)
            min_ask_units_float = float(min_ask_units) if min_ask_units else 0

            try:
                token_info = client.get_asset(ask_address)
                if isinstance(token_info, dict) and 'asset' in token_info:
                    decimals = token_info['asset'].get('decimals', 6)
                else:
                    decimals = 6
            except:
                decimals = 6

            ask_amount = ask_units_float / (10 ** decimals)
            min_ask_amount = min_ask_units_float / (10 ** decimals)

            result = {
                "success": True,
                "forward_swap": {
                    "ask_units": ask_units_float,
                    "ask_units_raw": ask_units,
                    "ask_amount": ask_amount,
                    "ask_amount_formatted": f"{ask_amount:.6f}",
                    "min_ask_units": min_ask_units_float,
                    "min_ask_amount": min_ask_amount,
                    "min_ask_amount_formatted": f"{min_ask_amount:.6f}",
                    "swap_rate": swap_result.get('swap_rate'),
                    "price_impact": swap_result.get('price_impact'),
                    "fee_percent": swap_result.get('fee_percent'),
                    "pool_address": swap_result.get('pool_address'),
                    "raw_response": swap_result
                },
                "timestamp": datetime.now().isoformat(),
                "swap_details": {
                    "offer_address": offer_address,
                    "ask_address": ask_address,
                    "units": units,
                    "units_readable": f"{float(units) / 1e9:.2f} TON",
                    "slippage": f"{slippage_tolerance*100:.1f}%",
                    "pool_address": pool_address or swap_result.get('pool_address', 'auto')
                }
            }
        except ValueError as ve:
            return StonFiDataValue({
                "success": False,
                "error": f"Error parsing swap amounts: {str(ve)}",
                "raw_response": swap_result,
                "timestamp": datetime.now().isoformat()
            })

        simulate_both = context.get('simulate_both_directions', False)
        if simulate_both:
            try:
                reverse_result = client.simulate_reverse_swap(
                    offer_address=offer_address,
                    ask_address=ask_address,
                    units=units,
                    slippage_tolerance=slippage_tolerance,
                    pool_address=pool_address
                )

                if reverse_result and isinstance(reverse_result, dict):
                    rev_ask_units = reverse_result.get('ask_units')
                    if rev_ask_units and rev_ask_units != '0':
                        try:
                            rev_ask_units_float = float(rev_ask_units)
                            rev_min_units = reverse_result.get('min_ask_units', '0')
                            rev_min_units_float = float(rev_min_units) if rev_min_units else 0

                            ton_decimals = 9
                            rev_ask_amount = rev_ask_units_float / (10 ** ton_decimals)
                            rev_min_amount = rev_min_units_float / (10 ** ton_decimals)

                            result["reverse_swap"] = {
                                "ask_units": rev_ask_units_float,
                                "ask_amount": rev_ask_amount,
                                "ask_amount_formatted": f"{rev_ask_amount:.6f}",
                                "min_ask_units": rev_min_units_float,
                                "min_ask_amount": rev_min_amount,
                                "min_ask_amount_formatted": f"{rev_min_amount:.6f}",
                                "raw_response": reverse_result
                            }
                        except ValueError:
                            result["reverse_swap_parse_error"] = "Could not parse reverse swap amounts"
            except Exception as e:
                result["reverse_swap_error"] = str(e)

        print("Processing swap results...")

        if result.get('success'):
            print(f"✅ Swap simulation successful!")

            forward = result.get('forward_swap', {})
            if forward:
                ask_amount = forward.get('ask_amount', 0)
                min_amount = forward.get('min_ask_amount', 0)
                swap_rate = forward.get('swap_rate')
                price_impact = forward.get('price_impact')
                fee_percent = forward.get('fee_percent')

                print(f"\n📊 Forward swap (TON → USDT):")
                print(f"   1 TON = {ask_amount:.6f} USDT")
                print(f"   Minimum output: {min_amount:.6f} USDT")

                if swap_rate:
                    print(f"   Exchange rate: 1 TON = {swap_rate} USDT")

                if price_impact:
                    print(f"   Price impact: {price_impact}%")

                if fee_percent:
                    print(f"   Fee: {fee_percent}%")

            reverse = result.get('reverse_swap', {})
            if reverse:
                rev_amount = reverse.get('ask_amount', 0)
                print(f"\n🔄 Reverse swap (USDT → TON):")
                print(f"   {ask_amount:.2f} USDT = {rev_amount:.6f} TON")

                if ask_amount > 0 and rev_amount > 0:
                    effective_rate = rev_amount / ask_amount
                    print(f"   Effective price: 1 USDT = {effective_rate:.6f} TON")

            details = result.get('swap_details', {})
            print(f"\n📋 Swap details:")
            print(f"   Amount: {details.get('units_readable', 'N/A')}")
            print(f"   Slippage: {details.get('slippage', 'N/A')}")

            pool_addr = forward.get('pool_address') or details.get('pool_address')
            if pool_addr and pool_addr != 'auto':
                short_pool = pool_addr[:8] + '...' + pool_addr[-6:]
                print(f"   Pool: {short_pool}")

            print(f"\n3. Pool analysis:")
            print("-" * 30)

            pool_result = client.get_pool(pool_address) if pool_address else None

            if pool_result and isinstance(pool_result, dict):
                print(f"✅ Pool analysis successful:")
                print(f"   Pair: {pool_result.get('pair', 'N/A')}")

                metrics = {
                    "liquidity_formatted": f"${float(pool_result.get('lp_total_supply_usd', 0)):,.2f}",
                    "volume_24h_formatted": f"${float(pool_result.get('volume_24h_usd', 0)):,.2f}",
                    "apy_30d_formatted": f"{float(pool_result.get('apy_30d', 0)) * 100:.2f}%",
                    "reserves_usd": {
                        "total_formatted": f"${(float(pool_result.get('reserve0', 0)) + float(pool_result.get('reserve1', 0))):,.2f}"
                    }
                }

                print(f"   Liquidity: {metrics.get('liquidity_formatted', '$0')}")
                print(f"   Volume 24h: {metrics.get('volume_24h_formatted', '$0')}")
                print(f"   APY 30d: {metrics.get('apy_30d_formatted', '0%')}")
                print(f"   Total reserves: {metrics['reserves_usd']['total_formatted']}")

                result["pool_analysis"] = {
                    "success": True,
                    "pool_data": pool_result,
                    "metrics": metrics
                }
            else:
                result["pool_analysis"] = {
                    "success": False,
                    "error": "Pool analysis not available"
                }
                print(f"ℹ️ Pool analysis not performed")

        else:
            error = result.get('error', 'Unknown error') if isinstance(result, dict) else str(result)
            print(f"\n❌ Error: {error}")

            if isinstance(result, dict) and 'swap_raw_response' in result:
                raw = result['swap_raw_response']
                print(f"\n📋 Raw API response:")
                print(f"   ask_units: {raw.get('ask_units', 'N/A')}")
                print(f"   min_ask_units: {raw.get('min_ask_units', 'N/A')}")
                print(f"   swap_rate: {raw.get('swap_rate', 'N/A')}")
                print(f"   pool_address: {raw.get('pool_address', 'N/A')}")

        return StonFiDataValue(result)

    except Exception as e:
        print(f"❌ Error in swap simulation: {e}")
        return StonFiDataValue({
            "success": False, 
            "error": f"Swap simulation failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        })

def pool_analysis_skill(context: Dict[str, Any]) -> StonFiDataValue:
    print("Starting pool_analysis_skill...")

    pool_address = context.get('pool_address')

    try:
        client = context.get('stonfi_client')

        if not client:
            result = {"success": False, "error": "StonFi client not available"}
            return StonFiDataValue(result)

        try:
            pool_response = client.get_pool(pool_address)

            if not pool_response or not isinstance(pool_response, dict):
                analysis = {
                    "success": False,
                    "error": "Invalid response from pool API",
                    "timestamp": datetime.now().isoformat()
                }
                return StonFiDataValue(analysis)

            pool_data = pool_response.get('pool', pool_response)

            if not pool_data or not isinstance(pool_data, dict):
                analysis = {
                    "success": False,
                    "error": "Invalid pool data structure",
                    "timestamp": datetime.now().isoformat()
                }
                return StonFiDataValue(analysis)

            token0_address = pool_data.get('token0_address')
            token1_address = pool_data.get('token1_address')

            tokens_info = {}

            for i, (token_addr, token_key) in enumerate([
                (token0_address, 'token0'),
                (token1_address, 'token1')
            ]):
                if token_addr:
                    try:
                        token_response = client.get_asset(token_addr)

                        if token_response and isinstance(token_response, dict) and 'asset' in token_response:
                            token_asset = token_response['asset']
                            symbol = token_asset.get('symbol', f'TOKEN{i+1}')
                            name = token_asset.get('display_name', f'Token {i+1}')

                            token_price = None
                            for price_key in ['dex_price_usd', 'dex_usd_price', 'third_party_price_usd', 'third_party_usd_price']:
                                if price_key in token_asset and token_asset[price_key]:
                                    try:
                                        token_price = float(token_asset[price_key])
                                        break
                                    except:
                                        continue

                            tokens_info[token_key] = {
                                'address': token_addr,
                                'symbol': symbol,
                                'name': name,
                                'price_usd': token_price,
                                'price_formatted': f"${token_price:.6f}" if token_price else "N/A",
                                'decimals': token_asset.get('decimals', 9)
                            }

                        else:
                            tokens_info[token_key] = {
                                'address': token_addr,
                                'symbol': token_addr[:8],
                                'name': f'Token {i+1}',
                                'price_usd': None,
                                'price_formatted': "N/A",
                                'decimals': 9
                            }

                    except Exception:
                        tokens_info[token_key] = {
                            'address': token_addr,
                            'symbol': token_addr[:8] if token_addr else f'TOKEN{i+1}',
                            'name': f'Token {i+1}',
                            'price_usd': None,
                            'price_formatted': "N/A",
                            'decimals': 9
                        }
                else:
                    tokens_info[token_key] = {
                        'address': '',
                        'symbol': f'TOKEN{i+1}',
                        'name': f'Token {i+1}',
                        'price_usd': None,
                        'price_formatted': "N/A",
                        'decimals': 9
                    }

            def safe_float(value, default=0):
                try:
                    return float(value) if value else default
                except:
                    return default

            lp_total_supply_usd = safe_float(pool_data.get('lp_total_supply_usd'))
            volume_24h_usd = safe_float(pool_data.get('volume_24h_usd'))
            reserve0 = safe_float(pool_data.get('reserve0'))
            reserve1 = safe_float(pool_data.get('reserve1'))
            apy_30d = safe_float(pool_data.get('apy_30d', 0)) * 100
            apy_7d = safe_float(pool_data.get('apy_7d', 0)) * 100
            apy_1d = safe_float(pool_data.get('apy_1d', 0)) * 100

            token0_decimals = tokens_info['token0'].get('decimals', 9)
            token1_decimals = tokens_info['token1'].get('decimals', 9)

            adjusted_reserve0 = reserve0 / (10 ** token0_decimals)
            adjusted_reserve1 = reserve1 / (10 ** token1_decimals)

            token0_symbol = tokens_info['token0']['symbol']
            token1_symbol = tokens_info['token1']['symbol']

            price_token1_in_token0 = adjusted_reserve1 / adjusted_reserve0 if adjusted_reserve0 > 0 else 0
            price_token0_in_token1 = adjusted_reserve0 / adjusted_reserve1 if adjusted_reserve1 > 0 else 0

            token0_price_usd = tokens_info['token0'].get('price_usd')
            token1_price_usd = tokens_info['token1'].get('price_usd')

            if token0_price_usd and token1_price_usd:
                implied_price_token0_in_token1 = token0_price_usd / token1_price_usd if token1_price_usd > 0 else 0
                implied_price_token1_in_token0 = token1_price_usd / token0_price_usd if token0_price_usd > 0 else 0

                price_diff_token0 = abs(price_token0_in_token1 - implied_price_token0_in_token1) / implied_price_token0_in_token1 * 100 if implied_price_token0_in_token1 > 0 else 100
                price_diff_token1 = abs(price_token1_in_token0 - implied_price_token1_in_token0) / implied_price_token1_in_token0 * 100 if implied_price_token1_in_token0 > 0 else 100

                price_diff_percent = min(price_diff_token0, price_diff_token1)
            else:
                price_diff_percent = 0
                implied_price_token0_in_token1 = 0
                implied_price_token1_in_token0 = 0

            reserve0_usd = adjusted_reserve0 * token0_price_usd if token0_price_usd else 0
            reserve1_usd = adjusted_reserve1 * token1_price_usd if token1_price_usd else 0
            total_reserves_usd = reserve0_usd + reserve1_usd

            tvl_imbalance = abs(reserve0_usd - reserve1_usd) / total_reserves_usd * 100 if total_reserves_usd > 0 else 100

            analysis = {
                "success": True,
                "pool_address": pool_address,
                "pair": f"{token0_symbol}/{token1_symbol}",
                "pair_names": f"{tokens_info['token0']['name']}/{tokens_info['token1']['name']}",
                "tokens": tokens_info,
                "metrics": {
                    "liquidity_usd": lp_total_supply_usd,
                    "liquidity_formatted": f"${lp_total_supply_usd:,.2f}",
                    "volume_24h_usd": volume_24h_usd,
                    "volume_24h_formatted": f"${volume_24h_usd:,.2f}",
                    "apy_30d": apy_30d,
                    "apy_30d_formatted": f"{apy_30d:.2f}%",
                    "apy_7d": apy_7d,
                    "apy_7d_formatted": f"{apy_7d:.2f}%",
                    "apy_1d": apy_1d,
                    "apy_1d_formatted": f"{apy_1d:.2f}%",
                    "reserves": {
                        "token0_raw": reserve0,
                        "token1_raw": reserve1,
                        "token0_adjusted": adjusted_reserve0,
                        "token1_adjusted": adjusted_reserve1,
                        "token0_formatted": f"{adjusted_reserve0:,.2f}",
                        "token1_formatted": f"{adjusted_reserve1:,.2f}"
                    },
                    "prices": {
                        "token1_in_token0": price_token1_in_token0,
                        "token1_in_token0_formatted": f"1 {token0_symbol} = {price_token1_in_token0:,.6f} {token1_symbol}",
                        "token0_in_token1": price_token0_in_token1,
                        "token0_in_token1_formatted": f"1 {token1_symbol} = {price_token0_in_token1:,.6f} {token0_symbol}",
                        "implied_token0_in_token1": implied_price_token0_in_token1,
                        "implied_token1_in_token0": implied_price_token1_in_token0,
                        "price_diff_percent": price_diff_percent,
                        "price_diff_formatted": f"{price_diff_percent:.2f}%"
                    },
                    "reserves_usd": {
                        "token0": reserve0_usd,
                        "token1": reserve1_usd,
                        "total": total_reserves_usd,
                        "token0_formatted": f"${reserve0_usd:,.2f}" if reserve0_usd else "N/A",
                        "token1_formatted": f"${reserve1_usd:,.2f}" if reserve1_usd else "N/A",
                        "total_formatted": f"${total_reserves_usd:,.2f}" if total_reserves_usd else "N/A",
                        "tvl_imbalance": tvl_imbalance,
                        "tvl_imbalance_formatted": f"{tvl_imbalance:.2f}%"
                    },
                    "lp_metrics": {
                        "total_supply": pool_data.get('lp_total_supply', '0'),
                        "price_usd": safe_float(pool_data.get('lp_price_usd')),
                        "price_usd_formatted": f"${safe_float(pool_data.get('lp_price_usd')):.6f}",
                        "fees": {
                            "lp_fee": pool_data.get('lp_fee', ''),
                            "protocol_fee": pool_data.get('protocol_fee', ''),
                            "total_fee_bps": f"{safe_float(pool_data.get('lp_fee', 0)) + safe_float(pool_data.get('protocol_fee', 0))}",
                            "total_fee_percent": f"{(safe_float(pool_data.get('lp_fee', 0)) + safe_float(pool_data.get('protocol_fee', 0))) / 10000:.4f}%"
                        }
                    },
                    "volume_ratio": (volume_24h_usd / lp_total_supply_usd * 100) if lp_total_supply_usd > 0 else 0,
                    "volume_ratio_formatted": f"{(volume_24h_usd / lp_total_supply_usd * 100):.2f}%" if lp_total_supply_usd > 0 else "0%",
                    "implied_daily_fees": volume_24h_usd * ((safe_float(pool_data.get('lp_fee', 0)) + safe_float(pool_data.get('protocol_fee', 0))) / 10000),
                    "implied_daily_fees_formatted": f"${volume_24h_usd * ((safe_float(pool_data.get('lp_fee', 0)) + safe_float(pool_data.get('protocol_fee', 0))) / 10000):,.2f}"
                },
                "metadata": {
                    "deprecated": pool_data.get('deprecated', False),
                    "popularity_index": pool_data.get('popularity_index', 0),
                    "tags": pool_data.get('tags', []),
                    "router_address": pool_data.get('router_address', '')
                },
                "timestamp": datetime.now().isoformat()
            }

            print(f"✅ Pool analysis: {token0_symbol}/{token1_symbol}")
            print(f"   Liquidity: ${lp_total_supply_usd:,.2f}")
            print(f"   Volume 24h: ${volume_24h_usd:,.2f}")
            print(f"   APY 30d: {apy_30d:.2f}%")
            print(f"   Price: 1 {token1_symbol} = {price_token0_in_token1:.6f} {token0_symbol}")

        except Exception as e:
            print(f"Error in pool analysis: {e}")
            analysis = {
                "success": False,
                "error": f"Failed to analyze pool: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return StonFiDataValue(analysis)

        if analysis.get('success'):
            try:
                stats_period_days = context.get('stats_period_days', 7)
                since_str = (datetime.now() - timedelta(days=stats_period_days)).strftime('%Y-%m-%dT%H:%M:%S')
                until_str = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

                pool_stats = client.get_pool_stats(
                    since=since_str,
                    until=until_str,
                    pool_address=pool_address
                )

                if pool_stats and isinstance(pool_stats, dict) and 'stats' in pool_stats:
                    stats_data = pool_stats['stats']

                    total_base_volume = 0
                    total_quote_volume = 0
                    daily_stats = []

                    for stat in stats_data:
                        if isinstance(stat, dict):
                            base_volume = safe_float(stat.get('base_volume', 0))
                            quote_volume = safe_float(stat.get('quote_volume', 0))
                            last_price = safe_float(stat.get('last_price', 0))
                            base_liquidity = safe_float(stat.get('base_liquidity', 0))
                            quote_liquidity = safe_float(stat.get('quote_liquidity', 0))
                            apy = safe_float(stat.get('apy', 0)) * 100 if stat.get('apy') else 0

                            total_base_volume += base_volume
                            total_quote_volume += quote_volume

                            base_symbol = stat.get('base_symbol', '')
                            quote_symbol = stat.get('quote_symbol', '')

                            base_name = stat.get('base_name', '')
                            quote_name = stat.get('quote_name', '')

                            daily_stats.append({
                                "date": "N/A",
                                "base_volume": base_volume,
                                "base_volume_formatted": f"{base_volume:,.2f} {base_symbol}",
                                "quote_volume": quote_volume,
                                "quote_volume_formatted": f"{quote_volume:,.2f} {quote_symbol}",
                                "total_volume_usd": (base_volume * token1_price_usd) + (quote_volume * token0_price_usd) if token0_price_usd and token1_price_usd else 0,
                                "last_price": last_price,
                                "last_price_formatted": f"1 {base_symbol} = {last_price:.6f} {quote_symbol}",
                                "base_liquidity": base_liquidity,
                                "quote_liquidity": quote_liquidity,
                                "apy": apy,
                                "apy_formatted": f"{apy:.2f}%" if apy else "N/A"
                            })

                    unique_wallets = pool_stats.get('unique_wallets_count', 0)

                    total_volume_usd = 0
                    if token0_price_usd and token1_price_usd:
                        total_volume_usd = (total_base_volume * token1_price_usd) + (total_quote_volume * token0_price_usd)

                    avg_daily_volume_usd = total_volume_usd / stats_period_days if stats_period_days > 0 else 0

                    analysis["historical_stats"] = {
                        "period_days": stats_period_days,
                        "data_points": len(stats_data),
                        "unique_wallets": unique_wallets,
                        "total_base_volume": total_base_volume,
                        "total_base_volume_formatted": f"{total_base_volume:,.2f} {stats_data[0].get('base_symbol', '') if stats_data else ''}",
                        "total_quote_volume": total_quote_volume,
                        "total_quote_volume_formatted": f"{total_quote_volume:,.2f} {stats_data[0].get('quote_symbol', '') if stats_data else ''}",
                        "total_volume_usd": total_volume_usd,
                        "total_volume_usd_formatted": f"${total_volume_usd:,.2f}" if total_volume_usd else "N/A",
                        "avg_daily_base_volume": total_base_volume / stats_period_days if stats_period_days > 0 else 0,
                        "avg_daily_quote_volume": total_quote_volume / stats_period_days if stats_period_days > 0 else 0,
                        "avg_daily_volume_usd": avg_daily_volume_usd,
                        "avg_daily_volume_usd_formatted": f"${avg_daily_volume_usd:,.2f}" if avg_daily_volume_usd else "N/A",
                        "daily_stats": daily_stats[-min(7, len(daily_stats)):] if daily_stats else []
                    }

                    if stats_data and len(stats_data) > 0:
                        latest_stat = stats_data[-1]
                        analysis["historical_stats"].update({
                            "latest_price": safe_float(latest_stat.get('last_price', 0)),
                            "latest_price_formatted": f"1 {latest_stat.get('base_symbol', '')} = {safe_float(latest_stat.get('last_price', 0)):.6f} {latest_stat.get('quote_symbol', '')}",
                            "latest_apy": safe_float(latest_stat.get('apy', 0)) * 100 if latest_stat.get('apy') else None,
                            "base_token": {
                                "symbol": latest_stat.get('base_symbol', ''),
                                "name": latest_stat.get('base_name', ''),
                                "address": latest_stat.get('base_id', '')
                            },
                            "quote_token": {
                                "symbol": latest_stat.get('quote_symbol', ''),
                                "name": latest_stat.get('quote_name', ''),
                                "address": latest_stat.get('quote_id', '')
                            }
                        })

                    print(f"   Historical stats: {len(stats_data)} data points")
                    print(f"   Unique wallets: {unique_wallets}")
                    print(f"   Total volume USD: ${total_volume_usd:,.2f}")
                    print(f"   Avg daily volume: ${avg_daily_volume_usd:,.2f}")

                else:
                    print(f"   No historical stats data available")
                    analysis["historical_stats"] = {
                        "available": False,
                        "note": "No historical data structure found in API response"
                    }

            except Exception as stats_error:
                print(f"Error fetching historical stats: {stats_error}")
                analysis["historical_stats_error"] = str(stats_error)
                analysis["historical_stats"] = {
                    "available": False,
                    "note": f"Error: {str(stats_error)}"
                }

        return StonFiDataValue(analysis)

    except Exception as e:
        print(f"Error in comprehensive_pool_analysis_skill: {e}")
        result = {"success": False, "error": str(e)}
        return StonFiDataValue(result)

def wallet_info_skill(context: Dict[str, Any]) -> StonFiDataValue:
    print("Starting wallet_info_skill...")

    wallet_address = context.get('wallet_address')
    if not wallet_address:
        result = {
            "success": False, 
            "error": "Wallet address is required",
            "timestamp": datetime.now().isoformat()
        }
        return StonFiDataValue(result)

    print(f"Analyzing wallet: {wallet_address[:12]}...")

    try:
        client = context.get('stonfi_client')
        if not client:
            result = {
                "success": False, 
                "error": "StonFi client not available",
                "timestamp": datetime.now().isoformat()
            }
            return StonFiDataValue(result)

        wallet_data = {
            "wallet_address": wallet_address,
            "wallet_short": f"{wallet_address[:8]}...{wallet_address[-6:]}",
            "address_type": "UQ" if wallet_address.startswith('UQ') else "EQ" if wallet_address.startswith('EQ') else "Other",
            "analysis_timestamp": datetime.now().isoformat(),
            "included_sections": []
        }

        total_value = 0

        include_assets = context.get('include_assets', True)
        if include_assets:
            print(f"   Fetching wallet assets...")
            try:
                assets_response = client.get_wallet_assets(wallet_address)

                if assets_response and isinstance(assets_response, dict):
                    asset_list = assets_response.get('asset_list', [])

                    if asset_list:
                        valuable_assets = []
                        assets_with_balance = []
                        assets_without_balance = []
                        assets_value = 0

                        for asset in asset_list:
                            if not isinstance(asset, dict):
                                continue

                            symbol = asset.get('symbol', 'UNKNOWN')
                            contract_address = asset.get('contract_address', '')
                            balance_str = asset.get('balance', '0')
                            decimals = int(asset.get('decimals', 9))
                            display_name = asset.get('display_name', symbol)
                            kind = asset.get('kind', 'N/A')

                            has_balance = 'balance' in asset and balance_str != '0'

                            price = None
                            price_source = None
                            price_fields = [
                                ('dex_price_usd', 'DEX'),
                                ('dex_usd_price', 'DEX'), 
                                ('third_party_price_usd', 'Third Party'),
                                ('third_party_usd_price', 'Third Party')
                            ]

                            for price_field, source in price_fields:
                                if price_field in asset and asset[price_field]:
                                    try:
                                        price = float(asset[price_field])
                                        price_source = source
                                        break
                                    except:
                                        continue

                            usd_value = 0
                            if price and has_balance:
                                try:
                                    balance_num = float(balance_str) / (10 ** decimals)
                                    usd_value = balance_num * price
                                except:
                                    pass

                            balance_readable = ""
                            if has_balance:
                                try:
                                    balance_num = float(balance_str) / (10 ** decimals)
                                    if balance_num >= 1000:
                                        balance_readable = f"{balance_num:,.0f}"
                                    elif balance_num >= 1:
                                        balance_readable = f"{balance_num:,.2f}"
                                    elif balance_num >= 0.01:
                                        balance_readable = f"{balance_num:,.4f}"
                                    else:
                                        balance_readable = f"{balance_num:,.6f}"
                                except:
                                    balance_readable = balance_str

                            asset_info = {
                                "symbol": symbol,
                                "name": display_name,
                                "contract_address": contract_address,
                                "contract_short": f"{contract_address[:8]}...{contract_address[-6:]}" if contract_address else "",
                                "wallet_address": asset.get('wallet_address', ''),
                                "balance": balance_str,
                                "balance_readable": balance_readable,
                                "decimals": decimals,
                                "kind": kind,
                                "price": price,
                                "price_formatted": f"${price:,.6f}" if price else "N/A",
                                "price_source": price_source,
                                "usd_value": usd_value,
                                "usd_value_formatted": f"${usd_value:,.2f}" if usd_value > 0 else "$0.00",
                                "has_balance": has_balance,
                                "image_url": asset.get('image_url', ''),
                                "tags": asset.get('tags', []),
                                "popularity_index": asset.get('popularity_index'),
                                "priority": asset.get('priority', 0),
                                "deprecated": asset.get('deprecated', False),
                                "community": asset.get('community', False),
                                "blacklisted": asset.get('blacklisted', False)
                            }

                            min_asset_value = context.get('min_asset_value', 0.01)

                            if has_balance:
                                assets_with_balance.append(asset_info)
                                if usd_value >= min_asset_value:
                                    valuable_assets.append(asset_info)
                                    assets_value += usd_value
                            else:
                                assets_without_balance.append(asset_info)

                        wallet_data["assets_statistics"] = {
                            "total_assets_in_list": len(asset_list),
                            "assets_with_balance": len(assets_with_balance),
                            "assets_without_balance": len(assets_without_balance),
                            "valuable_assets": len(valuable_assets)
                        }

                        if valuable_assets:
                            valuable_assets.sort(key=lambda x: x['usd_value'], reverse=True)
                            wallet_data["assets"] = valuable_assets
                            wallet_data["assets_count"] = len(valuable_assets)
                            wallet_data["assets_total_value"] = assets_value
                            wallet_data["assets_total_formatted"] = f"${assets_value:,.2f}"
                            wallet_data["included_sections"].append("assets")
                            total_value += assets_value

                            top_assets = valuable_assets[:3]
                            wallet_data["top_assets"] = [
                                {
                                    "symbol": a["symbol"],
                                    "value": a["usd_value_formatted"],
                                    "balance": a["balance_readable"]
                                }
                                for a in top_assets
                            ]

                            print(f"   ✅ Found {len(valuable_assets)} valuable assets worth ${assets_value:,.2f}")
                            print(f"      Top asset: {top_assets[0]['symbol']} - {top_assets[0]['usd_value_formatted']}")
                        else:
                            wallet_data["assets"] = []
                            wallet_data["assets_count"] = 0
                            wallet_data["assets_total_value"] = 0
                            print(f"   ℹ️ No valuable assets found (min: ${min_asset_value})")

                        if assets_with_balance:
                            wallet_data["all_assets_with_balance"] = assets_with_balance
                    else:
                        wallet_data["assets"] = []
                        wallet_data["assets_count"] = 0
                        wallet_data["assets_total_value"] = 0
                        print(f"   ℹ️ No asset data received")
                else:
                    wallet_data["assets_error"] = "Invalid assets response"
                    wallet_data["assets"] = []
                    wallet_data["assets_count"] = 0
                    print(f"   ❌ Invalid assets response")

            except Exception as e:
                error_msg = str(e)
                wallet_data["assets_error"] = error_msg
                wallet_data["assets"] = []
                wallet_data["assets_count"] = 0
                print(f"   ❌ Assets API error: {error_msg}")

        include_pools = context.get('include_pools', True)
        if include_pools:
            print(f"   Fetching liquidity pools...")
            try:
                pools_response = client.get_wallet_pools(wallet_address, dex_v2=True)

                if pools_response and isinstance(pools_response, dict):
                    pools_list = pools_response.get('pools', [])

                    if pools_list:
                        lp_positions = []
                        pools_value = 0

                        for pool in pools_list:
                            if not isinstance(pool, dict):
                                continue

                            lp_usd_value = 0
                            for value_field in ['lp_usd_value', 'usd_value', 'total_usd']:
                                if value_field in pool:
                                    try:
                                        lp_usd_value = float(pool[value_field])
                                        break
                                    except:
                                        continue

                            if lp_usd_value > 0:
                                token0_symbol = pool.get('token0_symbol', 'UNKNOWN')
                                token1_symbol = pool.get('token1_symbol', 'UNKNOWN')
                                token0_address = pool.get('token0_address', '')
                                token1_address = pool.get('token1_address', '')

                                lp_info = {
                                    "pool_address": pool.get('pool_address', ''),
                                    "pool_short": f"{pool.get('pool_address', '')[:8]}...{pool.get('pool_address', '')[-6:]}",
                                    "tokens": f"{token0_symbol}/{token1_symbol}",
                                    "token0": {
                                        "symbol": token0_symbol,
                                        "address": token0_address,
                                        "address_short": f"{token0_address[:6]}...{token0_address[-4:]}" if token0_address else ""
                                    },
                                    "token1": {
                                        "symbol": token1_symbol,
                                        "address": token1_address,
                                        "address_short": f"{token1_address[:6]}...{token1_address[-4:]}" if token1_address else ""
                                    },
                                    "lp_balance": pool.get('lp_balance', '0'),
                                    "lp_usd_value": lp_usd_value,
                                    "lp_usd_formatted": f"${lp_usd_value:,.2f}",
                                    "share_percentage": pool.get('share_percentage', '0'),
                                    "protocol_fee": pool.get('protocol_fee', '0'),
                                    "lp_fee": pool.get('lp_fee', '0'),
                                    "reserve0": pool.get('reserve0', '0'),
                                    "reserve1": pool.get('reserve1', '0')
                                }

                                lp_positions.append(lp_info)
                                pools_value += lp_usd_value

                        if lp_positions:
                            lp_positions.sort(key=lambda x: x['lp_usd_value'], reverse=True)
                            wallet_data["lp_positions"] = lp_positions
                            wallet_data["lp_positions_count"] = len(lp_positions)
                            wallet_data["lp_total_value"] = pools_value
                            wallet_data["lp_total_formatted"] = f"${pools_value:,.2f}"
                            wallet_data["included_sections"].append("liquidity_pools")
                            total_value += pools_value

                            top_pools = lp_positions[:3]
                            wallet_data["top_lp_positions"] = [
                                {
                                    "pair": p["tokens"],
                                    "value": p["lp_usd_formatted"],
                                    "share": f"{p['share_percentage']}%"
                                }
                                for p in top_pools
                            ]

                            print(f"   ✅ Found {len(lp_positions)} LP positions worth ${pools_value:,.2f}")
                        else:
                            wallet_data["lp_positions"] = []
                            wallet_data["lp_positions_count"] = 0
                            wallet_data["lp_total_value"] = 0
                            print(f"   ℹ️ No LP positions found")
                    else:
                        wallet_data["lp_positions"] = []
                        wallet_data["lp_positions_count"] = 0
                        wallet_data["lp_total_value"] = 0
                        print(f"   ℹ️ No LP data")
                else:
                    wallet_data["pools_error"] = "Invalid pools response"
                    wallet_data["lp_positions"] = []
                    wallet_data["lp_positions_count"] = 0
                    print(f"   ❌ Invalid pools response")

            except Exception as e:
                wallet_data["pools_error"] = str(e)
                wallet_data["lp_positions"] = []
                wallet_data["lp_positions_count"] = 0
                print(f"   ❌ Pools API error: {e}")

        include_farms = context.get('include_farms', True)
        if include_farms:
            print(f"   Fetching farming positions...")
            try:
                farms_response = client.get_wallet_farms(wallet_address, dex_v2=True, only_active=True)

                if farms_response and isinstance(farms_response, dict):
                    farms_list = farms_response.get('farms', [])

                    if farms_list:
                        farming_positions = []
                        farms_value = 0

                        for farm in farms_list:
                            if not isinstance(farm, dict):
                                continue

                            staked_usd = 0
                            for value_field in ['staked_usd_value', 'usd_value', 'total_usd']:
                                if value_field in farm:
                                    try:
                                        staked_usd = float(farm[value_field])
                                        break
                                    except:
                                        continue

                            if staked_usd > 0:
                                farm_info = {
                                    "farm_address": farm.get('farm_address', ''),
                                    "farm_short": f"{farm.get('farm_address', '')[:8]}...{farm.get('farm_address', '')[-6:]}",
                                    "pool_tokens": farm.get('pool_tokens', 'N/A'),
                                    "staked_amount": farm.get('staked_amount', '0'),
                                    "staked_usd_value": staked_usd,
                                    "staked_usd_formatted": f"${staked_usd:,.2f}",
                                    "apr": farm.get('apr', '0'),
                                    "apr_formatted": f"{farm.get('apr', '0')}%",
                                    "pending_rewards": farm.get('pending_rewards', '0'),
                                    "reward_token": farm.get('reward_token', ''),
                                    "is_active": farm.get('is_active', True)
                                }

                                farming_positions.append(farm_info)
                                farms_value += staked_usd

                        if farming_positions:
                            wallet_data["farming_positions"] = farming_positions
                            wallet_data["farming_positions_count"] = len(farming_positions)
                            wallet_data["farming_total_value"] = farms_value
                            wallet_data["farming_total_formatted"] = f"${farms_value:,.2f}"
                            wallet_data["included_sections"].append("farming")
                            total_value += farms_value

                            print(f"   ✅ Found {len(farming_positions)} farming positions worth ${farms_value:,.2f}")
                        else:
                            wallet_data["farming_positions"] = []
                            wallet_data["farming_positions_count"] = 0
                            wallet_data["farming_total_value"] = 0
                            print(f"   ℹ️ No farming positions found")
                    else:
                        wallet_data["farming_positions"] = []
                        wallet_data["farming_positions_count"] = 0
                        wallet_data["farming_total_value"] = 0
                        print(f"   ℹ️ No farming data")
                else:
                    wallet_data["farms_error"] = "Invalid farms response"
                    wallet_data["farming_positions"] = []
                    wallet_data["farming_positions_count"] = 0
                    print(f"   ❌ Invalid farms response")

            except Exception as e:
                wallet_data["farms_error"] = str(e)
                wallet_data["farming_positions"] = []
                wallet_data["farming_positions_count"] = 0
                print(f"   ❌ Farms API error: {e}")

        include_stakes = context.get('include_stakes', True)
        if include_stakes:
            print(f"   Fetching stakes...")
            try:
                stakes_response = client.get_wallet_stakes(wallet_address)

                if stakes_response and isinstance(stakes_response, dict):
                    stakes_list = stakes_response.get('stakes', [])

                    if stakes_list:
                        wallet_data["staking_positions"] = stakes_list[:10]
                        wallet_data["staking_count"] = len(stakes_list)
                        wallet_data["included_sections"].append("staking")
                        print(f"   ✅ Found {len(stakes_list)} staking positions")
                    else:
                        wallet_data["staking_positions"] = []
                        wallet_data["staking_count"] = 0
                        print(f"   ℹ️ No stakes found")
                else:
                    wallet_data["staking_error"] = "Invalid stakes response"
                    wallet_data["staking_positions"] = []
                    print(f"   ❌ Invalid stakes response")

            except Exception as e:
                wallet_data["staking_error"] = str(e)
                wallet_data["staking_positions"] = []
                print(f"   ❌ Stakes API error: {e}")

        wallet_data["total_wallet_value"] = total_value
        wallet_data["total_wallet_formatted"] = f"${total_value:,.2f}"

        wallet_data["value_by_category"] = {}
        if wallet_data.get('assets_count', 0) > 0:
            wallet_data["value_by_category"]["assets"] = wallet_data.get('assets_total_formatted', '$0')
        if wallet_data.get('lp_positions_count', 0) > 0:
            wallet_data["value_by_category"]["liquidity_pools"] = wallet_data.get('lp_total_formatted', '$0')
        if wallet_data.get('farming_positions_count', 0) > 0:
            wallet_data["value_by_category"]["farming"] = wallet_data.get('farming_total_formatted', '$0')
        wallet_data["value_by_category"]["total"] = wallet_data["total_wallet_formatted"]

        if total_value > 0:
            wallet_data["percentage_distribution"] = {}
            if wallet_data.get('assets_total_value', 0) > 0:
                wallet_data["percentage_distribution"]["assets"] = f"{(wallet_data['assets_total_value'] / total_value * 100):.1f}%"
            if wallet_data.get('lp_total_value', 0) > 0:
                wallet_data["percentage_distribution"]["liquidity_pools"] = f"{(wallet_data['lp_total_value'] / total_value * 100):.1f}%"
            if wallet_data.get('farming_total_value', 0) > 0:
                wallet_data["percentage_distribution"]["farming"] = f"{(wallet_data['farming_total_value'] / total_value * 100):.1f}%"

        wallet_size = ""
        if total_value == 0:
            wallet_size = "empty"
        elif total_value < 10:
            wallet_size = "very_small"
        elif total_value < 100:
            wallet_size = "small"
        elif total_value < 1000:
            wallet_size = "medium"
        elif total_value < 10000:
            wallet_size = "large"
        else:
            wallet_size = "very_large"

        wallet_data["wallet_size"] = wallet_size
        wallet_data["wallet_size_label"] = {
            "empty": "Empty",
            "very_small": "Very small (<$10)",
            "small": "Small ($10-$100)", 
            "medium": "Medium ($100-$1,000)",
            "large": "Large ($1,000-$10,000)",
            "very_large": "Very large (>$10,000)"
        }[wallet_size]

        wallet_data["success"] = True
        print(f"✅ Wallet analysis complete")
        print(f"   Total wallet value: ${total_value:,.2f}")

        return StonFiDataValue(wallet_data)

    except Exception as e:
        print(f"❌ Error in wallet analysis: {e}")
        result = {
            "success": False, 
            "error": f"Wallet analysis failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return StonFiDataValue(result)

def arbitrage_finder_skill(context: Dict[str, Any]) -> StonFiDataValue:
    print("Searching for arbitrage opportunities...")

    min_profit = context.get('min_profit_percentage', 0.1)
    max_tokens = context.get('max_tokens_to_analyze', 20)
    base_token_address = context.get('base_token', 'EQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM9c')
    user_tokens = context.get('tokens_to_analyze', [])
    min_pool_liquidity = context.get('min_pool_liquidity', 1000)
    max_route_length = context.get('max_route_length', 3)

    print(f"Analysis parameters:")
    print(f"   Base token: TON")
    print(f"   Minimum profit: {min_profit}%")
    print(f"   Tokens to analyze: {len(user_tokens)}")
    print(f"   Minimum pool liquidity: ${min_pool_liquidity}")
    print(f"   Maximum chain length: {max_route_length}")

    try:
        client = context.get('stonfi_client')
        if not client:
            return StonFiDataValue({"success": False, "error": "STON.FI client not available"})

        print(f"Step 1: Getting token information...")

        tokens_info = []
        tokens_to_check = user_tokens[:max_tokens]

        for i, token_address in enumerate(tokens_to_check, 1):
            try:
                asset = client.get_asset(token_address)
                if asset and 'asset' in asset:
                    symbol = asset['asset'].get('symbol', f'TOKEN_{i}')
                    tokens_info.append({
                        'address': token_address,
                        'symbol': symbol,
                        'display_name': f"{symbol} ({token_address[:8]}...)"
                    })
                    print(f"   [{i}/{len(tokens_to_check)}] {symbol}")
                else:
                    tokens_info.append({
                        'address': token_address,
                        'symbol': f'TOKEN_{i}',
                        'display_name': f"TOKEN_{i} ({token_address[:8]}...)"
                    })
                    print(f"   [{i}/{len(tokens_to_check)}] TOKEN_{i} (basic)")
            except Exception as e:
                print(f"   [{i}/{len(tokens_to_check)}] Error: {str(e)[:50]}...")
                continue

        print(f"   ✓ Loaded: {len(tokens_info)} tokens")

        if len(tokens_info) < 3:
            return StonFiDataValue({
                "success": False,
                "error": f"Insufficient tokens. Minimum 3 required, found: {len(tokens_info)}"
            })

        print(f"Step 2: Getting exchange rates TON ↔ Tokens...")

        ton_to_token_rates = {}
        token_to_ton_rates = {}
        pool_infos = {}

        for token in tokens_info:
            try:
                pools_response = client.get_pools_by_market(base_token_address, token['address'])

                if not pools_response or 'pool_list' not in pools_response:
                    print(f"   ✗ {token['symbol']}: pools not found")
                    continue

                pools = pools_response['pool_list']
                if not pools:
                    print(f"   ✗ {token['symbol']}: pool list empty")
                    continue

                pool = pools[0]

                liquidity = float(pool.get('lp_total_supply_usd', 0))
                if liquidity < min_pool_liquidity:
                    print(f"   ⚠ {token['symbol']}: low liquidity (${liquidity:,.0f})")
                    continue

                token0_address = pool.get('token0_address', '')
                reserve0 = float(pool.get('reserve0', 0))
                reserve1 = float(pool.get('reserve1', 0))

                if reserve0 <= 0 or reserve1 <= 0:
                    print(f"   ✗ {token['symbol']}: zero reserves")
                    continue

                if token0_address == base_token_address:
                    ton_to_token_rate = reserve1 / reserve0
                    token_to_ton_rate = reserve0 / reserve1
                else:
                    ton_to_token_rate = reserve0 / reserve1
                    token_to_ton_rate = reserve1 / reserve0

                if ton_to_token_rate <= 0 or token_to_ton_rate <= 0:
                    print(f"   ✗ {token['symbol']}: incorrect rate")
                    continue

                ton_to_token_rates[token['symbol']] = ton_to_token_rate
                token_to_ton_rates[token['symbol']] = token_to_ton_rate
                pool_infos[token['symbol']] = {
                    'liquidity': liquidity,
                    'reserve0': reserve0,
                    'reserve1': reserve1,
                    'rate_field': pool.get('rate', 'N/A')
                }

                rate_display = f"{ton_to_token_rate:.10f}".rstrip('0').rstrip('.')
                if '.' in rate_display and len(rate_display.split('.')[1]) > 6:
                    rate_display = f"{ton_to_token_rate}"

                print(f"   ✓ TON/{token['symbol']}: {rate_display} (liq.: ${liquidity:,.0f})")

            except Exception as e:
                print(f"   ✗ {token['symbol']}: error - {str(e)[:50]}...")
                continue

        print(f"   Statistics:")
        print(f"   Pairs successfully obtained: {len(ton_to_token_rates)}")
        print(f"   Tokens skipped: {len(tokens_info) - len(ton_to_token_rates)}")

        if len(ton_to_token_rates) < 3:
            return StonFiDataValue({
                "success": False,
                "error": f"Insufficient valid pairs. Found: {len(ton_to_token_rates)}, minimum 3 required",
                "debug_info": {
                    "total_tokens": len(tokens_info),
                    "valid_pairs": len(ton_to_token_rates),
                    "token_symbols": [t['symbol'] for t in tokens_info],
                    "valid_symbols": list(ton_to_token_rates.keys())
                }
            })

        print(f"Step 3: Searching for arbitrage opportunities (max length: {max_route_length})...")

        arbitrage_opportunities = []

        token_symbols = list(ton_to_token_rates.keys())

        for i in range(len(token_symbols)):
            for j in range(len(token_symbols)):
                if i == j:
                    continue

                token_a = token_symbols[i]
                token_b = token_symbols[j]

                try:
                    token_a_address = next(t['address'] for t in tokens_info if t['symbol'] == token_a)
                    token_b_address = next(t['address'] for t in tokens_info if t['symbol'] == token_b)

                    ab_pools_response = client.get_pools_by_market(token_a_address, token_b_address)

                    if not ab_pools_response or 'pool_list' not in ab_pools_response:
                        continue

                    ab_pools = ab_pools_response['pool_list']
                    if not ab_pools:
                        continue

                    ab_pool = ab_pools[0]

                    ab_liquidity = float(ab_pool.get('lp_total_supply_usd', 0))
                    if ab_liquidity < min_pool_liquidity:
                        continue

                    ab_token0 = ab_pool.get('token0_address', '')
                    ab_reserve0 = float(ab_pool.get('reserve0', 0))
                    ab_reserve1 = float(ab_pool.get('reserve1', 0))

                    if ab_reserve0 <= 0 or ab_reserve1 <= 0:
                        continue

                    if ab_token0 == token_a_address:
                        a_to_b_rate = ab_reserve1 / ab_reserve0
                        b_to_a_rate = ab_reserve0 / ab_reserve1
                    else:
                        a_to_b_rate = ab_reserve0 / ab_reserve1
                        b_to_a_rate = ab_reserve1 / ab_reserve0

                    if a_to_b_rate <= 0:
                        continue

                    cycle_profit = (
                        ton_to_token_rates[token_a] *
                        a_to_b_rate *
                        token_to_ton_rates[token_b]
                    )

                    profit_percent = (cycle_profit - 1) * 100

                    reverse_profit = (
                        ton_to_token_rates[token_b] *
                        b_to_a_rate *
                        token_to_ton_rates[token_a]
                    )

                    reverse_profit_percent = (reverse_profit - 1) * 100

                    if profit_percent >= reverse_profit_percent:
                        final_cycle = ['TON', token_a, token_b, 'TON']
                        final_profit = profit_percent
                        rates = [
                            ton_to_token_rates[token_a],
                            a_to_b_rate,
                            token_to_ton_rates[token_b]
                        ]
                        best_direction = "forward"
                    else:
                        final_cycle = ['TON', token_b, token_a, 'TON']
                        final_profit = reverse_profit_percent
                        rates = [
                            ton_to_token_rates[token_b],
                            b_to_a_rate,
                            token_to_ton_rates[token_a]
                        ]
                        best_direction = "reverse"

                    if final_profit >= min_profit:
                        rate_display_list = []
                        for idx, rate in enumerate(rates):
                            if idx == 0:
                                from_token = final_cycle[0]
                                to_token = final_cycle[1]
                            elif idx == 1:
                                from_token = final_cycle[1]
                                to_token = final_cycle[2]
                            else:
                                from_token = final_cycle[2]
                                to_token = final_cycle[3]

                            if rate < 0.000001:
                                rate_str = f"{rate:.10f}".rstrip('0').rstrip('.')
                            elif rate < 1:
                                rate_str = f"{rate:.6f}".rstrip('0').rstrip('.')
                            else:
                                rate_str = f"{rate:.4f}".rstrip('0').rstrip('.')

                            rate_display_list.append({
                                'from': from_token,
                                'to': to_token,
                                'rate': rate,
                                'display': rate_str
                            })

                        arbitrage_opportunities.append({
                            'cycle': final_cycle,
                            'profit_percentage': final_profit,
                            'profit_percentage_formatted': f"{final_profit:.4f}%",
                            'cycle_profit_ratio': cycle_profit if best_direction == "forward" else reverse_profit,
                            'rates': rate_display_list,
                            'liquidity': min(
                                pool_infos.get(token_a, {}).get('liquidity', 0),
                                pool_infos.get(token_b, {}).get('liquidity', 0),
                                ab_liquidity
                            ),
                            'type': 'triangular',
                            'direction': best_direction,
                            'route_length': 3
                        })

                        print(f"   Found opportunity: {' → '.join(final_cycle)} ({final_profit:.2f}%)")

                except Exception as e:
                    continue

        if max_route_length > 3:
            print(f"   Additional search for chains up to {max_route_length} steps...")
            print(f"   ⚠ Search for chains >3 steps temporarily not implemented")

        arbitrage_opportunities.sort(key=lambda x: x['profit_percentage'], reverse=True)

        unique_opportunities = []
        seen_cycles = set()

        for opp in arbitrage_opportunities:
            cycle_str = '->'.join(opp['cycle'])
            if cycle_str not in seen_cycles:
                seen_cycles.add(cycle_str)
                unique_opportunities.append(opp)

        arbitrage_opportunities = unique_opportunities[:10]

        print(f"\n" + "="*50)
        print(f"ARBITRAGE ANALYSIS RESULTS")
        print(f"="*50)

        result = {
            "success": True,
            "analysis": {
                "base_token": "TON",
                "tokens_analyzed": len(tokens_info),
                "valid_pairs_found": len(ton_to_token_rates),
                "min_profit_threshold": f"{min_profit}%",
                "min_liquidity_threshold": f"${min_pool_liquidity}",
                "max_route_length": max_route_length,
                "timestamp": datetime.now().isoformat()
            },
            "arbitrage_opportunities": arbitrage_opportunities,
            "summary": {
                "total_opportunities": len(arbitrage_opportunities),
                "max_profit": f"{arbitrage_opportunities[0]['profit_percentage_formatted']}" if arbitrage_opportunities else "0%",
                "profitable_cycles": len([o for o in arbitrage_opportunities if o['profit_percentage'] > 0]),
                "cycles_by_length": {
                    "triangular": len([o for o in arbitrage_opportunities if o['route_length'] == 3])
                }
            }
        }

        print(f"\nGENERAL STATISTICS:")
        print(f"   • Tokens analyzed: {len(tokens_info)}")
        print(f"   • Successful TON/token pairs: {len(ton_to_token_rates)}")
        print(f"   • Opportunities found: {len(arbitrage_opportunities)}")
        print(f"   • Maximum chain length in search: {max_route_length}")

        if arbitrage_opportunities:
            print(f"\nARBITRAGE OPPORTUNITIES:")

            for idx, opp in enumerate(arbitrage_opportunities[:5], 1):
                print(f"\n   {idx}. Profit: {opp['profit_percentage_formatted']}")
                print(f"      Cycle length: {opp.get('route_length', len(opp['cycle']) - 1)} steps")
                print(f"      Path: {' → '.join(opp['cycle'])}")
                print(f"      Type: {opp['type']}")

                if 'rates' in opp and isinstance(opp['rates'], list):
                    print(f"      Exchange rates:")
                    for rate_info in opp['rates']:
                        if isinstance(rate_info, dict):
                            from_token = rate_info.get('from', '')
                            to_token = rate_info.get('to', '')
                            rate_display = rate_info.get('display', '')
                            print(f"        • {from_token} → {to_token}: {rate_display}")
                        else:
                            print(f"        • Rate: {rate_info}")

                if opp['profit_percentage'] > 0:
                    gas_estimate = opp.get('route_length', 3) * 0.1
                    min_amount = gas_estimate / (opp['profit_percentage'] / 100)
                    print(f"      Min amount for profit: ~{min_amount:.2f} TON")

                    liquidity = opp.get('liquidity', 0)
                    if liquidity < 500:
                        print(f"      ⚠ Warning: low liquidity (${liquidity:,.0f})")
                    elif liquidity < 2000:
                        print(f"      ⚠ Average liquidity (${liquidity:,.0f})")
                    else:
                        print(f"      ✅ Normal liquidity (${liquidity:,.0f})")
        else:
            print(f"\nARBITRAGE OPPORTUNITIES NOT FOUND")
            print(f"   Market shows high efficiency")

            print(f"\nRECOMMENDATIONS:")
            print(f"   1. Decrease min_profit_percentage to 0.05%")
            print(f"   2. Decrease min_pool_liquidity to $50")
            if max_route_length <= 3:
                print(f"   3. Increase max_route_length to 4-5 for longer chains")
            print(f"   4. Try during high volatility periods")

        print(f"\nTOP TOKENS BY LIQUIDITY:")
        if pool_infos:
            token_liquidity = [(symbol, info['liquidity']) for symbol, info in pool_infos.items()]
            token_liquidity.sort(key=lambda x: x[1], reverse=True)

            for symbol, liquidity in token_liquidity[:5]:
                print(f"   • {symbol}: ${liquidity:,.0f}")
        else:
            print(f"   No liquidity data")

        print(f"\nAnalysis completed: {datetime.now().strftime('%H:%M:%S')}")

        return StonFiDataValue(result)

    except Exception as e:
        print(f"\nCRITICAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

        return StonFiDataValue({
            "success": False,
            "error": f"Analysis error: {str(e)}",
            "timestamp": datetime.now().isoformat()
        })
