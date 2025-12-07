"""
Logika alertów - sprawdzanie warunków i wysyłanie na Telegram
"""

import asyncio
import time
import requests

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, HISTORY


async def send_telegram_alert(message: str) -> None:
    """Wysyła alert na Telegram"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Brak konfiguracji Telegram.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }

    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code == 200:
            print(f"✅ Alert wysłany: {message[:50]}...")
        else:
            print(f"❌ Błąd wysyłania alertu: {response.status_code}")
    except Exception as e:
        print(f"❌ Błąd Telegram: {e}")


def check_binance_alert(coin: str, state_binance: dict, sent_alerts: set) -> None:
    """
    Sprawdza warunki alertu dla Binance.
    
    Warunki:
    1. Wolumen > 7.5x średnia
    2. Delta >= 30% (wzrost) LUB Delta <= -30% (spadek)
    3. Co najmniej 6 minut historii
    """
    # Sprawdź czy minęło co najmniej 6 minut od startu
    if time.time() - state_binance["start_time"] < 360:
        return

    # Sprawdź czy mamy wystarczające dane historyczne
    if len(state_binance["last_volumes"]) < HISTORY:
        return

    # Oblicz średnią z ostatnich 5 świec
    avg_volume = sum(state_binance["last_volumes"]) / len(state_binance["last_volumes"])
    
    # Bezpieczne obliczenie ratio wolumenu (zabezpieczenie przed dzieleniem przez zero)
    if avg_volume and avg_volume != 0:
        volume_ratio = state_binance['current_vol'] / avg_volume
    else:
        volume_ratio = 0

    # Warunek 1: Volume > 7.5x średnia
    volume_condition = state_binance["current_vol"] > 7.5 * avg_volume

    if volume_condition:
        # Określ kierunek świecy
        is_bullish = state_binance["current_candle_close"] > state_binance["current_candle_open"]
        is_bearish = state_binance["current_candle_close"] < state_binance["current_candle_open"]

        # Oblicz procent delty
        total_volume = state_binance["buy_vol"] + state_binance["sell_vol"]
        delta_percent = (state_binance["delta"] / total_volume * 100) if total_volume > 0 else 0

        # Warunek 2: Delta >= 30% dla świecy wzrostowej lub Delta <= -30% dla świecy spadkowej
        delta_condition = False
        alert_type = ""

        if is_bullish and delta_percent >= 30:
            delta_condition = True
            alert_type = "WZROSTOWY"
        elif is_bearish and delta_percent <= -30:
            delta_condition = True
            alert_type = "SPADKOWY"

        if delta_condition and not state_binance["alert_triggered"]:
            # Stwórz unikalny identyfikator alertu
            alert_id = f"{coin}_{state_binance['candle_id']}"

            if alert_id not in sent_alerts:
                # Przygotuj wiadomość
                message = (
                    f"🚨 <b>ALERT {alert_type} - {coin}</b> 🚨\n"
                    f"📊 Giełda: <b>Binance</b>\n"
                    f"💰 Skok: <b>{volume_ratio:.1f}</b>\n"
                    f"📈 Delta: <b>{state_binance['delta']:+.1f}</b> ({delta_percent:+.1f}%)\n"
                    f"🎯 Kierunek: {'🟢 WZROST' if is_bullish else '🔴 SPADEK'}\n"
                    f"⏰ Czas: {time.strftime('%H:%M:%S')}"
                )

                # Wyślij alert
                asyncio.create_task(send_telegram_alert(message))

                # Oznacz jako wysłany
                sent_alerts.add(alert_id)
                state_binance["alert_triggered"] = True
