
# utils/watchdog.py
try:
    import machine
except ImportError:
    import mock_machine as machine

from machine import WDT

class Watchdog:
    def __init__(self, timeout_ms=8000):
        # Se eu não alimentar o watchdog nesse tempo, a Pico reinicia
        self.wdt = WDT(timeout=timeout_ms)

    def feed(self):
        # Eu chamo isso no loop principal
        self.wdt.feed()
