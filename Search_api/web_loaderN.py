from typing import Any, Dict, List, Optional
from langchain_community.llms import OpenAI
from langchain.agents import initialize_agent, AgentType
import aiohttp
import requests
from pydantic.main import BaseModel
from typing_extensions import Literal
from langchain.tools import BaseTool

from Streamlit.secrets_manager import get_api_key

from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun
)

# Naver API를 통해 최저가와 별점 정보를 가져오는 클래스
class NaverSearchAPIWrapper(BaseModel):
    display: int = 5
    start: int = 1
    sort: str = "date"
    type: Literal["shop", "webkr"] = "webkr"  # 기본값을 webkr로 설정

    X_Naver_Client_Id: str = get_api_key("CLIENT_ID")
    X_Naver_Client_Secret: str = get_api_key("CLIENT_SECRET")

    aiosession: Optional[aiohttp.ClientSession] = None

    class Config:
        arbitrary_types_allowed = True

    # shop API로 최저가 정보를 가져오는 메서드
    def get_shop_results(self, query: str) -> Dict:
        self.type = "shop"
        return self._naver_search_api_results(query=query)

    # webkr API로 별점 정보 등의 상세 정보를 가져오는 메서드
    def get_webkr_results(self, query: str) -> Dict:
        self.type = "webkr"
        return self._naver_search_api_results(query=query)

    def _naver_search_api_results(self, query: str) -> Dict:
        headers = {
            "X-Naver-Client-Id": self.X_Naver_Client_Id,
            "X-Naver-Client-Secret": self.X_Naver_Client_Secret
        }
        params = {
            "query": query,
            "display": self.display,
            "start": self.start,
            "sort": self.sort
        }
        response = requests.get(
            f"https://openapi.naver.com/v1/search/{self.type}.json", headers=headers, params=params
        )
        response.raise_for_status()
        return response.json()

# 상품 정보를 비교하여 최저가와 별점을 가져오는 함수
def get_best_product_info(product_data):
    search = NaverSearchAPIWrapper(type="shop")

    comparison_results = []
    for product in product_data:
        # Step 1: shop API로 최저가 검색
        shop_results = search.get_shop_results(product["product name"])
        if not shop_results["items"]:
            continue  # 상품 검색 결과가 없는 경우 넘어가기

        # 최저가 정보 가져오기
        lowest_price_item = min(shop_results["items"], key=lambda x: int(x["lprice"]))
        lowest_price_link = lowest_price_item["link"]

        # Step 2: webkr API로 해당 링크에 대한 별점 정보 가져오기
        webkr_results = search.get_webkr_results(lowest_price_link)

        # 별점 정보를 파싱 (예시로 description 필드에서 별점이 있는지 확인)
        rating_info = "No rating found"
        for result in webkr_results["items"]:
            if "별점" in result["description"]:
                rating_info = result["description"]
                break

        comparison_results.append({
            "name": product["product name"],
            "lowest_price": lowest_price_item["lprice"],
            "mall_name": lowest_price_item["mallName"],
            "rating_info": rating_info
        })

    # 가격 및 별점 비교하여 최적의 상품을 결정
    sorted_results = sorted(comparison_results, key=lambda x: int(x["lowest_price"]))
    return sorted_results

# 입력 상품 데이터
product_data = [
    {"product name": "올리타리아 엑스트라버진 올리브유 500ml", "price": "22900"},
    {"product name": "폰타나 포도씨유", "price": "12980"}
]

# 최종 결과 출력
sorted_products = get_best_product_info(product_data)
for product in sorted_products:
    print(f"상품명: {product['name']}\n, 최저가: {product['lowest_price']}원\n, 판매처: {product['mall_name']}\n, 별점 정보: {product['rating_info']}\n")
