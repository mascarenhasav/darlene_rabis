
# net/http_client.py
import urequests


def post_json(url, payload, token=None):
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['X-Device-Token'] = token
    resp = urequests.post(url, json=payload, headers=headers)
    # opcional: ler resp.text() para debug
    resp.close()
