
# actuators/siren.py
from machine import Pin

class Siren:
    def __init__(self, pin, active_high=True):
        # Aqui eu configuro o pino da sirene
        self.pin = Pin(pin, Pin.OUT)
        self.active_high = active_high
        self.off()

    def on(self):
        # Eu ligo a sirene conforme a lógica elétrica configurada
        self.pin.value(1 if self.active_high else 0)

    def off(self):
        # Eu desligo a sirene
        self.pin.value(0 if self.active_high else 1)
