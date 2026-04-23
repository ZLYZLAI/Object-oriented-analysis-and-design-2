# fetcher.py - фоновый поток и запрос к API
# в отличие от core.py, здесь нет никакой абстракции подписчиков -
# просто получаем данные и отдаём их напрямую через один callback

import threading
import time
import requests
from datetime import datetime
from typing import Optional


class PriceFetcher:
    # класс знает только одно: как ходить в API и звать callback с результатом
    # кто и как обработает данные - не его дело, но он жёстко завязан на формат callback

    def __init__(self):
        self._running  = False
        self._thread: Optional[threading.Thread] = None
        self._interval = 15
        self._root     = None
        self._callback = None   # функция вида: callback(coin_id, symbol, price, change_24h, volume, market_cap, timestamp)
        self._error_cb = None

    def set_root(self, root) -> None:
        self._root = root

    def set_callback(self, cb) -> None:
        # единственный получатель данных - в отличие от паттерна, здесь нельзя добавить второго получателя не меняя этот класс
        self._callback = cb

    def set_error_callback(self, cb) -> None:
        self._error_cb = cb

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
            for _ in range(self._interval):
                if not self._running:
                    break
                time.sleep(1)

    def _fetch(self) -> None:
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

                # передаём все поля как отдельные аргументы - нет единого объекта-события,
                # поэтому сигнатура callback-а громоздкая и хрупкая: добавить новое поле - придёт менять и здесь, и в callback-е
                args = (
                    coin_id,
                    symbol,
                    d.get("usd", 0.0),
                    d.get("usd_24h_change", 0.0),
                    d.get("usd_24h_vol", 0.0),
                    d.get("usd_market_cap", 0.0),
                    now,
                )
                if self._root and self._callback:
                    self._root.after(0, lambda a=args: self._callback(*a))

        except requests.exceptions.RequestException as e:
            msg = f"Ошибка сети: {e}"
            if self._root and self._error_cb:
                self._root.after(0, lambda m=msg: self._error_cb(m))
        except Exception as e:
            msg = str(e)
            if self._root and self._error_cb:
                self._root.after(0, lambda m=msg: self._error_cb(m))
