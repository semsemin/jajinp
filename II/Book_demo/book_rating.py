__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

from langchain_core.documents import Document
from langchain_community.tools import TavilySearchResults
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.runnable import RunnablePassthrough
import json
import streamlit as st

def get_book_ratings_and_reviews(input_data):
    """
    책 제목 리스트를 받아 책의 별점과 리뷰 수를 검색하여 반환합니다.

    Args:
        input_data (list): 책 제목을 포함한 딕셔너리 리스트. 예: [{"title": "책 제목"}]

    Returns:
        list: 각 책의 별점과 리뷰 수를 포함한 JSON 리스트.
    """
    # API 키 설정
    os.environ["OPENAI_API_KEY"] = st.secrets["GPT_API_KEY"]
    os.environ["TAVILY_API_KEY"] = st.secrets["TAVILY_API_KEY"]

    # 텍스트 Splitter 설정
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=1000,
        chunk_overlap=200,
        encoding_name='cl100k_base'
    )

    # GPT 모델 설정
    llm = ChatOpenAI(
        model='gpt-4o',
        temperature=0,
        max_tokens=500,
    )

    # Prompt 정의

    template = '''
        ("system", "당신은 책의 리뷰와 별점 정보를 제공하는 AI입니다. 아래의 컨텍스트를 바탕으로 질문에 답변하세요. "
        "응답은 항상 JSON 형식으로 작성하며, 키는 'title', 'rating', 'review_count', 'best_seller'입니다. "
        "'title'은 책 제목,'rating'은 별점, 'review_count'는 리뷰 수, 'best_seller'는 베스트셀러 순위입니다."
        ),
        ("human", "컨텍스트: {context}\n\n질문: {question}")
    '''

    prompt = ChatPromptTemplate.from_template(template)

    def format_docs(docs):
        return '\n\n'.join([d.page_content for d in docs])
    
     # 최대 별점 추정 함수
    def estimate_max_rating(rating):
        if rating > 5:  # 별점이 5를 초과하면 10점 만점으로 간주
            return 10
        else:  # 그렇지 않으면 5점 만점으로 간주
            return 5

    # 숫자인지 확인하는 함수
    def is_valid_number(value):
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False

    # 결과 저장
    all_responses = {}

    # 입력 데이터 처리
    for book_title in input_data:
        query = f"{book_title['title']} 책의 별점과 리뷰 수, 그리고 교보문고 기준 베스트셀러 순위를 검색해서 알려줘."

        # Tavily 검색 수행
        web_search = TavilySearchResults(max_results=10)
        search_results = web_search.invoke(query)

        # 검색 결과에서 텍스트 추출 및 Document 생성
        documents = []
        for result in search_results:
            content = result.get('content', '')
            url = result.get('url', '')

            # 텍스트를 청크로 분리
            chunks = text_splitter.split_text(content)

            # 각 청크를 Document로 변환
            for chunk in chunks:
                document = Document(
                    page_content=chunk,
                    metadata={"url": url}
                )
                documents.append(document)

        # 문서 임베딩
        embedding_model = OpenAIEmbeddings()

        vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=embedding_model,
            collection_name='book_reviews',
            persist_directory="./chroma_db"
        )

        # 문서 검색
        retriever = vectorstore.as_retriever(
            search_type='mmr',
            search_kwargs={
                'k': 6,
                'fetch_k': 10,
                'lambda_mult': 0.8
            }
        )

        # Chain 생성
        chain = (
            {'context': retriever | format_docs, 'question': RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

        # Chain 실행
        response = chain.invoke(query)

        # 디버깅: response 출력
        print("Raw response:", response)

        # JSON 문자열을 딕셔너리로 변환
        if isinstance(response, str):
            try:
                response = json.loads(response.replace("```json", "").replace("```", "").strip())
            except json.JSONDecodeError:
            # 기본값 설정
                response = {
                    "title": book_title['title'],
                    "rating": "N/A",
                    "review_count": "N/A",
                    "best_seller": "N/A"
                }
        # 디버깅: JSON 변환 후 response 확인
        print("Parsed response:", response)     

        # Extract rating and normalize
        raw_rating = response.get('rating')
        normalized_rating = 'N/A'

        # 디버깅: raw_rating 값 확인
        print("Raw rating:", raw_rating)

        if is_valid_number(raw_rating):  # Check if raw_rating is a valid number
            raw_rating = float(raw_rating)
            max_rating = estimate_max_rating(raw_rating)
            normalized_rating = (raw_rating / max_rating) * 5

        # 디버깅: normalized_rating 값 확인
        print("Normalized rating:", normalized_rating)


        # Save results
        all_responses[book_title['title']] = {
            'title': book_title['title'],
            'review_count': response.get('review_count', 'N/A'),
            'rating': normalized_rating,
            'best_seller' : response.get('best_seller', 'N/A')
        }
        # 디버깅: 최종 저장 데이터 확인
        print("All responses:", all_responses)

    return all_responses