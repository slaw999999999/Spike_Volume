import os
import sys
import importlib
import tempfile
import pytest


def test_config_raises_when_tokens_missing():
    # Ensure any env tokens are removed
    os.environ.pop("TELEGRAM_BOT_TOKEN", None)
    os.environ.pop("TELEGRAM_CHAT_ID", None)

    # Remove cached module if already imported
    if 'config' in sys.modules:
        del sys.modules['config']

    # Import `config` from an isolated temporary working directory so
    # local `.env` files in the repository won't be loaded by python-dotenv.
    # This makes the test deterministic and avoids skipping on machines
    # that have a local .env with Telegram tokens.
    with tempfile.TemporaryDirectory() as td:
        old_cwd = os.getcwd()
        # Prevent python-dotenv from loading any .env (including parent dirs)
        import types
        original_dotenv = sys.modules.get('dotenv')
        fake_dotenv = types.ModuleType('dotenv')
        setattr(fake_dotenv, 'load_dotenv', lambda *a, **k: None)
        sys.modules['dotenv'] = fake_dotenv
        try:
            os.chdir(td)
            with pytest.raises(ValueError):
                importlib.import_module('config')
        finally:
            os.chdir(old_cwd)
            # restore original dotenv if it existed
            if original_dotenv is not None:
                sys.modules['dotenv'] = original_dotenv
            else:
                del sys.modules['dotenv']
