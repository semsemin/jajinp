import streamlit as st
import os
from datetime import datetime
from PIL import Image

def run_camera():
    st.subheader('카메라')
    enable = st.checkbox("enable camera")
    picture = st.camera_input("take a picture", disabled = not enable)

    if picture:
        st.image(picture)

def upload_image():
    st.subheader('이미지 업로드')
    img_file = st.file_uploader('', type=['png','jpg', 'jpeg'])

    if img_file is not None : 
        current_time = datetime.now()
        filename = current_time.isoformat().replace(":", "_")
        img_file.name = filename +'.jpg'

        if not os.path.exists('image'):
            os.makedirs('image')
        
        with open(os.path.join('image', img_file.name), 'wb') as f:
            f.write(img_file.getbuffer())

        st.success('이미지 업로드'+ img_file.name)

        st.subheader('이미지 업로드')
        img = Image.open('image/'+img_file.name)
        st.image(img)

