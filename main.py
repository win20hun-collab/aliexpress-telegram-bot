import requests, time
from bs4 import BeautifulSoup

URL = "https://www.aliexpress.com/item/1005010120015183.html"
CHECK_INTERVAL = 600
BOT_TOKEN = "8575667908:AAHxAxwEPBx30IWldmPc_EF9hEQLxp_H1o4"
CHAT_ID = "6646276816"

HEADERS = {"User-Agent": "Mozilla/5.0"}

def check_stock():
    try:
        r = requests.get(URL, headers=HEADERS, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        return bool(soup.select_one("button.add-to-cart"))
    except:
        return False

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=5)
    except:
        pass

while True:
    if check_stock():
        send_telegram(f"✅ 재입고!\n{URL}")
        print("재고 발견! 알림 전송 ✅")
    else:
        print("품절 상태...")
    time.sleep(CHECK_INTERVAL)
