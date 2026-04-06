import time
from flowex import Manager

SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]

mgr = Manager("binance")
mgr.subscribe(SYMBOLS)
time.sleep(2)

end = time.time() + 10
while time.time() < end:
    print(f"\n{'='*60}")
    for sym in SYMBOLS:
        snap = mgr.get_snapshot(sym)
        if snap is None:
            print(f"{sym}: no data yet")
            continue

        d = snap.depth
        c = snap.candles[-1] if snap.candles else None
        print(
            f"{sym}  mid={d.mid_price:.2f}  spread={d.spread_bps:.4f}bps  "
            f"close={c.close if c else '?'}  trades={len(snap.trades)}"
        )

    time.sleep(1)

mgr.close()
