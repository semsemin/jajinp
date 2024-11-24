import urllib.request
import json
import streamlit as st  # Streamlit 모듈을 가져옵니다.
from Streamlit.secrets_manager import get_api_key
from openai import OpenAI

client_id = get_api_key('CLIENT_ID')
client_secret = get_api_key('CLIENT_SECRET')
gpt_key = get_api_key('GPT_API_KEY')

def search_blog_reviews(product_name):
    query = urllib.parse.quote(f"{product_name}")
    url = f"https://openapi.naver.com/v1/search/blog.json?query={query}&display=5"

    request = urllib.request.Request(url)
    request.add_header('X-Naver-Client-Id', client_id)
    request.add_header('X-Naver-Client-Secret', client_secret)

    try:
        response = urllib.request.urlopen(request)
        response_code = response.getcode()
        if response_code != 200:
            print(f"Error: Received response code {response_code}")
            return None
        return response.read().decode('utf-8')
    except Exception as e:
        print(f"Error: {e}")
        return None


def parse_blog_response(json_data):
    try:
        data = json.loads(json_data)
        items = data.get("items", [])
        filtered_items = [
            item for item in items
            if "쿠팡" not in item["title"] and "파트너스" not in item["description"]
        ]
        return [
            {"title": item["title"], "description": item["description"], "link": item["link"]}
            for item in filtered_items
        ]
    except json.JSONDecodeError:
        print("Error: Failed to parse JSON.")
        return None


def summarize_blog_reviews(product_name, blog_reviews):
    try:
        client = OpenAI(api_key=gpt_key)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "당신은 제품 리뷰를 요약하는 전문가 AI입니다."},
                {"role": "user", "content": f"아래 리뷰를 바탕으로 '{product_name}'에 대한 짧고 간결한 한줄평을 작성해 주세요. 한국어로 작성하며, 리뷰의 핵심을 간단히 전달해 주세요.\n\n리뷰:\n{blog_reviews}"}
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error: {e}")
        return None


def fetch_and_display_review_summary(product_name):
    if "review_summaries" not in st.session_state:
        st.session_state["review_summaries"] = {}

    # Check if the summary for this product is already cached
    if product_name in st.session_state["review_summaries"]:
        return st.session_state["review_summaries"][product_name]

    # Fetch blog reviews
    blog_response = search_blog_reviews(product_name)
    if not blog_response:
        summary = "리뷰 데이터를 가져오는 데 실패했습니다."
        st.session_state["review_summaries"][product_name] = summary
        return summary

    # Parse blog response
    blog_result = parse_blog_response(blog_response)
    if not blog_result:
        summary = "리뷰 데이터를 분석할 수 없습니다."
        st.session_state["review_summaries"][product_name] = summary
        return summary

    # Summarize blog reviews
    summary = summarize_blog_reviews(product_name, blog_result)
    summary = summary or "한줄평 생성에 실패했습니다."

    # Cache the summary
    st.session_state["review_summaries"][product_name] = summary
    return summary
