from __future__ import annotations

import atexit
import ctypes
import json

from flowex._lib import lib as _lib
from flowex._models import (
    CandleHLCV,
    DepthMetrics,
    NormalizedTrade,
    Snapshot,
    TechnicalIndicators,
)

__all__ = [
    "Manager",
    "Snapshot",
    "CandleHLCV",
    "DepthMetrics",
    "NormalizedTrade",
    "TechnicalIndicators",
]

_shutdown_registered = False


class Manager:
    """Wraps a flowex exchange manager loaded via the shared library.

    Usage::

        with Manager("binance") as mgr:
            mgr.subscribe(["BTCUSDT", "ETHUSDT"])
            snap = mgr.get_snapshot("BTCUSDT")
    """

    def __init__(self, exchange: str) -> None:
        global _shutdown_registered
        self._exchange = exchange.lower()
        self._exchange_b = self._exchange.encode("utf-8")
        rc = _lib.FlowexInit(self._exchange_b)
        if rc != 0:
            raise RuntimeError(f"FlowexInit failed for {exchange!r}")
        if not _shutdown_registered:
            atexit.register(_lib.FlowexShutdown)
            _shutdown_registered = True

    def subscribe(self, symbols: list[str] | str) -> None:
        if isinstance(symbols, str):
            symbols = [symbols]
        arr = (ctypes.c_char_p * len(symbols))(
            *(s.encode("utf-8") for s in symbols)
        )
        rc = _lib.FlowexSubscribeBatch(self._exchange_b, arr, len(symbols))
        if rc != 0:
            raise RuntimeError("FlowexSubscribeBatch failed")

    def get_snapshot(self, symbol: str) -> Snapshot | None:
        ptr = _lib.FlowexGetSnapshot(self._exchange_b, symbol.encode("utf-8"))
        if not ptr:
            return None
        try:
            raw = ctypes.string_at(ptr)
            data = json.loads(raw)
        finally:
            _lib.FlowexFree(ptr)
        return Snapshot.from_dict(data)

    def get_all_snapshots(self) -> dict[str, Snapshot]:
        ptr = _lib.FlowexGetSnapshots(self._exchange_b)
        if not ptr:
            return {}
        try:
            raw = ctypes.string_at(ptr)
            data = json.loads(raw)
        finally:
            _lib.FlowexFree(ptr)
        return {sym: Snapshot.from_dict(snap) for sym, snap in data.items()}

    def subscribe_candle(self, symbol: str) -> None:
        rc = _lib.FlowexSubscribeCandle(self._exchange_b, symbol.encode("utf-8"))
        if rc != 0:
            raise RuntimeError(f"FlowexSubscribeCandle failed for {symbol!r}")

    def subscribe_depth(self, symbol: str) -> None:
        rc = _lib.FlowexSubscribeDepth(self._exchange_b, symbol.encode("utf-8"))
        if rc != 0:
            raise RuntimeError(f"FlowexSubscribeDepth failed for {symbol!r}")

    def subscribe_trade(self, symbol: str) -> None:
        rc = _lib.FlowexSubscribeTrade(self._exchange_b, symbol.encode("utf-8"))
        if rc != 0:
            raise RuntimeError(f"FlowexSubscribeTrade failed for {symbol!r}")

    def unsubscribe(self, symbol: str) -> None:
        rc = _lib.FlowexUnsubscribe(self._exchange_b, symbol.encode("utf-8"))
        if rc != 0:
            raise RuntimeError(f"FlowexUnsubscribe failed for {symbol!r}")

    def unsubscribe_stream(self, symbol: str, stream: str) -> None:
        """Unsubscribe a specific stream type: 'candle', 'depth', or 'trade'."""
        rc = _lib.FlowexUnsubscribeStream(
            self._exchange_b, symbol.encode("utf-8"), stream.encode("utf-8"),
        )
        if rc != 0:
            raise RuntimeError(
                f"FlowexUnsubscribeStream failed for {symbol!r} stream={stream!r}"
            )

    def get_status(self) -> dict:
        ptr = _lib.FlowexGetStatus(self._exchange_b)
        if not ptr:
            return {}
        try:
            return json.loads(ctypes.string_at(ptr))
        finally:
            _lib.FlowexFree(ptr)

    def get_depth_history(
        self, symbol: str, count: int = 0,
    ) -> list[DepthMetrics]:
        """Return recent depth metrics. *count=0* returns the full buffer."""
        ptr = _lib.FlowexGetDepthHistory(
            self._exchange_b, symbol.encode("utf-8"), count,
        )
        if not ptr:
            return []
        try:
            data = json.loads(ctypes.string_at(ptr))
        finally:
            _lib.FlowexFree(ptr)
        return [DepthMetrics.from_dict(m) for m in data]

    def get_depth_by_time_range(
        self, symbol: str, start_ms: int, end_ms: int,
    ) -> list[DepthMetrics]:
        """Return depth metrics within a Unix-ms time window (inclusive)."""
        ptr = _lib.FlowexGetDepthByTimeRange(
            self._exchange_b, symbol.encode("utf-8"), start_ms, end_ms,
        )
        if not ptr:
            return []
        try:
            data = json.loads(ctypes.string_at(ptr))
        finally:
            _lib.FlowexFree(ptr)
        return [DepthMetrics.from_dict(m) for m in data]

    def close(self) -> None:
        _lib.FlowexShutdown()

    def __enter__(self) -> Manager:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
