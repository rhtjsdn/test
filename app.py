import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="그리드샷 에임 트레이너", layout="wide")

# Streamlit 자체 iframe 테두리 및 여백 완전 제거
st.markdown("""
<style>
    iframe {
        border: none !important;
        outline: none !important;
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
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
    outline: none !important; /* 모든 포커스 테두리 강제 제거 */
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
    overflow: hidden;
  }

  /* 상단 점수판 */
  #header-bar {
    width: 1280px;
    height: 48px;
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 60px;
    font-size: 26px;
    font-weight: 800;
    color: #111111;
    visibility: hidden; /* 게임 중에만 표시 */
    margin-bottom: 8px;
  }

  /* 메인 캔버스 영역 */
  .stage-container {
    position: relative;
    width: 1280px;
    height: 680px;
  }

  canvas {
    display: block;
    width: 1280px;
    height: 680px;
    background-color: #ffffff;
    border: 3.5px solid #111111;
    border-radius: 20px;
    cursor: default;
  }

  /* 중앙 시작/재시작 버튼 (몽글몽글 스타일) */
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

  <div id="header-bar">
    <div>남은 시간: <span id="timer">30</span>초</div>
    <div>점수: <span id="score">0</span></div>
    <div>정확도: <span id="accuracy">100%</span></div>
  </div>

  <div class="stage-container">
    <canvas id="mainCanvas" width="1280" height="680"></canvas>
    <button id="actionBtn" class="center-btn" onclick="handleClick()">들어가기</button>
  </div>

<script>
  const canvas = document.getElementById("mainCanvas");
  const ctx = canvas.getContext("2d");
  const btn = document.getElementById("actionBtn");
  const headerBar = document.getElementById("header-bar");

  // 게임 상태: 'IDLE' -> 'WELCOME' -> 'PLAYING' -> 'RESULT'
  let state = "IDLE";

  const TARGET_COUNT = 3;
  const RADIUS = 28;
  let targets = [];
  let score = 0;
  let totalClicks = 0;
  let hits = 0;
  let timeLeft = 30;
  let timerInterval = null;

  // 진입 / 재시작 클릭 핸들러
  function handleClick() {
    btn.style.display = "none";

    // 1. 환영 단계로 전환
    state = "WELCOME";
    drawWelcomeScreen();

    // 폭죽 발사
    confetti({
      particleCount: 100,
      spread: 85,
      origin: { y: 0.6 }
    });

    // 2초 카운트 후 칼같이 게임 화면으로 전환
    setTimeout(() => {
      startGame();
    }, 2000);
  }

  // 캔버스 자체에 '환영합니다!' 텍스트 렌더링 (어떤 HTML 태그도 겹치지 않음)
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

  // 타겟 생성 (경계선 끝단까지 넓게 배치)
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

  // 게임 시작
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

  // 타겟 클릭 판정
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

  // 게임 종료 및 재시작 준비
  function endGame() {
    clearInterval(timerInterval);
    state = "RESULT";
    canvas.style.cursor = "default";
    headerBar.style.visibility = "hidden";

    // 결과 화면 캔버스 드로잉
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

    // 다시 시작 버튼 노출
    btn.innerText = "다시 시작하기";
    btn.style.top = "60%";
    btn.style.display = "block";
  }
</script>
</body>
</html>
"""

components.html(gridshot_html, height=760)
