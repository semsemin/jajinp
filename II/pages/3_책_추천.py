import streamlit as st
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import img_select

# 매장 정보 추출 기능을 수행하도록 설정
img_select.img_select(task_type='book')  