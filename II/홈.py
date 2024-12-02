import streamlit as st

st.set_page_config(
    page_title="Home",
    page_icon=":edit:",
)


# 제목 및 소개
st.write("## 이미지 분석을 통한 RAG기반 실시간 AI 추천 서비스")

st.markdown(
    """
    안녕하세요! 👋  \n
    이 모델은 이미지 분석을 통해 많은 선택지 중 **최적의 선택지**를 추천합니다.  
    아래의 서비스를 살펴보고 사이드바에서 원하는 항목을 선택해주세요.\n
    """
)

st.write(" ")


# 스타일: 서비스 설명 박스
def service_section(title, description, border_color, background_color, icon):
    st.markdown(
        f"""
        <div style="
            padding: 20px;
            border: 1.5px solid {border_color};
            border-radius: 12px;
            margin-bottom: 20px;
            background-color: {background_color};
            ">
            <h4 style="margin: 0; color: #333; display: flex; align-items: center;">
                <span style="font-size: 24px; margin-right: 10px;">{icon}</span>
                {title}
            </h4>
            <p style="margin-top: 10px; color: #555; font-size: 17px; line-height: 1.6;">
                {description}

        """,
        unsafe_allow_html=True,
    )

# 서비스 1: 상품 추천
service_section(
    "상품 추천",
    """
    이미지에서 상품명과 현장 가격 정보를 분석해 **온라인 최저가**, **평점**, **리뷰 수**를 바탕으로 최적의 상품을 추천합니다.  
    재고가 없을 경우, 유사도를 분석해 가장 비슷한 대체 상품을 제안하여 **합리적인 선택**을 유도합니다.
    """,
    border_color="#cdcbca", 
    background_color="#ffffff",  # 연한 회색 배경
    icon="🛍️"
)

# 서비스 2: 베스트 메뉴 추천
service_section(
    "메뉴 추천",
    """
    간판 이미지를 분석하여 **상호명을 자동으로 인식**하고, 해당 매장의 **베스트 메뉴**를 추천합니다.  
    복잡한 검색 없이 간판 사진만으로 매장의 인기 메뉴 정보를 손쉽게 확인할 수 있습니다. 
    """,
    border_color="#cdcbca", 
    background_color="#ffffff",  # 연한 회색 배경
    icon="🍽️"
)

# 서비스 3: 도서 추천
service_section(
    "도서 추천",
    """
    인식된 도서들의 평점, 리뷰 수, 베스트셀러 순위를 고려하여 **가장 읽을 만한 도서**를 추천합니다.  
    또한, 도서들의 **줄거리**와 **추천 독자** 정보를 함께 제공하여 독서 선택을 돕습니다.
    """,
    border_color="#cdcbca", 
    background_color="#ffffff",  # 연한 회색 배경
    icon="📚"
)
