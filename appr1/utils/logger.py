
# utils/logger.py
import time

def _ts():
    try:
        return str(time.time())
    except:
        return "0"

def info(msg):
    print("[INFO]", _ts(), msg)

def warn(msg):
    print("[WARN]", _ts(), msg)

def error(msg):
    print("[ERROR]", _ts(), msg)
