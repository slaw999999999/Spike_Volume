import os
import asyncio
from unittest.mock import MagicMock, patch


def setup_env():
    os.environ.setdefault("TELEGRAM_BOT_TOKEN", "test-token")
    os.environ.setdefault("TELEGRAM_CHAT_ID", "1")


def test_send_telegram_alert_non_200(capsys):
    setup_env()
    import alerts

    mock_resp = MagicMock()
    mock_resp.status_code = 500

    with patch("alerts.requests.post", return_value=mock_resp):
        asyncio.run(alerts.send_telegram_alert("hello-fail"))

    captured = capsys.readouterr()
    assert "Błąd wysyłania alertu" in captured.out


def test_send_telegram_alert_exception(capsys):
    setup_env()
    import alerts

    def raise_exc(*a, **k):
        raise RuntimeError("network")

    with patch("alerts.requests.post", side_effect=raise_exc):
        asyncio.run(alerts.send_telegram_alert("hello-exc"))

    captured = capsys.readouterr()
    assert "Błąd Telegram" in captured.out
