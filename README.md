# flowex

[![CI](https://github.com/KhavrTrading/flowex-py/actions/workflows/build.yml/badge.svg)](https://github.com/KhavrTrading/flowex-py/actions/workflows/build.yml)
[![PyPI](https://img.shields.io/pypi/v/flowex)](https://pypi.org/project/flowex/)
[![Python](https://img.shields.io/pypi/pyversions/flowex)](https://pypi.org/project/flowex/)
[![License](https://img.shields.io/github/license/KhavrTrading/flowex-py)](LICENSE)

Real-time multi-exchange crypto market data for Python — powered by Go via cgo shared library. WebSocket streaming, order book metrics, technical indicators, and per-symbol actor workers for Binance, Bybit, and Bitget.

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

# Technical indicators (RSI, MACD, Bollinger Bands, etc.)
if snap.indicators:
    print(snap.indicators.rsi_14)
    print(snap.indicators.macd_line)
    print(snap.indicators.bb_upper)

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

Subscribe to all streams (candle, depth, trade) for one or more symbols.

```python
mgr.subscribe("BTCUSDT")
mgr.subscribe(["BTCUSDT", "ETHUSDT", "SOLUSDT"])
```

### `mgr.subscribe_candle(symbol)` / `subscribe_depth(symbol)` / `subscribe_trade(symbol)`

Subscribe to individual stream types for granular control.

```python
mgr.subscribe_candle("BTCUSDT")   # candles only
mgr.subscribe_depth("ETHUSDT")    # depth only
mgr.subscribe_trade("SOLUSDT")    # trades only
```

### `mgr.get_snapshot(symbol) -> Snapshot | None`

Get the latest point-in-time snapshot for a symbol.

```python
snap = mgr.get_snapshot("BTCUSDT")
snap.timestamp      # Unix ms
snap.depth          # DepthMetrics
snap.candles        # list[CandleHLCV]
snap.trades         # list[NormalizedTrade]
snap.indicators     # TechnicalIndicators | None
```

### `mgr.get_all_snapshots() -> dict[str, Snapshot]`

Get snapshots for all subscribed symbols in one call.

### `mgr.get_status() -> dict`

Get manager status info (subscribed symbols, connection state).

### `mgr.get_depth_history(symbol, count=0) -> list[DepthMetrics]`

Get recent depth metrics from the ring buffer. `count=0` returns the full buffer (default 100 entries).

```python
history = mgr.get_depth_history("BTCUSDT", count=10)
for m in history:
    print(m.mid_price, m.spread_bps)
```

### `mgr.get_depth_by_time_range(symbol, start_ms, end_ms) -> list[DepthMetrics]`

Get depth metrics within a Unix-millisecond time window.

```python
import time
now = int(time.time() * 1000)
metrics = mgr.get_depth_by_time_range("BTCUSDT", now - 30_000, now)
```

### `mgr.unsubscribe(symbol)`

Remove all streams for a symbol.

### `mgr.unsubscribe_stream(symbol, stream)`

Remove a specific stream type: `"candle"`, `"depth"`, or `"trade"`.

```python
mgr.unsubscribe_stream("BTCUSDT", "depth")
```

### `mgr.close()`

Shutdown all managers and WebSocket connections.

## Data models

### `TechnicalIndicators`

Computed from candle history (needs ~20+ bars):

| Field | Description |
|-------|-------------|
| `rsi_14` | RSI (14-period) |
| `sma_20` / `sma_50` / `sma_200` | Simple Moving Averages |
| `ema_9` / `ema_12` / `ema_20` / `ema_21` / `ema_26` / `ema_50` / `ema_200` | Exponential Moving Averages |
| `macd_line` / `signal_line` / `histogram` | MACD |
| `bb_upper` / `bb_middle` / `bb_lower` | Bollinger Bands (20, 2σ) |
| `atr` | Average True Range (14-period) |
| `stoch_rsi` | Stochastic RSI |
| `mmi` | Market Manipulation Index (0–100) |
| `ma_summary` / `oscillator_sum` / `overall_sum` | Signal summary (-2 to 2) |

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
