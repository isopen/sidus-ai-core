from datetime import datetime, timedelta

SHOW_FULL_ADDRESSES = True

WALLETS = [
    ("Main Wallet", "UQDYzZmfsrGzhObKJUw4gzdeIxEai3jAFbiGKGwxvxHinf4K"),
    ("DeFi Wallet", "UQDYzZmfsrGzhObKJUw4gzdeIxEai3jAFbiGKGwxvxHinf4K"),
    ("Farm Wallet", "UQDYzZmfsrGzhObKJUw4gzdeIxEai3jAFbiGKGwxvxHinf4K")
]

POPULAR_TOKENS = [
    ("STON", "EQA2kCVNwVsil2EM2mB0SkXytxCqQjS4mttjDpnXmwG9T6bO"),
    ("NOT", "EQAvlWFDxGF2lXm67y4yzC17wYKD9A0guwPkMs1gOsM__NOT"),
    ("USDT", "EQCxE6mUtQJKFnGfaROTKOt1lZbDiiX1kCixRv7Nw2Id_sDs"),
    ("GRAM", "EQC47093oX5Xhb0xuk2lCr2RhS8rj-vul61u4W2UH5ORmG_O"),
    ("EVAA", "EQBKMfjX_a_dsOLm-juxyVZytFP7_KKnzGv6J01kGc72gVBp")
]

POPULAR_POOLS = [
    ("TON/USDT", "EQCGScrZe1xbyWqWDvdI6mzP-GAcAWFv6ZXuaJOuSqemxku4"),
    ("STON/USDT", "EQBbsMjyLRj-xJE4eqMbtgABvPq34TF_hwiAGEAUGUb5sNGO"),
    ("NOT/TON", "EQCaY8Ifl2S6lRBMBJeY35LIuMXPc8JfItWG4tl7lBGrSoR2"),
    ("GRAM/TON", "EQASBZLwa2vfdsgoDF2w96pdccBJJRxDNXXPUL7NMm0WdnMx")
]

ARBITRAGE_CONFIG = {
    "min_profit_usd": 10.0,
    "min_tvl": 1000.0,
    "max_price_diff": 0.10
}

TIME_CONFIG = {
    "since_days": 1,
    "until": datetime.now().isoformat(),
    "since": (datetime.now() - timedelta(days=1)).isoformat()
}
