import streamlit as st

option = st.sidebar.selectbox(
    'Menu',
    ('상품 추천', '메뉴 추천')
)
