import streamlit as st
import bring_img as bring_img
import gpt

# main 함수
def main():
    st.title("ItemInsight")
    bring_img.run_camera()
    bring_img.upload_image()
    gpt.get_gpt_response()



# main 실행
if __name__ == "__main__":
    main()

