
WIFI_SSID = "SUA_WIFI"
WIFI_PASSWORD = "SENHA"

GOOGLE_ENDPOINT = "https://script.google.com/macros/s/AKfycbxKn0e7BMBRK1wkRajZObXYyEEzjEIYhG7yHCPRSvrQ1vlYPecqMPdoqb5iFB5adfNz5w/exec"
GOOGLE_DEPLOYMENT_ID = "AKfycbxKn0e7BMBRK1wkRajZObXYyEEzjEIYhG7yHCPRSvrQ1vlYPecqMPdoqb5iFB5adfNz5w"
DEVICE_TOKEN = "darlene_rabis"

SAMPLE_MS = 500
UPLOAD_MS = 10000

DOORS = [
    {"name": "porta_dianteira", "pin": 2, "active_low": True},
    {"name": "porta_lateral", "pin": 3, "active_low": True},
]

ULTRASONIC = [
    {
        "name": "presenca_frente",
        "trigger": 6,
        "echo": 7,
        "threshold_cm": 120,
        "hysteresis_cm": 10,
    }
]