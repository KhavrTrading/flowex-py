from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field


@dataclass
class CandleHLCV:
    ts: int = 0
    open: float = 0.0
    high: float = 0.0
    low: float = 0.0
    close: float = 0.0
    volume: float = 0.0


@dataclass
class NormalizedTrade:
    timestamp: int = 0
    price: float = 0.0
    size: float = 0.0
    size_usd: float = 0.0
    side: str = ""
    trade_id: str = ""
    symbol: str = ""
    exchange: str = ""


@dataclass
class DepthMetrics:
    # Basic
    timestamp: int = 0
    symbol: str = ""
    best_bid: float = 0.0
    best_ask: float = 0.0
    spread: float = 0.0
    spread_bps: float = 0.0
    mid_price: float = 0.0

    # Liquidity (USD) at different depths
    bid_liquidity_5: float = 0.0
    ask_liquidity_5: float = 0.0
    bid_liquidity_10: float = 0.0
    ask_liquidity_10: float = 0.0
    bid_liquidity_20: float = 0.0
    ask_liquidity_20: float = 0.0
    bid_liquidity_50: float = 0.0
    ask_liquidity_50: float = 0.0

    # Volumes (coin size) at different depths
    bid_volume_5: float = 0.0
    ask_volume_5: float = 0.0
    bid_volume_10: float = 0.0
    ask_volume_10: float = 0.0
    bid_volume_20: float = 0.0
    ask_volume_20: float = 0.0
    bid_volume_50: float = 0.0
    ask_volume_50: float = 0.0

    # Imbalance ratios
    imbalance_ratio_5: float = 0.0
    imbalance_ratio_10: float = 0.0
    imbalance_ratio_20: float = 0.0
    imbalance_ratio_50: float = 0.0

    # Imbalance deltas
    imbalance_delta_10: float = 0.0
    imbalance_delta_20: float = 0.0

    # Largest single orders (walls)
    largest_bid_size: float = 0.0
    largest_bid_price: float = 0.0
    largest_bid_value: float = 0.0
    largest_ask_size: float = 0.0
    largest_ask_price: float = 0.0
    largest_ask_value: float = 0.0

    # Slippage estimation (%)
    slippage_buy_100: float = 0.0
    slippage_sell_100: float = 0.0
    slippage_buy_1k: float = 0.0
    slippage_sell_1k: float = 0.0
    slippage_buy_5k: float = 0.0
    slippage_sell_5k: float = 0.0
    slippage_buy_10k: float = 0.0
    slippage_sell_10k: float = 0.0
    slippage_buy_50k: float = 0.0
    slippage_sell_50k: float = 0.0
    slippage_buy_100k: float = 0.0
    slippage_sell_100k: float = 0.0
    slippage_buy_500k: float = 0.0
    slippage_sell_500k: float = 0.0
    slippage_buy_1m: float = 0.0
    slippage_sell_1m: float = 0.0

    # Velocity metrics
    liquidity_velocity_10: float = 0.0
    liquidity_velocity_50: float = 0.0
    imbalance_velocity: float = 0.0
    spread_velocity: float = 0.0
    wall_velocity: float = 0.0

    # Momentum
    buy_pressure_momentum: float = 0.0
    sell_pressure_momentum: float = 0.0
    wall_building_bid: bool = False
    wall_building_ask: bool = False

    # Z-scores
    liquidity_zscore_10: float = 0.0
    imbalance_zscore: float = 0.0
    spread_zscore: float = 0.0

    # Depth quality
    bid_levels_count: int = 0
    ask_levels_count: int = 0
    avg_bid_size_10: float = 0.0
    avg_ask_size_10: float = 0.0
    top_bid_concentration_5: float = 0.0
    top_ask_concentration_5: float = 0.0
    spread_norm_imbalance_delta_10: float = 0.0
    spread_norm_imbalance_delta_20: float = 0.0
    slippage_gradient_buy: float = 0.0
    slippage_gradient_sell: float = 0.0
    slippage_skew_1k: float = 0.0
    slippage_skew_10k: float = 0.0

    @classmethod
    def from_dict(cls, d: dict) -> DepthMetrics:
        known = {f.name for f in dataclasses.fields(cls)}
        return cls(**{k: v for k, v in d.items() if k in known})


@dataclass
class TechnicalIndicators:
    # RSI
    rsi_14: float = 0.0

    # Moving Averages
    sma_20: float = 0.0
    sma_50: float = 0.0
    sma_200: float = 0.0
    ema_9: float = 0.0
    ema_12: float = 0.0
    ema_20: float = 0.0
    ema_21: float = 0.0
    ema_26: float = 0.0
    ema_50: float = 0.0
    ema_200: float = 0.0

    # MACD
    macd_line: float = 0.0
    signal_line: float = 0.0
    histogram: float = 0.0

    # Bollinger Bands
    bb_upper: float = 0.0
    bb_middle: float = 0.0
    bb_lower: float = 0.0

    # Volatility & Advanced
    atr: float = 0.0
    stoch_rsi: float = 0.0
    mmi: float = 0.0

    # Summary Signals (-2=StrongSell, -1=Sell, 0=Neutral, 1=Buy, 2=StrongBuy)
    ma_summary: int = 0
    oscillator_sum: int = 0
    overall_sum: int = 0

    # Counts
    ma_buy: int = 0
    ma_sell: int = 0
    ma_neutral: int = 0
    oscill_buy: int = 0
    oscill_sell: int = 0
    oscill_neutral: int = 0

    @classmethod
    def from_dict(cls, d: dict) -> TechnicalIndicators:
        known = {f.name for f in dataclasses.fields(cls)}
        return cls(**{k: v for k, v in d.items() if k in known})


@dataclass
class Snapshot:
    timestamp: int = 0
    candles: list[CandleHLCV] = field(default_factory=list)
    depth: DepthMetrics | None = None
    trades: list[NormalizedTrade] = field(default_factory=list)
    indicators: TechnicalIndicators | None = None

    @classmethod
    def from_dict(cls, d: dict) -> Snapshot:
        return cls(
            timestamp=d.get("timestamp", 0),
            candles=[CandleHLCV(**c) for c in d.get("candles") or []],
            depth=DepthMetrics.from_dict(d["depth"]) if d.get("depth") else None,
            trades=[NormalizedTrade(**t) for t in d.get("trades") or []],
            indicators=TechnicalIndicators.from_dict(d["indicators"])
            if d.get("indicators")
            else None,
        )
