import threading
import time
import requests
from datetime import datetime
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class PriceEvent:
    # объект-событие - конверт данных, который издатель рассылает всем подписчикам
    coin_id:    str       # внутренний id в coingecko: "bitcoin" или "ethereum"
    symbol:     str       # тикер: "BTC" или "ETH"
    price:      float     # цена в USD
    change_24h: float     # изменение за 24 часа в процентах (нужно для объёма/mcap)
    volume:     float     # объём торгов за 24ч в USD
    market_cap: float     # рыночная капитализация в USD
    timestamp:  datetime  # время получения данных


class Observer:
    # базовый класс для всех наблюдателей
    # каждый подписчик наследует его и обязан реализовать update()
    def update(self, event: PriceEvent) -> None:
        raise NotImplementedError


class PricePublisher:
    # издатель - единственный кто трогает апи
    # он не знает, что делают подписчики, просто рассылает им события

    def __init__(self):
        self._observers: List[Observer] = []
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._interval = 15
        self._root     = None   # ссылка на окно tkinter - нужна для after()
        self._error_cb = None

    def set_root(self, root) -> None:
        self._root = root

    def set_error_callback(self, cb) -> None:
        self._error_cb = cb

    def subscribe(self, observer: Observer) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def unsubscribe(self, observer: Observer) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, event: PriceEvent) -> None:
        # рассылаем конверт всем подписчикам - каждый сам решает, что делать
        for obs in self._observers:
            try:
                obs.update(event)
            except Exception as e:
                print(f"[{obs.__class__.__name__}] ошибка в update: {e}")

    def set_interval(self, seconds: int) -> None:
        self._interval = seconds

    def is_running(self) -> bool:
        return self._running

    def start(self) -> None:
        if not self._running:
            self._running = True
            self._thread = threading.Thread(target=self._loop, daemon=True)
            self._thread.start()

    def stop(self) -> None:
        self._running = False

    def _loop(self) -> None:
        while self._running:
            self._fetch()
            # спим по 1 секунде, чтобы быстро реагировать на stop()
            for _ in range(self._interval):
                if not self._running:
                    break
                time.sleep(1)

    def _fetch(self) -> None:
        # один запрос - обе монеты сразу, чтобы не превышать лимит API
        try:
            resp = requests.get(
                "https://api.coingecko.com/api/v3/simple/price",
                params={
                    "ids":                 "bitcoin,ethereum",
                    "vs_currencies":       "usd",
                    "include_24hr_change": "true",
                    "include_24hr_vol":    "true",
                    "include_market_cap":  "true",
                },
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
            now  = datetime.now()

            coins = {"bitcoin": "BTC", "ethereum": "ETH"}
            for coin_id, symbol in coins.items():
                d = data.get(coin_id, {})
                event = PriceEvent(
                    coin_id    = coin_id,
                    symbol     = symbol,
                    price      = d.get("usd", 0.0),
                    change_24h = d.get("usd_24h_change", 0.0),
                    volume     = d.get("usd_24h_vol", 0.0),
                    market_cap = d.get("usd_market_cap", 0.0),
                    timestamp  = now,
                )
                # обновлять виджеты tkinter можно только из главного потока
                # after(0, ...) передаёт вызов в очередь главного потока
                if self._root:
                    self._root.after(0, lambda e=event: self.notify(e))

        except requests.exceptions.RequestException as e:
            # сохраняем текст ошибки в отдельную переменную до создания лямбды
            msg = f"Ошибка сети: {e}"
            if self._root and self._error_cb:
                self._root.after(0, lambda m=msg: self._error_cb(m))
        except Exception as e:
            msg = str(e)
            if self._root and self._error_cb:
                self._root.after(0, lambda m=msg: self._error_cb(m))