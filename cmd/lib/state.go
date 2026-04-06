package main

import (
	"sync"

	"github.com/KhavrTrading/flowex/binance"
	"github.com/KhavrTrading/flowex/bitget"
	"github.com/KhavrTrading/flowex/bybit"
	"github.com/KhavrTrading/flowex/ws"
)

type state struct {
	binance *binance.Manager
	bybit   *bybit.Manager
	bitget  *bitget.Manager
	mu      sync.RWMutex
}

var g = &state{}

func getManager(exchange string) ws.Manager {
	g.mu.RLock()
	defer g.mu.RUnlock()
	switch exchange {
	case "binance":
		if g.binance != nil {
			return g.binance
		}
	case "bybit":
		if g.bybit != nil {
			return g.bybit
		}
	case "bitget":
		if g.bitget != nil {
			return g.bitget
		}
	}
	return nil
}
