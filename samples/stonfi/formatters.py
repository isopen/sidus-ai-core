def print_section(title, symbol="📊"):
    print(f"\n{symbol} {'='*60}")
    print(f"{symbol} {title}")
    print(f"{symbol} {'='*60}")

def format_currency(value):
    if value >= 1_000_000_000:
        return f"${value/1_000_000_000:.2f}B"
    elif value >= 1_000_000:
        return f"${value/1_000_000:.2f}M"
    elif value >= 1_000:
        return f"${value/1_000:.2f}K"
    else:
        return f"${value:.2f}"

def format_currency_safe(value):
    try:
        if isinstance(value, (int, float)):
            num = float(value)
        else:
            num = float(value)

        if abs(num) > 1e15:
            return f"${num:.2e}"
        elif abs(num) >= 1_000_000_000:
            return f"${num/1_000_000_000:.2f}B"
        elif abs(num) >= 1_000_000:
            return f"${num/1_000_000:.2f}M"
        elif abs(num) >= 1_000:
            return f"${num/1_000:.2f}K"
        elif abs(num) >= 0.01:
            return f"${num:.2f}"
        else:
            return f"${num:.6f}"
    except:
        return "$0.00"

def get_risk_level(score):
    if score >= 80:
        return "🟢 LOW", "Excellent rating"
    elif score >= 60:
        return "🟡 MODERATE", "Average rating"
    elif score >= 40:
        return "🟠 ELEVATED", "Below average rating"
    else:
        return "🔴 HIGH", "Poor rating"

def get_liquidity_level(liquidity_usd):
    if liquidity_usd >= 1_000_000:
        return "💧 EXCELLENT", "High liquidity"
    elif liquidity_usd >= 100_000:
        return "💧 GOOD", "Sufficient liquidity"
    elif liquidity_usd >= 10_000:
        return "⚠️  MODERATE", "Limited liquidity"
    else:
        return "🚨 LOW", "Illiquidity risk"

def get_apy_level(apy):
    if apy >= 50:
        return "🚀 VERY HIGH", "Excellent returns"
    elif apy >= 20:
        return "📈 HIGH", "Good returns"
    elif apy >= 5:
        return "📊 MODERATE", "Average returns"
    else:
        return "📉 LOW", "Low returns"

def get_volume_level(volume_tvl_ratio):
    if volume_tvl_ratio >= 1.0:
        return "🔥 HIGH", "Excellent activity"
    elif volume_tvl_ratio >= 0.5:
        return "📊 MODERATE", "Good activity"
    elif volume_tvl_ratio >= 0.1:
        return "⚠️  LOW", "Limited activity"
    else:
        return "💤 VERY LOW", "Low activity"

def analyze_pool_health(pool_data):
    health_score = pool_data.get("health_score", 0)
    deprecated = pool_data.get("deprecated", False)
    tvl = pool_data.get("tvl_usd", 0)

    if deprecated:
        return "🔴 DEPRECATED", f"TVL: {format_currency(tvl)}"
    elif health_score >= 80:
        return "🟢 EXCELLENT", f"TVL: {format_currency(tvl)}"
    elif health_score >= 60:
        return "🟡 GOOD", f"TVL: {format_currency(tvl)}"
    elif health_score >= 40:
        return "🟠 MODERATE", f"TVL: {format_currency(tvl)}"
    else:
        return "🔴 POOR", f"TVL: {format_currency(tvl)}"

def format_percentage(value):
    try:
        num = float(value)
        if num >= 1:
            return f"{num:.1f}%"
        elif num >= 0.01:
            return f"{num:.2f}%"
        else:
            return f"{num:.4f}%"
    except:
        return "0.00%"
