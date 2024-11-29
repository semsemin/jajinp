from streamlit_cropper import st_cropper
from PIL import Image
import streamlit as st

def crop_and_save_image(image_path, save_path=None):
    img = Image.open(image_path)

    # st_cropper를 사용하여 크롭
    cropped_img = st_cropper(img, realtime_update=True, box_color='#FF6347', aspect_ratio=None)
    
    # 크롭된 이미지 보여주기
    st.write("크롭된 이미지:")
    st.image(cropped_img) 
        # 저장 경로 설정
    if save_path is None:
        # 기본 경로는 원본 경로에 "_cropped" 추가, 확장자는 .png로 고정
        save_path = image_path.rsplit(".", 1)[0] + "_cropped.png"

    # 확장자 확인 및 경로 처리
    if not save_path.lower().endswith(('.png', '.jpg', '.jpeg')):
        save_path += ".png"  # 기본 확장자 추가

    # 크롭된 이미지 저장
    cropped_img.save(save_path)

    return save_path
