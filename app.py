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
    transform: translateY(-2px);
}

.welcome-card {
    margin-top: 2rem;
    padding: 2.5rem 1.5rem;
    text-align: center;
    background-color: #fafafa;
    border-radius: 24px;
    border: 1px solid #f0f0f0;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03);
}

.game-title {
    text-align: center;
    font-size: 2.5rem;
    font-weight: 700;
    margin-bottom: 2rem;
}

.result-card {
    margin-top: 2rem;
    padding: 1.8rem;
    text-align: center;
    background-color: #f8fafc;
    border-radius: 20px;
    border: 1px solid #e2e8f0;
}
</style>
""", unsafe_allow_html=True)

# 3. 화면 단계 관리 (intro: 입장 화면, game: 가위바위보 게임 화면)
if "stage" not in st.session_state:
    st.session_state.stage = "intro"

# ----------------------------------------------------
# 화면 1: '들어가기' 인트로 화면
# ----------------------------------------------------
if st.session_state.stage == "intro":
    st.markdown("<h2 style='text-align: center; margin-bottom: 2rem;'>웹앱에 오신 것을 환영해요 ☁️</h2>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        start_btn = st.button("들어가기")

    if start_btn:
        st.balloons()
        st.markdown("""
        <div class="welcome-card">
            <p style="font-size: 2.2rem; font-weight: bold; margin: 0;">🎉 환영합니다! 🎉</p>
            <p style="color: #666; margin-top: 0.8rem;">잠시 후 게임으로 이동합니다...</p>
        </div>
        """, unsafe_allow_html=True)

        time.sleep(2)
        st.session_state.stage = "game"
        st.rerun()

# ----------------------------------------------------
# 화면 2: 가위바위보 게임 화면
# ----------------------------------------------------
elif st.session_state.stage == "game":
    st.markdown("<div class='game-title'>가위바위보! ✌️✊🖐️</div>", unsafe_allow_html=True)

    choices = ["가위", "바위", "보"]
    icons = {"가위": "✌️ 가위", "바위": "✊ 바위", "보": "🖐️ 보"}

    col1, col2, col3 = st.columns(3)
    user_choice = None

    with col1:
        if st.button(icons["가위"]):
            user_choice = "가위"
    with col2:
        if st.button(icons["바위"]):
            user_choice = "바위"
    with col3:
        if st.button(icons["보"]):
            user_choice = "보"

    if user_choice:
        computer_choice = random.choice(choices)

        if user_choice == computer_choice:
            result_text = "🤝 무승부"
        elif (user_choice == "가위" and computer_choice == "보") or \
             (user_choice == "바위" and computer_choice == "가위") or \
             (user_choice == "보" and computer_choice == "바위"):
            result_text = "🎉 승리!"
        else:
            result_text = "😢 패"

        # f-string 문자열 포맷팅으로 결과 안전하게 렌더링
        card_html = f"""
        <div class="result-card">
            <p style="font-size: 1.2rem; margin-bottom: 0.5rem;">
                나: <b>{icons[user_choice]}</b> vs 상대: <b>{icons[computer_choice]}</b>
            </p>
            <p style="font-size: 2rem; font-weight: bold; margin: 0;">
                {result_text}
            </p>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)
