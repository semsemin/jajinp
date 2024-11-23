import streamlit as st
from PIL import Image
import bring_img
import gpt
from image_cropper import crop_and_save_image  # 이미지 크롭 및 저장 기능
from recommand_algo import generate_content_based_recommendations  # recommand_algo.py에서 추천 알고리즘 함수 가져오기

def img_select(task_type):
    st.title("ItemInsight")
    input_option = st.radio("이미지 업로드 방식을 선택하세요.", ("카메라", "사진 보관함"))
    
    # 이미지 업로드
    if input_option == "카메라":
        image_path = bring_img.run_camera()
    else:
        image_path = bring_img.upload_image()

    # 이미지 크롭 및 저장
    if image_path:
        cropped_image_path = crop_and_save_image(image_path)

        if st.button("크롭된 이미지 사용하기"):
            # GPT로 데이터 추출
            if task_type == 'label':
                result = gpt.get_gpt_response(cropped_image_path)  # 상품 정보 추출
                st.write("GPT에서 추출한 데이터 (원본 결과):")
                st.json(result)  # 원본 데이터 확인
                
                if result:
                    # "product name" 키를 사용해 product_data 생성
                    product_data = [{"product_name": item["product name"]} for item in result]

                    # 상세 데이터 가져오기
                    detailed_data = fetch_online_product_data(product_data)
                    
                    # 정렬 및 표시를 위해 session_state에 저장
                    st.session_state["product_data"] = detailed_data
                    st.write("데이터가 정렬 및 표시될 준비가 완료되었습니다.")
                    
                    # display_sorted_products 호출
                    display_sorted_products()
                    recommendation_df, recommendations = generate_content_based_recommendations(result, detailed_data)
                    display_recommendations(recommendation_df, recommendations)

            elif task_type == 'ganpan':
                result = gpt.get_product_data(cropped_image_path)  # 매장 정보 추출
