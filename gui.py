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

        # Kontener z przewijaniem dla danych
        data_frame = ttk.Frame(main_frame)
        data_frame.pack(fill='both', expand=True)

        # Canvas i Scrollbar
        self.canvas = tk.Canvas(data_frame, bg=self.bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(data_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Nagłówki kolumn - styl tabeli z wyrównaniem
        headers_frame = ttk.Frame(self.scrollable_frame)
        headers_frame.pack(fill='x', pady=5, padx=5)
        
        # Tło nagłówków
        headers_bg = tk.Frame(headers_frame, bg=self.accent_color, height=30)
        headers_bg.pack(fill='x', pady=0)

        columns = [("💰 Coin", 8, 'w'), ("🏦 Exchange", 12, 'w'), 
                  ("📊 Volume", 10, 'e'), ("📈 Avg Vol", 10, 'e'), 
                  ("Δ Delta", 10, 'e'), ("Δ %", 10, 'e')]
        
        for i, (header, width, anchor) in enumerate(columns):
            label = tk.Label(headers_bg, text=header, bg=self.accent_color, fg="#ffffff",
                           font=('Segoe UI', 10, 'bold'), padx=8, pady=8, width=width, anchor=anchor)
            label.pack(side='left', padx=2)

        self.labels = {}
        self.coin_row_frames = {}  # Przechowuje wiersze każdego coina
        self.current_display_row = 0

        # Container na wszystkie dane
        data_container = ttk.Frame(self.scrollable_frame)
        data_container.pack(fill='x', pady=5, padx=5)
        self.data_container = data_container

        # Inicjalizacja labels dla każdego coina (ale bez wyświetlania)
        for coin in COINS:
            self.labels[coin] = {}
            self.coin_row_frames[coin] = []  # Lista wierszy dla tego coina

    def toggle_coin_display(self, coin: str) -> None:
        """Przełącza wyświetlanie coina i monitorowanie 3 giełd"""
        if self.coin_vars[coin].get():
            # Utwórz wiersze dla tego coina jeśli nie istnieją
            if not self.coin_row_frames[coin]:
                self._create_coin_rows(coin)
            self.visible_coins.add(coin)
            asyncio.run_coroutine_threadsafe(self.start_callback(coin), self.loop)
        else:
            # Usuń wiersze tego coina z GUI
            for row_widgets in self.coin_row_frames[coin]:
                for widget in row_widgets:
                    widget.grid_forget()
            # Jeśli istnieje separator
            if len(self.coin_row_frames[coin]) > 0:
                pass  # Separatory usuniemy razem z wierszami
            self.coin_row_frames[coin] = []
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

        # Znaleź ostatni wiersz
        all_children = self.data_container.grid_slaves()
        last_row = 0
        for widget in all_children:
            grid_info = widget.grid_info()
            if grid_info and 'row' in grid_info:
                row = grid_info['row']
                if row >= last_row:
                    last_row = row + 1

        insert_row = last_row

        for row_idx, exchange in enumerate(exchanges):
            # Nazwa coina (tylko dla pierwszego wiersza)
            coin_display = coin if row_idx == 0 else ""
            coin_label = tk.Label(self.data_container, text=coin_display, font=('Segoe UI', 9, 'bold'),
                                 bg=self.bg_color, fg=self.accent_color, width=8, anchor='w')
            coin_label.grid(row=insert_row + row_idx, column=0, padx=8, pady=4, sticky='w')

            # Exchange
            exchange_label = tk.Label(self.data_container, text=f"{exchange_emoji.get(exchange, '')} {exchange}",
                                     font=('Segoe UI', 9), bg=self.bg_color, fg="#00ffff", width=12, anchor='w')
            exchange_label.grid(row=insert_row + row_idx, column=1, padx=8, pady=4, sticky='w')

            # Volume
            vol_label = tk.Label(self.data_container, text="0.0", font=('Segoe UI', 9),
                                bg=self.bg_color, fg=self.fg_color, width=10, anchor='e')
            vol_label.grid(row=insert_row + row_idx, column=2, padx=8, pady=4, sticky='e')

            # Avg Volume
            avg_label = tk.Label(self.data_container, text="0.0", font=('Segoe UI', 9),
                                bg=self.bg_color, fg="#b0b0b0", width=10, anchor='e')
            avg_label.grid(row=insert_row + row_idx, column=3, padx=8, pady=4, sticky='e')

            # Delta
            delta_label = tk.Label(self.data_container, text="0.0", font=('Segoe UI', 9, 'bold'),
                                  bg=self.bg_color, fg=self.fg_color, width=10, anchor='e')
            delta_label.grid(row=insert_row + row_idx, column=4, padx=8, pady=4, sticky='e')

            # Delta %
            delta_percent_label = tk.Label(self.data_container, text="0.0%", font=('Segoe UI', 9, 'bold'),
                                          bg=self.bg_color, fg=self.fg_color, width=10, anchor='e')
            delta_percent_label.grid(row=insert_row + row_idx, column=5, padx=8, pady=4, sticky='e')

            self.labels[coin][exchange] = {
                'volume': vol_label,
                'avg_volume': avg_label,
                'delta': delta_label,
                'delta_percent': delta_percent_label
            }

            self.coin_row_frames[coin].append(
                [coin_label, exchange_label, vol_label, avg_label, delta_label, delta_percent_label]
            )

    def select_all_coins(self) -> None:
        """Zaznacza wszystkie coiny"""
        for coin in COINS:
            self.coin_vars[coin].set(True)
            if not self.coin_row_frames[coin]:
                self._create_coin_rows(coin)
            self.visible_coins.add(coin)
            asyncio.run_coroutine_threadsafe(self.start_callback(coin), self.loop)

    def deselect_all_coins(self) -> None:
        """Odznacza wszystkie coiny"""
        for coin in COINS:
            self.coin_vars[coin].set(False)
            for row_widgets in self.coin_row_frames[coin]:
                for widget in row_widgets:
                    widget.grid_forget()
            self.coin_row_frames[coin] = []
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
            self.labels[coin]["COMBINED"]['volume'].config(
                text=f"{state_combined['current_vol']:.1f}")
            self.labels[coin]["COMBINED"]['avg_volume'].config(
                text=f"{state_combined['avg_vol']:.1f}")
            self._set_delta_color(
                self.labels[coin]["COMBINED"]['delta'], state_combined['delta'])
            self._set_delta_color(
                self.labels[coin]["COMBINED"]['delta_percent'], combined_delta_percent)
            self.labels[coin]["COMBINED"]['delta'].config(
                text=f"{state_combined['delta']:+.1f}")
            self.labels[coin]["COMBINED"]['delta_percent'].config(
                text=f"{combined_delta_percent:+.1f}%")

        self.root.after(int(REFRESH_RATE * 1000), self.update_display)

    def _update_exchange_data(self, coin: str, exchange: str, state: dict) -> None:
        """Aktualizuje dane dla jednej giełdy"""
        total_vol = state["buy_vol"] + state["sell_vol"]
        delta_percent = (state["delta"] / total_vol * 100) if total_vol > 0 else 0

        self.labels[coin][exchange]['volume'].config(text=f"{state['current_vol']:.1f}")
        self.labels[coin][exchange]['avg_volume'].config(text=f"{state['avg_vol']:.1f}")

        self._set_delta_color(self.labels[coin][exchange]['delta'], state['delta'])
        self.labels[coin][exchange]['delta'].config(text=f"{state['delta']:+.1f}")

        self._set_delta_color(
            self.labels[coin][exchange]['delta_percent'], delta_percent)
        self.labels[coin][exchange]['delta_percent'].config(
            text=f"{delta_percent:+.1f}%")

    @staticmethod
    def _set_delta_color(label: tk.Label, value: float) -> None:
        """Ustawia kolor labela na podstawie wartości delty"""
        if value > 0:
            label.config(fg="#00ff41")  # Jasna zieleń
        elif value < 0:
            label.config(fg="#ff2e63")  # Jasna czerwień
        else:
            label.config(fg="#b0b0b0")  # Szary dla zera
