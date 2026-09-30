"""
Minimal example — publish a symbol to all your subscribers.
"""
from ibotvision import PublisherClient
from ibotvision.error_handling import AuthErrorHandling, IBOTVisionErrorHandling, PublishErrorHandling

client = PublisherClient(api_key="vow_pub_YOUR_KEY_HERE")

try:
    result = client.publish(
        symbol="AAPL",
        action="BUY",
        lots=100,
        price=220.50,
        comment="breakout confirmed",
    )
    print("Published:", result)

except AuthErrorHandling as e:
    print("Auth failed — check your API key:", e)
except PublishErrorHandling as e:
    print("Publish rejected:", e)
except IBOTVisionErrorHandling as e:
    print("Error:", e)
