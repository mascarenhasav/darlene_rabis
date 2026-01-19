
# sensors/door_switch.py
from machine import Pin
import time

class DoorSwitch:
    def __init__(self, name, pin, active_low=True, debounce_ms=50):
        self.name = name
        self.pin = Pin(pin, Pin.IN, Pin.PULL_UP)
        self.active_low = active_low
        self.debounce = debounce_ms
        self._last = self.pin.value()
        self._last_time = time.ticks_ms()

    def read(self):
        val = self.pin.value()
        now = time.ticks_ms()
        if val != self._last and time.ticks_diff(now, self._last_time) > self.debounce:
            self._last = val
            self._last_time = now

        aberta = (val == 0) if self.active_low else (val == 1)
        return {f"{self.name}_aberta": aberta}
