# flowex

[![CI](https://github.com/KhavrTrading/flowex-py/actions/workflows/build.yml/badge.svg)](https://github.com/KhavrTrading/flowex-py/actions/workflows/build.yml)
[![PyPI](https://img.shields.io/pypi/v/flowex)](https://pypi.org/project/flowex/)
[![Python](https://img.shields.io/pypi/pyversions/flowex)](https://pypi.org/project/flowex/)
[![License](https://img.shields.io/github/license/KhavrTrading/flowex-py)](LICENSE)

Real-time multi-exchange crypto market data for Python — powered by Go via cgo shared library. WebSocket streaming, order book metrics, and per-symbol actor workers for Binance, Bybit, and Bitget.

No subprocess, no gRPC, no serialization overhead on the hot path. The Go runtime lives inside the Python process. Every symbol gets its own goroutine. `get_snapshot()` hits the atomic store directly.

## Install

```bash
pip install flowex
```

## Quick start

```python
import time
from flowex import Manager

mgr = Manager("binance")
mgr.subscribe(["BTCUSDT", "ETHUSDT", "SOLUSDT"])
time.sleep(2)

snap = mgr.get_snapshot("BTCUSDT")
print(snap.depth.spread_bps)
print(snap.depth.mid_price)
print(snap.candles[-1].close)

mgr.close()
```

Or use as a context manager:

```python
with Manager("binance") as mgr:
    mgr.subscribe(["BTCUSDT"])
    time.sleep(2)
    snap = mgr.get_snapshot("BTCUSDT")
```

## Supported exchanges

- **Binance** — futures WebSocket (candles, depth, aggTrade)
- **Bybit** — linear futures WebSocket
- **Bitget** — USDT futures WebSocket

## API

### `Manager(exchange)`

Create a manager for an exchange. Initializes the Go runtime and WebSocket connections.

```python
mgr = Manager("binance")  # or "bybit", "bitget"
```

### `mgr.subscribe(symbols)`

Subscribe to one or more symbols. Starts candle, depth, and trade streams for each.

```python
mgr.subscribe("BTCUSDT")
mgr.subscribe(["BTCUSDT", "ETHUSDT", "SOLUSDT"])
```

### `mgr.get_snapshot(symbol) -> Snapshot | None`

Get the latest point-in-time snapshot for a symbol.

```python
snap = mgr.get_snapshot("BTCUSDT")
snap.timestamp      # Unix ms
snap.depth          # DepthMetrics
snap.candles        # list[CandleHLCV]
snap.trades         # list[NormalizedTrade]
```

### `mgr.get_all_snapshots() -> dict[str, Snapshot]`

Get snapshots for all subscribed symbols in one call.

### `mgr.unsubscribe(symbol)`

Remove all streams for a symbol.

### `mgr.close()`

Shutdown all managers and WebSocket connections.

## Data models

### `DepthMetrics`

Order book metrics computed from raw depth data:

| Field | Description |
|-------|-------------|
| `mid_price` | (best_bid + best_ask) / 2 |
| `spread_bps` | Spread in basis points |
| `bid_liquidity_10` | USD liquidity, top 10 bid levels |
| `ask_liquidity_10` | USD liquidity, top 10 ask levels |
| `imbalance_ratio_10` | bid_liq / ask_liq (>1 = bullish) |
| `slippage_buy_10k` | Estimated slippage % for $10k buy |

Plus 70+ more fields: liquidity at 5/10/20/50 levels, volumes, imbalance deltas, largest walls, slippage at 8 USD sizes, velocity, momentum, z-scores, and depth quality metrics.

### `CandleHLCV`

```python
candle.ts       # Unix ms
candle.open
candle.high
candle.low
candle.close
candle.volume
```

### `NormalizedTrade`

```python
trade.timestamp  # Unix ms
trade.price
trade.size
trade.side       # "buy" or "sell"
trade.symbol
```

## Architecture

```
Python process
|
+-- ctypes loads libflowex.so  <--  Go runtime starts inside Python
|                                    |
|                                    +-- Manager (binance)
|                                    |     +-- Worker: BTCUSDT -> atomic snapshot
|                                    |     +-- Worker: ETHUSDT -> atomic snapshot
|                                    |     +-- Worker: SOLUSDT -> atomic snapshot
|                                    |
|                                    +-- Manager (bybit)
|                                          +-- Worker: BTCUSDT -> atomic snapshot
|
+-- mgr.subscribe(["BTCUSDT"])     ->  FlowexSubscribeBatch()
+-- mgr.get_snapshot("BTCUSDT")    ->  FlowexGetSnapshot() -> atomic.Load -> JSON -> Python
+-- mgr.get_all_snapshots()        ->  FlowexGetSnapshots() -> one call, all symbols
```

## Build from source

Requires Go 1.22+ and Python 3.10+.

```bash
# macOS (Apple Silicon)
make build-mac

# Linux (amd64)
make build-linux

# All platforms (requires cross-compilers)
make build-all
```

## License

MIT
