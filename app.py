import streamlit as st
import streamlit.components.v1 as components

# 페이지 설정
st.set_page_config(page_title="그리드샷 에임 트레이너", layout="centered")

# HTML/JS/CSS 통합 컴포넌트
gridshot_html = """
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<!-- 몽글몽글한 느낌의 폰트 (동글 & 고운도둠) 로드 -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Dongle:wght@700&family=Gowun+Dodum&display=swap" rel="stylesheet">
<!-- 폭죽 효과 라이브러리 (canvas-confetti) -->
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
    font-family: 'Gowun Dodum', sans-serif;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 600px;
    overflow: hidden;
  }

  /* 시작 화면 스타일 */
  #intro-screen {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 20px;
  }

  .start-btn {
    font-family: 'Dongle', sans-serif;
    font-size: 38px;
    line-height: 1;
    background-color: #ffffff;
    color: #111111;
    border: 3px solid #111111;
    border-radius: 40px;
    padding: 10px 40px;
    cursor: pointer;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    transition: all 0.2s ease-in-out;
  }
  .start-btn:hover {
    background-color: #f7f7f7;
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.12);
  }
  .start-btn:active {
    transform: translateY(1px);
  }

  /* 환영 화면 스타일 */
  #welcome-screen {
    display: none;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    animation: fadeIn 0.6s ease-out forwards;
  }

  .welcome-title {
    font-family: 'Dongle', sans-serif;
    font-size: 72px;
    font-weight: 700;
    color: #111111;
    margin: 0;
    line-height: 1;
  }
  .welcome-sub {
    font-size: 20px;
    color: #555555;
    margin-top: 10px;
  }

  /* 게임 화면 스타일 */
  #game-screen {
    display: none;
    flex-direction: column;
    align-items: center;
    width: 100%;
  }

  .scoreboard {
    display: flex;
    gap: 30px;
    font-size: 22px;
    font-weight: bold;
    margin-bottom: 12px;
    color: #111111;
  }

  canvas {
    border: 3px solid #111111;
    border-radius: 24px;
    background-color: #ffffff;
    cursor: crosshair;
    box-shadow: 0 8px 30px rgba(0,0,0,0.06);
  }

  @keyframes fadeIn {
    from { opacity: 0; transform: scale(0.92); }
    to { opacity: 1; transform: scale(1); }
  }
</style>
</head>
<body>

  <!-- 1. 처음 화면: 들어가기 버튼 -->
  <div id="intro-screen">
    <button class="start-btn" onclick="handleEnter()">들어가기</button>
  </div>

  <!-- 2. 환영 화면: 환영합니다 & 폭죽 -->
  <div id="welcome-screen">
    <div class="welcome-title">환영합니다!</div>
    <div class="welcome-sub">잠시 후 그리드샷 훈련이 시작됩니다...</div>
  </div>

  <!-- 3. 그리드샷 게임 화면 -->
  <div id="game-screen">
    <div class="scoreboard">
      <div>남은 시간: <span id="timer">30</span>초</div>
      <div>점수: <span id="score">0</span></div>
      <div>정확도: <span id="accuracy">100%</span></div>
    </div>
    <canvas id="gridCanvas" width="650" height="450"></canvas>
  </div>

<script>
  const introScreen = document.getElementById("intro-screen");
  const welcomeScreen = document.getElementById("welcome-screen");
  const gameScreen = document.getElementById("game-screen");

  const canvas = document.getElementById("gridCanvas");
  const ctx = canvas.getContext("2d");

  // 그리드샷 설정
  const TARGET_COUNT = 3;       // 항상 유지되는 타겟 수
  const RADIUS = 28;            // 타겟 구 크기
  let targets = [];
  let score = 0;
  let totalClicks = 0;
  let hits = 0;
  let timeLeft = 30;
  let isPlaying = false;
  let gameInterval = null;

  // 들어가기 클릭 시
  function handleEnter() {
    introScreen.style.display = "none";
    welcomeScreen.style.display = "flex";

    // 자연스러운 폭죽 효과
    confetti({
      particleCount: 80,
      spread: 70,
      origin: { y: 0.6 }
    });

    // 2초 뒤 그리드샷 시작
    setTimeout(() => {
      welcomeScreen.style.display = "none";
      gameScreen.style.display = "flex";
      startGame();
    }, 2000);
  }

  // 타겟 위치 겹침 방지 생성 함수
  function generatePosition() {
    const pad = RADIUS + 20;
    let x, y, overlap;
    let attempts = 0;

    do {
      overlap = false;
      x = Math.random() * (canvas.width - pad * 2) + pad;
      y = Math.random() * (canvas.height - pad * 2) + pad;

      for (let t of targets) {
        if (Math.hypot(x - t.x, y - t.y) < RADIUS * 2.5) {
          overlap = true;
          break;
        }
      }
      attempts++;
    } while (overlap && attempts < 100);

    return { x, y };
  }

  // 입체적인 파란색 구 그리기
  function drawSphere(x, y, r) {
    ctx.save();
    ctx.beginPath();
    ctx.arc(x, y, r, 0, Math.PI * 2);

    // 하이라이트가 들어간 방사형 그래디언트 (3D 구 질감)
    const gradient = ctx.createRadialGradient(
      x - r * 0.35, y - r * 0.35, r * 0.05,
      x, y, r
    );
    gradient.addColorStop(0, '#a5d8ff');   // 반사광 (밝은 파랑)
    gradient.addColorStop(0.3, '#339af0');  // 기본 밝은 파랑
    gradient.addColorStop(0.8, '#1c7ed6');  // 중간 파랑
    gradient.addColorStop(1, '#1864ab');    // 외곽 음영 (어두운 파랑)

    ctx.fillStyle = gradient;
    ctx.fill();

    // 부드러운 외곽선
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
    isPlaying = true;
    score = 0;
    totalClicks = 0;
    hits = 0;
    timeLeft = 30;
    targets = [];

    // 타겟 3개 초기화
    for (let i = 0; i < TARGET_COUNT; i++) {
      targets.push(generatePosition());
    }

    updateUI();
    render();

    // 1초 타이머
    gameInterval = setInterval(() => {
      timeLeft--;
      document.getElementById("timer").innerText = timeLeft;

      if (timeLeft <= 0) {
        endGame();
      }
    }, 1000);
  }

  // 클릭 판정
  canvas.addEventListener("mousedown", (e) => {
    if (!isPlaying) return;

    totalClicks++;
    const rect = canvas.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const clickY = e.clientY - rect.top;

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
      // 맞은 타겟은 새 위치로 재생성 (그리드샷 규칙)
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

    ctx.font = "32px 'Gowun Dodum'";
    ctx.fillStyle = "#111111";
    ctx.textAlign = "center";
    ctx.fillText("훈련 완료!", canvas.width / 2, canvas.height / 2 - 20);

    ctx.font = "20px 'Gowun Dodum'";
    const acc = totalClicks > 0 ? ((hits / totalClicks) * 100).toFixed(1) : 0;
    ctx.fillText(`최종 점수: ${score}점 | 정확도: ${acc}%`, canvas.width / 2, canvas.height / 2 + 25);
  }
</script>
</body>
</html>
"""

# 컴포넌트 렌더링
components.html(gridshot_html, height=620)
