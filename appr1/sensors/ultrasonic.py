# sensors/ultrasonic.py
try:
    import machine
except ImportError:
    import mock_machine as machine
from machine import Pin, time_pulse_us
import time

class Ultrasonic:
    def __init__(self, name, trigger, echo, threshold_cm, hyst_cm):
        self.name = name
        self.trig = Pin(trigger, Pin.OUT)
        self.echo = Pin(echo, Pin.IN)
        self.threshold = threshold_cm
        self.hyst = hyst_cm
        self.state = False

    def _distance(self):
        self.trig.low()
        time.sleep_us(2)
        self.trig.high()
        time.sleep_us(10)
        self.trig.low()
        pulse = time_pulse_us(self.echo, 1, 30000)
        if pulse < 0:
            return None
        return (pulse / 2) / 29.1

    def read(self):
        dist = self._distance()
        if dist is None:
            return {}

        if self.state:
            if dist > self.threshold + self.hyst:
                self.state = False
        else:
            if dist <= self.threshold:
                self.state = True

        return {
            f"{self.name}_dist_cm": round(dist, 1),
            f"{self.name}_presenca": self.state,
        }