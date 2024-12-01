import os
import streamlit as st

def delete_all_files_in_folder(folder_path):
    """지정된 폴더의 모든 파일 삭제"""
    if os.path.exists(folder_path):
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            if os.path.isfile(file_path):  # 파일인지 확인
                os.remove(file_path)
    else:
        st.write(f"Folder does not exist: {folder_path}")

# Streamlit UI
st.markdown("""
<div style="background-color: #f9f9f9; padding: 15px; border: 1px solid #ddd; border-radius: 5px;">
    <h4>파일 삭제</h4>
    <p>
        <strong>image</strong> 폴더에 저장된 모든 이미지 파일을 삭제하시려면 아래의 <strong>파일 모두 삭제</strong> 버튼을 눌러주세요. <br>
        <span style="color: red;">⚠️ 버튼 클릭 후 파일은 복구할 수 없습니다. 신중히 눌러주세요.</span>
    </p>
</div>
""", unsafe_allow_html=True)

# 폴더 경로 설정
folder_to_clear = "image/"
st.write("")

# 버튼을 눌렀을 때 파일 삭제
if st.button("🗑️ 파일 모두 삭제"):
    delete_all_files_in_folder(folder_to_clear)
    st.success(f"{folder_to_clear} 폴더의 모든 파일이 삭제되었습니다.")
