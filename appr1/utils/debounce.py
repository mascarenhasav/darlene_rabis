
# utils/debounce.py
import time

class DebouncedInput:
    """
    Debounce de leitura digital por software.
    Uso:
        di = DebouncedInput(pin_callable=lambda: pin.value(), debounce_ms=50)
        val = di.read()  # valor "estável"
    """
    def __init__(self, pin_callable, debounce_ms=50, initial=None):
        self._pin = pin_callable
        self._debounce = debounce_ms
        now = time.ticks_ms()
        v = initial if initial is not None else self._pin()
        self._last_raw = v
        self._stable = v
        self._t = now

    def read(self):
        now = time.ticks_ms()
        raw = self._pin()
        if raw != self._last_raw:
            # borda detectada, reinicia janela
            self._last_raw = raw
            self._t = now
        else:
            # se manteve igual o suficiente, torna estável
            if time.ticks_diff(now, self._t) >= self._debounce:
                self._stable = raw
        return self._stable

    @property
    def stable(self):
        return self._stable
