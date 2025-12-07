"""
Interfejs graficzny - Tkinter z tabelą danych dla każdego coina
"""

import tkinter as tk
from tkinter import ttk, Checkbutton, BooleanVar
import asyncio

from config import COINS, REFRESH_RATE


class CryptoMonitorGUI:
    """GUI do monitorowania i kontroli coinów"""

    def __init__(self, root: tk.Tk, loop: asyncio.AbstractEventLoop, states: dict,
                 start_callback, stop_callback):
        self.root = root
        self.loop = loop
        self.states = states
        self.start_callback = start_callback  # async funkcja start_other_exchanges
        self.stop_callback = stop_callback    # async funkcja stop_other_exchanges

        self.root.title("📊 Spike Volume Monitor")
        self.root.geometry("1600x950")
        self.root.configure(bg="#1e1e1e")

        # Zmienne dla checkboxów
        self.coin_vars = {}
        self.visible_coins = set()
        
        # Kolory - dark theme
        self.bg_color = "#1e1e1e"
        self.fg_color = "#ffffff"
        self.accent_color = "#0d7377"
        self.button_color = "#14919b"

        # Nowoczesny styl
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure("TFrame", background=self.bg_color)
        style.configure("TLabel", background=self.bg_color, foreground=self.fg_color)
        style.configure("TLabelframe", background=self.bg_color, foreground=self.fg_color, borderwidth=2)
        style.configure("TLabelframe.Label", background=self.bg_color, foreground=self.fg_color, font=('Segoe UI', 10, 'bold'))
        style.configure("TButton", font=('Segoe UI', 9))
        style.map("TButton", background=[('active', self.button_color)])
        
        style.configure("Positive.TLabel", foreground="#00ff41", background=self.bg_color, font=('Segoe UI', 9, 'bold'))
        style.configure("Negative.TLabel", foreground="#ff2e63", background=self.bg_color, font=('Segoe UI', 9, 'bold'))
        style.configure("Neutral.TLabel", foreground="#b0b0b0", background=self.bg_color, font=('Segoe UI', 9))
        style.configure("Header.TLabel", font=('Segoe UI', 10, 'bold'), foreground=self.accent_color, background=self.bg_color)
        style.configure("Title.TLabel", font=('Segoe UI', 14, 'bold'), foreground=self.accent_color, background=self.bg_color)

        # Treeview style for dark theme
        style.configure("Custom.Treeview",
                background=self.bg_color,
                fieldbackground=self.bg_color,
                foreground=self.fg_color,
                rowheight=22,
                font=('Segoe UI', 9))
        style.configure("Custom.Treeview.Heading",
                background=self.accent_color,
                foreground="#ffffff",
                font=('Segoe UI', 10, 'bold'))
        style.map("Custom.Treeview.Heading",
              background=[('active', self.accent_color)])

        # Główny kontener
        main_frame = ttk.Frame(root)
        main_frame.pack(fill='both', expand=True, padx=12, pady=12)

        # NAGŁÓWEK
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill='x', pady=(0, 15))
        ttk.Label(header_frame, text="📊 SPIKE VOLUME MONITOR", style="Title.TLabel").pack(anchor='w')
        ttk.Label(header_frame, text="Monitoruj wolumeny i delty na 4 giełdach", 
                  foreground="#888888", background=self.bg_color, font=('Segoe UI', 9)).pack(anchor='w')

        # PANEL WYBORU COINÓW
        selection_frame = ttk.LabelFrame(main_frame, text="🎯 Wybierz Coiny do Wyświetlania", padding=12)
        selection_frame.pack(fill='x', pady=(0, 15))

        # Checkboxów w rzędach po 8
        row_frame = None
        for i, coin in enumerate(COINS):
            if i % 8 == 0:
                row_frame = ttk.Frame(selection_frame)
                row_frame.pack(fill='x', pady=3)

            var = BooleanVar(value=False)
            self.coin_vars[coin] = var
            cb = Checkbutton(row_frame, text=coin, variable=var,
                           command=lambda c=coin: self.toggle_coin_display(c),
                           font=('Segoe UI', 9), bg=self.bg_color, fg=self.fg_color,
                           selectcolor=self.accent_color, activebackground=self.bg_color)
            cb.pack(side='left', padx=8)

        # Przyciski szybkiego wyboru
        button_frame = ttk.Frame(selection_frame)
        button_frame.pack(fill='x', pady=10)

        ttk.Button(button_frame, text="✅ Wszystkie",
                  command=self.select_all_coins).pack(side='left', padx=5)
        ttk.Button(button_frame, text="❌ Żadne",
                  command=self.deselect_all_coins).pack(side='left', padx=5)

        # Kontener z tabelą danych - używamy ttk.Treeview żeby kolumny były idealnie wyrównane
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill='both', expand=True)

        cols = ('coin', 'exchange', 'volume', 'avg', 'delta', 'delta_pct')
        self.tree = ttk.Treeview(table_frame, columns=cols, show='headings', style='Custom.Treeview', selectmode='none')

        # Nagłówki i format kolumn
        self.tree.heading('coin', text='💰 Coin', anchor='center')
        self.tree.column('coin', anchor='center', width=120, stretch=False)

        self.tree.heading('exchange', text='🏦 Exchange', anchor='center')
        self.tree.column('exchange', anchor='center', width=140, stretch=False)

        self.tree.heading('volume', text='📊 Volume', anchor='center')
        self.tree.column('volume', anchor='center', width=120, stretch=False)

        self.tree.heading('avg', text='📈 Avg Vol', anchor='center')
        self.tree.column('avg', anchor='center', width=120, stretch=False)

        self.tree.heading('delta', text='Δ Delta', anchor='center')
        self.tree.column('delta', anchor='center', width=120, stretch=False)

        self.tree.heading('delta_pct', text='Δ %', anchor='center')
        self.tree.column('delta_pct', anchor='center', width=90, stretch=False)

        # Styl i kolorowanie tagów
        self.tree.tag_configure('positive', foreground='#00ff41')
        self.tree.tag_configure('negative', foreground='#ff2e63')
        self.tree.tag_configure('neutral', foreground='#b0b0b0')
        # Row background tags for alternating rows
        style_bg_even = '#1b1b1b'
        style_bg_odd = '#161616'
        self.tree.tag_configure('even', background=style_bg_even)
        self.tree.tag_configure('odd', background=style_bg_odd)
        # Separator row (visual break between coin groups)
        self.tree.tag_configure('sep', background='#0f0f0f')

        # Scrollbar dla tabeli
        vsb = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side='left', fill='both', expand=True)
        vsb.pack(side='right', fill='y')

        # Mapa itemów w drzewie: self.tree_item_ids[coin][exchange] -> item_id
        self.tree_item_ids = {coin: {} for coin in COINS}

    def toggle_coin_display(self, coin: str) -> None:
        """Przełącza wyświetlanie coina i monitorowanie 3 giełd"""
        if self.coin_vars[coin].get():
            # Utwórz wiersze dla tego coina w drzewie jeśli jeszcze nie istnieją
            if not self.tree_item_ids.get(coin) or len(self.tree_item_ids[coin]) == 0:
                self._create_coin_rows(coin)
            self.visible_coins.add(coin)
            asyncio.run_coroutine_threadsafe(self.start_callback(coin), self.loop)
        else:
            # Usuń wiersze tego coina z drzewa
            for exchange, item_id in list(self.tree_item_ids.get(coin, {}).items()):
                try:
                    self.tree.delete(item_id)
                except Exception:
                    pass
            self.tree_item_ids[coin] = {}
            self.visible_coins.discard(coin)
            asyncio.run_coroutine_threadsafe(self.stop_callback(coin), self.loop)

    def _create_coin_rows(self, coin: str) -> None:
        """Tworzy i wyświetla wiersze dla danego coina"""
        exchanges = ["BINANCE", "BYBIT", "GATE.IO", "OKX", "COMBINED"]
        exchange_emoji = {
            "BINANCE": "🔶",
            "BYBIT": "🟦",
            "GATE.IO": "🟧",
            "OKX": "🟩",
            "COMBINED": "📊"
        }

        for row_idx, exchange in enumerate(exchanges):
            coin_display = coin if row_idx == 0 else ""
            exchange_text = f"{exchange_emoji.get(exchange, '')} {exchange}"
            idx = len(self.tree.get_children())
            parity_tag = 'even' if idx % 2 == 0 else 'odd'
            item = self.tree.insert('', 'end', values=(coin_display, exchange_text, '0.0', '0.0', '0.0', '0.0%'), tags=(parity_tag, 'neutral'))
            self.tree_item_ids[coin][exchange] = item

        # Insert a thin separator row after the coin group to visually separate groups
        sep_idx = len(self.tree.get_children())
        sep_tag = 'even' if sep_idx % 2 == 0 else 'odd'
        sep_item = self.tree.insert('', 'end', values=('', '', '', '', '', ''), tags=(sep_tag, 'sep'))
        self.tree_item_ids[coin]['__sep__'] = sep_item

    def select_all_coins(self) -> None:
        """Zaznacza wszystkie coiny"""
        for coin in COINS:
            self.coin_vars[coin].set(True)
            if not self.tree_item_ids.get(coin) or len(self.tree_item_ids[coin]) == 0:
                self._create_coin_rows(coin)
            self.visible_coins.add(coin)
            asyncio.run_coroutine_threadsafe(self.start_callback(coin), self.loop)

    def deselect_all_coins(self) -> None:
        """Odznacza wszystkie coiny"""
        for coin in COINS:
            self.coin_vars[coin].set(False)
            for exchange, item_id in list(self.tree_item_ids.get(coin, {}).items()):
                try:
                    self.tree.delete(item_id)
                except Exception:
                    pass
            self.tree_item_ids[coin] = {}
            self.visible_coins.discard(coin)
            asyncio.run_coroutine_threadsafe(self.stop_callback(coin), self.loop)

    def update_display(self) -> None:
        """Aktualizuje wyświetlane dane dla widocznych coinów"""
        for coin in self.visible_coins:
            state_combined = self.states[coin]["combined"]
            state_binance = self.states[coin]["binance"]
            state_bybit = self.states[coin]["bybit"]
            state_gate = self.states[coin]["gate"]
            state_okx = self.states[coin]["okx"]

            # Oblicz sumy dla kombinowanych danych
            state_combined["current_vol"] = (
                state_binance["current_vol"] + state_bybit["current_vol"] +
                state_gate["current_vol"] + state_okx["current_vol"]
            )
            state_combined["avg_vol"] = (
                state_binance["avg_vol"] + state_bybit["avg_vol"] +
                state_gate["avg_vol"] + state_okx["avg_vol"]
            )
            state_combined["delta"] = (
                state_binance["delta"] + state_bybit["delta"] +
                state_gate["delta"] + state_okx["delta"]
            )

            # Oblicz CAŁKOWITY wolumen dla kombinowanych
            total_buy_vol = (
                state_binance["buy_vol"] + state_bybit["buy_vol"] +
                state_gate["buy_vol"] + state_okx["buy_vol"]
            )
            total_sell_vol = (
                state_binance["sell_vol"] + state_bybit["sell_vol"] +
                state_gate["sell_vol"] + state_okx["sell_vol"]
            )
            total_combined_vol = total_buy_vol + total_sell_vol

            # Oblicz procent delty dla kombinowanych
            combined_delta_percent = (
                (state_combined["delta"] / total_combined_vol * 100)
                if total_combined_vol > 0 else 0
            )

            # Update danych dla każdej giełdy
            self._update_exchange_data(coin, "BINANCE", state_binance)
            self._update_exchange_data(coin, "BYBIT", state_bybit)
            self._update_exchange_data(coin, "GATE.IO", state_gate)
            self._update_exchange_data(coin, "OKX", state_okx)

            # Update Combined
            combined_item = self.tree_item_ids[coin].get('COMBINED')
            if combined_item:
                tag = self._tag_for_value(state_combined['delta'])
                self.tree.item(combined_item, values=(coin, 'COMBINED',
                                                     f"{state_combined['current_vol']:.1f}",
                                                     f"{state_combined['avg_vol']:.1f}",
                                                     f"{state_combined['delta']:+.1f}",
                                                     f"{combined_delta_percent:+.1f}%"), tags=(tag,))

        self.root.after(int(REFRESH_RATE * 1000), self.update_display)

    def _update_exchange_data(self, coin: str, exchange: str, state: dict) -> None:
        """Aktualizuje dane dla jednej giełdy"""
        total_vol = state["buy_vol"] + state["sell_vol"]
        delta_percent = (state["delta"] / total_vol * 100) if total_vol > 0 else 0
        item = self.tree_item_ids[coin].get(exchange)
        if item:
            # preserve parity tag (odd/even) and set value tag for coloring
            existing_tags = list(self.tree.item(item, 'tags') or [])
            parity_tag = next((t for t in existing_tags if t in ('odd', 'even')), None)
            value_tag = self._tag_for_value(state['delta'])
            new_tags = tuple(t for t in (parity_tag, value_tag) if t)
            self.tree.item(item, values=(coin, exchange,
                                         f"{state['current_vol']:.1f}",
                                         f"{state['avg_vol']:.1f}",
                                         f"{state['delta']:+.1f}",
                                         f"{delta_percent:+.1f}%"), tags=new_tags)

    @staticmethod
    def _set_delta_color(label: tk.Label, value: float) -> None:
        """Ustawia kolor labela na podstawie wartości delty"""
        # Deprecated for Treeview usage
        if value > 0:
            label.config(fg="#00ff41")
        elif value < 0:
            label.config(fg="#ff2e63")
        else:
            label.config(fg="#b0b0b0")

    @staticmethod
    def _tag_for_value(value: float) -> str:
        if value > 0:
            return 'positive'
        elif value < 0:
            return 'negative'
        else:
            return 'neutral'
