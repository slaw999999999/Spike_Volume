import os


def test_initialize_states_structure():
    # Ensure env vars exist before importing config (config.py validates them at import time)
    os.environ.setdefault("TELEGRAM_BOT_TOKEN", "test-token")
    os.environ.setdefault("TELEGRAM_CHAT_ID", "1")

    from config import initialize_states, COINS, HISTORY

    states = initialize_states()
    assert isinstance(states, dict)

    # Every coin must be present and contain expected exchange keys
    for coin in COINS:
        assert coin in states
        s = states[coin]
        for exch in ["binance", "bybit", "gate", "okx", "combined"]:
            assert exch in s

    # Verify deque maxlen equals HISTORY for binance
    some_coin = next(iter(COINS))
    assert hasattr(states[some_coin]["binance"]["last_volumes"], "maxlen")
    assert states[some_coin]["binance"]["last_volumes"].maxlen == HISTORY
