import os
import requests
from flask import Flask

# --- 환경 변수 가져오기 (비밀번호처럼 안전하게 숨겨둔 토큰과 ID를 가져옵니다) ---
# 이 정보들은 Render에 설정해 두었기 때문에 여기서 직접 쓰지 않아도 됩니다.
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# 알림을 받고 싶은 제품 URL (알리익스프레스 주소)
TARGET_URL = "https://www.aliexpress.us/item/3256809933700431.html"

# 이전 상태 저장 (봇이 완전히 꺼졌다 켜지지 않는 한, 알림이 계속 오는 것을 막아줍니다)
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

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(TARGET_URL, headers=headers, timeout=15)
        response.raise_for_status() 
        html_content = response.text
        
        # --- 재고 확인 로직 (가장 중요) ---
        # 알리익스프레스에서 품절일 때 나오는 문구를 찾습니다.
        OUT_OF_STOCK_INDICATOR = "no longer available" 
        
        if OUT_OF_STOCK_INDICATOR in html_content:
            current_status = "OUT_OF_STOCK"
            print(f"❌ {current_status}: 아직 품절 상태입니다.")
        else:
            current_status = "IN_STOCK"
            print(f"✅ {current_status}: 재고가 들어왔다고 감지되었습니다!")

        # --- 알림을 보낼지 결정 ---
        # 현재 재고가 들어왔고 (IN_STOCK), 이전 상태가 품절(OUT_OF_STOCK)일 때만 알림을 보냅니다.
        if current_status == "IN_STOCK" and LAST_STOCK_STATUS == "OUT_OF_STOCK":
            message = (
                "🎉🎉 재고 알림! 🎉🎉\n"
                "원하던 알리익스프레스 제품의 재고가 들어왔습니다.\n"
                f"바로 확인하세요: {TARGET_URL}"
            )
            send_telegram_message(message)
            # 알림을 보낸 후 상태를 '재고 있음'으로 바꿔서 알림이 5분마다 계속 오는 것을 막습니다.
            LAST_STOCK_STATUS = "IN_STOCK"
        elif current_status == "OUT_OF_STOCK" and LAST_STOCK_STATUS == "IN_STOCK":
            # 다시 품절되면 상태를 원래대로 돌려놓습니다.
            LAST_STOCK_STATUS = "OUT_OF_STOCK"

    except requests.exceptions.RequestException as e:
        print(f"웹사이트 접속 오류 발생: {e}")

# --- Render와 UptimeRobot이 우리 봇에게 '똑똑' 하고 문을 두드리는 곳 ---
@app.route("/")
def main_endpoint():
    print("-" * 30)
    print("5분마다 핑 요청을 받았습니다. 재고 확인 시작.")
    check_aliexpress_stock()
    
    # "나는 잘 작동하고 있어요!" 하고 대답해 줍니다. (이게 있어야 '로딩' 문제가 사라집니다)
    return "AliExpress Stock Checker is alive.", 200

# 봇을 실행하는 부분은 Render가 알아서 처리하므로 그대로 둡니다.
