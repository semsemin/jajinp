import streamlit as st
from openai import OpenAI
from secrets_manager import get_secret_key

# gpt api key 가져오기
gpt_key = get_secret_key()

# gpt 응답가져오기
def get_gpt_response():
    client = OpenAI(api_key=gpt_key)
    response = client.chat.completions.create(
    model ="gpt-4o",


        messages=[
            {"role": "system", "content": "You are an assistant specialized in extracting product names and prices from price tags. Please locate each product label (up to 8 labels) within the image. For each label, extract the text *exactly as it appears on the label*, including any unique spellings, symbols, parentheses, or formatting. Extract the product name precisely as written, as though performing OCR, and capture any numbers as the price. Return the extracted information in JSON format without any line breaks or extra spaces. The format should be as follows: [{'product name': 'exact text from label for product name', 'price': 'price'}]. For multiple products, return a list of objects, omitting '원' or '₩' symbols from the price so that only the numeric value remains."},
            {"role": "user", "content": [
                {"type": "text", "text": "Based on this data, please write the name and price in JSON format as [{'product name': 'exact text from label for product name', 'price': 'price'}]. For multiple products, return a list of objects without '원' or '₩' in price, just the number. Please read and transcribe each label's text exactly as it appears, capturing the unique spelling and formatting in the product name."},
                {"type": "image_url", "image_url": {
                    "url": f"data:image/png;base64,st.image(img)"}
                }
            ]}
        ],
    )
    print(response.choices[0].message.content)


