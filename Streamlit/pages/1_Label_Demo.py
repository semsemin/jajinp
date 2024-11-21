import streamlit as st
import img_select
from Tavily_search import process_extracted_data

# �긽�뭹 �젙蹂� 異붿텧 湲곕뒫�쓣 �닔�뻾�븯�룄濡� �꽕�젙
extracted_data= img_select.img_select(task_type='label')

# extracted_data가 비어 있지 않으면 리뷰 검색 및 정렬
if extracted_data:
    # 리뷰를 높은 순으로 정렬하는 함수 실행
    top_reviewed_products = process_extracted_data(extracted_data)

    # 결과 출력
    for product in top_reviewed_products:
        st.write(f"**Product:** {product['product name']}")
        st.write(f"**Reviews and Source URLs:**\n{product['reviews']}")
        st.write("---")
else:
    st.warning("상품 정보를 추출할 수 없습니다. 이미지를 다시 확인해주세요.")
