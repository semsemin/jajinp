from openai import OpenAI
from Streamlit.secrets_manager import get_api_key
import json

# gpt api key 불러오기
gpt_key = get_api_key(api_name='GPT_API_KEY')

# 제품 데이터를 JSON 형식의 문자열로 변환
product_data = [
    {"product name": "올리타리아)엑스트라버진올리브유500ml", "price": "22900"},
    {"product name": "폰타나포도씨유", "price": "12980"}
]
product_data_str = json.dumps(product_data)

# gpt 응답받는 함수
client = OpenAI(api_key=gpt_key)
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "Answer Based on this data, list the products in the order of good reviews. If you can't find the review, do a web search. The products are: "},
        {"role": "user", "content": product_data_str}
    ]
)
print(response.choices[0].message.content)

