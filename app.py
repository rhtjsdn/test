import streamlit as st
import streamlit.components.v1 as components

# 와이드 화면 레이아웃
st.set_page_config(page_title="그리드샷 에임 트레이너", layout="wide")

gridshot_html = """
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<!-- 폭죽 효과 라이브러리 -->
<script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>

<style>
  * {
    box-sizing: border-box;
    user-select: none;
  }
  body {
    margin: 0;
    padding: 0;
    background-color: #ffffff;
    color: #111111;
    /* 몽글몽글하고 둥근 폰트 스타일 (시스템 폰트 폴백 적용) */
    font-family: "Apple SD Gothic Neo", "Malgun Gothic", "Nanum Gothic", sans-serif;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;
    width: 100vw;
    height: 100vh;
    overflow: hidden;
  }

  /* 1. 시작 화면 */
  #intro-screen {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 75vh;
  }

  .bubble-btn {
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
  }
  .bubble-btn:hover {
    background-color: #f7f7f7;
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.12);
  }
  .bubble-btn:active {
    transform: translateY(1px);
  }

  /* 2. 환영 화면 (흰색 박스 및 테두리 완전히 제거) */
  #welcome-screen {
    display: none;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 75vh;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    background: transparent !important;
    animation: fadeIn 0.4s ease-out forwards;
  }

  .welcome-title {
    font-size: 68px;
    font-weight: 900;
    color: #111111;
    margin: 0;
    line-height: 1.2;
    letter-spacing: -1px;
  }
  .welcome-sub {
    font-size: 22px;
    font-weight: 600;
    color: #666666;
    margin-top: 15px;
  }

  /* 3. 게임 화면 */
  #game-screen {
    display: none;
    flex-direction: column;
    align-items: center;
    width: 98%;
    max-width: 1300px;
    margin: 10px auto;
  }

  .scoreboard {
    display: flex;
    gap: 50px;
    font-size: 26px;
    font-weight: 800;
    margin-bottom: 12px;
    color: #111111;
  }

  .canvas-wrapper {
    position: relative;
    width: 100%;
    display: flex;
    justify-content: center;
  }

  /* 훈련장 테두리 */
  canvas {
    width: 100%;
    max-width: 1280px;
    height: 680px;
    border: 3.5px solid #111111;
    border-radius: 20px;
    background-color: #ffffff;
    cursor: crosshair;
    box-shadow: 0 10px 30px rgba(0,0,0,0.06);
    display: block;
  }

  /* 결과 및 재시작 레이어 */
  #result-overlay {
    display: none;
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    border-radius: 20px;
    background-color: rgba(255, 255, 255, 0.94);
    flex-direction: column;
    align-items: center;
    justify-content: center;
    animation: fadeIn 0.3s ease-out forwards;
  }

  .result-title {
    font-size: 64px;
    font-weight: 900;
    margin: 0;
    line-height: 1.2;
  }
  .result-desc {
    font-size: 24px;
    font-weight: 700;
    color: #333333;
    margin: 12px 0 28px 0;
  }

  @keyframes fadeIn {
    from { opacity: 0; transform: scale(0.96); }
    to { opacity: 1; transform: scale(1); }
  }
</style>
</head>
<body>

  <!-- 1. 시작 화면 -->
  <div id="intro-screen">
    <button class="bubble-btn" onclick="handleEnter()">들어가기</button>
  </div>

  <!-- 2. 환영 화면 (텍스트만 깔끔하게 노출) -->
  <div id="welcome-screen">
    <div class="welcome-title">환영합니다!</div>
    <div class="welcome-sub">잠시 후 그리드샷 훈련이 시작됩니다...</div>
  </div>

  <!-- 3. 게임 화면 -->
  <div id="game-screen">
    <div class="scoreboard">
      <div>남은 시간: <span id="timer">30</span>초</div>
      <div>점수: <span id="score">0</span></div>
      <div>정확도: <span id="accuracy">100%</span></div>
    </div>
    
    <div class="canvas-wrapper">
      <canvas id="gridCanvas" width="1280" height="680"></canvas>

      <div id="result-overlay">
        <div class="result-title">훈련 종료!</div>
        <div class="result-desc" id="final-stats">점수: 0 | 정확도: 0%</div>
        <button class="bubble-btn" onclick="restartGame()">다시 시작하기</button>
      </div>
    </div>
  </div>

<script>
  const introScreen = document.getElementById("intro-screen");
  const welcomeScreen = document.getElementById("welcome-screen");
  const gameScreen = document.getElementById("game-screen");
  const resultOverlay = document.getElementById("result-overlay");

  const canvas = document.getElementById("gridCanvas");
  const ctx = canvas.getContext("2d");

  const TARGET_COUNT = 3;
  const RADIUS = 28;
  let targets = [];
  let score = 0;
  let totalClicks = 0;
  let hits = 0;
  let timeLeft = 30;
  let isPlaying = false;
  let gameInterval = null;

  function handleEnter() {
    introScreen.style.display = "none";
    welcomeScreen.style.display = "flex";

    // 자연스러운 폭죽 효과
    confetti({
      particleCount: 90,
      spread: 80,
      origin: { y: 0.6 }
    });

    // 2초 뒤 바로 그리드샷 진입
    setTimeout(() => {
      welcomeScreen.style.display = "none";
      gameScreen.style.display = "flex";
      startGame();
    }, 2000);
  }

  function generatePosition() {
    const padX = RADIUS + 15;
    const padY = RADIUS + 15;
    let x, y, overlap;
    let attempts = 0;

    do {
      overlap = false;
      x = Math.random() * (canvas.width - padX * 2) + padX;
      y = Math.random() * (canvas.height - padY * 2) + padY;

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

  function render() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    if (!isPlaying) return;

    for (let t of targets) {
      drawSphere(t.x, t.y, RADIUS);
    }
  }

  function startGame() {
    resultOverlay.style.display = "none";
    isPlaying = true;
    score = 0;
    totalClicks = 0;
    hits = 0;
    timeLeft = 30;
    targets = [];

    for (let i = 0; i < TARGET_COUNT; i++) {
      targets.push(generatePosition());
    }

    updateUI();
    render();

    gameInterval = setInterval(() => {
      timeLeft--;
      document.getElementById("timer").innerText = timeLeft;

      if (timeLeft <= 0) {
        endGame();
      }
    }, 1000);
  }

  function restartGame() {
    clearInterval(gameInterval);
    startGame();
  }

  canvas.addEventListener("mousedown", (e) => {
    if (!isPlaying) return;

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

    updateUI();
    render();
  });

  function updateUI() {
    document.getElementById("score").innerText = score;
    const acc = totalClicks > 0 ? ((hits / totalClicks) * 100).toFixed(1) : 100;
    document.getElementById("accuracy").innerText = `${acc}%`;
  }

  function endGame() {
    clearInterval(gameInterval);
    isPlaying = false;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const acc = totalClicks > 0 ? ((hits / totalClicks) * 100).toFixed(1) : 0;
    document.getElementById("final-stats").innerText = `최종 점수: ${score}점  |  정확도: ${acc}%`;
    resultOverlay.style.display = "flex";
  }
</script>
</body>
</html>
"""

components.html(gridshot_html, height=820)
