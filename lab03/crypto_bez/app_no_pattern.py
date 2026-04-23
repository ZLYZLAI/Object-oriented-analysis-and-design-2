
# главное отличие от паттерна: метод _on_price_update() знает обо всех компонентах
# и сам решает, кого вызвать. добавить новый компонент = лезть и менять этот метод

import tkinter as tk
from tkinter import ttk, scrolledtext
from collections import deque
from typing import Optional, List
from datetime import datetime

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from fetcher import PriceFetcher


BG_DARK      = "#0d1117"
BG_CARD      = "#161b22"
BG_PANEL     = "#1c2128"
GREEN        = "#3fb950"
RED          = "#f85149"
BLUE         = "#58a6ff"
YELLOW       = "#e3b341"
TEXT_PRIMARY = "#e6edf3"
TEXT_MUTED   = "#7d8590"
BORDER       = "#30363d"


class PriceChart:
    # компонент графика - теперь это просто вспомогательный класс без связи с паттерном
    # он не знает ни про какого издателя, его метод draw() вызывается напрямую из _on_price_update

    MAX_POINTS = 60

    def __init__(self, frame: tk.Frame, symbol: str):
        self._symbol      = symbol
        self._prices      = deque(maxlen=self.MAX_POINTS)
        self._times       = deque(maxlen=self.MAX_POINTS)
        self._start_price: Optional[float] = None

        self._fig = Figure(figsize=(5, 2.6), dpi=96, facecolor=BG_CARD)
        self._ax  = self._fig.add_subplot(111)
        self._ax.set_facecolor(BG_DARK)

        self._canvas = FigureCanvasTkAgg(self._fig, master=frame)
        self._canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self._placeholder()

    def _placeholder(self):
        self._ax.clear()
        self._ax.set_facecolor(BG_DARK)
        self._ax.text(0.5, 0.5, "Ожидание данных...", ha="center", va="center",
                      color=TEXT_MUTED, fontsize=10, transform=self._ax.transAxes)
        self._ax.set_title(self._symbol, color=TEXT_PRIMARY, fontsize=10, pad=6)
        self._style()
        self._canvas.draw()

    def draw(self, price: float, timestamp: datetime) -> None:
        # метод называется draw(), а не update() - здесь нет никакого интерфейса Observer,
        # просто конкретный метод с конкретным названием, который знает _on_price_update
        if self._start_price is None:
            self._start_price = price
        self._prices.append(price)
        self._times.append(timestamp)
        self._redraw()

    def _redraw(self):
        self._ax.clear()
        self._ax.set_facecolor(BG_DARK)
        prices = list(self._prices)
        times  = list(self._times)

        if len(prices) < 2:
            self._ax.text(0.5, 0.5, "Собираем данные...", ha="center", va="center",
                          color=TEXT_MUTED, fontsize=10, transform=self._ax.transAxes)
            self._ax.set_title(self._symbol, color=TEXT_PRIMARY, fontsize=10, pad=6)
        else:
            c = GREEN if prices[-1] >= prices[0] else RED
            self._ax.plot(times, prices, color=c, linewidth=2)
            self._ax.fill_between(times, prices, min(prices), alpha=0.12, color=c)
            self._ax.axhline(y=prices[0], color=TEXT_MUTED, linestyle="--",
                             linewidth=0.8, alpha=0.4)
            self._ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
            self._fig.autofmt_xdate(rotation=0, ha="center")
            self._ax.yaxis.set_major_formatter(
                mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))

            pct  = (prices[-1] - prices[0]) / prices[0] * 100
            sign = "+" if pct >= 0 else ""
            col  = GREEN if pct >= 0 else RED
            self._ax.set_title(f"{self._symbol}  {sign}{pct:.2f}% сессии",
                               color=col, fontsize=10, pad=6)

        self._style()
        self._fig.tight_layout(pad=1.5)
        self._canvas.draw()

    def _style(self):
        self._ax.tick_params(colors=TEXT_MUTED, labelsize=8)
        for s in self._ax.spines.values():
            s.set_color(BORDER)


class AlertsPanel:
    # панель алертов - тоже просто компонент, его метод check() зовёт _on_price_update напрямую

    def __init__(self, frame: tk.Frame):
        self._alerts: List[dict] = []
        self._build(frame)

    def _build(self, frame: tk.Frame):
        tk.Label(frame, text="🔔 Алерты", bg=BG_CARD, fg=TEXT_PRIMARY,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=10, pady=(10, 4))

        form = tk.Frame(frame, bg=BG_CARD)
        form.pack(fill=tk.X, padx=8, pady=2)

        self._dir_var = tk.StringVar(value=">")
        ttk.Combobox(form, textvariable=self._dir_var, values=[">", "<"],
                     width=3, state="readonly").pack(side=tk.LEFT, padx=(0, 4))

        self._thr_var = tk.StringVar(value="50000")
        tk.Entry(form, textvariable=self._thr_var, bg=BG_PANEL, fg=TEXT_PRIMARY,
                 insertbackground=TEXT_PRIMARY, relief="flat", width=10,
                 font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(0, 6))

        tk.Button(form, text="+ BTC", bg=YELLOW, fg="#000", relief="flat",
                  font=("Segoe UI", 9, "bold"), cursor="hand2",
                  command=lambda: self._add("bitcoin", "BTC")).pack(side=tk.LEFT, padx=(0, 3))

        tk.Button(form, text="+ ETH", bg=BLUE, fg="#000", relief="flat",
                  font=("Segoe UI", 9, "bold"), cursor="hand2",
                  command=lambda: self._add("ethereum", "ETH")).pack(side=tk.LEFT)

        self._listbox = tk.Listbox(frame, bg=BG_PANEL, fg=TEXT_PRIMARY,
                                   selectbackground=BORDER, relief="flat",
                                   font=("Consolas", 9), height=3, highlightthickness=0)
        self._listbox.pack(fill=tk.X, padx=8, pady=4)

        btn_row = tk.Frame(frame, bg=BG_CARD)
        btn_row.pack(fill=tk.X, padx=8)

        tk.Button(btn_row, text="✕ Удалить", bg=BG_PANEL, fg=RED, relief="flat",
                  font=("Segoe UI", 9), cursor="hand2",
                  command=self._remove).pack(side=tk.LEFT)

        tk.Button(btn_row, text="↺ Сбросить", bg=BG_PANEL, fg=TEXT_MUTED, relief="flat",
                  font=("Segoe UI", 9), cursor="hand2",
                  command=self._reset).pack(side=tk.LEFT, padx=(6, 0))

        tk.Label(frame, text="История срабатываний:", bg=BG_CARD, fg=TEXT_MUTED,
                 font=("Segoe UI", 9)).pack(anchor="w", padx=10, pady=(8, 2))

        self._history = tk.Text(frame, bg=BG_PANEL, fg=YELLOW, relief="flat",
                                font=("Consolas", 9), height=3,
                                state="disabled", highlightthickness=0)
        self._history.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

    def _add(self, coin_id: str, symbol: str):
        try:
            thr = float(self._thr_var.get().replace(",", ""))
        except ValueError:
            return
        self._alerts.append({"coin_id": coin_id, "symbol": symbol,
                              "direction": self._dir_var.get(),
                              "threshold": thr, "triggered": False})
        self._refresh()

    def _remove(self):
        sel = self._listbox.curselection()
        if sel:
            self._alerts.pop(sel[0])
            self._refresh()

    def _reset(self):
        for a in self._alerts:
            a["triggered"] = False
        self._refresh()

    def _refresh(self):
        self._listbox.delete(0, tk.END)
        for a in self._alerts:
            icon = "✓" if a["triggered"] else "○"
            self._listbox.insert(
                tk.END,
                f"  {icon}  {a['symbol']} {a['direction']} ${a['threshold']:,.0f}")
            if a["triggered"]:
                self._listbox.itemconfig(tk.END, fg=RED)

    def check(self, coin_id: str, symbol: str, price: float, timestamp: datetime) -> None:
        # метод называется check() - не update(), потому что нет никакого интерфейса
        for a in self._alerts:
            if a["triggered"] or a["coin_id"] != coin_id:
                continue
            fired = (a["direction"] == ">" and price > a["threshold"]) or \
                    (a["direction"] == "<" and price < a["threshold"])
            if fired:
                a["triggered"] = True
                msg = (f"⚡ {a['symbol']} {a['direction']} ${a['threshold']:,.0f}  "
                       f"Цена: ${price:,.2f}  "
                       f"{timestamp.strftime('%H:%M:%S')}\n")
                self._history.config(state="normal")
                self._history.insert("1.0", msg)
                self._history.config(state="disabled")
        self._refresh()


class PortfolioPanel:
    # панель портфеля - метод recalculate() зовут напрямую из _on_price_update

    def __init__(self, frame: tk.Frame):
        self._amounts  = {"bitcoin": 0.0, "ethereum": 0.0}
        self._initials = {"bitcoin": None, "ethereum": None}
        self._last     = {"bitcoin": None, "ethereum": None}
        self._build(frame)

    def _build(self, frame: tk.Frame):
        tk.Label(frame, text="💼 Портфель", bg=BG_CARD, fg=TEXT_PRIMARY,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=10, pady=(10, 4))

        for coin_id, symbol, color in [("bitcoin", "BTC", YELLOW),
                                        ("ethereum", "ETH", BLUE)]:
            row = tk.Frame(frame, bg=BG_CARD)
            row.pack(fill=tk.X, padx=8, pady=2)

            tk.Label(row, text=f"{symbol}:", bg=BG_CARD, fg=color,
                     font=("Segoe UI", 9, "bold"), width=4).pack(side=tk.LEFT)

            var = tk.StringVar(value="1.0")
            setattr(self, f"_var_{coin_id}", var)

            tk.Entry(row, textvariable=var, bg=BG_PANEL, fg=TEXT_PRIMARY,
                     insertbackground=TEXT_PRIMARY, relief="flat", width=8,
                     font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=4)

            tk.Button(row, text="Применить", bg=BLUE, fg="#000", relief="flat",
                      font=("Segoe UI", 9), cursor="hand2",
                      command=lambda c=coin_id: self._apply(c)).pack(side=tk.LEFT)

        self._btc_val = tk.Label(frame, text="BTC: —", bg=BG_PANEL, fg=YELLOW,
                                  font=("Segoe UI", 12, "bold"), pady=3)
        self._btc_val.pack(fill=tk.X, padx=8, pady=(6, 1))
        self._btc_pnl = tk.Label(frame, text="Итог сессии: —", bg=BG_CARD,
                                  fg=TEXT_MUTED, font=("Segoe UI", 9))
        self._btc_pnl.pack()

        self._eth_val = tk.Label(frame, text="ETH: —", bg=BG_PANEL, fg=BLUE,
                                  font=("Segoe UI", 12, "bold"), pady=3)
        self._eth_val.pack(fill=tk.X, padx=8, pady=(6, 1))
        self._eth_pnl = tk.Label(frame, text="Итог сессии: —", bg=BG_CARD,
                                  fg=TEXT_MUTED, font=("Segoe UI", 9))
        self._eth_pnl.pack()

        self._total_lbl = tk.Label(frame, text="Итого: —", bg=BG_CARD, fg=TEXT_PRIMARY,
                                    font=("Segoe UI", 10, "bold"))
        self._total_lbl.pack(pady=(5, 6))

    def _apply(self, coin_id: str):
        var = getattr(self, f"_var_{coin_id}")
        try:
            self._amounts[coin_id] = float(var.get().replace(",", "."))
        except ValueError:
            return
        self._initials[coin_id] = None
        if self._last[coin_id]:
            # вызываем recalculate() сами на себе - без паттерна нет notify,
            # поэтому пересчёт после "Применить" приходится делать вручную
            price, ts = self._last[coin_id]
            self.recalculate(coin_id, price, ts)

    def recalculate(self, coin_id: str, price: float, timestamp: datetime) -> None:
        # метод называется recalculate() - конкретное имя вместо абстрактного update()
        self._last[coin_id] = (price, timestamp)
        amount = self._amounts.get(coin_id, 0.0)
        if amount <= 0:
            return

        val = amount * price

        if self._initials[coin_id] is None:
            self._initials[coin_id] = val

        init  = self._initials[coin_id]
        pnl   = val - init
        pct   = (pnl / init * 100) if init else 0.0
        color = GREEN if pnl >= 0 else RED
        sign  = "+" if pnl >= 0 else ""
        pnl_text = f"Итог сессии: {sign}${pnl:,.2f} ({sign}{pct:.2f}%)"

        if coin_id == "bitcoin":
            self._btc_val.config(text=f"BTC: ${val:,.2f}")
            self._btc_pnl.config(text=pnl_text, fg=color)
        else:
            self._eth_val.config(text=f"ETH: ${val:,.2f}")
            self._eth_pnl.config(text=pnl_text, fg=color)

        # пересчёт итога - нужны цены обеих монет, берём из последних сохранённых
        btc = self._last.get("bitcoin")
        eth = self._last.get("ethereum")
        btc_price = btc[0] if btc else 0
        eth_price = eth[0] if eth else 0
        total = self._amounts["bitcoin"] * btc_price + self._amounts["ethereum"] * eth_price
        if total > 0:
            self._total_lbl.config(text=f"Итого: ${total:,.2f}")


class EventLog:
    # лог событий - метод write() зовут напрямую из _on_price_update

    def __init__(self, frame: tk.Frame):
        self._prev  = {"bitcoin": 0.0, "ethereum": 0.0}
        self._start = {"bitcoin": None, "ethereum": None}
        self._build(frame)

    def _build(self, frame: tk.Frame):
        header = tk.Frame(frame, bg=BG_CARD)
        header.pack(fill=tk.X, padx=8, pady=(8, 4))

        tk.Label(header, text="📋 Лог событий", bg=BG_CARD, fg=TEXT_PRIMARY,
                 font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT)

        tk.Button(header, text="Очистить", bg=BG_PANEL, fg=TEXT_MUTED, relief="flat",
                  font=("Segoe UI", 9), cursor="hand2",
                  command=self._clear).pack(side=tk.RIGHT)

        self._text = scrolledtext.ScrolledText(
            frame, bg=BG_DARK, fg=TEXT_PRIMARY, relief="flat",
            font=("Consolas", 9), state="disabled", height=5, highlightthickness=0)
        self._text.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        self._text.tag_config("up",   foreground=GREEN)
        self._text.tag_config("down", foreground=RED)
        self._text.tag_config("flat", foreground=TEXT_MUTED)

    def write(self, coin_id: str, symbol: str, price: float,
              timestamp: datetime) -> None:
        # метод называется write() - конкретное имя для конкретного действия
        prev = self._prev[coin_id]

        if self._start[coin_id] is None:
            self._start[coin_id] = price

        if prev == 0:
            arrow, tag = "▶", "flat"
        elif price > prev:
            arrow, tag = "▲", "up"
        elif price < prev:
            arrow, tag = "▼", "down"
        else:
            arrow, tag = "▶", "flat"

        start     = self._start[coin_id]
        sess_pct  = (price - start) / start * 100 if start else 0.0
        sess_sign = "+" if sess_pct >= 0 else ""

        line = (f"{timestamp.strftime('%H:%M:%S')}  "
                f"{symbol:<3}  {arrow} ${price:>12,.2f}  "
                f"сессия: {sess_sign}{sess_pct:.2f}%\n")

        self._text.config(state="normal")
        self._text.insert("1.0", line, tag)
        self._text.config(state="disabled")

        self._prev[coin_id] = price

    def _clear(self):
        self._text.config(state="normal")
        self._text.delete("1.0", tk.END)
        self._text.config(state="disabled")


class CryptoApp:
    # главный класс - и здесь главное отличие от паттерна:
    # _on_price_update() знает о каждом компоненте по имени и дёргает каждый вручную
    # это жёсткая связанность - добавить компонент = менять этот метод

    INTERVALS = {"15 сек": 15, "30 сек": 30, "60 сек": 60}

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🤯КРИПТОМИЛЛИОНЕРЫЧ🤯")
        self.root.configure(bg=BG_DARK)
        self.root.geometry("1500x860")
        self.root.minsize(1100, 700)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TCombobox",
                         fieldbackground=BG_PANEL, background=BG_PANEL,
                         foreground=TEXT_PRIMARY, selectbackground=BG_PANEL,
                         selectforeground=TEXT_PRIMARY, arrowcolor=TEXT_MUTED)
        style.map("TCombobox",
                  fieldbackground=[("readonly", BG_PANEL)],
                  foreground=[("readonly", TEXT_PRIMARY)])

        self.fetcher = PriceFetcher()
        self.fetcher.set_root(self.root)
        # передаём ОДИН конкретный метод - не список подписчиков, а один обработчик
        self.fetcher.set_callback(self._on_price_update)
        self.fetcher.set_error_callback(self._on_error)

        self._build_layout()
        self._init_components()

        # хранилища стартовых цен - в паттерне это было внутри каждого Observer,
        # здесь это лежит в главном классе, потому что он всем управляет
        self._start_prices = {"bitcoin": None, "ethereum": None}

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_layout(self):
        outer = tk.Frame(self.root, bg=BG_DARK)
        outer.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self._left = tk.Frame(outer, bg=BG_CARD, width=245)
        self._left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        self._left.pack_propagate(False)
        self._build_left(self._left)

        right = tk.Frame(outer, bg=BG_DARK)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        charts_row = tk.Frame(right, bg=BG_DARK)
        charts_row.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        self.btc_chart_frame = tk.Frame(charts_row, bg=BG_CARD)
        self.btc_chart_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        self.eth_chart_frame = tk.Frame(charts_row, bg=BG_CARD)
        self.eth_chart_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        mid = tk.Frame(right, bg=BG_DARK, height=270)
        mid.pack(fill=tk.X, pady=(0, 8))
        mid.pack_propagate(False)

        self.alerts_frame = tk.Frame(mid, bg=BG_CARD)
        self.alerts_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        self.portfolio_frame = tk.Frame(mid, bg=BG_CARD)
        self.portfolio_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.log_frame = tk.Frame(right, bg=BG_CARD, height=165)
        self.log_frame.pack(fill=tk.X)
        self.log_frame.pack_propagate(False)

    def _init_components(self):
        # создаём компоненты и держим ссылки на них - потому что _on_price_update будет обращаться к каждому по имени
        self._btc_chart  = PriceChart(self.btc_chart_frame, "BTC")
        self._eth_chart  = PriceChart(self.eth_chart_frame, "ETH")
        self._alerts     = AlertsPanel(self.alerts_frame)
        self._portfolio  = PortfolioPanel(self.portfolio_frame)
        self._log        = EventLog(self.log_frame)

    def _on_price_update(self, coin_id: str, symbol: str, price: float,
                         change_24h: float, volume: float,
                         market_cap: float, timestamp: datetime) -> None:
        # вот сердце "подхода без паттерна"
        # этот метод знает о каждом компоненте и вызывает каждый по имени
        #
        # notify() из паттерна:
        #   for obs in self._observers:
        #       obs.update(event)         # два слова - всё
        #
        # здесь же мы вынуждены перечислять каждый компонент вручную
        # добавить новый компонент - придти сюда и вписать ещё одну строчку
        # убрать компонент - тоже сюда, переименовать метод компонента - тоже сюда

        if self._start_prices[coin_id] is None:
            self._start_prices[coin_id] = price

        chart = self._btc_chart if coin_id == "bitcoin" else self._eth_chart
        chart.draw(price, timestamp)

        self._alerts.check(coin_id, symbol, price, timestamp)

        self._portfolio.recalculate(coin_id, price, timestamp)

        self._log.write(coin_id, symbol, price, timestamp)

        self._update_panel(coin_id, symbol, price, volume, market_cap)

        self._update_timestamp(timestamp)

    def _update_panel(self, coin_id: str, symbol: str, price: float,
                      volume: float, market_cap: float) -> None:
        # обновляем ценовые лейблы в левой панели - в паттерне это был PanelObserver,
        # теперь это просто метод главного класса, который напрямую трогает self.btc_price и т.д.
        start = self._start_prices[coin_id]
        pct   = (price - start) / start * 100 if start else 0.0
        up    = pct >= 0
        color = GREEN if up else RED
        arrow = "▲" if up else "▼"
        sign  = "+" if up else ""

        def fmt_big(n):
            if n >= 1e12: return f"${n/1e12:.2f}T"
            if n >= 1e9:  return f"${n/1e9:.2f}B"
            if n >= 1e6:  return f"${n/1e6:.1f}M"
            return f"${n:,.0f}"

        if coin_id == "bitcoin":
            self.btc_price.config(text=f"${price:,.2f}")
            self.btc_change.config(text=f"{arrow} {sign}{pct:.2f}% сессии", fg=color)
            self.btc_vol.config(text=f"Объём (24ч): {fmt_big(volume)}")
            self.btc_mcap.config(text=f"MCap: {fmt_big(market_cap)}")
        else:
            self.eth_price.config(text=f"${price:,.2f}")
            self.eth_change.config(text=f"{arrow} {sign}{pct:.2f}% сессии", fg=color)
            self.eth_vol.config(text=f"Объём (24ч): {fmt_big(volume)}")
            self.eth_mcap.config(text=f"MCap: {fmt_big(market_cap)}")

    def _update_timestamp(self, timestamp: datetime) -> None:
        self.updated_lbl.config(text=f"Обновлено: {timestamp.strftime('%H:%M:%S')}")

    def _build_left(self, p: tk.Frame):
        tk.Label(p, text="🤯", bg=BG_CARD, font=("Segoe UI", 26)).pack(pady=(14, 0))
        tk.Label(p, text="КРИПТО\nМИЛЛИОНЕРЫЧ", bg=BG_CARD, fg=BLUE,
                 font=("Segoe UI", 12, "bold"), justify="center").pack()

        self._sep(p)

        tk.Label(p, text="Интервал обновления", bg=BG_CARD, fg=TEXT_MUTED,
                 font=("Segoe UI", 9)).pack(anchor="w", padx=14)

        self._interval_var = tk.StringVar(value="15 сек")
        ttk.Combobox(p, textvariable=self._interval_var,
                     values=list(self.INTERVALS.keys()),
                     state="readonly").pack(fill=tk.X, padx=12, pady=(2, 8))

        self._sep(p)

        self.start_btn = tk.Button(p, text="▶  СТАРТ", bg=BG_PANEL, fg=GREEN,
                                    font=("Segoe UI", 11, "bold"), relief="flat",
                                    cursor="hand2", pady=8, command=self._start)
        self.start_btn.pack(fill=tk.X, padx=12, pady=(10, 4))

        self.stop_btn = tk.Button(p, text="⏹  СТОП", bg=BG_PANEL, fg=RED,
                                   font=("Segoe UI", 11, "bold"), relief="flat",
                                   cursor="hand2", pady=8, state="disabled",
                                   command=self._stop)
        self.stop_btn.pack(fill=tk.X, padx=12, pady=(0, 4))

        self._sep(p)

        tk.Label(p, text="Bitcoin (BTC)", bg=BG_CARD, fg=YELLOW,
                 font=("Segoe UI", 9, "bold")).pack(pady=(10, 0))
        self.btc_price  = tk.Label(p, text="$ —", bg=BG_CARD, fg=TEXT_PRIMARY,
                                    font=("Segoe UI", 18, "bold"))
        self.btc_price.pack()
        self.btc_change = tk.Label(p, text="—", bg=BG_CARD, fg=TEXT_MUTED,
                                    font=("Segoe UI", 10))
        self.btc_change.pack()
        self.btc_vol    = tk.Label(p, text="Объём (24ч): —", bg=BG_CARD,
                                    fg=TEXT_MUTED, font=("Segoe UI", 8))
        self.btc_vol.pack()
        self.btc_mcap   = tk.Label(p, text="MCap: —", bg=BG_CARD,
                                    fg=TEXT_MUTED, font=("Segoe UI", 8))
        self.btc_mcap.pack()

        self._sep(p)

        tk.Label(p, text="Ethereum (ETH)", bg=BG_CARD, fg=BLUE,
                 font=("Segoe UI", 9, "bold")).pack(pady=(4, 0))
        self.eth_price  = tk.Label(p, text="$ —", bg=BG_CARD, fg=TEXT_PRIMARY,
                                    font=("Segoe UI", 18, "bold"))
        self.eth_price.pack()
        self.eth_change = tk.Label(p, text="—", bg=BG_CARD, fg=TEXT_MUTED,
                                    font=("Segoe UI", 10))
        self.eth_change.pack()
        self.eth_vol    = tk.Label(p, text="Объём (24ч): —", bg=BG_CARD,
                                    fg=TEXT_MUTED, font=("Segoe UI", 8))
        self.eth_vol.pack()
        self.eth_mcap   = tk.Label(p, text="MCap: —", bg=BG_CARD,
                                    fg=TEXT_MUTED, font=("Segoe UI", 8))
        self.eth_mcap.pack()

        self._sep(p)

        self.status_lbl = tk.Label(p, text="⚪  Остановлен", bg=BG_CARD,
                                    fg=TEXT_MUTED, font=("Segoe UI", 9),
                                    wraplength=220)
        self.status_lbl.pack(pady=(8, 2))

        self.updated_lbl = tk.Label(p, text="", bg=BG_CARD,
                                     fg=TEXT_MUTED, font=("Segoe UI", 8))
        self.updated_lbl.pack()

    def _sep(self, p: tk.Frame):
        tk.Frame(p, bg=BORDER, height=1).pack(fill=tk.X, padx=12, pady=5)

    def _start(self):
        self.fetcher.set_interval(self.INTERVALS[self._interval_var.get()])
        self.fetcher.start()
        self.start_btn.config(state="disabled", fg=TEXT_MUTED)
        self.stop_btn.config(state="normal")
        self.status_lbl.config(text="🟢  Работает", fg=GREEN)

    def _stop(self):
        self.fetcher.stop()
        self.start_btn.config(state="normal", fg=GREEN)
        self.stop_btn.config(state="disabled")
        self.status_lbl.config(text="⚪  Остановлен", fg=TEXT_MUTED)

    def _on_error(self, msg: str):
        self.status_lbl.config(text=f"⚠  {msg}", fg=YELLOW)
        self.root.after(6000, self._clear_error)

    def _clear_error(self):
        if self.fetcher.is_running():
            self.status_lbl.config(text="🟢  Работает", fg=GREEN)
        else:
            self.status_lbl.config(text="⚪  Остановлен", fg=TEXT_MUTED)

    def _on_close(self):
        self.fetcher.stop()
        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = CryptoApp()
    app.run()
