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
        messages =[
            {"role" : "system" , "content" :" "},
            {"role": "user", "content": "  "}
        ]
    )
    print(response.choices[0].message.content)


