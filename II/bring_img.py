import streamlit as st
import os
from datetime import datetime
from PIL import Image

def run_camera():
    st.write("")
    st.subheader('카메라')
    enable = st.checkbox("enable camera")
    picture = st.camera_input("take a picture", disabled = not enable)

    if picture:
        current_time = datetime.now()
        filename = current_time.isoformat().replace(":", "_") + '.jpg'

        if not os.path.exists('image'):
            os.makedirs('image')

        image_path = os.path.join('image', filename)
        
        with open(image_path, 'wb') as f:
            f.write(picture.getbuffer())

        st.image(picture)
        st.success('이미지 업로드'+ image_path)
        
        return image_path 
    return 

def upload_image():
    st.write("")
    st.subheader('이미지 업로드')
    img_file = st.file_uploader ('이미지', type=['png','jpg', 'jpeg'])

    if img_file is not None : 
        current_time = datetime.now()
        filename = current_time.isoformat().replace(":", "_")
        img_file.name = filename +'.jpg'

        if not os.path.exists('image'):
            os.makedirs('image')

        image_path = os.path.join('image', filename)
        
        with open(image_path, 'wb') as f:
            f.write(img_file.getbuffer())

        st.success('이미지 업로드 '+ image_path)
        img = Image.open(image_path)
        st.image(img)

        return image_path