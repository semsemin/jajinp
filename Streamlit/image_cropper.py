from streamlit_cropper import st_cropper
from PIL import Image
import streamlit as st

def crop_and_save_image(image_path, save_path=None):
    img = Image.open(image_path)
    st.write("이미지를 크롭하세요.")

    # st_cropper를 사용하여 크롭
    cropped_img = st_cropper(img, realtime_update=True, box_color='#FF6347', aspect_ratio=None)
    
    # 크롭된 이미지 보여주기
    st.write("크롭된 이미지:")
    st.image(cropped_img) 

    # 저장 경로 설정 (save_path가 없으면 원본 경로에 "_cropped" 추가)
    if save_path is None:
        save_path = image_path.rsplit(".", 1)[0] + "_cropped.png"

    # 크롭된 이미지 저장
    cropped_img.save(save_path)

    return save_path
