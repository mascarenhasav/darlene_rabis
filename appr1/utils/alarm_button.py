
# utils/alarm_button.py
from machine import Pin
import time

class AlarmButton:
    def __init__(self, pin, debounce_ms=300):
        self.pin = Pin(pin, Pin.IN, Pin.PULL_UP)
        self.debounce = debounce_ms
        self._last = 1
        self._last_time = time.ticks_ms()

    def pressed(self):
        now = time.ticks_ms()
        cur = self.pin.value()

        if cur == 0 and self._last == 1:
            if time.ticks_diff(now, self._last_time) > self.debounce:
                self._last_time = now
                self._last = cur
                return True

        self._last = cur
        return False
