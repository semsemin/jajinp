import streamlit as st
import base64
from openai import OpenAI
from secrets_manager import get_api_key
import json

# gpt api key 불러오기
gpt_key = get_api_key(api_name='GPT_API_KEY')

# 상품 정보 추출 함수
def get_gpt_response(image_path):
    base64_image = encode_image(image_path)

    # OpenAI API 요청
    client = OpenAI(api_key=gpt_key)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an assistant specialized in extracting product names and prices from price tags. Please locate each product label (up to 8 labels) within the image. For each label, extract the text *exactly as it appears on the label*, including any unique spellings, symbols, parentheses, or formatting. Extract the product name precisely as written, as though performing OCR, and capture any numbers as the price. Return the extracted information in JSON format without any line breaks or extra spaces. The format should be as follows: [{'product name': 'exact text from label for product name', 'price': 'price'}]. For multiple products, return a list of objects, omitting '원' or '₩' symbols from the price so that only the numeric value remains."},
            {"role": "user", "content": [
                {"type": "text", "text": "Based on this data, please write the name and price in JSON format as [{'product name': 'exact text from label for product name', 'price': 'price'}]. For multiple products, return a list of objects without '원' or '₩' in price, just the number. Please read and transcribe each label's text exactly as it appears, capturing the unique spelling and formatting in the product name."},
                {"type": "image_url", "image_url": {
                    "url": f"data:image/png;base64,{base64_image}"
                }}
            ]}
        ],
    )

    response_content = response.choices[0].message.content

    # 응답 내용 문자열을 JSON 형식으로 정제
    formatted_response = response_content.replace("'", '"')
    formatted_response = formatted_response.replace('\n', '').strip()
    cleaned_string = formatted_response.replace('json', '').strip()
    cleaned_string = cleaned_string.replace('```', '')

    try:
        predicted_json = json.loads(cleaned_string)
    except json.JSONDecodeError:
        print("JSONDecodeError: 응답 내용을 JSON 형식으로 변환할 수 없습니다.")
        predicted_json = {}  # 변환 실패 시 빈 딕셔너리 반환
    
    print(predicted_json)
    return predicted_json

# 매장 정보 추출 함수
def get_product_data(image_path):
    base64_image = encode_image(image_path)

    # OpenAI API 요청
    client = OpenAI(api_key=gpt_key)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an assistant specialized in extracting store names and branch from images of store exteriors. Please examine the image carefully to identify the store name and the branch location, even if the branch information is displayed outside the signboard, such as on the building or other signage."},
            {"role": "user", "content": [
                {"type": "text", "text": "Please return the information in JSON format as {'store name': 'store name', 'branch': 'branch'}. Ensure the branch location is included if it's visible anywhere on the store exterior."},
                {"type": "image_url", "image_url": {
                    "url": f"data:image/png;base64,{base64_image}"
                }}
            ]}
        ],     
        temperature=0.0,
    )

    response_content = response.choices[0].message.content

    # 응답 내용 문자열을 JSON 형식으로 정제
    formatted_response = response_content.replace("'", '"')
    formatted_response = formatted_response.replace('\n', '').strip()
    cleaned_string = formatted_response.replace('json', '').strip()
    cleaned_string = cleaned_string.replace('```', '')

    try:
        predicted_json = json.loads(cleaned_string)
    except json.JSONDecodeError:
        print("JSONDecodeError: 응답 내용을 JSON 형식으로 변환할 수 없습니다.")
        predicted_json = {}  # 변환 실패 시 빈 딕셔너리 반환
    
    print(predicted_json)
    return predicted_json

# gpt로 이미지 글자 인식 함수
def gpt_img(image_path):
    with open(image_path, "rb") as image_file:
        base64_image= base64.b64encode(image_file.read()).decode("utf-8")

    client = OpenAI(api_key=gpt_key)
    response = client.chat.completions.create(
    model ="gpt-4o",
        messages =[
            {"role" : "system" , "content" :" You are an assistant specialized in extracting product names and prices from price tags. Please read the price tag and extract the product names and their corresponding prices."},
            {"role": "user", "content": [
            {"type": "text", "text": "Based on this data, please write the name and price in JSON format as [{{'product name': 'product name', 'price': 'price'}}]. For multiple products, return a list of objects without '원' or '₩' in price, just the number."},
            {"type": "image_url", "image_url": {
                "url": f"data:image/png;base64,{base64_image}"}
            }  
        ]}
        ]
    )
    print(response.choices[0].message.content)  
    
# 이미지 파일을 base64로 인코딩하는 함수
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")
    return base64_image

