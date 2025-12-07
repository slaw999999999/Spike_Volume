"""
Główny plik - zarządzanie event loop, WebSocket takami, GUI i uruchamianie aplikacji
"""

import asyncio
import threading
import tkinter as tk

from config import COINS, initialize_states
from websockets_tasks import (
    kline_task_binance, aggtrade_task_binance,
    kline_task_bybit, trade_task_bybit,
    trades_task_gate,
    trade_task_okx
)
from gui import CryptoMonitorGUI


# ======================== GLOBALNE ZMIENNE ========================
states = initialize_states()
sent_alerts = set()
active_other_exchanges = set()
other_exchange_tasks = {}
loop = None


# ======================== ZARZĄDZANIE TASKAMI (INNE GIEŁDY) ========================

async def start_other_exchanges(coin: str) -> None:
    """Uruchamia monitoring na 3 dodatkowych giełdach dla danego coina"""
    global other_exchange_tasks

    if coin in other_exchange_tasks:
        return  # Już uruchomione

    print(f"🚀 Uruchamiam monitoring 3 giełd dla {coin}")

    tasks = [
        asyncio.create_task(kline_task_bybit(coin, states, active_other_exchanges)),
        asyncio.create_task(trade_task_bybit(coin, states, active_other_exchanges)),
        asyncio.create_task(trades_task_gate(coin, states, active_other_exchanges)),
        asyncio.create_task(trade_task_okx(coin, states, active_other_exchanges))
    ]

    other_exchange_tasks[coin] = tasks
    active_other_exchanges.add(coin)


async def stop_other_exchanges(coin: str) -> None:
    """Zatrzymuje monitoring na 3 dodatkowych giełdach dla danego coina"""
    global other_exchange_tasks

    if coin not in other_exchange_tasks:
        return  # Nie uruchomione

    print(f"🛑 Zatrzymuję monitoring 3 giełd dla {coin}")

    # Usuń z aktywnych
    active_other_exchanges.discard(coin)

    # Anuluj taski
    for task in other_exchange_tasks[coin]:
        task.cancel()

    # Poczekaj na zakończenie tasków
    await asyncio.gather(*other_exchange_tasks[coin], return_exceptions=True)
    del other_exchange_tasks[coin]


# ======================== ASYNCIO EVENT LOOP (BINANCE ZAWSZE) ========================

async def run_websockets() -> None:
    """
    Główna coroutine - uruchamia wszystkie Binance taski (zawsze aktywne).
    Pozostałe giełdy są uruchamiane na żądanie w start_other_exchanges().
    """
    global loop
    loop = asyncio.get_running_loop()

    tasks = []

    print("🚀 Uruchamiam monitorowanie...")
    print(f"📈 Monitorowane kryptowaluty: {len(COINS)} coinów")
    print("✅ Binance: ZAWSZE aktywne dla wszystkich coinów (w tle)")
    print("⚡ Pozostałe giełdy: aktywowane przez zaznaczenie w GUI")
    print("👁️ GUI: początkowo czysty ekran - zaznacz coiny aby je zobaczyć")
    print("⏳ Zbieranie danych historycznych Binance...")

    # Uruchom TYLKO taski Binance dla wszystkich coinów
    for coin in COINS:
        tasks.append(kline_task_binance(coin, states, sent_alerts))
        tasks.append(aggtrade_task_binance(coin, states, sent_alerts))

    await asyncio.gather(*tasks, return_exceptions=True)


def run_asyncio() -> None:
    """Uruchamia event loop w osobnym wątku"""
    asyncio.run(run_websockets())


# ======================== URUCHOMIENIE APLIKACJI ========================

def main() -> None:
    """Główna funkcja - uruchamia WebSockety i GUI"""

    # Uruchom WebSockety w osobnym wątku
    ws_thread = threading.Thread(target=run_asyncio, daemon=True)
    ws_thread.start()

    # Czekaj aż loop się inicjalizuje
    while loop is None:
        threading.Event().wait(0.1)

    # Uruchom GUI w głównym wątku
    root = tk.Tk()
    app = CryptoMonitorGUI(
        root,
        loop,
        states,
        start_callback=start_other_exchanges,
        stop_callback=stop_other_exchanges
    )
    app.update_display()
    root.mainloop()


if __name__ == "__main__":
    main()
