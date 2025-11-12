import requests, time

URL = "https://ko.aliexpress.com/item/1005010120015183.html?invitationCode=ZXRlQUNVNkpPRUd3N2lRNlhCUGcvcGVhbGdxWXhWTkNhckJpcnN5UXQ3MmVQemFTZUJrNWVWT0s1MU1hdTAyWg&srcSns=sns_KakaoTalk&sourceType=1&spreadType=socialShare&social_params=6000370900927&bizType=ProductDetail&spreadCode=ZXRlQUNVNkpPRUd3N2lRNlhCUGcvcGVhbGdxWXhWTkNhckJpcnN5UXQ3MmVQemFTZUJrNWVWT0s1MU1hdTAyWg&aff_fcid=b74c0bc49c3a45f29dd48b8dce73799d-1762955153404-07205-_c4DXaxzR&tt=MG&aff_fsk=_c4DXaxzR&aff_platform=default&sk=_c4DXaxzR&aff_trace_key=b74c0bc49c3a45f29dd48b8dce73799d-1762955153404-07205-_c4DXaxzR&shareId=6000370900927&businessType=ProductDetail&platform=AE&terminal_id=0aaa77ecea0643c7b35d9dd7cefd9ac9&afSmartRedirect=y&gatewayAdapt=glo2kor"  # 상품 링크 넣기
CHECK_INTERVAL = 600  # 10분마다 확인
BOT_TOKEN = "8575667908:AAHxAxwEPBx30IWldmPc_EF9hEQLxp_H1o4"
CHAT_ID = "6646276816"

def check_stock():
    headers = {"User-Agent": "Mozilla/5.0"}
    html = requests.get(URL, headers=headers).text
    return "Out of Stock" not in html

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg}
    requests.post(url, data=payload)

while True:
    try:
        if check_stock():
            send_telegram(f"✅ 알리 상품 재입고!\n{URL}")
            print("재고 발견! 텔레그램 발송 완료 ✅")
        else:
            print("아직 품절 상태... 다시 확인 중")
    except Exception as e:
        print("오류:", e)
    time.sleep(CHECK_INTERVAL)
