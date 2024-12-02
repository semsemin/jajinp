import urllib.request
import json
from II.secrets_manager import get_api_key

# 네이버 API 클라이언트 정보 설정
client_id = get_api_key(api_name='CLIENT_ID')
client_secret = get_api_key(api_name='CLIENT_SECRET')

# 검색을 위한 제품 정보 목록
extracted_data = [
    {"product name": "올리타리아 엑스트라버진 올리브유 500ml", "price": "22900"},
    {"product name": "폰타나 포도씨유", "price": "12980"}
]

def search_product(product_name):
    query = urllib.parse.quote(product_name)
    url = f"https://openapi.naver.com/v1/search/shop.json?query={query}&display=3"  # display=3으로 결과 제한

    request = urllib.request.Request(url)
    request.add_header('X-Naver-Client-Id', client_id)
    request.add_header('X-Naver-Client-Secret', client_secret)

    response = urllib.request.urlopen(request)
    response_code = response.getcode()
    response_body = response.read().decode('utf-8')

    # 응답 코드가 200(성공)이 아닐 경우 오류 출력
    if response_code != 200:
        print(f"Error: Received response code {response_code}")
        print(response_body)
        return None

    return response_body

def parse_json_response(json_data):
    try:
        # JSON 데이터 로드
        data = json.loads(json_data)
        items = data.get("items", [])

        # 결과 정보를 리스트로 저장
        product_info = []
        for item in items:
            product_info.append({
                "title": item["title"],
                "link": item["link"],
                "price": item["lprice"],  # 낮은 가격 정보
                "hprice" : item["hprice"],
                "image" : item["image"],
                "mallName" : item["mallName"]

            })
        
        return json.dumps(product_info, indent=4, ensure_ascii=False)
    except json.JSONDecodeError:
        print("Error: Failed to parse JSON. The response may not be in JSON format.")
        print("Response content:", json_data)
        return None

# 제품 목록에서 검색 수행
for product in extracted_data:
    product_name = product["product name"]
    json_response = search_product(product_name)

    # 응답이 있는 경우 JSON 파싱
    if json_response:
        json_result = parse_json_response(json_response)
        if json_result:
            print(f"Search results for '{product_name}':")
            print(json_result)
            print("\n" + "="*50 + "\n")

