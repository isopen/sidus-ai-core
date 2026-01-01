from typing import Dict, Any
from datetime import datetime

class OKXDataValue:
    def __init__(self, data: Dict[str, Any]):
        self.value = data

def get_instruments_skill(context: Dict[str, Any]) -> OKXDataValue:
    print("Starting get_instruments_skill...")

    inst_type = context.get('inst_type', 'SPOT')
    uly = context.get('uly')
    inst_family = context.get('inst_family')
    inst_id = context.get('inst_id')

    try:
        client = context.get('okx_client')

        if not client:
            result = {"success": False, "error": "OKX client not available"}
            return OKXDataValue(result)

        try:
            response = client.get_instruments(
                inst_type=inst_type,
                uly=uly,
                inst_family=inst_family,
                inst_id=inst_id
            )

            if response.get('code') == '0':
                instruments = response.get('data', [])

                analysis_result = {
                    "success": True,
                    "code": "0",
                    "inst_type": inst_type,
                    "instruments_count": len(instruments),
                    "instruments": [],
                    "summary": {
                        "spot_count": 0,
                        "swap_count": 0,
                        "futures_count": 0,
                        "option_count": 0,
                        "live_count": 0,
                        "suspended_count": 0
                    },
                    "timestamp": datetime.now().isoformat()
                }

                for instrument in instruments[:100]:
                    inst_type_instr = instrument.get('instType', '')
                    state = instrument.get('state', '')

                    if inst_type_instr == 'SPOT':
                        analysis_result["summary"]["spot_count"] += 1
                    elif inst_type_instr == 'SWAP':
                        analysis_result["summary"]["swap_count"] += 1
                    elif inst_type_instr == 'FUTURES':
                        analysis_result["summary"]["futures_count"] += 1
                    elif inst_type_instr == 'OPTION':
                        analysis_result["summary"]["option_count"] += 1

                    if state == 'live':
                        analysis_result["summary"]["live_count"] += 1
                    elif state == 'suspend':
                        analysis_result["summary"]["suspended_count"] += 1

                    instrument_data = {
                        "instId": instrument.get('instId', ''),
                        "instType": inst_type_instr,
                        "baseCcy": instrument.get('baseCcy', ''),
                        "quoteCcy": instrument.get('quoteCcy', ''),
                        "pair": f"{instrument.get('baseCcy', '')}/{instrument.get('quoteCcy', '')}",
                        "state": state,
                        "minSz": instrument.get('minSz', '0'),
                        "tickSz": instrument.get('tickSz', '0'),
                        "lotSz": instrument.get('lotSz', '0'),
                        "lever": instrument.get('lever', ''),
                        "listTime": instrument.get('listTime', ''),
                        "listTimeReadable": datetime.fromtimestamp(int(instrument.get('listTime', '0'))/1000).strftime('%Y-%m-%d %H:%M:%S') if instrument.get('listTime') else '',
                        "maxLmtSz": instrument.get('maxLmtSz', ''),
                        "maxMktSz": instrument.get('maxMktSz', ''),
                        "maxTriggerSz": instrument.get('maxTriggerSz', ''),
                        "maxTwapSz": instrument.get('maxTwapSz', ''),
                        "maxIcebergSz": instrument.get('maxIcebergSz', ''),
                        "maxLmtAmt": instrument.get('maxLmtAmt', ''),
                        "maxMktAmt": instrument.get('maxMktAmt', ''),
                        "maxStopSz": instrument.get('maxStopSz', ''),
                        "category": instrument.get('category', ''),
                        "alias": instrument.get('alias', ''),
                        "settleCcy": instrument.get('settleCcy', ''),
                        "ctVal": instrument.get('ctVal', ''),
                        "ctMult": instrument.get('ctMult', ''),
                        "ctValCcy": instrument.get('ctValCcy', ''),
                        "expTime": instrument.get('expTime', ''),
                        "optType": instrument.get('optType', ''),
                        "stk": instrument.get('stk', ''),
                        "uly": instrument.get('uly', ''),
                        "instFamily": instrument.get('instFamily', ''),
                        "openType": instrument.get('openType', ''),
                        "preMktSwTime": instrument.get('preMktSwTime', ''),
                        "auctionEndTime": instrument.get('auctionEndTime', ''),
                        "futureSettlement": instrument.get('futureSettlement', False),
                        "groupId": instrument.get('groupId', '')
                    }

                    analysis_result["instruments"].append(instrument_data)

                analysis_result["instruments"].sort(key=lambda x: x["instId"])

                print(f"✅ Instruments analysis: Found {len(instruments)} instruments")
                print(f"   Spot: {analysis_result['summary']['spot_count']}")
                print(f"   Swap: {analysis_result['summary']['swap_count']}")
                print(f"   Futures: {analysis_result['summary']['futures_count']}")
                print(f"   Options: {analysis_result['summary']['option_count']}")
                print(f"   Live: {analysis_result['summary']['live_count']}")
                print(f"   Suspended: {analysis_result['summary']['suspended_count']}")

                if analysis_result["instruments"]:
                    print(f"\nTop 5 instruments:")
                    for i, instr in enumerate(analysis_result["instruments"][:5]):
                        print(f"   {i+1}. {instr['instId']} ({instr['state']}) - Min: {instr['minSz']}, Tick: {instr['tickSz']}")

            else:
                analysis_result = {
                    "success": False,
                    "code": response.get('code'),
                    "error": response.get('msg', 'Unknown error'),
                    "timestamp": datetime.now().isoformat()
                }
                print(f"❌ Instruments API error: {response.get('msg')}")

            return OKXDataValue(analysis_result)

        except Exception as e:
            print(f"Error getting instruments: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to get instruments: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return OKXDataValue(analysis_result)

    except Exception as e:
        print(f"Error in get_instruments_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return OKXDataValue(result)

def get_server_time_skill(context: Dict[str, Any]) -> OKXDataValue:
    print("Starting get_server_time_skill...")

    try:
        client = context.get('okx_client')

        if not client:
            result = {"success": False, "error": "OKX client not available"}
            return OKXDataValue(result)

        try:
            response = client.get_server_time()

            if response.get('code') == '0':
                data = response.get('data', [{}])[0] if response.get('data') else {}
                ts = data.get('ts', '')

                if ts:
                    timestamp_int = int(ts)
                    server_time = datetime.fromtimestamp(timestamp_int / 1000)
                    local_time = datetime.now()
                    time_diff = server_time - local_time

                    analysis_result = {
                        "success": True,
                        "code": "0",
                        "server_timestamp": ts,
                        "server_time": server_time.isoformat(),
                        "server_time_readable": server_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                        "local_time": local_time.isoformat(),
                        "local_time_readable": local_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                        "time_difference_ms": time_diff.total_seconds() * 1000,
                        "time_difference_formatted": f"{time_diff.total_seconds() * 1000:.0f} ms",
                        "server_in_sync": abs(time_diff.total_seconds()) < 5,
                        "timestamp": datetime.now().isoformat()
                    }

                    print(f"✅ Server time: {analysis_result['server_time_readable']}")
                    print(f"   Local time: {analysis_result['local_time_readable']}")
                    print(f"   Time difference: {analysis_result['time_difference_formatted']}")
                    print(f"   In sync: {'✅ Yes' if analysis_result['server_in_sync'] else '❌ No'}")

                else:
                    analysis_result = {
                        "success": False,
                        "error": "No timestamp in response",
                        "response": response,
                        "timestamp": datetime.now().isoformat()
                    }
                    print(f"❌ No timestamp in response")
            else:
                analysis_result = {
                    "success": False,
                    "code": response.get('code'),
                    "error": response.get('msg', 'Unknown error'),
                    "timestamp": datetime.now().isoformat()
                }
                print(f"❌ Server time API error: {response.get('msg')}")

            return OKXDataValue(analysis_result)

        except Exception as e:
            print(f"Error getting server time: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to get server time: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return OKXDataValue(analysis_result)

    except Exception as e:
        print(f"Error in get_server_time_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return OKXDataValue(result)

def get_position_tiers_skill(context: Dict[str, Any]) -> OKXDataValue:
    print("Starting get_position_tiers_skill...")

    inst_type = context.get('inst_type', 'SWAP')
    uly = context.get('uly')
    inst_family = context.get('inst_family')
    inst_id = context.get('inst_id')
    td_mode = context.get('td_mode', 'cross')

    try:
        client = context.get('okx_client')

        if not client:
            result = {"success": False, "error": "OKX client not available"}
            return OKXDataValue(result)

        try:
            response = client.get_position_tiers(
                inst_type=inst_type,
                uly=uly,
                inst_family=inst_family,
                inst_id=inst_id,
                td_mode=td_mode
            )

            if response.get('code') == '0':
                tiers = response.get('data', [])

                analysis_result = {
                    "success": True,
                    "code": "0",
                    "inst_type": inst_type,
                    "td_mode": td_mode,
                    "tiers_count": len(tiers),
                    "tiers": [],
                    "summary": {
                        "total_tiers": len(tiers),
                        "unique_instruments": len(set(t.get('instId', '') for t in tiers)),
                        "max_lever_range": "",
                        "margin_requirements": []
                    },
                    "timestamp": datetime.now().isoformat()
                }

                max_levers = []
                imr_values = []
                mmr_values = []

                for tier in tiers:
                    inst_id_tier = tier.get('instId', '')
                    tier_num = tier.get('tier', '')
                    max_lever = tier.get('maxLever', '')
                    imr = tier.get('imr', '')
                    mmr = tier.get('mmr', '')
                    max_sz = tier.get('maxSz', '')
                    min_sz = tier.get('minSz', '')
                    base_max_loan = tier.get('baseMaxLoan', '')
                    quote_max_loan = tier.get('quoteMaxLoan', '')

                    if max_lever:
                        try:
                            max_levers.append(float(max_lever))
                        except:
                            pass

                    if imr:
                        try:
                            imr_values.append(float(imr))
                        except:
                            pass

                    if mmr:
                        try:
                            mmr_values.append(float(mmr))
                        except:
                            pass

                    tier_data = {
                        "instId": inst_id_tier,
                        "tier": tier_num,
                        "maxLever": max_lever,
                        "maxLever_numeric": float(max_lever) if max_lever else 0,
                        "imr": imr,
                        "imr_numeric": float(imr) if imr else 0,
                        "imr_percentage": f"{float(imr)*100:.2f}%" if imr else "",
                        "mmr": mmr,
                        "mmr_numeric": float(mmr) if mmr else 0,
                        "mmr_percentage": f"{float(mmr)*100:.2f}%" if mmr else "",
                        "maxSz": max_sz,
                        "maxSz_numeric": float(max_sz) if max_sz else 0,
                        "minSz": min_sz,
                        "minSz_numeric": float(min_sz) if min_sz else 0,
                        "baseMaxLoan": base_max_loan,
                        "baseMaxLoan_numeric": float(base_max_loan) if base_max_loan else 0,
                        "quoteMaxLoan": quote_max_loan,
                        "quoteMaxLoan_numeric": float(quote_max_loan) if quote_max_loan else 0,
                        "optMgnFactor": tier.get('optMgnFactor', ''),
                        "uly": tier.get('uly', ''),
                        "instFamily": tier.get('instFamily', '')
                    }

                    analysis_result["tiers"].append(tier_data)

                analysis_result["tiers"].sort(key=lambda x: (x["instId"], int(x["tier"]) if x["tier"].isdigit() else 0))

                if max_levers:
                    analysis_result["summary"]["max_lever_range"] = f"{min(max_levers)}x - {max(max_levers)}x"

                if imr_values:
                    analysis_result["summary"]["margin_requirements"] = {
                        "min_imr": f"{min(imr_values)*100:.2f}%",
                        "max_imr": f"{max(imr_values)*100:.2f}%",
                        "avg_imr": f"{(sum(imr_values)/len(imr_values))*100:.2f}%"
                    }

                print(f"✅ Position tiers analysis: Found {len(tiers)} tiers")
                print(f"   Instruments: {analysis_result['summary']['unique_instruments']}")
                print(f"   Max leverage range: {analysis_result['summary']['max_lever_range']}")

                if analysis_result["tiers"]:
                    instruments = {}
                    for tier in analysis_result["tiers"]:
                        inst_id = tier["instId"]
                        if inst_id not in instruments:
                            instruments[inst_id] = []
                        instruments[inst_id].append(tier)

                    print(f"\nTop 3 instruments by max leverage:")
                    for i, (inst_id, tiers_list) in enumerate(list(instruments.items())[:3]):
                        max_tier = max(tiers_list, key=lambda x: x["maxLever_numeric"])
                        print(f"   {i+1}. {inst_id}: Max {max_tier['maxLever']}x leverage, IMR: {max_tier['imr_percentage']}")

            else:
                analysis_result = {
                    "success": False,
                    "code": response.get('code'),
                    "error": response.get('msg', 'Unknown error'),
                    "timestamp": datetime.now().isoformat()
                }
                print(f"❌ Position tiers API error: {response.get('msg')}")

            return OKXDataValue(analysis_result)

        except Exception as e:
            print(f"Error getting position tiers: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to get position tiers: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return OKXDataValue(analysis_result)

    except Exception as e:
        print(f"Error in get_position_tiers_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return OKXDataValue(result)

def get_insurance_fund_skill(context: Dict[str, Any]) -> OKXDataValue:
    print("Starting get_insurance_fund_skill...")

    inst_type = context.get('inst_type', 'SWAP')
    uly = context.get('uly')
    inst_family = context.get('inst_family')
    ccy = context.get('ccy')
    before = context.get('before')
    after = context.get('after')
    limit = context.get('limit', '100')

    try:
        client = context.get('okx_client')

        if not client:
            result = {"success": False, "error": "OKX client not available"}
            return OKXDataValue(result)

        try:
            response = client.get_insurance_fund(
                inst_type=inst_type,
                uly=uly,
                inst_family=inst_family,
                ccy=ccy,
                before=before,
                after=after,
                limit=limit
            )

            if response.get('code') == '0':
                data_list = response.get('data', [])

                analysis_result = {
                    "success": True,
                    "code": "0",
                    "inst_type": inst_type,
                    "insurance_funds": [],
                    "summary": {
                        "total_funds": len(data_list),
                        "total_amount": 0,
                        "currencies": set(),
                        "largest_fund": {"amount": 0, "currency": "", "type": ""},
                        "recent_updates": []
                    },
                    "timestamp": datetime.now().isoformat()
                }

                total_amount = 0

                for fund_data in data_list:
                    inst_type_fund = fund_data.get('instType', '')
                    inst_family_fund = fund_data.get('instFamily', '')
                    total_fund = fund_data.get('total', '0')

                    try:
                        total_amount_val = float(total_fund)
                        total_amount += total_amount_val
                    except:
                        total_amount_val = 0

                    details = fund_data.get('details', [])

                    fund_info = {
                        "instType": inst_type_fund,
                        "instFamily": inst_family_fund,
                        "total": total_fund,
                        "total_numeric": total_amount_val,
                        "total_formatted": f"{total_amount_val:,.2f}" if total_amount_val >= 1000 else f"{total_amount_val:,.4f}",
                        "details_count": len(details),
                        "details": []
                    }

                    for detail in details[:10]:
                        balance = detail.get('balance', '0')
                        ccy_detail = detail.get('ccy', '')
                        ts = detail.get('ts', '')
                        adl_type = detail.get('adlType', '')
                        detail_type = detail.get('type', '')
                        amt = detail.get('amt', '')
                        max_bal = detail.get('maxBal', '')
                        max_bal_ts = detail.get('maxBalTs', '')

                        if ccy_detail:
                            analysis_result["summary"]["currencies"].add(ccy_detail)

                        try:
                            balance_val = float(balance)
                            if balance_val > analysis_result["summary"]["largest_fund"]["amount"]:
                                analysis_result["summary"]["largest_fund"] = {
                                    "amount": balance_val,
                                    "currency": ccy_detail,
                                    "type": detail_type
                                }
                        except:
                            balance_val = 0

                        ts_readable = ""
                        if ts:
                            try:
                                ts_int = int(ts)
                                ts_readable = datetime.fromtimestamp(ts_int / 1000).strftime('%Y-%m-%d %H:%M:%S')
                            except:
                                pass

                        detail_info = {
                            "balance": balance,
                            "balance_numeric": balance_val,
                            "balance_formatted": f"{balance_val:,.2f}" if balance_val >= 1000 else f"{balance_val:,.4f}",
                            "currency": ccy_detail,
                            "timestamp": ts,
                            "timestamp_readable": ts_readable,
                            "adl_type": adl_type,
                            "type": detail_type,
                            "amount": amt,
                            "amount_numeric": float(amt) if amt else 0,
                            "max_balance": max_bal,
                            "max_balance_numeric": float(max_bal) if max_bal else 0,
                            "max_balance_timestamp": max_bal_ts,
                            "max_balance_timestamp_readable": datetime.fromtimestamp(int(max_bal_ts)/1000).strftime('%Y-%m-%d %H:%M:%S') if max_bal_ts else ""
                        }

                        fund_info["details"].append(detail_info)

                        if ts_readable:
                            analysis_result["summary"]["recent_updates"].append({
                                "timestamp": ts_readable,
                                "currency": ccy_detail,
                                "balance": balance_val,
                                "type": detail_type
                            })

                    analysis_result["insurance_funds"].append(fund_info)

                analysis_result["summary"]["total_amount"] = total_amount
                analysis_result["summary"]["total_amount_formatted"] = f"{total_amount:,.2f}"
                analysis_result["summary"]["currencies"] = list(analysis_result["summary"]["currencies"])

                analysis_result["summary"]["recent_updates"].sort(key=lambda x: x["timestamp"], reverse=True)
                analysis_result["summary"]["recent_updates"] = analysis_result["summary"]["recent_updates"][:5]

                print(f"✅ Insurance fund analysis: Found {len(data_list)} funds")
                print(f"   Total amount: {analysis_result['summary']['total_amount_formatted']}")
                print(f"   Currencies: {', '.join(analysis_result['summary']['currencies'])}")

                if analysis_result["summary"]["largest_fund"]["amount"] > 0:
                    largest = analysis_result["summary"]["largest_fund"]
                    print(f"   Largest fund: {largest['amount']:,.2f} {largest['currency']} ({largest['type']})")

                if analysis_result["insurance_funds"]:
                    print(f"\nTop 3 funds by total amount:")
                    sorted_funds = sorted(analysis_result["insurance_funds"], key=lambda x: x["total_numeric"], reverse=True)
                    for i, fund in enumerate(sorted_funds[:3]):
                        print(f"   {i+1}. {fund['instFamily'] or fund['instType']}: {fund['total_formatted']} ({fund['details_count']} details)")

            else:
                analysis_result = {
                    "success": False,
                    "code": response.get('code'),
                    "error": response.get('msg', 'Unknown error'),
                    "timestamp": datetime.now().isoformat()
                }
                print(f"❌ Insurance fund API error: {response.get('msg')}")

            return OKXDataValue(analysis_result)

        except Exception as e:
            print(f"Error getting insurance fund: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to get insurance fund: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return OKXDataValue(analysis_result)

    except Exception as e:
        print(f"Error in get_insurance_fund_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return OKXDataValue(result)
