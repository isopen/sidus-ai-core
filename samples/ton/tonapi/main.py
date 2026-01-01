import os
import sys
import time
sys.path.append(os.environ.get('SIDUS_AI_CORE_PATH', '.'))
from sidusai.plugins.ton.tonapi import create_tonapi_agent

def main():
    print("TON API")
    print("=" * 60)

    api_key = os.environ.get('TONAPI_API_KEY', '')
    agent = create_tonapi_agent(api_key=api_key)

    print(f"\n1. ACCOUNT INFORMATION")
    print("-" * 40)
    result = agent.get_account(
        account_id="UQDYzZmfsrGzhObKJUw4gzdeIxEai3jAFbiGKGwxvxHinf4K"
    )
    print(f"Account data: {'Success' if result.get('success') else 'Failed'}")
    if result.get('success'):
        data = result.get('data', {})
        balance = data.get('balance', 0)
        print(f"Balance: {balance / 1000000000:.6f} TON")
        print(f"Status: {data.get('status', 'Not available')}")
        print(f"Name: {data.get('name', 'Not available')}")
    time.sleep(2)

    print("\n2. BULK ACCOUNTS")
    print("-" * 40)
    result = agent.get_accounts_bulk(
        account_ids=[
            "UQDYzZmfsrGzhObKJUw4gzdeIxEai3jAFbiGKGwxvxHinf4K",
            "EQBG-g6ahkAUGWpefWbx-D_9sQ8oWbvy6puuq78U2c4NUDFS",
            "EQBKMfjX_a_dsOLm-juxyVZytFP7_KKnzGv6J01kGc72gVBp"
        ]
    )
    print(f"Bulk accounts: {'Success' if result.get('success') else 'Failed'}")
    if result.get('success'):
        data = result.get('data', {})
        accounts = data.get('accounts', [])
        print(f"Found {len(accounts)} accounts")
    time.sleep(2)

    print("\n3. ACCOUNT JETTONS BALANCES")
    print("-" * 40)
    result = agent.get_account_jettons_balances(
        account_id="UQDYzZmfsrGzhObKJUw4gzdeIxEai3jAFbiGKGwxvxHinf4K",
        currencies=["ton", "usd"]
    )
    print(f"Jetton balances: {'Success' if result.get('success') else 'Failed'}")
    if result.get('success'):
        data = result.get('data', {})
        balances = data.get('balances', [])
        print(f"{len(balances)} jetton balances")
    time.sleep(2)

    print("\n4. ACCOUNT NFT ITEMS")
    print("-" * 40)
    result = agent.get_account_nft_items(
        account_id="UQDYzZmfsrGzhObKJUw4gzdeIxEai3jAFbiGKGwxvxHinf4K",
        limit=10,
        offset=0
    )
    print(f"NFT items: {'Success' if result.get('success') else 'Failed'}")
    if result.get('success'):
        data = result.get('data', {})
        nft_items = data.get('nft_items', [])
        print(f"{len(nft_items)} NFT items")
    time.sleep(2)

    print("\n5. ACCOUNT EVENTS")
    print("-" * 40)
    result = agent.get_account_events(
        account_id="UQDYzZmfsrGzhObKJUw4gzdeIxEai3jAFbiGKGwxvxHinf4K",
        limit=10
    )
    print(f"Account events: {'Success' if result.get('success') else 'Failed'}")
    if result.get('success'):
        data = result.get('data', {})
        events = data.get('events', [])
        print(f"{len(events)} events found")
    time.sleep(2)

    print("\n6. ACCOUNT SUBSCRIPTIONS")
    print("-" * 40)
    result = agent.get_account_subscriptions(
        account_id="UQDYzZmfsrGzhObKJUw4gzdeIxEai3jAFbiGKGwxvxHinf4K"
    )
    print(f"Subscriptions: {'Success' if result.get('success') else 'Failed'}")
    if result.get('success'):
        data = result.get('data', {})
        subscriptions = data.get('subscriptions', [])
        print(f"{len(subscriptions)} subscriptions")
    time.sleep(2)

    print("\n7. NFT COLLECTIONS")
    print("-" * 40)
    result = agent.get_nft_collections(
        limit=10,
        offset=0
    )
    print(f"NFT collections: {'Success' if result.get('success') else 'Failed'}")
    if result.get('success'):
        data = result.get('data', {})
        collections = data.get('nft_collections', [])
        print(f"{len(collections)} collections")
    time.sleep(2)

    print("\n8. NFT COLLECTION ITEMS")
    print("-" * 40)
    result = agent.get_nft_collection_items(
        collection_id="EQBG-g6ahkAUGWpefWbx-D_9sQ8oWbvy6puuq78U2c4NUDFS",
        limit=10,
        offset=0
    )
    print(f"Collection items: {'Success' if result.get('success') else 'Failed'}")
    if result.get('success'):
        data = result.get('data', {})
        items = data.get('nft_items', [])
        print(f"{len(items)} items in collection")
    time.sleep(2)

    print("\n9. NFT ITEMS BULK")
    print("-" * 40)
    collection_items_result = agent.get_nft_collection_items(
        collection_id="EQBG-g6ahkAUGWpefWbx-D_9sQ8oWbvy6puuq78U2c4NUDFS",
        limit=3,
        offset=0
    )

    if collection_items_result.get('success'):
        data = collection_items_result.get('data', {})
        nft_items = data.get('nft_items', [])
        nft_addresses = [item.get('address', '') for item in nft_items[:3] if item.get('address')]

        if nft_addresses:
            result = agent.get_nft_items_bulk(
                nft_addresses=nft_addresses
            )
            print(f"NFT bulk: {'Success' if result.get('success') else 'Failed'}")
            if result.get('success'):
                data = result.get('data', {})
                items = data.get('nft_items', [])
                print(f"{len(items)} items retrieved")
        else:
            print("NFT bulk: Failed - No NFT addresses found")
    else:
        print("NFT bulk: Failed - Could not get collection items")
    time.sleep(2)

    print("\n10. JETTONS LIST")
    print("-" * 40)
    result = agent.get_jettons_list(
        limit=10,
        offset=0
    )
    print(f"Jettons list: {'Success' if result.get('success') else 'Failed'}")
    if result.get('success'):
        data = result.get('data', {})
        jettons = data.get('jettons', [])
        print(f"{len(jettons)} jettons")
    time.sleep(2)

    print("\n11. JETTONS BULK")
    print("-" * 40)
    result = agent.get_jettons_bulk(
        jetton_addresses=["EQBKMfjX_a_dsOLm-juxyVZytFP7_KKnzGv6J01kGc72gVBp"]
    )
    print(f"Jettons bulk: {'Success' if result.get('success') else 'Failed'}")
    if result.get('success'):
        data = result.get('data', {})
        jettons = data.get('jettons', [])
        print(f"{len(jettons)} jettons retrieved")
    time.sleep(2)

    print("\n12. JETTON HOLDERS FULL")
    print("-" * 40)
    result = agent.get_jetton_holders_full(
        jetton_id="EQBKMfjX_a_dsOLm-juxyVZytFP7_KKnzGv6J01kGc72gVBp",
        limit=10,
        offset=0
    )
    print(f"Jetton holders: {'Success' if result.get('success') else 'Failed'}")
    if result.get('success'):
        data = result.get('data', {})
        total = data.get('total', 0)
        print(f"Total holders: {total}")
    time.sleep(2)

    print("\n13. DNS INFO")
    print("-" * 40)
    result = agent.get_dns_info(
        domain_name="testertesterov.ton"
    )
    print(f"DNS info: {'Success' if result.get('success') else 'Failed'}")
    if result.get('success'):
        data = result.get('data', {})
        name = data.get('name', 'Not available')
        print(f"Domain: {name}")
    time.sleep(2)

    print("\n14. DNS RESOLVE")
    print("-" * 40)
    result = agent.dns_resolve(
        domain_name="testertesterov.ton"
    )
    print(f"DNS resolve: {'Success' if result.get('success') else 'Failed'}")
    if result.get('success'):
        print(f"DNS records retrieved")
    time.sleep(2)

    print("\n15. DOMAIN BIDS")
    print("-" * 40)
    result = agent.get_domain_bids(
        domain_name="testertesterov.ton"
    )
    print(f"Domain bids: {'Success' if result.get('success') else 'Failed'}")
    if result.get('success'):
        data = result.get('data', {})
        bids = data.get('data', [])
        print(f"{len(bids)} bids found")
    time.sleep(2)

    print("\n16. RATES FULL")
    print("-" * 40)
    result = agent.get_rates_full(
        tokens=["ton"],
        currencies=["USD", "EUR", "RUB"]
    )
    print(f"Rates: {'Success' if result.get('success') else 'Failed'}")
    time.sleep(2)

    print("\n17. CHART RATES")
    print("-" * 40)
    result = agent.get_chart_rates(
        token="EQBKMfjX_a_dsOLm-juxyVZytFP7_KKnzGv6J01kGc72gVBp",
        currency="usd",
        points_count=50
    )
    print(f"Chart rates: {'Success' if result.get('success') else 'Failed'}")
    if result.get('success'):
        data = result.get('data', {})
        points = data.get('points', [])
        print(f"{len(points)} chart points")
    time.sleep(2)

    print("\n18. MARKETS RATES")
    print("-" * 40)
    result = agent.get_markets_rates()
    print(f"Market rates: {'Success' if result.get('success') else 'Failed'}")
    if result.get('success'):
        data = result.get('data', {})
        markets = data.get('markets', [])
        print(f"{len(markets)} markets")
    time.sleep(2)

    print("\n19. STAKING POOLS")
    print("-" * 40)
    result = agent.get_staking_pools()
    print(f"Staking pools: {'Success' if result.get('success') else 'Failed'}")
    if result.get('success'):
        data = result.get('data', {})
        pools = data.get('pools', [])
        print(f"{len(pools)} pools")
    time.sleep(2)

    print("\n20. STAKING POOL INFO")
    print("-" * 40)
    result = agent.get_staking_pool_info(
        pool_address="EQCkR1cGmnsE45N4K0otPl5EnxnRakmGqeJUNua5fkWhales"
    )
    print(f"Pool info: {'Success' if result.get('success') else 'Failed'}")
    if result.get('success'):
        pool_info = result.get('pool_info', {})
        print(f"Name: {pool_info.get('name', 'Unknown')}")
        print(f"Total Staked: {pool_info.get('total_amount', 0):,.2f} TON")
        print(f"APY: {pool_info.get('apy', 0):.2f}%")
        print(f"Nominators: {pool_info.get('current_nominators', 0):,}")
    time.sleep(2)

    print("\n21. ACCOUNT NOMINATORS POOLS")
    print("-" * 40)
    result = agent.get_account_nominators_pools(
        account_id="EQAnDtu0UfrA6CDhB7JTWuO7tx7oSgRSeDbrJiKwCAwnUG1L"
    )
    time.sleep(2)

if __name__ == "__main__":
    main()
