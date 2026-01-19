
# utils/timeutils.py
import time

# Epoch de MicroPython costuma ser 2000 ou 1970 dependendo do build.
# Vamos manter simples e retornar UNIX epoch (segundos) quando possível.
# Se não houver RTC setado, ainda assim retornará um contador relativo.

_last_monotonic = time.ticks_ms()
_epoch_guess = 0  # pode ser ajustado via NTP em boot.py

def set_epoch_offset(unix_epoch_now):
    """
    Ajusta o offset para que now_s() retorne UNIX epoch real.
    Chame isso após sincronizar via NTP.
    """
    global _epoch_guess, _last_monotonic
    _last_monotonic = time.ticks_ms()
    _epoch_guess = int(unix_epoch_now)

def now_s():
    """
    Retorna um timestamp em segundos.
    - Se NTP configurado (via set_epoch_offset), retorna UNIX epoch.
    - Caso contrário, retorna 'uptime' em segundos desde boot.
    """
    dt_ms = time.ticks_diff(time.ticks_ms(), _last_monotonic)
    return int(_epoch_guess + dt_ms / 1000)
