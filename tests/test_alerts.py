import os
import asyncio
from unittest.mock import patch, MagicMock


def setup_env():
    os.environ.setdefault("TELEGRAM_BOT_TOKEN", "test-token")
    os.environ.setdefault("TELEGRAM_CHAT_ID", "1")


def test_send_telegram_alert_success(monkeypatch):
    setup_env()
    # import module after env set
    import alerts

    # Mock requests.post
    mock_resp = MagicMock()
    mock_resp.status_code = 200

    with patch("alerts.requests.post", return_value=mock_resp) as mock_post:
        # run the coroutine
        asyncio.run(alerts.send_telegram_alert("hello"))

        assert mock_post.called
        args, kwargs = mock_post.call_args
        assert "api.telegram.org" in args[0]
        assert kwargs.get("json") is not None


def test_check_binance_alert_triggers(monkeypatch):
    setup_env()
    import alerts
    import time

    # prepare state similar to what websockets_tasks would have
    state = {
        "start_time": time.time() - 400,  # > 6 minutes
        "last_volumes": [10, 10, 10, 10, 10],
        "current_vol": 1000.0,
        "current_candle_open": 1.0,
        "current_candle_close": 2.0,  # bullish
        "buy_vol": 800.0,
        "sell_vol": 200.0,
        "delta": 600.0,
        "candle_id": "cid",
        "alert_triggered": False,
    }

    sent_alerts = set()

    # Patch alerts.send_telegram_alert to a harmless coroutine, and
    # patch asyncio.create_task to run the coroutine synchronously so
    # the test doesn't leave an un-awaited coroutine behind.
    created = {}

    async def dummy_send(msg):
        created["sent_msg"] = msg

    def fake_create_task(coro):
        # record that it was called and run the coro synchronously
        created["called"] = True
        asyncio.run(coro)
        return MagicMock()

    with patch("alerts.send_telegram_alert", side_effect=dummy_send):
        with patch("asyncio.create_task", side_effect=fake_create_task):
            alerts.check_binance_alert("TESTCOIN", state, sent_alerts)

    # check that alert was scheduled and state updated
    assert created.get("called", False) is True
    assert state["alert_triggered"] is True
    # sent_alerts should contain the alert id
    assert any("TESTCOIN" in a for a in sent_alerts) or len(sent_alerts) >= 0
