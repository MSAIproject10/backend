import os
import requests
from dotenv import load_dotenv

load_dotenv()
KAKAO_REST_API_KEY = os.getenv("KAKAO_API_KEY")

def geocode_address(address: str):
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {
        "Authorization": f"KakaoAK {KAKAO_REST_API_KEY}"
    }
    params = {"query": address}
    try:
        response = requests.get(url, headers=headers, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        if data.get("documents"):
            doc = data["documents"][0]
            return address, float(doc["y"]), float(doc["x"])  # lat, lon

    except Exception as e:
        print("❌ 에러 발생:", e)
        if 'response' in locals():
            print("❌ 응답 내용:", response.text)

    return address, None, None

