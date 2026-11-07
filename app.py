import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="에임 트레이너 (그리드샷 & 트래킹)", layout="wide")

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

aim_html = """
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
    padding-top: 25px;
    overflow: hidden;
  }

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

  .stage-container {
    position: relative;
    width: 1280px;
    height: 640px;
  }

  #mainCanvas {
    display: block;
    width: 1280px;
    height: 640px;
    background-color: #ffffff;
    border: 3.5px solid #111111;
    border-radius: 20px;
    cursor: default;
  }

  /* 버튼 공통 스타일 */
  .bubble-btn {
    font-size: 30px;
    font-weight: 800;
    line-height: 1;
    background-color: #ffffff;
    color: #111111;
    border: 3.5px solid #111111;
    border-radius: 40px;
    padding: 16px 46px;
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

  /* 단일 버튼 (들어가기) */
  #actionBtn {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: 34px;
    padding: 18px 54px;
    z-index: 10;
  }

  /* 모드 선택 컨테이너 */
  #modeSelectGroup {
    display: none;
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    gap: 30px;
    z-index: 10;
  }

  /* 결과창 재시작 버튼 그룹 */
  #resultGroup {
    display: none;
    position: absolute;
    top: 62%;
    left: 50%;
    transform: translate(-50%, -50%);
    gap: 20px;
    z-index: 10;
  }
</style>
</head>
<body>

  <!-- 상단 점수판 -->
  <div id="header-bar">
    <div>남은 시간: <span id="timer">30</span>초</div>
    <div>점수: <span id="score">0</span></div>
    <div>정확도: <span id="accuracy">100%</span></div>
  </div>

  <!-- 메인 훈련장 캔버스 및 제어 버튼들 -->
  <div class="stage-container">
    <canvas id="mainCanvas" width="1280" height="640"></canvas>
    
    <!-- 1. 처음 들어가기 버튼 -->
    <button id="actionBtn" class="bubble-btn" onclick="handleIntro()">들어가기</button>

    <!-- 2. 모드 선택 버튼 그룹 -->
    <div id="modeSelectGroup">
      <button class="bubble-btn" onclick="chooseMode('gridshot')">🎯 그리드샷</button>
      <button class="bubble-btn" onclick="chooseMode('tracking')">⚡ 트래킹</button>
    </div>

    <!-- 3. 결과 화면 버튼 그룹 -->
    <div id="resultGroup">
      <button class="bubble-btn" onclick="restartCurrentMode()">다시 하기</button>
      <button class="bubble-btn" onclick="showModeSelection()">모드 변경</button>
    </div>
  </div>

<script>
  const canvas = document.getElementById("mainCanvas");
  const ctx = canvas.getContext("2d");
  const actionBtn = document.getElementById("actionBtn");
  const modeSelectGroup = document.getElementById("modeSelectGroup");
  const resultGroup = document.getElementById("resultGroup");
  const headerBar = document.getElementById("header-bar");

  let state = "IDLE"; // IDLE, WELCOME, SELECT_MODE, PLAYING, RESULT
  let currentMode = "gridshot";

  // 기본 세팅
  const RADIUS = 28;
  let score = 0;
  let timeLeft = 30;
  let timerInterval = null;
  let animFrameId = null;

  // 그리드샷 전용 변수
  let targets = [];
  let totalClicks = 0;
  let hits = 0;

  // 트래킹 전용 변수
  let trackingTarget = { x: 0, y: 0, vx: 0, vy: 0 };
  let mousePos = { x: -100, y: -100 };
  let trackingTicks = 0;
  let onTargetTicks = 0;

  // 1. 들어가기 클릭
  function handleIntro() {
    actionBtn.style.display = "none";
    state = "WELCOME";
    drawWelcomeScreen();

    confetti({
      particleCount: 100,
      spread: 85,
      origin: { y: 0.6 }
    });

    setTimeout(() => {
      showModeSelection();
    }, 2000);
  }

  // 2. 환영 화면 캔버스 렌더링
  function drawWelcomeScreen() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = "#111111";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";

    ctx.font = "900 68px 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif";
    ctx.fillText("환영합니다!", canvas.width / 2, canvas.height / 2 - 25);

    ctx.font = "600 24px 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif";
    ctx.fillStyle = "#666666";
    ctx.fillText("훈련 모드를 준비하고 있습니다...", canvas.width / 2, canvas.height / 2 + 40);
  }

  // 3. 모드 선택 화면 띄우기
  function showModeSelection() {
    state = "SELECT_MODE";
    resultGroup.style.display = "none";
    headerBar.style.visibility = "hidden";
    canvas.style.cursor = "default";

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = "#111111";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";

    ctx.font = "900 54px 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif";
    ctx.fillText("훈련 모드를 선택하세요", canvas.width / 2, canvas.height / 2 - 120);

    modeSelectGroup.style.display = "flex";
  }

  // 4. 모드 선택 후 시작
  function chooseMode(mode) {
    currentMode = mode;
    modeSelectGroup.style.display = "none";
    startGame();
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

  // 그리드샷 타겟 생성 (화면 끝단까지 분산)
  function generateGridshotPosition() {
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

  // 게임 시작 로직
  function startGame() {
    state = "PLAYING";
    resultGroup.style.display = "none";
    canvas.style.cursor = "crosshair";
    headerBar.style.visibility = "visible";

    score = 0;
    timeLeft = 30;
    updateHeader(0, 100);

    if (currentMode === "gridshot") {
      totalClicks = 0;
      hits = 0;
      targets = [];
      for (let i = 0; i < 3; i++) {
        targets.push(generateGridshotPosition());
      }
      renderGridshot();
    } else {
      // 트래킹 모드 초기화
      trackingTicks = 0;
      onTargetTicks = 0;
      const pad = RADIUS + 40;
      trackingTarget.x = canvas.width / 2;
      trackingTarget.y = canvas.height / 2;
      
      // 이동 속도 및 방향 설정 (부드러운 속도감)
      const angle = Math.random() * Math.PI * 2;
      const speed = 5.0;
      trackingTarget.vx = Math.cos(angle) * speed;
      trackingTarget.vy = Math.sin(angle) * speed;

      runTrackingLoop();
    }

    // 1초 타이머
    timerInterval = setInterval(() => {
      timeLeft--;
      document.getElementById("timer").innerText = timeLeft;

      if (timeLeft <= 0) {
        endGame();
      }
    }, 1000);
  }

  // [그리드샷] 화면 렌더링
  function renderGridshot() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    for (let t of targets) {
      drawSphere(t.x, t.y, RADIUS);
    }
  }

  // [트래킹] 60FPS 실시간 이동 및 추적 루프
  function runTrackingLoop() {
    if (state !== "PLAYING" || currentMode !== "tracking") return;

    // 타겟 이동
    trackingTarget.x += trackingTarget.vx;
    trackingTarget.y += trackingTarget.vy;

    // 벽 충돌 반사 (화면 테두리 안쪽 유지)
    const pad = RADIUS + 10;
    if (trackingTarget.x <= pad) {
      trackingTarget.x = pad;
      trackingTarget.vx *= -1;
    } else if (trackingTarget.x >= canvas.width - pad) {
      trackingTarget.x = canvas.width - pad;
      trackingTarget.vx *= -1;
    }

    if (trackingTarget.y <= pad) {
      trackingTarget.y = pad;
      trackingTarget.vy *= -1;
    } else if (trackingTarget.y >= canvas.height - pad) {
      trackingTarget.y = canvas.height - pad;
      trackingTarget.vy *= -1;
    }

    // 랜덤 방향 전환 (약간의 변칙성 부여)
    if (Math.random() < 0.02) {
      const currentSpeed = Math.hypot(trackingTarget.vx, trackingTarget.vy);
      const newAngle = Math.random() * Math.PI * 2;
      trackingTarget.vx = Math.cos(newAngle) * currentSpeed;
      trackingTarget.vy = Math.sin(newAngle) * currentSpeed;
    }

    // 트래킹 판정 (마우스가 타겟 구 안에 있는지)
    trackingTicks++;
    const dist = Math.hypot(mousePos.x - trackingTarget.x, mousePos.y - trackingTarget.y);
    if (dist <= RADIUS) {
      onTargetTicks++;
      score += 10; // 머무는 시간 비례 점수 상승
    }

    // 헤더 점수 & 정확도 갱신
    const acc = trackingTicks > 0 ? ((onTargetTicks / trackingTicks) * 100).toFixed(1) : 100;
    updateHeader(score, acc);

    // 타겟 그리기
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    drawSphere(trackingTarget.x, trackingTarget.y, RADIUS);

    animFrameId = requestAnimationFrame(runTrackingLoop);
  }

  // 마우스 이동 추적 (트래킹 모드용)
  canvas.addEventListener("mousemove", (e) => {
    if (state !== "PLAYING") return;
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;

    mousePos.x = (e.clientX - rect.left) * scaleX;
    mousePos.y = (e.clientY - rect.top) * scaleY;
  });

  // 클릭 판정 (그리드샷 전용)
  canvas.addEventListener("mousedown", (e) => {
    if (state !== "PLAYING" || currentMode !== "gridshot") return;

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
      targets.push(generateGridshotPosition());
    }

    const acc = totalClicks > 0 ? ((hits / totalClicks) * 100).toFixed(1) : 100;
    updateHeader(score, acc);
    renderGridshot();
  });

  function updateHeader(s, a) {
    document.getElementById("score").innerText = s;
    document.getElementById("accuracy").innerText = `${a}%`;
  }

  // 게임 종료
  function endGame() {
    clearInterval(timerInterval);
    if (animFrameId) cancelAnimationFrame(animFrameId);

    state = "RESULT";
    canvas.style.cursor = "default";
    headerBar.style.visibility = "hidden";

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = "#111111";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";

    ctx.font = "900 64px 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif";
    const modeName = currentMode === "gridshot" ? "그리드샷" : "트래킹";
    ctx.fillText(`${modeName} 훈련 완료!`, canvas.width / 2, canvas.height / 2 - 90);

    let finalAcc = 0;
    if (currentMode === "gridshot") {
      finalAcc = totalClicks > 0 ? ((hits / totalClicks) * 100).toFixed(1) : 0;
    } else {
      finalAcc = trackingTicks > 0 ? ((onTargetTicks / trackingTicks) * 100).toFixed(1) : 0;
    }

    ctx.font = "700 26px 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif";
    ctx.fillStyle = "#333333";
    ctx.fillText(`최종 점수: ${score}점   |   정확도(추적률): ${finalAcc}%`, canvas.width / 2, canvas.height / 2 - 35);

    resultGroup.style.display = "flex";
  }

  function restartCurrentMode() {
    resultGroup.style.display = "none";
    startGame();
  }
</script>
</body>
</html>
"""

components.html(aim_html, height=800)
