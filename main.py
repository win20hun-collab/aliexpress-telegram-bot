import os
import requests
from flask import Flask

# --- 환경 변수 가져오기 (Render 설정에서 자동으로 가져옴) ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# --- 크롤링 대상 URL 설정 ---
TARGET_URL = "https://www.aliexpress.us/item/3256809933700431.html"

# --- 재고 상태 지속성 (봇이 꺼지지 않는 한 알림 중복 방지) ---
# 초기 상태를 '품절'로 설정하여 재고가 들어오는 순간만 알림이 오게 합니다.
LAST_STOCK_STATUS = "OUT_OF_STOCK" 

app = Flask(__name__)

# --- 텔레그램 알림 보내는 기능 ---
def send_telegram_message(message):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("토큰이나 ID가 없어서 알림을 보낼 수 없습니다.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    try:
        requests.post(
            url,
            data={"chat_id": CHAT_ID, "text": message, "disable_web_page_preview": True},
            timeout=10
        )
        print(f"알림 전송 성공: {message}")
    except requests.exceptions.RequestException as e:
        print(f"알림 전송 실패: {e}")


# --- 알리익스프레스 재고를 확인하는 기능 ---
def check_aliexpress_stock():
    global LAST_STOCK_STATUS

    # 알리익스프레스가 봇 접근을 막지 않도록 User-Agent 설정
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(TARGET_URL, headers=headers, timeout=15)
        response.raise_for_status() 
        html_content = response.text
        
        # --- 재고 확인 로직 (수정된 부분) ---
        # 알리익스프레스 HTML 소스에서 품절 상태를 나타내는 가장 확실한 키워드입니다.
        OUT_OF_STOCK_INDICATOR = "PAGE_NOT_FOUND_NOTICE" 
        
        if OUT_OF_STOCK_INDICATOR in html_content:
            current_status = "OUT_OF_STOCK"
            print(f"❌ {current_status}: 아직 품절 상태입니다.")
        else:
            # 품절 키워드가 없으면 재고가 들어온 것으로 간주
            current_status = "IN_STOCK"
            print(f"✅ {current_status}: 재고가 들어왔다고 감지되었습니다!")

        # --- 알림을 보낼지 결정 (상태 변화 감지) ---
        # 현재 재고가 들어왔고, 이전 상태가 품절이었을 때만 알림을 보냅니다.
        if current_status == "IN_STOCK" and LAST_STOCK_STATUS == "OUT_OF_STOCK":
            message = (
                "🎉🎉 재고 알림! 🎉🎉\n"
                "원하던 알리익스프레스 제품의 재고가 들어왔습니다.\n"
                f"바로 확인하세요: {TARGET_URL}"
            )
            send_telegram_message(message)
            # 알림을 보낸 후 상태를 '재고 있음'으로 변경하여 중복 알림을 막습니다.
            LAST_STOCK_STATUS = "IN_STOCK"
        elif current_status == "OUT_OF_STOCK" and LAST_STOCK_STATUS == "IN_STOCK":
            # 다시 품절되면 상태를 '품절'로 돌려놓아 다음에 재고가 들어올 때 알림을 보낼 수 있게 합니다.
            LAST_STOCK_STATUS = "OUT_OF_STOCK"

    except requests.exceptions.RequestException as e:
        print(f"웹사이트 접속 오류 발생: {e}")

# --- Render와 UptimeRobot 핑에 응답하는 웹 엔드포인트 ---
@app.route("/")
def main_endpoint():
    print("-" * 30)
    print("5분마다 핑 요청을 받았습니다. 재고 확인 시작.")
    check_aliexpress_stock()
    
    # 핑 요청에 응답하여 봇이 깨어있음을 알리고 '로딩'을 방지합니다.
    return "AliExpress Stock Checker is alive.", 200

# Gunicorn이 이 Flask 앱을 Render 환경에서 실행합니다.
