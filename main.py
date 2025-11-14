import os
import requests
from flask import Flask

# --- 환경 변수 가져오기 ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
# 모니터링 대상 URL
TARGET_URL = "https://ko.aliexpress.com/item/1005010120015183.html" 
LAST_STOCK_STATUS = "OUT_OF_STOCK" 

app = Flask(__name__)

# --- 텔레그램 알림 보내는 기능 ---
def send_telegram_message(message):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("토큰이나 ID가 없어서 알림을 보낼 수 없습니다.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": message, "disable_web_page_preview": True}, timeout=10)
        print(f"알림 전송 성공: {message}")
    except requests.exceptions.RequestException as e:
        print(f"알림 전송 실패: {e}")


# --- 알리익스프레스 재고를 확인하는 기능 ---
def check_aliexpress_stock():
    global LAST_STOCK_STATUS
    # 브라우저인 것처럼 위장하여 접속 오류를 줄입니다.
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(TARGET_URL, headers=headers, timeout=15)
        response.raise_for_status() 
        html_content = response.text
        
        # --- 재고 확인 로직 (가장 정확한 '품절' 키워드 사용) ---
        # 품절 상태일 때 화면에 보이는 정확한 텍스트 "품절"을 사용합니다.
        OUT_OF_STOCK_TEXT = "품절" 
        
        # '품절' 텍스트가 HTML 내용에 포함되어 있지 않은 경우에만 재고가 "있는" 것으로 판단합니다.
        if OUT_OF_STOCK_TEXT not in html_content:
            current_status = "IN_STOCK"
            print(f"✅ {current_status}: '품절' 텍스트가 사라져 재고가 감지되었습니다!")
        else:
            current_status = "OUT_OF_STOCK"
            print(f"❌ {current_status}: '품절' 텍스트가 여전히 존재합니다.")

        # --- 알림을 보낼지 결정 (상태 변화 감지) ---
        if current_status == "IN_STOCK" and LAST_STOCK_STATUS == "OUT_OF_STOCK":
            message = (
                "🎉🎉 재고 알림! 🎉🎉\n"
                "원하던 알리익스프레스 제품의 재고가 들어왔습니다.\n"
                f"바로 확인하세요: {TARGET_URL}"
            )
            send_telegram_message(message)
            LAST_STOCK_STATUS = "IN_STOCK"
        elif current_status == "OUT_OF_STOCK" and LAST_STOCK_STATUS == "IN_STOCK":
            LAST_STOCK_STATUS = "OUT_OF_STOCK"

    except requests.exceptions.RequestException as e:
        print(f"웹사이트 접속 오류 발생: {e}")

# --- 엔드포인트는 그대로 유지 ---
@app.route("/")
def main_endpoint():
    print("-" * 30)
    print("재고 확인 시작.")
    check_aliexpress_stock()
    return "AliExpress Stock Checker is alive.", 200
