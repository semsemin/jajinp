from langchain_core.documents import Document
from langchain_community.tools import TavilySearchResults
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
import sys, os
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from secrets_manager import get_api_key
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.runnable import RunnablePassthrough

os.environ["OPENAI_API_KEY"] = get_api_key('GPT_API_KEY')
os.environ["TAVILY_API_KEY"] = get_api_key('TAVILY_API_KEY')

# 사용자 입력 데이터
input_data = {
    'store_name': "베나레스",
    'branch_name': "숙대점"
}

# 상호명과 지점명 추출
store_name = input_data['store_name']
branch_name = input_data['branch_name']

# 텍스트 Splitter 설정
text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=1000,
    chunk_overlap=200,
    encoding_name='cl100k_base'
)

query = f"{store_name} {branch_name}의 베스트 메뉴를 검색해서 알려줘."
print(f"질문: {query}")

# Tavily 검색 수행
web_search = TavilySearchResults(max_results=10)
search_results = web_search.invoke(query)

# 검색 결과에서 텍스트 추출
texts = [result['content'] for result in search_results]

# 검색 결과를 텍스트 청크로 분리하여 Document 생성
documents = []
for result in search_results:
    content = result['content']
    url = result['url']

    # 텍스트를 청크로 분리
    chunks = text_splitter.split_text(content)

    # 각 청크를 Document로 변환
    for chunk in chunks:
        document = Document(
            page_content=chunk,
            metadata={"url": url}  # URL 메타데이터 포함
        )
        documents.append(document)

# 문서 임베딩
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
print("\n[추천 베스트 메뉴]")
print(response)