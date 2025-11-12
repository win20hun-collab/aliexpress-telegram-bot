import requests, time
from bs4 import BeautifulSoup

# ================= 설정 =================
URL = "https://a.aliexpress.com/_c2QihnfL"  # 영어 페이지 권장
CHECK_INTERVAL = 600  # 10분마다 확인
BOT_TOKEN = "8575667908:AAHxAxwEPBx30IWldmPc_EF9hEQLxp_H1o4"
CHAT_ID = "6646276816"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}

# ============ 재고 확인 함수 ============
def check_stock():
    try:
        response = requests.get(URL, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Add to Cart 버튼 존재 시 재고 있음
        add_to_cart = soup.select_one("button.add-to-cart")
        return add_to_cart is not None
    except Exception as e:
        print("재고 확인 중 오류:", e)
        return False

# ============ 텔레그램 알림 ============
def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg}
    try:
        requests.post(url, data=payload, timeout=5)
    except Exception as e:
        print("텔레그램 전송 오류:", e)

# ============ 메인 루프 ============
while True:
    in_stock = check_stock()
    if in_stock:
        send_telegram(f"✅ 알리 상품 재입고!\n{URL}")
        print("재고 발견! 텔레그램 발송 완료 ✅")
    else:
        print("아직 품절 상태... 다시 확인 중")
    time.sleep(CHECK_INTERVAL)
