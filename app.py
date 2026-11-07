import streamlit as st
import time

# 1. 페이지 기본 설정 (와이드 모드, 아이콘 등)
st.set_page_config(
    page_title="환영 웹앱",
    page_icon="✨",
    layout="centered"
)

# 2. 커스텀 CSS 적용 (흰색 배경, 검은색 글씨, 몽글몽글한 고운도둠 폰트)
st.markdown("""
    <style>
    /* 구글 웹폰트 불러오기 (고운도둠) */
    @import url('https://fonts.googleapis.com/css2?family=Gowun+Dodum&display=swap');

    /* 전체 앱 배경 흰색, 글씨 검은색, 폰트 적용 */
    .stApp {
        background-color: #ffffff;
        color: #1a1a1a;
        font-family: 'Gowun Dodum', sans-serif !important;
    }

    /* 모든 텍스트 요소에 폰트 강제 적용 */
    h1, h2, h3, h4, p, span, div, button {
        font-family: 'Gowun Dodum', sans-serif !important;
        color: #1a1a1a;
    }

    /* 버튼 스타일 커스텀 */
    div.stButton > button {
        background-color: #f0f0f0;
        color: #111111;
        border: 1.5px solid #dcdcdc;
        border-radius: 20px;
        padding: 10px 28px;
        font-size: 1.1rem;
        font-weight: bold;
        transition: all 0.2s ease-in-out;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
    }

    /* 버튼에 마우스 올렸을 때 */
    div.stButton > button:hover {
        background-color: #e5e5e5;
        border-color: #b0b0b0;
        transform: translateY(-2px);
    }

    /* 환영 메시지 박스 스타일 */
    .welcome-card {
        margin-top: 2rem;
        padding: 2.5rem 1.5rem;
        text-align: center;
        background-color: #fafafa;
        border-radius: 24px;
        border: 1px solid #f0f0f0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03);
        animation: fadeIn 0.8s ease-in-out;
    }

    .welcome-text {
        font-size: 2.4rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }

    .sub-text {
        font-size: 1.1rem;
        color: #555555;
        margin-top: 0.8rem;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    </style>
""", unsafe_allow_html=True)

# 3. 화면 UI 구성
st.markdown("<h2 style='text-align: center; margin-bottom: 2rem;'>웹앱에 오신 것을 환영해요 ☁️</h2>", unsafe_allow_html=True)

# 가운데 정렬을 위한 컬럼 분할
col1, col2, col3 = st.columns([1, 1, 1])

with col2:
    clicked = st.button("들어가기", use_container_width=True)

# 4. 버튼 클릭 시 동작
if clicked:
    # 폭죽(축하 꽃가루) 효과
    st.balloons()
    
    # 환영 문구 렌더링
    st.markdown("""
        <div class="welcome-card">
            <p class="welcome-text">🎉 환영합니다! 🎉</p>
            <p class="sub-text">소중한 발걸음을 해주셔서 감사합니다 :)</p>
        </div>
    """, unsafe_allow_html=True)
import streamlit as st
import time
import random

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="가위바위보 게임",
    page_icon="✊",
    layout="centered"
)

# 2. 커스텀 CSS 적용 (흰색 배경, 검은 글씨, 몽글몽글한 고운도둠 폰트)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Gowun+Dodum&display=swap');

    .stApp {
        background-color: #ffffff;
        color: #1a1a1a;
        font-family: 'Gowun Dodum', sans-serif !important;
    }

    h1, h2, h3, h4, p, span, div, button {
        font-family: 'Gowun Dodum', sans-serif !important;
        color: #1a1a1a;
    }

    /* 둥글둥글한 버튼 스타일 */
    div.stButton > button {
        background-color: #f8f9fa;
        color: #111111;
        border: 1.5px solid #e2e8f0;
        border-radius: 16px;
        padding: 12px 20px;
        font-size: 1.15rem;
        font-weight: bold;
        transition: all 0.2s ease-in-out;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
        width: 100%;
    }

    div.stButton > button:hover {
        background-color: #edf2f7;
        border-color: #cbd5e1;
        transform: translateY(-2px
