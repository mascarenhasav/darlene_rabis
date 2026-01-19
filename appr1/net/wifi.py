
# net/wifi.py
import network
import time

def connect(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    for _ in range(20):
        if wlan.isconnected():
            return wlan
        time.sleep(1)
    return None
