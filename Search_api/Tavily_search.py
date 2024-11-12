import os
from langchain_openai import ChatOpenAI
from langchain_community.retrievers import TavilySearchAPIRetriever
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from Streamlit.secrets_manager import get_api_key

# OpenAI API Key
os.environ["OPENAI_API_KEY"] = get_api_key('GPT_API_KEY')

# Tavily API key
os.environ["TAVILY_API_KEY"] = get_api_key('TAVILY_API_KEY')

# GPT 검색을 통해 상품 리뷰가 높은 순으로 정렬
extracted_data = [
   {"product name": "올리타리아)엑스트라버진올리브유500ml", "price": "22900"},
   {"product name": "폰타나포도씨유", "price": "12980"}
]

def format_docs(docs):
    return "\n\n".join([
        f"{d.page_content}\nSource URL: {d.metadata.get('url', 'URL not available')}"
        for d in docs
    ])

# LCEL 기반으로 검색 수행
template = """Answer the question based only on the following context:

{context}

Question: {question}
"""
prompt = ChatPromptTemplate.from_template(template)
llm = ChatOpenAI(model="gpt-4o", temperature=0)
retriever = TavilySearchAPIRetriever(k=3)

# LCEL 체인 설정
chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
)

# 상품에 대한 리뷰가 높은 순 정렬 결과 출력 함수
def get_top_reviewed_products(extracted_data):
    sorted_products = []
    for item in extracted_data:
        question = f"Please find reviews and ratings for '{item['product name']}' and sort by highest review score."
        result = chain.invoke(question)
        sorted_products.append({
            "product name": item["product name"],
            "reviews": result.content,
        })
    sorted_products.sort(key=lambda x: x['reviews'], reverse=True)  # 리뷰 높은 순 정렬
    return sorted_products

# 결과 확인
top_reviewed_products = get_top_reviewed_products(extracted_data)
for product in top_reviewed_products:
    print(f"Product: {product['product name']}")
    print(f"Reviews and Source URLs:\n{product['reviews']}\n")

# import os
# from langchain_openai import ChatOpenAI
# from langchain_community.retrievers import TavilySearchAPIRetriever
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.runnables import RunnablePassthrough
# from Streamlit.secrets_manager import get_api_key

# # OpenAI API Key
# os.environ["OPENAI_API_KEY"] =  get_api_key('GPT_API_KEY')

# # Tavily API key
# os.environ["TAVILY_API_KEY"] = get_api_key('TAVILY_API_KEY')


# def format_docs(docs):
#     return "\n\n".join([d.page_content for d in docs])


# template = """Answer the question based only on the following context:

# {context}

# Question: {question}
# """
# prompt = ChatPromptTemplate.from_template(template)
# llm = ChatOpenAI(model="gpt-4o", temperature=0)
# retriever = TavilySearchAPIRetriever(k=3)

# chain = (
#     {"context": retriever | format_docs, "question": RunnablePassthrough()}
#     | prompt
#     | llm
# )

# result = chain.invoke("2024년 한국 뮤지컬 시카고의 주연 배우들은 누구인가요?")

# print(result.content)