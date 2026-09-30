"""
Zero-cloud local publish — posts directly to the VOW App running on this machine.

No internet connection required. The VOW App must be running locally.
Use this when your bot and the VOW App are on the same machine (MT4, MT5,
any local process).

Action values: LONG / SHORT / BUY / SELL
"""
import httpx

VOW_APP_URL = "http://localhost:7777/alert"


def publish_local(
    ticker: str,
    action: str,
    entry:  float,
    bot_id: str = "local",
) -> dict:
    resp = httpx.post(
        VOW_APP_URL,
        json={
            "ticker": ticker.upper(),
            "signal": action.upper(),
            "entry":  entry,
            "botId":  bot_id,
        },
        timeout=5,
    )
    resp.raise_for_status()
    return resp.json()


if __name__ == "__main__":
    result = publish_local(
        ticker="AAPL",
        action="LONG",
        entry=195.50,
        bot_id="my-local-strategy",
    )
    print(result)
