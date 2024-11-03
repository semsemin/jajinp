import streamlit as st
import bring_img
import gpt

# main �븿�닔
def main():
    st.title("ItemInsight")
    input_option = st.radio("이미지 업로드 방식을 선택하세요", ("카메라", "사진 보관함"))
    
    if input_option == "카메라":
        image_path = bring_img.run_camera()
        print(image_path)
    else:
        image_path = bring_img.upload_image()
        print(image_path)

    if image_path:
        gpt.gpt_img(image_path)


# main �떎�뻾
if __name__ == "__main__":
    main()
