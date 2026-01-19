
# pc_simulator.py
import time
import random
import threading
import json
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import requests  # pip install requests

# =======================
# CONFIGURAÇÕES SIMULADOR
# =======================

GOOGLE_ENDPOINT = "https://script.google.com/macros/s/AKfycbxKn0e7BMBRK1wkRajZObXYyEEzjEIYhG7yHCPRSvrQ1vlYPecqMPdoqb5iFB5adfNz5w/exec"
DEVICE_TOKEN = "darlene_rabis"

SAMPLE_MS = 500          # período de amostragem
UPLOAD_MS = 10_000       # período de envio
BATCH_MAX = 100          # tamanho máximo do lote por envio

# Definição dos sensores (NOMES devem casar com Apps Script COLUMNS)
DOORS = [
    # pattern pode ser "random:0.05" (troca ~5% por amostra)
    # ou "pattern:closed_open_closed" (ciclo finito/repetição)
    {"name": "porta_dianteira", "pattern": "pattern:closed_open_closed"},
    {"name": "porta_lateral",   "pattern": "random:0.03"},
]

ULTRASONIC = [
    # presence pode ser "random_presence:0.05" (troca ~5% por amostra)
    # distâncias típicas: 80 cm quando presente, 250 cm quando ausente
    {"name": "presenca_frente", "presence": "random_presence:0.07", "dist_present": 90.0, "dist_absent": 240.0},
]

# =======================
# MODELOS E UTILITÁRIOS
# =======================

@dataclass
class Buffer:
    max_items: int = 1000
    q: List[Dict[str, Any]] = field(default_factory=list)

    def push(self, data: Dict[str, Any]):
        if len(self.q) < self.max_items:
            self.q.append(data)

    def pop_batch(self, n: int) -> List[Dict[str, Any]]:
        if not self.q:
            return []
        batch = self.q[:n]
        self.q = self.q[n:]
        return batch

# Porta simulada
class SimDoor:
    def __init__(self, name: str, pattern: str = "random:0.02"):
        self.name = name
        self.open = False
        self._mode = "random"
        self._p = 0.02
        self._sequence = []
        self._idx = 0

        if pattern.startswith("random:"):
            self._mode = "random"
            try:
                self._p = float(pattern.split(":")[1])
            except:
                self._p = 0.02
        elif pattern.startswith("pattern:"):
            self._mode = "sequence"
            seq = pattern.split(":", 1)[1]
            # exemplo: closed_open_closed
            items = seq.split("_")
            # traduz para bool
            mapv = {"closed": False, "open": True, "aberta": True, "fechada": False}
            self._sequence = [mapv.get(it, False) for it in items if it]
            if not self._sequence:
                self._sequence = [False, True, False]

    def read(self) -> Dict[str, Any]:
        if self._mode == "random":
            if random.random() < self._p:
                self.open = not self.open
        else:
            self.open = self._sequence[self._idx % len(self._sequence)]
            self._idx += 1
        return {f"{self.name}_aberta": self.open}

# Ultrassônico simulado
class SimUltrasonic:
    def __init__(self, name: str, presence: str = "random_presence:0.05",
                 dist_present: float = 90.0, dist_absent: float = 240.0):
        self.name = name
        self.present = False
        self.dist_present = dist_present
        self.dist_absent = dist_absent
        self._p = 0.05
        if presence.startswith("random_presence:"):
            try:
                self._p = float(presence.split(":")[1])
            except:
                self._p = 0.05

    def read(self) -> Dict[str, Any]:
        # alterna chance p
        if random.random() < self._p:
            self.present = not self.present
        dist = self.dist_present if self.present else self.dist_absent
        return {
            f"{self.name}_dist_cm": round(dist + random.uniform(-5, 5), 1),  # ruído leve
            f"{self.name}_presenca": self.present
        }

# Envio HTTP para Apps Script
def post_json(url: str, payload: List[Dict[str, Any]], token: Optional[str] = None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["X-Device-Token"] = token
    # Opcional: imprimir para depuração
    print(f"[HTTP] POST {url} ({len(payload)} registros)")
    # print(json.dumps(payload, ensure_ascii=False, indent=2))
    r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=20)
    try:
        print("[HTTP] Status:", r.status_code, "Resp:", r.text[:200])
    finally:
        r.close()

# =======================
# LOOP DO SIMULADOR
# =======================

def main():
    buffer = Buffer(max_items=5000)
    doors = [SimDoor(d["name"], d.get("pattern", "random:0.02")) for d in DOORS]
    ultras = [SimUltrasonic(u["name"],
                            u.get("presence", "random_presence:0.05"),
                            u.get("dist_present", 90.0),
                            u.get("dist_absent", 240.0)) for u in ULTRASONIC]

    last_upload = time.time()
    print("[SIM] Iniciando simulador. Enviando para:", GOOGLE_ENDPOINT)

    while True:
        # Monta uma leitura
        data = {"ts": int(time.time())}

        for d in doors:
            data.update(d.read())

        for u in ultras:
            data.update(u.read())

        buffer.push(data)
        print("[SIM] Amostra:", data)

        # Envio periódico
        now = time.time()
        if (now - last_upload) * 1000.0 >= UPLOAD_MS:
            batch = buffer.pop_batch(BATCH_MAX)
            if batch:
                try:
                    post_json(GOOGLE_ENDPOINT, batch, token=DEVICE_TOKEN)
                except Exception as e:
                    print("[HTTP] Falha no envio, re-enfileirando. Erro:", e)
                    # re-insere no início
                    buffer.q = batch + buffer.q
            last_upload = now

        time.sleep(SAMPLE_MS / 1000.0)

if __name__ == "__main__":
    main()
