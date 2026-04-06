package main

/*
#include <stdlib.h>
*/
import "C"
import (
	"encoding/json"
	"unsafe"

	"github.com/KhavrTrading/flowex/binance"
	"github.com/KhavrTrading/flowex/bitget"
	"github.com/KhavrTrading/flowex/bybit"
	"github.com/KhavrTrading/flowex/depth"
	"github.com/KhavrTrading/flowex/ws"

	log "github.com/sirupsen/logrus"
)

// JSON serialization types with proper tags.

type jsonSnapshot struct {
	Timestamp int64               `json:"timestamp"`
	Candles   []jsonCandle        `json:"candles"`
	Depth     *depth.DepthMetrics `json:"depth"`
	Trades    []jsonTrade         `json:"trades"`
}

type jsonCandle struct {
	Ts     int64   `json:"ts"`
	Open   float64 `json:"open"`
	High   float64 `json:"high"`
	Low    float64 `json:"low"`
	Close  float64 `json:"close"`
	Volume float64 `json:"volume"`
}

type jsonTrade struct {
	Timestamp int64   `json:"timestamp"`
	Price     float64 `json:"price"`
	Size      float64 `json:"size"`
	SizeUSD   float64 `json:"size_usd"`
	Side      string  `json:"side"`
	TradeID   string  `json:"trade_id"`
	Symbol    string  `json:"symbol"`
	Exchange  string  `json:"exchange"`
}

func init() {
	log.SetLevel(log.FatalLevel)
}

func marshalSnapshot(snap *ws.Snapshot) ([]byte, error) {
	js := jsonSnapshot{
		Timestamp: snap.Timestamp.UnixMilli(),
		Candles:   make([]jsonCandle, len(snap.Candles)),
		Trades:    make([]jsonTrade, len(snap.Trades)),
	}
	for i, c := range snap.Candles {
		js.Candles[i] = jsonCandle{
			Ts: c.Ts, Open: c.Open, High: c.High,
			Low: c.Low, Close: c.Close, Volume: c.Volume,
		}
	}
	if snap.DepthStore != nil {
		js.Depth = snap.DepthStore.GetLatest()
	}
	for i, t := range snap.Trades {
		js.Trades[i] = jsonTrade{
			Timestamp: t.Timestamp, Price: t.Price, Size: t.Size,
			SizeUSD: t.SizeUSD, Side: t.Side, TradeID: t.TradeID,
			Symbol: t.Symbol, Exchange: t.Exchange,
		}
	}
	return json.Marshal(js)
}

//export FlowexInit
func FlowexInit(cExchange *C.char) C.int {
	exchange := C.GoString(cExchange)
	g.mu.Lock()
	defer g.mu.Unlock()

	switch exchange {
	case "binance":
		if g.binance == nil {
			g.binance = binance.NewManager()
		}
	case "bybit":
		if g.bybit == nil {
			g.bybit = bybit.NewManager()
		}
	case "bitget":
		if g.bitget == nil {
			g.bitget = bitget.NewManager()
		}
	default:
		return -1
	}
	return 0
}

//export FlowexSubscribe
func FlowexSubscribe(cExchange *C.char, cSymbol *C.char) C.int {
	exchange := C.GoString(cExchange)
	symbol := C.GoString(cSymbol)
	mgr := getManager(exchange)
	if mgr == nil {
		return -1
	}
	if err := mgr.SubscribeAll(symbol, nil, nil, nil); err != nil {
		return -1
	}
	return 0
}

//export FlowexSubscribeBatch
func FlowexSubscribeBatch(cExchange *C.char, cSymbols **C.char, count C.int) C.int {
	exchange := C.GoString(cExchange)
	mgr := getManager(exchange)
	if mgr == nil {
		return -1
	}
	n := int(count)
	symbolPtrs := unsafe.Slice(cSymbols, n)
	for _, sp := range symbolPtrs {
		symbol := C.GoString(sp)
		if err := mgr.SubscribeAll(symbol, nil, nil, nil); err != nil {
			return -1
		}
	}
	return 0
}

//export FlowexGetSnapshot
func FlowexGetSnapshot(cExchange *C.char, cSymbol *C.char) *C.char {
	exchange := C.GoString(cExchange)
	symbol := C.GoString(cSymbol)
	mgr := getManager(exchange)
	if mgr == nil {
		return nil
	}
	snap := mgr.GetSnapshot(symbol)
	if snap == nil {
		return nil
	}
	data, err := marshalSnapshot(snap)
	if err != nil {
		return nil
	}
	return C.CString(string(data))
}

//export FlowexGetSnapshots
func FlowexGetSnapshots(cExchange *C.char) *C.char {
	exchange := C.GoString(cExchange)
	mgr := getManager(exchange)
	if mgr == nil {
		return C.CString("{}")
	}
	status := mgr.GetStatus()
	symbols, ok := status["symbols"].([]string)
	if !ok || len(symbols) == 0 {
		return C.CString("{}")
	}
	result := make(map[string]json.RawMessage)
	for _, sym := range symbols {
		snap := mgr.GetSnapshot(sym)
		if snap == nil {
			continue
		}
		data, err := marshalSnapshot(snap)
		if err != nil {
			continue
		}
		result[sym] = data
	}
	out, _ := json.Marshal(result)
	return C.CString(string(out))
}

//export FlowexUnsubscribe
func FlowexUnsubscribe(cExchange *C.char, cSymbol *C.char) C.int {
	exchange := C.GoString(cExchange)
	symbol := C.GoString(cSymbol)
	mgr := getManager(exchange)
	if mgr == nil {
		return -1
	}
	if err := mgr.UnsubscribeAll(symbol); err != nil {
		return -1
	}
	return 0
}

//export FlowexShutdown
func FlowexShutdown() {
	g.mu.Lock()
	defer g.mu.Unlock()
	if g.binance != nil {
		g.binance.Shutdown()
		g.binance = nil
	}
	if g.bybit != nil {
		g.bybit.Shutdown()
		g.bybit = nil
	}
	if g.bitget != nil {
		g.bitget.Shutdown()
		g.bitget = nil
	}
}

//export FlowexFree
func FlowexFree(ptr *C.char) {
	C.free(unsafe.Pointer(ptr))
}
