from langchain_core.documents import Document
from langchain_community.tools import TavilySearchResults
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.runnable import RunnablePassthrough
from langchain_openai import ChatOpenAI
from secrets_manager import get_api_key
import os
import json


def recommend_best_menus(input_data):
    # API 키 설정
    os.environ["OPENAI_API_KEY"] = get_api_key('GPT_API_KEY')
    os.environ["TAVILY_API_KEY"] = get_api_key('TAVILY_API_KEY')

    # 사용자 입력 데이터
    store_name = input_data['store name']
    branch_name = input_data['branch']

    # Tavily 검색 수행
    query = f"{store_name} {branch_name}의 베스트 메뉴를 검색해서 알려줘."
    print(f"질문: {query}")
    web_search = TavilySearchResults(max_results=10)
    search_results = web_search.invoke(query)

    # 텍스트 Splitter 설정
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=1000,
        chunk_overlap=200,
        encoding_name='cl100k_base'
    )

    # 검색 결과를 문서로 변환
    documents = []
    for result in search_results:
        content = result['content']
        url = result['url']
        chunks = text_splitter.split_text(content)
        for chunk in chunks:
            document = Document(
                page_content=chunk,
                metadata={"url": url}
            )
            documents.append(document)

    # 문서 임베딩 및 벡터스토어 생성
    embedding_model = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embedding_model,
        collection_name='restaurant_best_menu',
        collection_metadata={'hnsw:space': 'cosine'},
        persist_directory="./chroma_db"
    )

    # 문서 검색
    retriever = vectorstore.as_retriever(
        search_type='mmr',
        search_kwargs={
            'k': 6,  # 상위 6개
            'fetch_k': 10,  # 총 10개 중
            'lambda_mult': 0.8  # 관련성 0.8, 다양성 0.2
        }
    )

    # GPT 설정
    llm = ChatOpenAI(
        model='gpt-4o',
        temperature=0,
        max_tokens=500,
    )

    # Prompt 정의
    template = '''    
        ("system", "당신은 매장의 베스트메뉴를 고객에게 추천하는 AI입니다. 아래의 컨텍스트를 바탕으로 질문에 답변하세요. "
        "응답은 JSON 형식으로 작성하며, 키는 'best_menus'이며, 값은 메뉴 이름과 설명의 리스트입니다."
        ""),
        ("human", "컨텍스트: {context}\n\n질문: {question}")
    '''
    prompt = ChatPromptTemplate.from_template(template)

    def format_docs(docs):
        return '\n\n'.join([d.page_content for d in docs])

    # Chain 생성
    chain = (
        {'context': retriever | format_docs, 'question': RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    # Chain 실행
    response = chain.invoke(query)

    # 응답 처리
    if response.startswith("```json"):
        response = response[7:]  # ```json 제거
    if response.endswith("```"):
        response = response[:-3]  # ``` 제거
    response = response.replace("'", '"')  # 작은따옴표를 큰따옴표로 변환

    # JSON으로 변환
    try:
        result = json.loads(response)
    except json.JSONDecodeError as e:
        print("JSON 디코딩 에러:", e)
        result = {"error": "JSON parsing failed"}

    print("\n[추천 베스트 메뉴]")
    print(json.dumps(result, indent=4, ensure_ascii=False))

    return result

