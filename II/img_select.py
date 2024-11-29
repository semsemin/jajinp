import streamlit as st
from PIL import Image
import bring_img
import gpt
from Label_demo.product_data import fetch_online_product_data
from Label_demo.st_sort import display_sorted_products  # st_sort.py에서 display_sorted_products 가져오기
from img_crop import crop_and_save_image  # 이미지 크롭 및 저장 기능
from Label_demo.recommand_algo import generate_content_based_recommendations  # recommand_algo.py에서 추천 알고리즘 함수 가져오기
from Label_demo.display_total_recommendation import display_recommendations  # display_total_recommendation.py에서 결과 출력 함수 가져오기
from Ganpan_demo.menu_recom import recommend_best_menus
from Book_demo.book_data import fetch_book_data 
from Book_demo.book_sort import display_sorted_books
from Book_demo.book_recommand_algo import process_book_data
from Book_demo.book_display import book_display_recommendations
import time  
import pandas as pd

def img_select(task_type):
    st.title("ItemInsight")

    if task_type == 'label':
        # CSS 스타일 추가
        st.markdown("""
            <style>
            .service-title {
            line-height: 1.5; 
            font-size: 20px; 
            font-weight: bold;
            color: #4A90E2;
            margin-bottom: 10px;
            }
            .instruction-box {
            line-height: 1.5; 
            font-size: 16px; 
            border: 1px solid #ddd; 
            padding: 15px; 
            border-radius: 5px; 
            background-color: #f9f9f9;
            margin-bottom: 10px;
            }
            div[data-baseweb="radio"] {
            background-color: #f8f9fa;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 10px;
            }
            div[data-baseweb="radio"] > div {
            margin-right: 15px;
            }
            </style>
            """, unsafe_allow_html=True)

        # 서비스 제목 및 설명
        st.markdown("""
            <div class="service-title">
            상품 추천 서비스
            </div>
            <div class="instruction-box">
            상품 라벨을 촬영하거나 업로드하면, <br>
            해당 상품의 이름과 가격을 인식하여 상품을 추천해드립니다.
            </div>
            """, unsafe_allow_html=True)

        input_option = st.radio("이미지 업로드 방식을 선택하세요.", ("카메라", "사진 보관함"))
        
        if input_option == "카메라":
            st.markdown("""
            <div style="line-height: 1.5; font-size: 16px; border: 1px solid #ddd; padding: 10px; border-radius: 5px; background-color: #f9f9f9;">
                카메라를 사용해 상품 라벨을 촬영해주세요!<br>
                상품명과 가격이 선명하게 보이도록 사진을 찍어주세요.
            </div>
            """, unsafe_allow_html=True)
            image_path = bring_img.run_camera()
        else:
            st.markdown("""
            <div style="line-height: 1.5; font-size: 16px; border: 1px solid #ddd; padding: 10px; border-radius: 5px; background-color: #f9f9f9;">
                상품명과 가격이 선명하게 보이는 이미지를 선택해주세요!<br>
                사진이 흐리거나 라벨이 가려져 있으면 정확한 인식이 어려울 수 있습니다.
            </div>
            """, unsafe_allow_html=True)
            image_path = bring_img.upload_image()

        if image_path:
            st.write("상품 라벨을 크롭해주세요.")
            cropped_image_path = crop_and_save_image(image_path)

    elif task_type == 'ganpan':
        # CSS 스타일 추가
        st.markdown("""
            <style>
            .service-title {
            line-height: 1.5; 
            font-size: 20px; 
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
            }
            .instruction-box {
            line-height: 1.5; 
            font-size: 16px; 
            border: 1px solid #ddd; 
            padding: 15px; 
            border-radius: 5px; 
            background-color: #f9f9f9;
            margin-bottom: 10px;
            }
            div[data-baseweb="radio"] {
            background-color: #f8f9fa;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 10px;
            }
            div[data-baseweb="radio"] > div {
            margin-right: 15px;
            }
            </style>
            """, unsafe_allow_html=True)

        # 서비스 제목 및 설명
        st.markdown("""
            <div class="service-title">
            메뉴 추천 서비스
            </div>
            <div class="instruction-box">
            매장 간판을 촬영하거나 업로드하면, <br>
            해당 가게의 이름과 지점을 인식하여 추천 메뉴를 제공합니다.
            </div>
            """, unsafe_allow_html=True)

        input_option = st.radio("이미지 업로드 방식을 선택하세요.", ("카메라", "사진 보관함"))
        
        if input_option == "카메라":
            st.markdown("""
            <div style="line-height: 1.5; font-size: 16px; border: 1px solid #ddd; padding: 10px; border-radius: 5px; background-color: #f9f9f9;">
                카메라를 사용해 매장 간판을 촬영해주세요! <br>
                매장 이름과 지점명이 선명하게 보이도록 사진을 찍어주세요.
            </div>
            """, unsafe_allow_html=True)
            image_path = bring_img.run_camera()
        else:
            st.markdown("""
            <div style="line-height: 1.5; font-size: 16px; border: 1px solid #ddd; padding: 10px; border-radius: 5px; background-color: #f9f9f9;">
                매장 이름과 지점명이 선명하게 보이는 이미지를 선택해주세요!<br>
                사진이 흐리거나 간판이 가려져 있으면 정확한 인식이 어려울 수 있습니다.
            </div>
            """, unsafe_allow_html=True)
            image_path = bring_img.upload_image()

        if image_path:
            st.write("매장 이름과 지점명이 보이도록 크롭해주세요.")
            cropped_image_path = crop_and_save_image(image_path)

    elif task_type == 'book':
               # CSS 스타일 추가
        st.markdown("""
            <style>
            .service-title {
            line-height: 1.5; 
            font-size: 20px; 
            font-weight: bold;
            color:  #9ACD32;
            margin-bottom: 10px;
            }
            .instruction-box {
            line-height: 1.5; 
            font-size: 16px; 
            border: 1px solid #ddd; 
            padding: 15px; 
            border-radius: 5px; 
            background-color: #f9f9f9;
            margin-bottom: 10px;
            }
            div[data-baseweb="radio"] {
            background-color: #f8f9fa;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 10px;
            }
            div[data-baseweb="radio"] > div {
            margin-right: 15px;
            }
            </style>
            """, unsafe_allow_html=True)

        # 서비스 제목 및 설명
        st.markdown("""
            <div class="service-title">
            책 추천 서비스
            </div>
            <div class="instruction-box">
            책 제목을 촬영하거나 업로드하면, <br>
            책의 줄거리와 정보를 바탕으로 책을 추천해드립니다.
            </div>
            """, unsafe_allow_html=True)

        input_option = st.radio("이미지 업로드 방식을 선택하세요.", ("카메라", "사진 보관함"))
        
        if input_option == "카메라":
            st.markdown("""
            <div style="line-height: 1.5; font-size: 16px; border: 1px solid #ddd; padding: 10px; border-radius: 5px; background-color: #f9f9f9;">
                카메라를 사용해 책 표지를 촬영해주세요!<br>
                제목이 선명하게 보이도록 사진을 찍어주세요.
            </div>
            """, unsafe_allow_html=True)
            image_path = bring_img.run_camera()

        else:
            st.markdown("""
            <div style="line-height: 1.5; font-size: 16px; border: 1px solid #ddd; padding: 10px; border-radius: 5px; background-color: #f9f9f9;">
                책 제목이 선명하게 보이는 이미지를 선택해주세요!<br>
                사진이 흐리거나 표지가 가려져 있으면 정확한 인식이 어려울 수 있습니다.
            </div>
            """, unsafe_allow_html=True)
            image_path = bring_img.upload_image()

        if image_path:
            st.write("책 제목이 보이도록 크롭해주세요.")
            cropped_image_path = crop_and_save_image(image_path)

    # 크롭된 이미지 사용하기
    if image_path and cropped_image_path:
        if st.button("크롭된 이미지 사용하기"):
            if task_type == 'label':
                result = gpt.get_gpt_response(cropped_image_path)
                st.write("GPT에서 추출한 데이터 :")
                st.json(result)
                
                if result:
                    # 로딩 중 컴포넌트 시작
                    latest_iteration = st.empty()
                    progress_bar = st.progress(0)

                    # 데이터 처리 중 로딩 상태 표시
                    for i in range(50):
                        latest_iteration.text(f"Loading data... {i}%")
                        progress_bar.progress(i)
                        
                        time.sleep(0.02)  # 로딩 속도 조정 가능

                    # "product name" 키를 사용해 product_data 생성
                    product_data = [{"product_name": item["product_name"]} for item in result]

                    # 상세 데이터 가져오기
                    detailed_data = fetch_online_product_data(product_data)
                    
                    # 정렬 및 표시를 위해 session_state에 저장
                    st.session_state["product_data"] = detailed_data
                    local_data = result

                    # 로딩 완료 상태 표시
                    for i in range(30, 101):
                        latest_iteration.text(f"Processing data... {i}%")
                        progress_bar.progress(i)
                        time.sleep(0.02)

                    # 로딩 컴포넌트 제거
                    latest_iteration.empty()
                    progress_bar.empty()

                    # display_sorted_products 호출
                    display_sorted_products()
                    recommendation_df, recommendations = generate_content_based_recommendations(local_data, detailed_data)
                    display_recommendations(recommendation_df, recommendations)

                
            elif task_type == 'ganpan':
                result = gpt.get_product_data(cropped_image_path)
                st.write("GPT에서 추출한 데이터 :")
                st.json(result)
                best_menu = recommend_best_menus(result)
                st.write("베스트 메뉴 추천 :")
                if "best_menus" in best_menu:
                    # "best_menus" 리스트를 DataFrame으로 변환
                    df = pd.DataFrame(best_menu["best_menus"], columns=["name", "description"])
                    st.table(df)  # 표로 출력
                else:
                    st.write("베스트 메뉴 데이터가 없습니다.")
        

            elif task_type == 'book':
                result = gpt.get_book_data(cropped_image_path)
                st.write("GPT에서 추출한 데이터 :")
                st.json(result)
                # 로딩 중 컴포넌트 시작
                latest_iteration = st.empty()
                progress_bar = st.progress(0)

                # 데이터 처리 중 로딩 상태 표시
                for i in range(30):
                    latest_iteration.text(f"Loading data... {i}%")
                    progress_bar.progress(i)
                        
                    time.sleep(0.02)  # 로딩 속도 조정 가능
                if result:
                    # "product name" 키를 사용해 product_data 생성
                    title_data = [{"title": item["title"]} for item in result]

                    book_data = fetch_book_data(title_data) 

                    # 정렬 및 표시를 위해 session_state에 저장
                    st.session_state["title"] = book_data
                    local_data = result

                    # 로딩 완료 상태 표시
                    for i in range(30, 101):
                        latest_iteration.text(f"Processing data... {i}%")
                        progress_bar.progress(i)
                        time.sleep(0.02)
                    # 로딩 컴포넌트 제거
                    latest_iteration.empty()
                    progress_bar.empty()

                    # display_sorted_products 호출
                    display_sorted_books()
                    recommendation_df, recommendations = process_book_data(book_data)
                    book_display_recommendations(recommendation_df, recommendations)