"""
Enterprise multi-account fan-out — publish one symbol simultaneously across
multiple subscriber groups using separate publisher keys per strategy.

Each key routes to its own isolated subscriber channel on your self-hosted
NATS mesh. Subscribers on each channel execute on their own broker accounts.
"""
from ibotvision import PublisherClient
from ibotvision.error_handling import IBOTVisionErrorHandling

GATEWAY = "https://your-own-gateway.internal"

strategies = {
    "momentum": PublisherClient(api_key="vow_pub_STRATEGY_A", gateway_url=GATEWAY),
    "mean_rev": PublisherClient(api_key="vow_pub_STRATEGY_B", gateway_url=GATEWAY),
    "breakout": PublisherClient(api_key="vow_pub_STRATEGY_C", gateway_url=GATEWAY),
}


def broadcast(symbol: str, action: str, lots: float, price: float):
    for name, client in strategies.items():
        try:
            result = client.publish(symbol=symbol, action=action, lots=lots, price=price)
            print(f"[{name}] published → {result}")
        except IBOTVisionErrorHandling as e:
            print(f"[{name}] failed: {e}")


if __name__ == "__main__":
    broadcast("NVDA", "BUY", 50, 875.00)
