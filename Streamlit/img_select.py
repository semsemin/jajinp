# -*- coding: utf-8 -*-
import streamlit as st
from streamlit_cropper import st_cropper
from PIL import Image
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
        # 이미지를 크롭할 수 있도록 사용자가 크롭 영역을 지정
        img = Image.open(image_path)
        st.write("이미지를 크롭하세요.")
        
        # st_cropper 사용하여 크롭 기능 제공
        cropped_img = st_cropper(img, realtime_update=True, box_color='#FF6347', aspect_ratio=None)
        
        # 크롭된 이미지 보여주기
        st.write("크롭된 이미지:")
        st.image(cropped_img, use_column_width=True)

        # 크롭된 이미지를 임시 파일로 저장
        cropped_image_path = image_path + ".png"
        cropped_img.save(cropped_image_path)

        # task_type에 따라 다른 GPT 기능 호출
        if task_type == 'label':
            result = gpt.get_gpt_response(cropped_image_path)  # 상품 정보 추출
        elif task_type == 'ganpan':
            result = gpt.get_product_data(cropped_image_path)  # 매장 정보 추출

        # 결과를 화면에 표시
        if result:
            st.json(result)
