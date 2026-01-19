
# boot.py
import time
import network
from config import WIFI_SSID, WIFI_PASSWORD
try:
    import ntptime  # pode não existir em todos os firmwares
    _HAS_NTP = True
except:
    _HAS_NTP = False

try:
    from utils.timeutils import set_epoch_offset
except:
    def set_epoch_offset(_): pass

def connect_wifi(ssid, password, attempts=20, delay_s=1):
    wlan = network.WLAN(network.STA_IF)
    if not wlan.active():
        wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(ssid, password)
        for _ in range(attempts):
            if wlan.isconnected():
                break
            time.sleep(delay_s)
    return wlan

def sync_time_with_ntp():
    if not _HAS_NTP:
        return False
    try:
        ntptime.settime()  # atualiza RTC interno (epoch do firmware)
        # Convertendo para UNIX epoch aproximado:
        # Em muitos firmwares MicroPython já fica correto como UNIX epoch.
        # Se não, você pode ajustar manualmente lendo time.localtime() e convertendo.
        set_epoch_offset(time.time())
        return True
    except:
        return False

# Executa na inicialização:
wlan = connect_wifi(WIFI_SSID, WIFI_PASSWORD)
# Tenta NTP (ignora se falhar)
if wlan and wlan.isconnected():
    sync_time_with_ntp()
