import streamlit as st
import base64
from openai import OpenAI
from secrets_manager import get_secret_key

# gpt api key 불러오기
gpt_key = get_secret_key()

# gpt 응답받는 함수
def get_gpt_response():
    client = OpenAI(api_key=gpt_key)
    response = client.chat.completions.create(
    model ="gpt-4o",
        messages =[
            {"role" : "system" , "content" :" "},
            {"role": "user", "content": "  "}
        ]
    )
    print(response.choices[0].message.content)

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
    

