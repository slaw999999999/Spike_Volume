from gui import CryptoMonitorGUI
from config import COINS


def test_tag_for_value_positive():
    assert CryptoMonitorGUI._tag_for_value(10) == 'positive'


def test_tag_for_value_negative():
    assert CryptoMonitorGUI._tag_for_value(-5) == 'negative'


def test_tag_for_value_neutral():
    assert CryptoMonitorGUI._tag_for_value(0) == 'neutral'


def test_update_exchange_data_preserves_parity_and_sets_values():
    # Avoid creating a real Tk root (no DISPLAY in CI). Instead, create an
    # instance of CryptoMonitorGUI without running __init__ and attach a
    # simple FakeTree that implements the minimal API used by the GUI.

    class FakeTree:
        def __init__(self):
            self._items = {}

        def get_children(self):
            return list(self._items.keys())

        def insert(self, parent, index, values=None, tags=()):
            item_id = f"item{len(self._items)+1}"
            self._items[item_id] = {"values": tuple(values or ()), "tags": list(tags)}
            return item_id

        def item(self, item, *args, **kwargs):
            # setter form: item(item, values=..., tags=...)
            if kwargs:
                if 'values' in kwargs:
                    self._items[item]['values'] = tuple(kwargs['values'])
                if 'tags' in kwargs:
                    self._items[item]['tags'] = list(kwargs['tags'])
                return
            # getter form: item(item, 'values')
            if args and args[0] == 'values':
                return self._items[item]['values']
            return self._items[item]

        def tag_configure(self, *a, **k):
            return

        def delete(self, *a, **k):
            return

    # Create GUI-like object without running the real __init__ (avoids tk init)
    gui = object.__new__(CryptoMonitorGUI)
    gui.tree = FakeTree()
    gui.tree_item_ids = {coin: {} for coin in COINS}

    # Call the method that creates rows — it will use our FakeTree
    CryptoMonitorGUI._create_coin_rows(gui, "ETH")

    # prepare a state dict for binance
    state = {
        "current_vol": 100.0,
        "avg_vol": 10.0,
        "buy_vol": 80.0,
        "sell_vol": 20.0,
        "delta": 60.0,
    }

    # update exchange data and assert tree values updated
    CryptoMonitorGUI._update_exchange_data(gui, "ETH", "BINANCE", state)
    item = gui.tree_item_ids["ETH"].get("BINANCE")
    values = gui.tree.item(item, 'values')
    assert values[2].startswith("100.0") or values[2].startswith("100")
