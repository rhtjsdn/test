import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="그리드샷 에임 트레이너", layout="wide")

# Streamlit 기본 여백 및 iframe 초기화
st.markdown("""
<style>
    iframe {
        border: none !important;
        outline: none !important;
    }
    .main .block-container {
        padding: 1.5rem 1rem 0rem 1rem !important;
    }
</style>
""", unsafe_allow_html=True)

gridshot_html = """
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>

<style>
  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
    user-select: none;
    -webkit-tap-highlight-color: transparent;
    outline: none !important;
  }

  body {
    background-color: #ffffff;
    color: #111111;
    font-family: "Apple SD Gothic Neo", "Malgun Gothic", sans-serif;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;
    width: 100vw;
    height: 100vh;
    padding-top: 25px; /* 상단이 짤리지 않도록 여백 확보 */
    overflow: hidden;
  }

  /* 폭죽 라이브러리가 자동 생성하는 캔버스의 배경 및 테두리 완전 투명화 */
  canvas:not(#mainCanvas) {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    outline: none !important;
  }

  /* 상단 점수판 */
  #header-bar {
    width: 1280px;
    height: 50px;
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 60px;
    font-size: 26px;
    font-weight: 800;
    color: #111111;
    visibility: hidden;
    margin-bottom: 12px;
  }

  /* 훈련장 컨테이너 */
  .stage-container {
    position: relative;
    width: 1280px;
    height: 640px;
  }

  /* 실제 조준 캔버스 */
  #mainCanvas {
    display: block;
    width: 1280px;
    height: 640px;
    background-color: #ffffff;
    border: 3.5px solid #111111;
    border-radius: 20px;
    cursor: default;
  }

  /* 시작/재시작 버튼 */
  .center-btn {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: 34px;
    font-weight: 800;
    line-height: 1;
    background-color: #ffffff;
    color: #111111;
    border: 3.5px solid #111111;
    border-radius: 40px;
    padding: 16px 52px;
    cursor: pointer;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    transition: all 0.2s ease-in-out;
    z-index: 10;
  }

  .center-btn:hover {
    background-color: #f7f7f7;
    transform: translate(-50%, -52%);
    box-shadow: 0 6px 20px rgba(0,0,0,0.12);
  }
  .center-btn:active {
    transform: translate(-50%, -49%);
  }
</style>
</head>
<body>

  <!-- 상단 점수판 (짤림 방지 위치 조정) -->
  <div id="header-bar">
    <div>남은 시간: <span id="timer">30</span>초</div>
    <div>점수: <span id="score">0</span></div>
    <div>정확도: <span id="accuracy">100%</span></div>
  </div>

  <!-- 메인 훈련장 -->
  <div class="stage-container">
    <canvas id="mainCanvas" width="1280" height="640"></canvas>
    <button id="actionBtn" class="center-btn" onclick="handleClick()">들어가기</button>
  </div>

<script>
  const canvas = document.getElementById("mainCanvas");
  const ctx = canvas.getContext("2d");
  const btn = document.getElementById("actionBtn");
  const headerBar = document.getElementById("header-bar");

  let state = "IDLE";

  const TARGET_COUNT = 3;
  const RADIUS = 28;
  let targets = [];
  let score = 0;
  let totalClicks = 0;
  let hits = 0;
  let timeLeft = 30;
  let timerInterval = null;

  function handleClick() {
    btn.style.display = "none";
    state = "WELCOME";
    drawWelcomeScreen();

    // 폭죽 효과
    confetti({
      particleCount: 100,
      spread: 85,
      origin: { y: 0.6 }
    });

    setTimeout(() => {
      startGame();
    }, 2000);
  }

  // 캔버스 내부에 텍스트 출력
  function drawWelcomeScreen() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    ctx.fillStyle = "#111111";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";

    ctx.font = "900 68px 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif";
    ctx.fillText("환영합니다!", canvas.width / 2, canvas.height / 2 - 25);

    ctx.font = "600 24px 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif";
    ctx.fillStyle = "#666666";
    ctx.fillText("잠시 후 그리드샷 훈련이 시작됩니다...", canvas.width / 2, canvas.height / 2 + 40);
  }

  // 타겟 위치 분산 생성
  function generatePosition() {
    const pad = RADIUS + 15;
    let x, y, overlap;
    let attempts = 0;

    do {
      overlap = false;
      x = Math.random() * (canvas.width - pad * 2) + pad;
      y = Math.random() * (canvas.height - pad * 2) + pad;

      for (let t of targets) {
        if (Math.hypot(x - t.x, y - t.y) < RADIUS * 3.5) {
          overlap = true;
          break;
        }
      }
      attempts++;
    } while (overlap && attempts < 100);

    return { x, y };
  }

  // 파란색 3D 구 렌더링
  function drawSphere(x, y, r) {
    ctx.save();
    ctx.beginPath();
    ctx.arc(x, y, r, 0, Math.PI * 2);

    const gradient = ctx.createRadialGradient(
      x - r * 0.35, y - r * 0.35, r * 0.05,
      x, y, r
    );
    gradient.addColorStop(0, '#a5d8ff');
    gradient.addColorStop(0.3, '#339af0');
    gradient.addColorStop(0.8, '#1c7ed6');
    gradient.addColorStop(1, '#1864ab');

    ctx.fillStyle = gradient;
    ctx.fill();

    ctx.lineWidth = 1.5;
    ctx.strokeStyle = '#1864ab';
    ctx.stroke();
    ctx.restore();
  }

  function renderGame() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    for (let t of targets) {
      drawSphere(t.x, t.y, RADIUS);
    }
  }

  function startGame() {
    state = "PLAYING";
    canvas.style.cursor = "crosshair";
    headerBar.style.visibility = "visible";

    score = 0;
    totalClicks = 0;
    hits = 0;
    timeLeft = 30;
    targets = [];

    for (let i = 0; i < TARGET_COUNT; i++) {
      targets.push(generatePosition());
    }

    updateHeader();
    renderGame();

    timerInterval = setInterval(() => {
      timeLeft--;
      document.getElementById("timer").innerText = timeLeft;

      if (timeLeft <= 0) {
        endGame();
      }
    }, 1000);
  }

  // 마우스 클릭 판정
  canvas.addEventListener("mousedown", (e) => {
    if (state !== "PLAYING") return;

    totalClicks++;
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;

    const clickX = (e.clientX - rect.left) * scaleX;
    const clickY = (e.clientY - rect.top) * scaleY;

    let hitIndex = -1;
    for (let i = 0; i < targets.length; i++) {
      const dist = Math.hypot(clickX - targets[i].x, clickY - targets[i].y);
      if (dist <= RADIUS) {
        hitIndex = i;
        break;
      }
    }

    if (hitIndex !== -1) {
      hits++;
      score += 100;
      targets.splice(hitIndex, 1);
      targets.push(generatePosition());
    }

    updateHeader();
    renderGame();
  });

  function updateHeader() {
    document.getElementById("score").innerText = score;
    const acc = totalClicks > 0 ? ((hits / totalClicks) * 100).toFixed(1) : 100;
    document.getElementById("accuracy").innerText = `${acc}%`;
  }

  function endGame() {
    clearInterval(timerInterval);
    state = "RESULT";
    canvas.style.cursor = "default";
    headerBar.style.visibility = "hidden";

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    ctx.fillStyle = "#111111";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";

    ctx.font = "900 64px 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif";
    ctx.fillText("훈련 완료!", canvas.width / 2, canvas.height / 2 - 90);

    const acc = totalClicks > 0 ? ((hits / totalClicks) * 100).toFixed(1) : 0;
    ctx.font = "700 26px 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif";
    ctx.fillStyle = "#333333";
    ctx.fillText(`최종 점수: ${score}점   |   정확도: ${acc}%`, canvas.width / 2, canvas.height / 2 - 35);

    btn.innerText = "다시 시작하기";
    btn.style.top = "60%";
    btn.style.display = "block";
  }
</script>
</body>
</html>
"""

# 상단 여백을 고려해 iframe 전체 높이를 800px로 지정
components.html(gridshot_html, height=800)
