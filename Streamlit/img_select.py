# -*- coding: utf-8 -*-
import streamlit as st
import bring_img
import gpt

# main 함수 수정: 어떤 기능을 수행할지 결정할 수 있는 기능 추가
def img_select(task_type):
    st.title("ItemInsight")
    input_option = st.radio("이미지 업로드 방식을 선택하세요.", ("카메라", "사진 보관함"))
    
    if input_option == "카메라":
        image_path = bring_img.run_camera()
    else:
        image_path = bring_img.upload_image()

    if image_path:
        # task_type에 따라 다른 GPT 기능 호출
        if task_type == 'label':
            result = gpt.get_gpt_response(image_path)  # 상품 정보 추출
            
        elif task_type == 'ganpan':
            result = gpt.get_product_data(image_path)  # 매장 정보 추출
