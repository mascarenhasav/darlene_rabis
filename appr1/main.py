
# main.py
# ==========================================================
# SISTEMA DE ALARME AUTOMOTIVO — KOMB I
# Raspberry Pi Pico 2 W
#
# Neste arquivo eu integro:
# - Sensores
# - Comunicação com Google
# - Sirene local (não-bloqueante)
# - Botão físico de alarme
# - Deep sleep para economia de energia
# - Watchdog para segurança
# ==========================================================

import time
import urequests

from config import *
from sensors.door_switch import DoorSwitch
from sensors.ultrasonic import Ultrasonic
from storage.buffer import Buffer
from net.wifi import connect
from net.http_client import post_json
from utils.alarm_button import AlarmButton
from actuators.siren import Siren
from power.sleep import PowerManager
from utils.watchdog import Watchdog

# ==========================================================
# HARDWARE — ATUADORES E BOTÕES
# ==========================================================

# Aqui eu configuro a sirene física. Ela é controlada de forma não-bloqueante.
SIREN_PIN = 15
siren = Siren(pin=SIREN_PIN)

# Este botão externo alterna o modo alarme e também silencia a sirene.
alarm_button = AlarmButton(pin=10)

# Cache local do estado do alarme (a fonte da verdade é o Google)
alarm_enabled = False

# ==========================================================
# CONTROLE DA SIRENE (NÃO-BLOQUEANTE)
# ==========================================================

# Eu controlo a sirene por estado, nunca usando sleep().
siren_active = False
siren_until = 0  # timestamp (ticks_ms) para desligar automaticamente

# ==========================================================
# SENSORES
# ==========================================================

# Inicializo os sensores declarados no config.py
doors = [DoorSwitch(**d) for d in DOORS]
ultras = [Ultrasonic(**u) for u in ULTRASONIC]

# Buffer local para proteger contra falhas de rede
buffer = Buffer()

# ==========================================================
# REDE
# ==========================================================

# Conecto no Wi‑Fi uma única vez no boot
wifi = connect(WIFI_SSID, WIFI_PASSWORD)

# ==========================================================
# GERENCIAMENTO DE ENERGIA E SEGURANÇA
# ==========================================================

# Este gerenciador decide quando posso entrar em deep sleep
power = PowerManager(sleep_after_s=120)

# Watchdog garante reboot automático caso algo trave
wd = Watchdog(timeout_ms=8000)

# ==========================================================
# TIMERS DO SISTEMA
# ==========================================================

last_upload = time.ticks_ms()
last_sync = time.ticks_ms()
last_actions = time.ticks_ms()

# ==========================================================
# FUNÇÕES AUXILIARES
# ==========================================================

def sync_alarm_state():
    """
    Aqui eu consulto o Google para saber se o modo alarme
    foi alterado remotamente.
    """
    try:
        r = urequests.get(
            GOOGLE_ENDPOINT + "?cmd=get_alarm",
            headers={"X-Device-Token": DEVICE_TOKEN}
        )
        data = r.json()
        r.close()
        return bool(data.get("alarm_enabled", False))
    except:
        return None


def fetch_actions():
    """
    Aqui eu busco ações pendentes (ex.: ligar sirene)
    que o Google colocou na fila.
    """
    try:
        r = urequests.get(
            GOOGLE_ENDPOINT + "?cmd=get_actions",
            headers={"X-Device-Token": DEVICE_TOKEN}
        )
        data = r.json()
        r.close()
        return data.get("actions", [])
    except:
        return []


def start_siren(duration_s):
    """
    Aqui eu ligo a sirene por um tempo determinado,
    sem travar o loop principal.
    """
    global siren_active, siren_until
    siren.on()
    siren_active = True
    siren_until = time.ticks_add(time.ticks_ms(), duration_s * 1000)
    power.notify_activity()
    print("[SIRENE] ON por", duration_s, "s")


def stop_siren():
    """
    Aqui eu desligo a sirene imediatamente.
    """
    global siren_active
    siren.off()
    siren_active = False
    print("[SIRENE] OFF")


def handle_command(cmd):
    """
    Aqui eu interpreto comandos vindos do Google.
    Atualmente eu trato apenas comandos de sirene,
    mas este formato permite expansão futura.
    """
    if cmd.get("cmd") != "siren":
        return

    action = cmd.get("action")
    duration = int(cmd.get("duration", 5))

    if action == "on" and alarm_enabled:
        start_siren(duration)

    elif action == "off":
        stop_siren()

# ==========================================================
# LOOP PRINCIPAL
# ==========================================================

while True:
    now = time.ticks_ms()

    # ------------------------------------------------------
    # CONTROLE DE TEMPO DA SIRENE (NÃO-BLOQUEANTE)
    # ------------------------------------------------------
    if siren_active and time.ticks_diff(now, siren_until) >= 0:
        stop_siren()

    # ------------------------------------------------------
    # SINCRONIZAÇÃO DO ALARME COM O GOOGLE
    # ------------------------------------------------------
    if time.ticks_diff(now, last_sync) > 60000:  # a cada 1 minuto
        v = sync_alarm_state()
        if v is not None:
            alarm_enabled = v
        last_sync = now

    # ------------------------------------------------------
    # BOTÃO FÍSICO DO ALARME
    # ------------------------------------------------------
    if alarm_button.pressed():
        # Um clique alterna o modo alarme
        alarm_enabled = not alarm_enabled
        power.notify_activity()

        print("[ALARM] Modo:", "ON" if alarm_enabled else "OFF")

        # Se alguém apertar o botão, eu desligo a sirene na hora
        stop_siren()

        # Informo o Google da mudança
        post_json(
            GOOGLE_ENDPOINT + "?cmd=set_alarm",
            {"enabled": alarm_enabled},
            token=DEVICE_TOKEN
        )

    # ------------------------------------------------------
    # BUSCA DE AÇÕES REMOTAS (SIRENE)
    # ------------------------------------------------------
    if time.ticks_diff(now, last_actions) > 3000:  # polling leve
        for action in fetch_actions():
            handle_command(action)
        last_actions = now

    # ------------------------------------------------------
    # LEITURA DE SENSORES
    # ------------------------------------------------------
    data = {
        "device": DEVICE_ID,
        "ts": int(time.time())
    }

    for d in doors:
        v = d.read()
        data.update(v)
        if True in v.values():
            power.notify_activity()

    for u in ultras:
        v = u.read()
        data.update(v)
        if v.get("presenca", False):
            power.notify_activity()

    buffer.push(data)

    # ------------------------------------------------------
    # ENVIO PARA O GOOGLE
    # ------------------------------------------------------
    if time.ticks_diff(now, last_upload) > UPLOAD_MS and wifi:
        batch = buffer.pop_all()
        if batch:
            post_json(GOOGLE_ENDPOINT, batch, token=DEVICE_TOKEN)
            power.notify_activity()
        last_upload = now

    # ------------------------------------------------------
    # DECISÃO DE DEEP SLEEP
    # ------------------------------------------------------
    if power.should_sleep(
        siren_active=siren_active,
        buffer_empty=buffer.is_empty()
    ):
        # Eu permito acordar pelo botão e pelos sensores de porta
        wake_pins = [alarm_button.pin] + [d.pin for d in doors]
        power.go_to_sleep(wake_pins=wake_pins)

    # ------------------------------------------------------
    # WATCHDOG — SEGURANÇA
    # ------------------------------------------------------
    wd.feed()

    # ------------------------------------------------------
    # DELAY COOPERATIVO
    # ------------------------------------------------------
    time.sleep_ms(SAMPLE_MS)
