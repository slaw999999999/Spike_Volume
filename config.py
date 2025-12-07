"""
Konfiguracja globalna - parametry, URL, tokeny, lista coinów
"""

import os
from collections import deque

# ========= PARAMETRY SYSTEMU ==========
HISTORY = 5  # Liczba świec do historii
REFRESH_RATE = 0.5  # Częstotliwość odświeżania GUI (sekundy)

# ========= TELEGRAM ==========
from dotenv import load_dotenv
load_dotenv()  # Ładuje zmienne z .env

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Dodaj walidację - program się nie uruchomi bez tokenów
if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    raise ValueError("Brak tokenów Telegram w zmiennych środowiskowych! Utwórz plik .env")

# ========= TIMEFRAMES ==========
TF_BINANCE = "1m"
TF_BYBIT = "1"

# ========= WEBSOCKET URLs ==========
BINANCE_WS_URL = "wss://fstream.binance.com/ws/"
BYBIT_WS_URL = "wss://stream.bybit.com/v5/public/linear"
GATE_WS_URL = "wss://fx-ws.gateio.ws/v4/ws/usdt"
OKX_WS_URL = "wss://ws.okx.com:8443/ws/v5/public"

# ========= LISTA COINÓW ==========
COINS = {
    "ETH": {
        "binance": "ethusdt",
        "bybit": "ETHUSDT",
        "gate": "ETH_USDT",
        "okx": "ETH-USDT-SWAP",
        "gate_contract_size": 0.01,
        "okx_contract_size": 0.1
    },
    "BTC": {
        "binance": "btcusdt",
        "bybit": "BTCUSDT",
        "gate": "BTC_USDT",
        "okx": "BTC-USDT-SWAP",
        "gate_contract_size": 0.0001,
        "okx_contract_size": 0.01
    },
    "SOL": {
        "binance": "solusdt",
        "bybit": "SOLUSDT",
        "gate": "SOL_USDT",
        "okx": "SOL-USDT-SWAP",
        "gate_contract_size": 1.0,
        "okx_contract_size": 1.0
    },
    "SUI": {
        "binance": "suiusdt",
        "bybit": "SUIUSDT",
        "gate": "SUI_USDT",
        "okx": "SUI-USDT-SWAP",
        "gate_contract_size": 1.0,
        "okx_contract_size": 1.0
    },
    "DOGE": {
        "binance": "dogeusdt",
        "bybit": "DOGEUSDT",
        "gate": "DOGE_USDT",
        "okx": "DOGE-USDT-SWAP",
        "gate_contract_size": 1.0,
        "okx_contract_size": 1.0
    },
    "ADA": {
        "binance": "adausdt",
        "bybit": "ADAUSDT",
        "gate": "ADA_USDT",
        "okx": "ADA-USDT-SWAP",
        "gate_contract_size": 1.0,
        "okx_contract_size": 1.0
    },
    "BNB": {
        "binance": "bnbusdt",
        "bybit": "BNBUSDT",
        "gate": "BNB_USDT",
        "okx": "BNB-USDT-SWAP",
        "gate_contract_size": 0.01,
        "okx_contract_size": 0.1
    },
    "ENA": {
        "binance": "enausdt",
        "bybit": "ENAUSDT",
        "gate": "ENA_USDT",
        "okx": "ENA-USDT-SWAP",
        "gate_contract_size": 1.0,
        "okx_contract_size": 1.0
    },
    "LINK": {
        "binance": "linkusdt",
        "bybit": "LINKUSDT",
        "gate": "LINK_USDT",
        "okx": "LINK-USDT-SWAP",
        "gate_contract_size": 1.0,
        "okx_contract_size": 1.0
    },
    "LTC": {
        "binance": "ltcusdt",
        "bybit": "LTCUSDT",
        "gate": "LTC_USDT",
        "okx": "LTC-USDT-SWAP",
        "gate_contract_size": 1.0,
        "okx_contract_size": 1.0
    },
    "FET": {
        "binance": "fetusdt",
        "bybit": "FETUSDT",
        "gate": "FET_USDT",
        "okx": "FET-USDT-SWAP",
        "gate_contract_size": 1.0,
        "okx_contract_size": 1.0
    },
    "APT": {
        "binance": "aptusdt",
        "bybit": "APTUSDT",
        "gate": "APT_USDT",
        "okx": "APT-USDT-SWAP",
        "gate_contract_size": 1.0,
        "okx_contract_size": 1.0
    },
    "DASH": {
        "binance": "dashusdt",
        "bybit": "DASHUSDT",
        "gate": "DASH_USDT",
        "okx": "DASH-USDT-SWAP",
        "gate_contract_size": 0.1,
        "okx_contract_size": 0.1
    },
    "AAVE": {
        "binance": "aaveusdt",
        "bybit": "AAVEUSDT",
        "gate": "AAVE_USDT",
        "okx": "AAVE-USDT-SWAP",
        "gate_contract_size": 0.1,
        "okx_contract_size": 0.1
    },
    "ATOM": {
        "binance": "atomusdt",
        "bybit": "ATOMUSDT",
        "gate": "ATOM_USDT",
        "okx": "ATOM-USDT-SWAP",
        "gate_contract_size": 1.0,
        "okx_contract_size": 1.0
    },
    "ETC": {
        "binance": "etcusdt",
        "bybit": "ETCUSDT",
        "gate": "ETC_USDT",
        "okx": "ETC-USDT-SWAP",
        "gate_contract_size": 1.0,
        "okx_contract_size": 1.0
    },
    "XLM": {
        "binance": "xlmusdt",
        "bybit": "XLMUSDT",
        "gate": "XLM_USDT",
        "okx": "XLM-USDT-SWAP",
        "gate_contract_size": 1.0,
        "okx_contract_size": 1.0
    },
    "ASTER": {
        "binance": "asterusdt",
        "bybit": "ASTERUSDT",
        "gate": "ASTER_USDT",
        "okx": "ASTER-USDT-SWAP",
        "gate_contract_size": 1.0,
        "okx_contract_size": 1.0
    },
    "JUP": {
        "binance": "jupusdt",
        "bybit": "JUPUSDT",
        "gate": "JUP_USDT",
        "okx": "JUP-USDT-SWAP",
        "gate_contract_size": 1.0,
        "okx_contract_size": 1.0
    },
    "INJ": {
        "binance": "injusdt",
        "bybit": "INJUSDT",
        "gate": "INJ_USDT",
        "okx": "INJ-USDT-SWAP",
        "gate_contract_size": 1.0,
        "okx_contract_size": 1.0
    }
}


def initialize_states():
    """Inicjalizuje stan dla wszystkich coinów i giełd"""
    import time
    
    states = {}
    for coin in COINS:
        states[coin] = {
            "binance": {
                "current_vol": 0.0,
                "avg_vol": 0.0,
                "last_volumes": deque(maxlen=HISTORY),
                "buy_vol": 0.0,
                "sell_vol": 0.0,
                "delta": 0.0,
                "candle_id": None,
                "current_candle_open": 0.0,
                "current_candle_close": 0.0,
                "current_candle_high": 0.0,
                "current_candle_low": 0.0,
                "alert_triggered": False,
                "start_time": time.time()
            },
            "bybit": {
                "current_vol": 0.0,
                "avg_vol": 0.0,
                "last_volumes": deque(maxlen=HISTORY),
                "buy_vol": 0.0,
                "sell_vol": 0.0,
                "delta": 0.0,
                "candle_id": None,
            },
            "gate": {
                "current_vol": 0.0,
                "avg_vol": 0.0,
                "last_volumes": deque(maxlen=HISTORY),
                "buy_vol": 0.0,
                "sell_vol": 0.0,
                "delta": 0.0,
                "candle_start": None,
            },
            "okx": {
                "current_vol": 0.0,
                "avg_vol": 0.0,
                "last_volumes": deque(maxlen=HISTORY),
                "buy_vol": 0.0,
                "sell_vol": 0.0,
                "delta": 0.0,
                "candle_id": None,
            },
            "combined": {
                "current_vol": 0.0,
                "avg_vol": 0.0,
                "delta": 0.0,
            }
        }
    return states
