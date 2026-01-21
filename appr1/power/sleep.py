
# power/sleep.py
try:
    import machine
except ImportError:
    import mock_machine as machine
import time


class PowerManager:
    def __init__(self, sleep_after_s=120):
        # Aqui eu defino quanto tempo de ociosidade é necessário antes de dormir
        self.sleep_after_ms = sleep_after_s * 1000
        self._last_activity = time.ticks_ms()

    def notify_activity(self):
        # Chamo isso sempre que algo "importante" acontece
        self._last_activity = time.ticks_ms()

    def should_sleep(self, siren_active, buffer_empty):
        # Só durmo se eu estiver realmente ocioso
        if siren_active:
            return False
        if not buffer_empty:
            return False

        idle = time.ticks_diff(time.ticks_ms(), self._last_activity)
        return idle > self.sleep_after_ms

    def go_to_sleep(self, wake_pins):
        """
        wake_pins: lista de objetos machine.Pin configurados como entradas com PULL_UP.
        """
        print("[POWER] Entrando em deep sleep")

        # Eu configuro os pinos que podem acordar a Pico
        for pin in wake_pins:
            pin.irq(
                trigger=machine.Pin.IRQ_FALLING,
                handler=lambda p: None
            )

        time.sleep_ms(50)  # pequeno delay de estabilização
        machine.deepsleep()
