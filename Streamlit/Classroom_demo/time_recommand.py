import streamlit as st
import pandas as pd
from datetime import datetime
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.runnable import RunnablePassthrough
from langchain_openai import ChatOpenAI
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from secrets_manager import get_api_key
import json


def select_date():
    # 날짜 선택 위젯
    selected_date = st.date_input("날짜를 선택하세요: ", datetime.today())
    # 성공 메시지 출력
    st.success(f'{selected_date} 에 예약 가능한 시간대를 알려드리겠습니다.')
    # 선택한 날짜 반환
    return selected_date


def find_empty_timeslots(classroom_name, selected_date):
    # API 키 설정
    os.environ["OPENAI_API_KEY"] = get_api_key('GPT_API_KEY')

    # 날짜 포맷 변환
    date = selected_date.strftime("%Y%m%d")

    # 엑셀 데이터 로드
    excel_path = "/Users/nimess/Desktop/project/jajinp/Streamlit/Classroom_demo/classroom_dataset/ms.xlsx"
    sheet_name = "EXPORT"
    data = pd.read_excel(excel_path, sheet_name=sheet_name)

    # 특정 강의실과 날짜 필터링
    filtered_data = data[(data['시설명'] == classroom_name) & (data['사용일자'] == int(date))]

    if filtered_data.empty:
        return {"error": f"{classroom_name}에 {date}에 대한 데이터가 없습니다."}

    # 빈 시간대 추출 (연속된 빈 시간대 묶기)
    empty_slots = []
    time_slots = filtered_data.columns[3:]  # 시간대 열만 추출
    current_start = None

    for i, time_slot in enumerate(time_slots):
        status = filtered_data[time_slot].values[0]
        if pd.isna(status):  # 빈칸이면
            if current_start is None:
                current_start = time_slot  # 빈 시간대 시작 설정
            # 마지막 시간대 처리
            if i == len(time_slots) - 1 :
                empty_slots.append(f"{current_start}~{time_slot}")
        else:  # 빈칸이 끊겼을 때
            if current_start is not None:
                # 현재까지의 연속된 시간대를 저장
                prev_time = time_slots[i]  # 직전 시간대
                empty_slots.append(f"{current_start}~{prev_time}")
                current_start = None

    # 텍스트 Splitter 설정
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=1000,
        chunk_overlap=200,
        encoding_name='cl100k_base'
    )

    # 데이터 분리 및 문서 생성
    documents = []
    chunks = text_splitter.split_text("\n".join(empty_slots))
    for chunk in chunks:
        document = Document(
            page_content=chunk,
            metadata={"classroom": classroom_name, "date": date}
        )
        documents.append(document)

    # 문서 임베딩 및 벡터스토어 생성
    embedding_model = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embedding_model,
        collection_name='classroom_schedule',
        collection_metadata={'hnsw:space': 'cosine'},
        persist_directory="./chroma_db"
    )

    # 문서 검색
    retriever = vectorstore.as_retriever(
        search_type='mmr',
        search_kwargs={
            'k': 5,  # 상위 5개
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
        ("system", "당신은 강의실의 빈 시간대를 찾는 AI입니다. 아래의 컨텍스트를 바탕으로 질문에 답변하세요."
        "응답은 JSON 형식으로 작성하며, 키는 'empty_timeslots'이며, 값은 빈 시간대의 리스트입니다."
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

    # 질문 생성
    query = f"{classroom_name} 강의실의 {date} 빈 시간대를 알려줘. "
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
        st.error("JSON 디코딩 에러:", e)
        result = {"error": "JSON parsing failed"}

    return {"empty_timeslots": empty_slots}


# Streamlit 앱 실행
st.title("강의실 빈 시간대 찾기")

# 강의실 입력
classroom_name = st.text_input("강의실명을 입력하세요 (예: 명신관201):", "명신관201")

# 날짜 선택
selected_date = select_date()

# 실행 버튼
if st.button("예약 가능한 시간대 찾기"):
    result = find_empty_timeslots(classroom_name, selected_date)
    st.json(result)

