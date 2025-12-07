"""
WebSocket taski dla każdej giełdy - przetwarzanie streamów danych
"""

import asyncio
import json
import time
import websockets

from config import (
    COINS, BINANCE_WS_URL, BYBIT_WS_URL, GATE_WS_URL, OKX_WS_URL,
    TF_BINANCE, TF_BYBIT, HISTORY
)
from alerts import check_binance_alert


# ======================== BINANCE (ZAWSZE AKTYWNE) ========================

async def kline_task_binance(coin: str, states: dict, sent_alerts: set) -> None:
    """
    Monitoruje świece (klines) na Binance.
    Aktualizuje current_vol, OHLC, średnią wolumenu.
    """
    symbol = COINS[coin]["binance"]
    url = f"{BINANCE_WS_URL}{symbol}@kline_{TF_BINANCE}"
    state = states[coin]["binance"]

    while True:
        try:
            async with websockets.connect(url) as ws:
                while True:
                    msg = await ws.recv()
                    data = json.loads(msg)
                    k = data["k"]

                    vol = float(k["v"])
                    is_closed = k["x"]

                    # Aktualizuj dane świecy
                    state["current_vol"] = vol
                    state["current_candle_open"] = float(k["o"])
                    state["current_candle_close"] = float(k["c"])
                    state["current_candle_high"] = float(k["h"])
                    state["current_candle_low"] = float(k["l"])

                    if is_closed:
                        state["last_volumes"].append(vol)
                        if len(state["last_volumes"]) > 0:
                            state["avg_vol"] = sum(state["last_volumes"]) / len(
                                state["last_volumes"]
                            )

                        # Resetuj flagę alertu dla nowej świecy
                        state["alert_triggered"] = False

                    # Sprawdź warunki alertu
                    check_binance_alert(coin, state, sent_alerts)

        except Exception as e:
            print(f"❌ Błąd kline Binance dla {coin}: {e}")
            await asyncio.sleep(5)


async def aggtrade_task_binance(coin: str, states: dict, sent_alerts: set) -> None:
    """
    Monitoruje aggregate trades na Binance.
    Aktualizuje buy_vol, sell_vol, delta dla każdego candle.
    """
    symbol = COINS[coin]["binance"]
    url = f"{BINANCE_WS_URL}{symbol}@aggTrade"
    state = states[coin]["binance"]

    while True:
        try:
            async with websockets.connect(url) as ws:
                while True:
                    msg = await ws.recv()
                    data = json.loads(msg)

                    qty = float(data["q"])
                    is_sell = data["m"]

                    candle = int(data["T"]) // 60000

                    if state["candle_id"] is None:
                        state["candle_id"] = candle
                    elif candle != state["candle_id"]:
                        state["buy_vol"] = 0.0
                        state["sell_vol"] = 0.0
                        state["candle_id"] = candle
                        state["alert_triggered"] = False

                    if is_sell:
                        state["sell_vol"] += qty
                    else:
                        state["buy_vol"] += qty

                    state["delta"] = state["buy_vol"] - state["sell_vol"]

                    # Sprawdź warunki alertu po każdej transakcji
                    check_binance_alert(coin, state, sent_alerts)

        except Exception as e:
            print(f"❌ Błąd aggtrade Binance dla {coin}: {e}")
            await asyncio.sleep(5)


# ======================== BYBIT (NA ŻĄDANIE) ========================

async def kline_task_bybit(coin: str, states: dict, active_other_exchanges: set) -> None:
    """Monitoruje świece na Bybit"""
    symbol = COINS[coin]["bybit"]
    state = states[coin]["bybit"]

    while coin in active_other_exchanges:
        try:
            async with websockets.connect(BYBIT_WS_URL) as ws:
                subscribe_msg = {
                    "op": "subscribe",
                    "args": [f"kline.{TF_BYBIT}.{symbol}"]
                }
                await ws.send(json.dumps(subscribe_msg))

                while coin in active_other_exchanges:
                    try:
                        msg = await asyncio.wait_for(ws.recv(), timeout=1.0)
                        data = json.loads(msg)

                        if "topic" in data and data["topic"].startswith("kline"):
                            kline_data = data["data"][0]

                            vol = float(kline_data["volume"])
                            is_closed = kline_data["confirm"]

                            state["current_vol"] = vol

                            if is_closed:
                                state["last_volumes"].append(vol)
                                if len(state["last_volumes"]) > 0:
                                    state["avg_vol"] = sum(state["last_volumes"]) / len(
                                        state["last_volumes"]
                                    )
                    except asyncio.TimeoutError:
                        continue
        except Exception as e:
            print(f"❌ Błąd kline Bybit dla {coin}: {e}")
            await asyncio.sleep(5)


async def trade_task_bybit(coin: str, states: dict, active_other_exchanges: set) -> None:
    """Monitoruje trades na Bybit"""
    symbol = COINS[coin]["bybit"]
    state = states[coin]["bybit"]

    while coin in active_other_exchanges:
        try:
            async with websockets.connect(BYBIT_WS_URL) as ws:
                subscribe_msg = {
                    "op": "subscribe",
                    "args": [f"publicTrade.{symbol}"]
                }
                await ws.send(json.dumps(subscribe_msg))

                while coin in active_other_exchanges:
                    try:
                        msg = await asyncio.wait_for(ws.recv(), timeout=1.0)
                        data = json.loads(msg)

                        if "topic" in data and data["topic"] == f"publicTrade.{symbol}":
                            trades = data["data"]

                            for trade in trades:
                                qty = float(trade["v"])
                                side = trade["S"]

                                ts = trade["T"]
                                candle = ts // 60000

                                if state["candle_id"] is None:
                                    state["candle_id"] = candle
                                elif candle != state["candle_id"]:
                                    state["buy_vol"] = 0.0
                                    state["sell_vol"] = 0.0
                                    state["candle_id"] = candle

                                if side == "Sell":
                                    state["sell_vol"] += qty
                                else:
                                    state["buy_vol"] += qty

                                state["delta"] = state["buy_vol"] - state["sell_vol"]
                    except asyncio.TimeoutError:
                        continue
        except Exception as e:
            print(f"❌ Błąd trade Bybit dla {coin}: {e}")
            await asyncio.sleep(5)


# ======================== GATE.IO (NA ŻĄDANIE) ========================

def process_trade_gate(coin: str, states: dict, trade_data: dict) -> None:
    """Przetworzenie jednej transakcji z Gate.io"""
    state = states[coin]["gate"]
    contract_size = COINS[coin]["gate_contract_size"]

    try:
        size = trade_data["size"]
        timestamp = trade_data["create_time_ms"]

        is_buy = size > 0
        size_coin = abs(size) * contract_size

        current_candle = (timestamp // 60000) * 60000

        if state["candle_start"] is None:
            state["candle_start"] = current_candle
        elif current_candle != state["candle_start"]:
            state["last_volumes"].append(state["current_vol"])
            if len(state["last_volumes"]) > 0:
                state["avg_vol"] = sum(state["last_volumes"]) / len(state["last_volumes"])

            state["current_vol"] = 0.0
            state["buy_vol"] = 0.0
            state["sell_vol"] = 0.0
            state["candle_start"] = current_candle

        state["current_vol"] += size_coin

        if is_buy:
            state["buy_vol"] += size_coin
        else:
            state["sell_vol"] += size_coin

        state["delta"] = state["buy_vol"] - state["sell_vol"]

    except Exception as e:
        print(f"❌ Błąd przetwarzania transakcji Gate.io dla {coin}: {e}")


async def trades_task_gate(coin: str, states: dict, active_other_exchanges: set) -> None:
    """Monitoruje trades na Gate.io"""
    symbol = COINS[coin]["gate"]

    while coin in active_other_exchanges:
        try:
            async with websockets.connect(GATE_WS_URL) as ws:
                sub_msg = {
                    "time": int(time.time()),
                    "channel": "futures.trades",
                    "event": "subscribe",
                    "payload": [symbol]
                }

                await ws.send(json.dumps(sub_msg))

                while coin in active_other_exchanges:
                    try:
                        msg = await asyncio.wait_for(ws.recv(), timeout=1.0)
                        data = json.loads(msg)

                        if data.get("event") == "update" and "result" in data:
                            for trade in data["result"]:
                                process_trade_gate(coin, states, trade)
                    except asyncio.TimeoutError:
                        continue
        except Exception as e:
            print(f"❌ Błąd Gate.io dla {coin}: {e}")
            await asyncio.sleep(5)


# ======================== OKX (NA ŻĄDANIE) ========================

async def trade_task_okx(coin: str, states: dict, active_other_exchanges: set) -> None:
    """Monitoruje trades na OKX"""
    symbol = COINS[coin]["okx"]
    contract_size = COINS[coin]["okx_contract_size"]
    state = states[coin]["okx"]

    subscribe_msg = {
        "op": "subscribe",
        "args": [{
            "channel": "trades",
            "instId": symbol
        }]
    }

    while coin in active_other_exchanges:
        try:
            async with websockets.connect(OKX_WS_URL) as ws:
                await ws.send(json.dumps(subscribe_msg))

                while coin in active_other_exchanges:
                    try:
                        msg = await asyncio.wait_for(ws.recv(), timeout=1.0)
                        data = json.loads(msg)

                        if "event" in data:
                            continue

                        if "data" in data:
                            trades = data["data"]
                            for trade in trades:
                                contracts = float(trade["sz"])
                                qty = contracts * contract_size

                                side = trade["side"]

                                ts = int(trade["ts"])
                                candle = ts // 60000

                                if state["candle_id"] is None:
                                    state["candle_id"] = candle
                                elif candle != state["candle_id"]:
                                    state["last_volumes"].append(state["current_vol"])
                                    if len(state["last_volumes"]) > 0:
                                        state["avg_vol"] = sum(state["last_volumes"]) / len(
                                            state["last_volumes"]
                                        )

                                    state["current_vol"] = 0.0
                                    state["buy_vol"] = 0.0
                                    state["sell_vol"] = 0.0
                                    state["candle_id"] = candle

                                state["current_vol"] += qty

                                if side == "sell":
                                    state["sell_vol"] += qty
                                else:
                                    state["buy_vol"] += qty

                                state["delta"] = state["buy_vol"] - state["sell_vol"]
                    except asyncio.TimeoutError:
                        continue
        except Exception as e:
            print(f"❌ Błąd OKX dla {coin}: {e}")
            await asyncio.sleep(5)
