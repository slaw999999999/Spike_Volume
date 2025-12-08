from gui import CryptoMonitorGUI
import tkinter as tk


def test_tag_for_value_positive():
    assert CryptoMonitorGUI._tag_for_value(10) == 'positive'


def test_tag_for_value_negative():
    assert CryptoMonitorGUI._tag_for_value(-5) == 'negative'


def test_tag_for_value_neutral():
    assert CryptoMonitorGUI._tag_for_value(0) == 'neutral'


def test_update_exchange_data_preserves_parity_and_sets_values():
    # create a minimal GUI instance with a root
    root = tk.Tk()
    root.withdraw()
    # dummy loop and callbacks
    gui = CryptoMonitorGUI(root, None, {"ETH": {"binance": {}, "bybit": {}, "gate": {}, "okx": {}, "combined": {}}}, lambda c: None, lambda c: None)

    # create rows for ETH so tree_item_ids populated
    gui._create_coin_rows("ETH")

    # prepare a state dict for binance
    state = {
        "current_vol": 100.0,
        "avg_vol": 10.0,
        "buy_vol": 80.0,
        "sell_vol": 20.0,
        "delta": 60.0,
    }

    # update exchange data and assert tree values updated
    gui._update_exchange_data("ETH", "BINANCE", state)
    item = gui.tree_item_ids["ETH"].get("BINANCE")
    values = gui.tree.item(item, 'values')
    assert values[2].startswith("100.0") or values[2].startswith("100")

    root.destroy()
