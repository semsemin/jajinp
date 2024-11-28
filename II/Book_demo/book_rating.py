from langchain_core.documents import Document
from langchain_community.tools import TavilySearchResults
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from secrets_manager import get_api_key
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.runnable import RunnablePassthrough

def get_book_ratings_and_reviews(input_data):
    """
    책 제목 리스트를 받아 책의 별점과 리뷰 수를 검색하여 반환합니다.

    Args:
        input_data (list): 책 제목을 포함한 딕셔너리 리스트. 예: [{"title": "책 제목"}]

    Returns:
        list: 각 책의 별점과 리뷰 수를 포함한 JSON 리스트.
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

    # Prompt 정의
    template = '''    
        ("system", "당신은 책의 리뷰와 별점 정보를 제공하는 AI입니다. 아래의 컨텍스트를 바탕으로 질문에 답변하세요. "
        "응답은 JSON 형식으로 작성하며, 키는 'title', 'rating', 'review_count'입니다. "
        "'title'은 책 제목, 'rating'은 별점, 'review_count'는 리뷰 수입니다."
        ""),
        ("human", "컨텍스트: {context}\n\n질문: {question}")
    '''
    prompt = ChatPromptTemplate.from_template(template)

    def format_docs(docs):
        return '\n\n'.join([d.page_content for d in docs])

    # 결과 저장
    all_responses = []

    # 입력 데이터 처리
    for book_title in input_data:
        query = f"{book_title['title']} 책의 별점과 리뷰 수를 검색해서 알려줘."

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
        all_responses.append(response)

    return all_responses
