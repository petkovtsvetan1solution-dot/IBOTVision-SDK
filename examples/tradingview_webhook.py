"""
TradingView webhook bridge — receives TradingView alerts and forwards them
to IBOTVision as symbol publishes.

Setup:
  1. pip install uvicorn fastapi
  2. Run: python tradingview_webhook.py
  3. In TradingView alert settings set webhook URL to:
       http://YOUR-SERVER-IP:8080/alert

TradingView alert message (JSON body):
  {
    "symbol":  "{{ticker}}",
    "action":  "{{strategy.order.action}}",
    "price":   {{close}},
    "lots":    100
  }
"""
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from ibotvision import PublisherClient
from ibotvision.error_handling import AuthErrorHandling, IBOTVisionErrorHandling, PublishErrorHandling

app    = FastAPI()
client = PublisherClient(api_key="vow_pub_YOUR_KEY_HERE")


@app.post("/alert")
async def receive_alert(request: Request):
    body   = await request.json()
    symbol = body.get("symbol", "").upper()
    action = body.get("action", "").upper()
    price  = float(body.get("price", 0))
    lots   = float(body.get("lots", 100))

    if not symbol or action not in ("BUY", "SELL"):
        return JSONResponse(status_code=400, content={
            "ok": False, "error": "symbol and action (BUY/SELL) required"
        })

    try:
        result = client.publish(symbol=symbol, action=action, lots=lots, price=price)
        return {"ok": True, "result": result}
    except AuthErrorHandling as e:
        return JSONResponse(status_code=401, content={"ok": False, "error": str(e)})
    except PublishErrorHandling as e:
        return JSONResponse(status_code=422, content={"ok": False, "error": str(e)})
    except IBOTVisionErrorHandling as e:
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
