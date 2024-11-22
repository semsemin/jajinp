from langchain_core.documents import Document
from langchain_community.tools import TavilySearchResults
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from secrets_manager import get_api_key
from langchain_openai import ChatOpenAI
from langchain.schema.runnable import RunnablePassthrough
import os
import json

os.environ["OPENAI_API_KEY"] = get_api_key('GPT_API_KEY')
os.environ["TAVILY_API_KEY"] = get_api_key('TAVILY_API_KEY')

# 입력 데이터
product_data = [
    {'product_name': '동원 매운고추참치 90g', 'price': 3300},
    {'product_name': '동원 야채참치 90g', 'price': 3300}
]

# 결과 저장
all_responses = {}

# GPT 설정
llm = ChatOpenAI(
    model='gpt-4o',
    temperature=0,
    max_tokens=500,
)

# Prompt 정의
template = '''    
    You are a shopping assistant AI. Answer the question based on the context below.
    Respond in JSON format with keys 'review_count' and 'rating'.
    
    Context: {context}
    
    Question: {question}
    
    Response (JSON format):
'''
prompt = ChatPromptTemplate.from_template(template)

# JSON Output Parser
json_parser = JsonOutputParser()

# Chain 생성
chain = (
    {'context': RunnablePassthrough(), 'question': RunnablePassthrough()}
    | prompt
    | llm
    | json_parser
)

# Tavily 검색 설정
web_search = TavilySearchResults(max_results=10)

# 루프를 통해 각 제품 처리
for product in product_data:
    query = f"{product['product_name']}에 대한 리뷰, 별점을 https://www.coupang.com 에서 검색해서 알려줘"
    # print(f"질문: {query}")

    # Tavily 검색 수행
    search_results = web_search.invoke(query)

    # 검색 결과를 바로 context로 전달
    context = "\n\n".join([f"URL: {result['url']}\n내용: {result['content']}" for result in search_results])

    # Chain 실행
    response = chain.invoke({'context': context, 'question': query})
    
    # 결과를 딕셔너리에 저장
    all_responses[product['product_name']] = {
        'product_name': product['product_name'],
        'review_count': response.get('review_count', 'N/A'),
        'rating': response.get('rating', 'N/A')
    }

# 최종 결과 출력
print("최종 결과:")
print(json.dumps(all_responses, ensure_ascii=False, indent=2))
  
