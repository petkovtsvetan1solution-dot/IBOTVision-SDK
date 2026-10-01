# IBOTVision SDK

**Institutional-grade symbol routing infrastructure. P2P message routing. Zero external dependency for enterprise.**

[![PyPI version](https://badge.fury.io/py/ibotvision-sdk.svg)](https://pypi.org/project/ibotvision-sdk/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## What is the IBOTVision SDK?


IBOTVision SDK

The IBOTVision SDK is the integration layer for the Enterprise — Full Stack Package. It is built for developers, individuals, small family firms, and small-to-medium funds that want to own and operate the complete IBOTVision technology stack as a kit — on their own hardware, under their own control.

Use the SDK to connect your own bots, strategies, and multi-account systems to the IBOTVision symbol infrastructure. The rest of the stack — IBOTVision Gateway, NATS JetStream mesh, VOW App, Data Centre, and Web UI — runs natively in your environment. Execution is broker-agnostic: connect through Interactive Brokers, Tradier, Alpaca, TradeStation, OANDA, Saxo Bank, Fortex, or any FIX-compliant broker. Market data is institutional-grade: Bloomberg B-PIPE, LSEG Refinitiv, FactSet, ICE Data Services, Nasdaq Data Link, Cboe, Polygon, and similar providers feed directly into your NATS mesh. Futu and Finviz remain optional sandbox connectors for prototyping only.

The SDK is not a consumer product. End users who want to follow symbols download the VOW App from ibotvision.com. The SDK is for the builders and operators behind those symbols — individual developers, family offices, and emerging or small-to-medium funds that want to deploy, control, and own the full infrastructure themselves.



---

## Two Deployment Models


Two Deployment Models
Hosted Gateway (Developer / Marketplace)
Your bot publishes symbols to the IBOTVision-hosted gateway. Subscribed VOW App users receive and execute those symbols on their own broker accounts. You never touch their money or orders.

Self-Hosted (Enterprise — Full Stack Package)
You run the entire IBOTVision stack — Gateway, NATS JetStream mesh, VOW App, Data Centre, Web UI — on your own hardware. Full control over data, execution, and infrastructure.
```
Your bot  ──►  POST /api/v1/publish  ──►  IBOTVision Gateway
                                                │
                                         NATS Symbol Mesh
                                         (3-node, JetStream)
                                                │
                                  ┌─────────────┴──────────────┐
                                  ▼                            ▼
                           Subscriber A                  Subscriber B
                           VOW App                       VOW App
                           (their broker)                (their broker)
```

**What crosses the network:** your symbol payload only.
**What never leaves each subscriber:** their orders, positions, credentials.

---

### Self-Hosted Enterprise (Full Stack, Zero External Dependency)

Enterprise clients purchase the full IBOTVision package and deploy it entirely on
their own hardware. No IBOTVision cloud involvement. No keepalives. No external
dependency of any kind.

```
┌──────────────────────────────────────────────────────────────────────┐
│                     YOUR OWN INFRASTRUCTURE                          │
│                                                                      │
│  Your Bot / Strategy  ──►  IBOTVision Gateway  ──►  NATS Mesh       │
│                            (your own server)    (your own nodes)    │
│                                                        │             │
│                              ┌─────────────────────────┤            │
│                              ▼                         ▼            │
│                        Account A                  Account B         │
│                        VOW App                    VOW App           │
│                        (local IBKR)               (local IBKR)     │
│                                                                      │
│  Data Centre (your own hardware)                                     │
│  ├── Market data collectors  ──►  NATS                              │
│  ├── Basket builder                                                  │
│  └── EOD persistence                                                 │
└──────────────────────────────────────────────────────────────────────┘
```

Use case: in-house multi-account, multi-strategy orchestration. No subscription
to IBOTVision services required. You own and operate every node.

→ **Enterprise licensing:** [ibotvision.com](https://ibotvision.com)

---

## Quick Start — Publishing a Symbol

### 1. Get a publisher key

Register at [ibotvision.com](https://ibotvision.com) or via the API:

```bash
curl -X POST https://api.ibotvision.com/api/v1/publisher/register \
  -H "Content-Type: application/json" \
  -d '{"display_name": "My Strategy Bot", "email": "you@example.com"}'
```

Your `vow_pub_` key is emailed to you.

### 2. Publish a symbol

```bash
curl -X POST https://api.ibotvision.com/api/v1/publish \
  -H "X-API-Key: vow_pub_YOUR_KEY_HERE" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "action": "BUY", "lots": 100, "price": 220.50}'
```

### 3. Python SDK

```bash
pip install ibotvision-sdk
```

```python
from ibotvision import PublisherClient

client = PublisherClient(api_key="vow_pub_YOUR_KEY_HERE")

# Publish a symbol to all your subscribers
client.publish(symbol="AAPL", action="BUY", lots=100, price=220.50)

# Publish with a comment
client.publish(
    symbol="NVDA",
    action="SELL",
    lots=50,
    price=875.00,
    comment="momentum reversal — pattern confirmed",
)
```

---

## P2P Symbol Routing

IBOTVision uses a peer-to-peer symbol model. Your symbol travels from your bot
into the NATS mesh and is delivered directly to each subscriber's VOW App, which
then places the order on that subscriber's own broker account.

**The platform is the routing fabric only.** It never holds a position, never
places an order, never touches subscriber funds.

Each subscriber's VOW App connects to:
- Their own NATS subject (scoped to their UID and subscribed bot channel)
- Their own IB Gateway running locally on their machine
- Their own IBKR account

A subscriber can follow symbols from multiple published bots simultaneously.
Each bot channel is a separate NATS subject, isolated by publisher UID and bot ID.

---

## Local Webhook (Zero Cloud)

For setups where your bot and the VOW App run on the same machine — MT4, MT5,
TradingView desktop, or any local process — you can bypass the cloud gateway
entirely using the VOW App's local webhook:

```bash
# POST directly to the locally running VOW App — no internet required
curl -X POST http://localhost:7777/alert \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL", "symbol": "LONG", "entry": 195.50}'
```

```python
import httpx

response = httpx.post("http://localhost:7777/alert", json={
    "ticker": "AAPL",
    "symbol": "LONG",   # LONG / SHORT / BUY / SELL
    "entry":  195.50,
    "botId":  "my-local-strategy",
})
```

Symbol values: `LONG` / `SHORT` / `BUY` / `SELL`

---


## Symbol Payload Reference

```json
{
  "symbol":  "AAPL",
  "action":  "BUY",
  "lots":    100,
  "price":   220.50,
  "comment": "optional — passed through to subscriber logs"
}
```

| Field | Required | Values | Notes |
|-------|----------|--------|-------|
| `symbol` | ✅ | e.g. `"AAPL"` | Ticker symbol |
| `action` | ✅ | `"BUY"` / `"SELL"` | Symbol direction |
| `lots` | ✅ | number | Share count or contract size |
| `price` | ✅ | number | Reference price at symbol time |
| `comment` | — | string | Optional note — logged, not traded |

---

## VOW App — Subscriber Side

Subscribers download and install the **VOW App** — a standalone desktop application
for macOS, Windows, and Linux. It:

- Connects to their own IB Gateway (local process)
- Authenticates to the NATS mesh via the IBOTVision gateway
- Subscribes to their chosen bot symbol channels from the Marketplace
- Applies their own execution rules (size, order type, stop-loss, take-profit)
- Places orders on their own IBKR account only

→ **VOW App download:** [ibotvision.com](https://ibotvision.com)

The platform never touches subscriber accounts. Execution is always local to
the subscriber's machine.

---

## Integration Examples

| File | What it demonstrates |
|------|----------------------|
| `examples/publish_symbol.py` | Minimal symbol publish |
| `examples/tradingview_webhook.py` | Receive TradingView alerts and forward to IBOTVision |
| `examples/mt4_bridge.py` | Forward MT4/MT5 EA symbols |
| `examples/local_webhook.py` | Zero-cloud local symbol via VOW App |

| `examples/multi_account.py` | Enterprise multi-account symbol fan-out |

---

## Authentication Reference

| Key format | Scope | How to get |
|---|---|---|
| `vow_pub_...` | Publish symbols to the platform | Register at ibotvision.com or via `/api/v1/publisher/register` |
| Firebase token | VOW App user authentication | Handled by the VOW App — not needed for SDK |

---

## Enterprise — Full Stack Package

Enterprise clients receive:

| Component | What it is |
|---|---|
| IBOTVision Gateway | FastAPI symbol router — authenticated entrance to your NATS mesh |
| NATS Mesh | 3-node JetStream cluster — runs natively on each of your machines |
| VOW App | Desktop execution app — connects to your local IB Gateway |
| Data Centre | Market data pipeline — Futu/Finviz collectors → your NATS |
| Web UI | React/DuckDB strategy builder and backtest dashboard |

All components run on your hardware. No external cloud dependency.
The NATS mesh connects your nodes via Tailscale (or your own VPN).

**To connect your own bots to a self-hosted stack, point the SDK at your
own gateway URL:**

```python
from ibotvision import PublisherClient

client = PublisherClient(
    api_key="vow_pub_YOUR_KEY_HERE",
    gateway_url="https://your-own-gateway.internal",
)
client.publish(symbol="AAPL", action="BUY", lots=100, price=220.50)
```

---

## Contributing

SDK contributions welcome: language clients (Go, Node.js, Rust), broker connector
examples, integration guides. The core platform components (Gateway, VOW App,
Data Centre) are closed-source and not open to external contributions.

```bash
git checkout -b feature/nodejs-client
git push origin feature/nodejs-client
# open a pull request
```

Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting.

---

## Security

To report a vulnerability, see [SECURITY.md](SECURITY.md).

---

## License

MIT — see [LICENSE](LICENSE)

---

## Links & Resources

- 🌐 **Official Website & Commercial Licenses:** [ibotvision.com](https://ibotvision.com)
- 💾 **Core Engine Runtime (Closed-Source Binary):** [Download Center](https://ibotvision.com)
- 📚 **SDK Documentation & API Reference:** [ibotvision.com/docs/sdk](https://ibotvision.com/docs/sdk)
- 🛒 **Strategy & Extensions Marketplace:** [ibotvision.com/marketplace](https://ibotvision.com/marketplace)
- 💬 **Developer Community:** Discord coming soon

---

IBOT Limited · Registered in Bulgaria (EU) · Company Registration No. [207152547]

P2P message routing with local execution. Near-Zero external dependencies—Cloudflare is required only for [DNS / ingress / signaling / auth / relay], not for routing or execution.
