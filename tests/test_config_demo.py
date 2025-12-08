import os


def test_config_respects_disable_telegram():
    # Ensure DISABLE_TELEGRAM env is set before importing config
    os.environ["DISABLE_TELEGRAM"] = "1"
    # Ensure tokens are absent
    os.environ.pop("TELEGRAM_BOT_TOKEN", None)
    os.environ.pop("TELEGRAM_CHAT_ID", None)

    # import after env set
    import importlib
    import config
    importlib.reload(config)

    assert config.DISABLE_TELEGRAM is True
    assert config.TELEGRAM_ENABLED is False
