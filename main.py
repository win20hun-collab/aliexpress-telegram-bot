import os
import requests
from flask import Flask

# --- 환경 변수 가져오기 (Render 설정에서 자동으로 가져옴) ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# --- 크롤링 대상 URL 설정 ---
TARGET_URL = "https://ko.aliexpress.com/item/1005010120015183.html" # 이 URL은 당신의 실제 URL로 변경해야 할 수 있습니다.

# --- 재고 상태 지속성 (봇이 꺼지지 않는 한 알림 중복 방지) ---
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
        
        # --- 재고 확인 로직 (긍정적 지표로 수정) ---
        # 재고가 있을 때만 페이지 소스에 존재하는 제품의 고유한 이름으로 판단합니다.
        # 품절일 때는 이 부분이 없거나, 페이지 자체가 다르게 로드됩니다.
        # 당신이 보내준 HTML 소스에서 확인된 제품명 일부를 사용합니다.
        IN_STOCK_INDICATOR = "레노버 리전 Y700" 
        
        if IN_STOCK_INDICATOR in html_content:
            current_status = "IN_STOCK"
            print(f"✅ {current_status}: 긍정적 지표 ('{IN_STOCK_INDICATOR}')가 감지되었습니다.")
        else:
            # 긍정적 지표가 없으면 품절이나 페이지 오류로 간주
            current_status = "OUT_OF_STOCK"
            print(f"❌ {current_status}: 긍정적 지표를 찾지 못했습니다. 품절 상태입니다.")

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

# --- Render와 UptimeRobot 핑에 응답하는 웹 엔드포인트 ---
@app.route("/")
def main_endpoint():
    print("-" * 30)
    print("재고 확인 시작.")
    check_aliexpress_stock()
    return "AliExpress Stock Checker is alive.", 200
