import os
import json
import streamlit as st  # Streamlit 모듈을 가져옵니다.
from langchain_core.documents import Document
from langchain_community.tools import TavilySearchResults
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.runnable import RunnablePassthrough
from secrets_manager import get_api_key

def get_book_summaries_and_recommendations(input_data):
    """
    책 제목 리스트를 받아 각 책의 줄거리 요약과 추천 독자 정보를 검색하여 반환합니다.

    Args:
        input_data (list): 책 제목을 포함한 딕셔너리 리스트. 예: [{"title": "해리포터와 마법사의 돌"}, {"title": "반지의 제왕"}]

    Returns:
        list: 각 책의 제목, 줄거리 요약, 추천 독자를 포함한 JSON 리스트.
    """
    # API 키 설정
    os.environ["OPENAI_API_KEY"] = get_api_key('GPT_API_KEY')
    os.environ["TAVILY_API_KEY"] = get_api_key('TAVILY_API_KEY')

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

    # Prompt 수정
    template = '''    
        ("system", "당신은 책의 줄거리를 요약하고 추천 독자 정보를 제공하는 AI입니다. 아래의 컨텍스트를 바탕으로 질문에 답변하세요. "
        "응답은 JSON 형식으로 작성하며, 키는 'title', 'book_summary', 'recommended_for'입니다. "
        "'title'은 책 제목, 'book_summary'는 책의 줄거리 한줄 요약, 'recommended_for'는 추천 독자(예: 로맨스를 좋아하는 사람 등)입니다."
        ""),
        ("human", "컨텍스트: {context}\n\n질문: {question}")
    '''
    prompt = ChatPromptTemplate.from_template(template)

    def format_docs(docs):
        return '\n\n'.join([d.page_content for d in docs])

    # 캐시 초기화
    if "book_summaries" not in st.session_state:
        st.session_state["book_summaries"] = {}

    # 결과 저장
    all_responses = []

    # 입력된 각 책에 대해 검색 수행
    for book_title in input_data:
        title = book_title["title"]

        # 캐시 확인
        if title in st.session_state["book_summaries"]:
            all_responses.append(st.session_state["book_summaries"][title])
            continue

        query = f"{title} 책의 줄거리를 검색해서 알려줘."

        # Tavily 검색 수행
        web_search = TavilySearchResults(max_results=7)
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
            collection_name='book_recommendation',
            persist_directory="./chroma_db"
        )

        # 문서 검색
        retriever = vectorstore.as_retriever(
            search_type='mmr',
            search_kwargs={
                'k': 3,
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

        # 불필요한 ```json 포맷 제거
        if isinstance(response, str):
            response = response.replace("```json", "").replace("```", "").strip()

        # JSON 문자열을 딕셔너리로 변환
        try:
            response = json.loads(response)
        except json.JSONDecodeError:
            response = {
                "title": title,
                "book_summary": "요약 정보 없음",
                "recommended_for": "추천 정보 없음"
            }

        # 캐시에 저장
        st.session_state["book_summaries"][title] = response
        all_responses.append(response)

    return all_responses