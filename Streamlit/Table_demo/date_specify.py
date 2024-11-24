import datetime
import streamlit as st


def select_date():
    # 날짜 선택 위젯
    selected_date = st.date_input("날짜를 선택하세요: ", datetime.date.today())
    # 성공 메시지 출력
    st.success(f'{selected_date} 에 예약 가능한 시간대를 알려드리겠습니다.')
    # 선택한 날짜 반환
    return selected_date
