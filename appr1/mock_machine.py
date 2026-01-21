# mock_machine.py
class Pin:
    OUT = 0

    def __init__(self, pin, mode):
        self.pin = pin
        self.mode = mode

    def value(self, v=None):
        if v is not None:
            print(f"Pin {self.pin} = {v}")
