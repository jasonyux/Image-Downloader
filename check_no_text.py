# encoding=utf-8
from datetime import date, timedelta
import requests

REQUEST_URL = "http://9.91.84.155:11112/ocrPredict"
DAILY_UPPERBOUND = 2000 # the maximum number of no-text image pulled each day


def check_clean(img_path):
    no_text = 1
    try:
        resp = requests.post(
            REQUEST_URL, files={"file": open(img_path, "rb")}, timeout=10
        )
    except requests.exceptions.RequestException:
        return -1 #error

    # expecting data in the form of { 'data': [ { 'box':..., 'text':'xxx' }, { 'box':..., 'text':'xxx' }, ... ] }
    resp = resp.json()
    if resp is None or resp.get("data") is None:
        return -1 #error

    for ocr_data in resp.get("data"):
        parsed_text = ocr_data.get("text")
        # image with text
        if parsed_text is not None or parsed_text.strip():
            no_text = 0
            break
    return no_text
