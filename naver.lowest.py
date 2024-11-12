import requests
import json
import re

# secret.json 파일에서 CLIENT_ID와 CLIENT_SECRET 읽기
with open("Streamlit/secrets.json") as f:
    secrets = json.load(f)
    CLIENT_ID = secrets["CLIENT_ID"]
    CLIENT_SECRET = secrets["CLIENT_SECRET"]

def remove_html_tags(text):
    # 정규 표현식을 사용하여 HTML 태그 제거
    clean_text = re.sub(r'<.*?>', '', text)
    return clean_text

def get_lowest_price(product_json):
    product_name = product_json["product name"]  # JSON에서 product name 추출

    # 네이버 쇼핑 API URL
    url = 'https://openapi.naver.com/v1/search/shop.json'
    
    # 요청 파라미터 설정
    params = {
        'query': product_name,  # 상품명
        'display': 1,           # 검색 결과 1개만 요청 (최저가만 필요하므로)
        'sort': 'asc'           # 가격 오름차순 정렬
    }
    
    # 헤더 설정
    headers = {
        'X-Naver-Client-Id': CLIENT_ID,
        'X-Naver-Client-Secret': CLIENT_SECRET
    }
    
    # API 호출
    response = requests.get(url, headers=headers, params=params)
    
    # 응답 상태 확인
    if response.status_code == 200:
        data = response.json()
        # 최저가 상품의 정보 추출
        if data['items']:
            lowest_price_item = data['items'][0]
            lowest_price = lowest_price_item['lprice']
            product_name = remove_html_tags(lowest_price_item['title'])  # HTML 태그 제거
            return f"상품명: {product_name}\n최저가: {lowest_price}원\n"
        else:
            return "검색된 상품이 없습니다.\n"
    else:
        return f"API 호출 실패, 상태 코드: {response.status_code}\n"

def get_lowest_prices_for_multiple_products(product_list):
    results = []
    for product_json in product_list:
        result = get_lowest_price(product_json)
        results.append(f"상품 '{product_json['product name']}'의 최저가 검색 결과:\n{result}")
    return "\n".join(results)

# 예시: 여러 상품의 최저가 검색
product_list = [
    {"product name": "아이디얼포맨 퍼펙트올인원 상시기획", "price": "20900"},
    {"product name": "아이디얼포맨 시카올인원 상시기획", "price": "19900"},
]
print(get_lowest_prices_for_multiple_products(product_list))
