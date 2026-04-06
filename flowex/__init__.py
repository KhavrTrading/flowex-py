from __future__ import annotations

import atexit
import ctypes
import json

from flowex._lib import lib as _lib
from flowex._models import CandleHLCV, DepthMetrics, NormalizedTrade, Snapshot

__all__ = [
    "Manager",
    "Snapshot",
    "CandleHLCV",
    "DepthMetrics",
    "NormalizedTrade",
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

    def unsubscribe(self, symbol: str) -> None:
        rc = _lib.FlowexUnsubscribe(self._exchange_b, symbol.encode("utf-8"))
        if rc != 0:
            raise RuntimeError(f"FlowexUnsubscribe failed for {symbol!r}")

    def close(self) -> None:
        _lib.FlowexShutdown()

    def __enter__(self) -> Manager:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
