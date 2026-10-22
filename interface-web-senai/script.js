/**
 * SENAI - Experiência Touchless
 * Paleta Oficial Totem SENAI (#E30613, Branco, Ondas Fluidas)
 * Áudio Sintetizado Web Audio API (Zero Dependências Externas)
 * 4 Áreas: Área de Testes (Playground), Desafios da Mão, Flip Bird, Fruit Ninja
 */

document.addEventListener("DOMContentLoaded", () => {
  // ===================================================================
  // 1. SINTETIZADOR DE ÁUDIO WEB (WEB AUDIO API - ZERO ARQUIVOS EXTERNOS)
  // ===================================================================
  let audioCtx = null;
  let isMuted = false;

  function initAudio() {
    if (!audioCtx) {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (AudioContext) {
        audioCtx = new AudioContext();
      }
    }
    if (audioCtx && audioCtx.state === "suspended") {
      audioCtx.resume();
    }
  }

  const Sound = {
    hover() {
      if (isMuted) return;
      initAudio();
      if (!audioCtx) return;
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.type = "sine";
      osc.frequency.setValueAtTime(1400, audioCtx.currentTime);
      gain.gain.setValueAtTime(0.02, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + 0.04);
      osc.connect(gain);
      gain.connect(audioCtx.destination);
      osc.start();
      osc.stop(audioCtx.currentTime + 0.04);
    },

    click() {
      if (isMuted) return;
      initAudio();
      if (!audioCtx) return;
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.type = "triangle";
      osc.frequency.setValueAtTime(700, audioCtx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(1200, audioCtx.currentTime + 0.06);
      gain.gain.setValueAtTime(0.12, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.07);
      osc.connect(gain);
      gain.connect(audioCtx.destination);
      osc.start();
      osc.stop(audioCtx.currentTime + 0.07);
    },

    flap() {
      if (isMuted) return;
      initAudio();
      if (!audioCtx) return;
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.type = "sine";
      osc.frequency.setValueAtTime(450, audioCtx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(950, audioCtx.currentTime + 0.1);
      gain.gain.setValueAtTime(0.15, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.11);
      osc.connect(gain);
      gain.connect(audioCtx.destination);
      osc.start();
      osc.stop(audioCtx.currentTime + 0.11);
    },

    point() {
      if (isMuted) return;
      initAudio();
      if (!audioCtx) return;
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.type = "sine";
      osc.frequency.setValueAtTime(1200, audioCtx.currentTime);
      osc.frequency.setValueAtTime(1600, audioCtx.currentTime + 0.08);
      gain.gain.setValueAtTime(0.14, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.25);
      osc.connect(gain);
      gain.connect(audioCtx.destination);
      osc.start();
      osc.stop(audioCtx.currentTime + 0.25);
    },

    hit() {
      if (isMuted) return;
      initAudio();
      if (!audioCtx) return;
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.type = "square";
      osc.frequency.setValueAtTime(180, audioCtx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(60, audioCtx.currentTime + 0.18);
      gain.gain.setValueAtTime(0.2, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.18);
      osc.connect(gain);
      gain.connect(audioCtx.destination);
      osc.start();
      osc.stop(audioCtx.currentTime + 0.18);
    },

    slice() {
      if (isMuted) return;
      initAudio();
      if (!audioCtx) return;
      // Som de corte rápido (ruído branco filtrado)
      const bufferSize = audioCtx.sampleRate * 0.08;
      const buffer = audioCtx.createBuffer(1, bufferSize, audioCtx.sampleRate);
      const data = buffer.getChannelData(0);
      for (let i = 0; i < bufferSize; i++) {
        data[i] = Math.random() * 2 - 1;
      }
      const noise = audioCtx.createBufferSource();
      noise.buffer = buffer;
      const filter = audioCtx.createBiquadFilter();
      filter.type = "bandpass";
      filter.frequency.setValueAtTime(2800, audioCtx.currentTime);
      filter.frequency.exponentialRampToValueAtTime(800, audioCtx.currentTime + 0.08);
      const gain = audioCtx.createGain();
      gain.gain.setValueAtTime(0.25, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.08);
      noise.connect(filter);
      filter.connect(gain);
      gain.connect(audioCtx.destination);
      noise.start();
    },

    splat() {
      if (isMuted) return;
      initAudio();
      if (!audioCtx) return;
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.type = "sine";
      osc.frequency.setValueAtTime(320, audioCtx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(110, audioCtx.currentTime + 0.12);
      gain.gain.setValueAtTime(0.18, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.12);
      osc.connect(gain);
      gain.connect(audioCtx.destination);
      osc.start();
      osc.stop(audioCtx.currentTime + 0.12);
    },

    victory() {
      if (isMuted) return;
      initAudio();
      if (!audioCtx) return;
      const notes = [523.25, 659.25, 783.99, 1046.50]; // Acorde Maior C E G C
      notes.forEach((freq, idx) => {
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = "sine";
        osc.frequency.setValueAtTime(freq, audioCtx.currentTime + idx * 0.09);
        gain.gain.setValueAtTime(0.15, audioCtx.currentTime + idx * 0.09);
        gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + idx * 0.09 + 0.35);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start(audioCtx.currentTime + idx * 0.09);
        osc.stop(audioCtx.currentTime + idx * 0.09 + 0.35);
      });
    }
  };

  // Botão Mute / Unmute
  const btnToggleSound = document.getElementById("btnToggleSound");
  const soundIcon = document.getElementById("soundIcon");
  btnToggleSound.addEventListener("click", () => {
    isMuted = !isMuted;
    soundIcon.textContent = isMuted ? "🔇" : "🔊";
    if (!isMuted) Sound.click();
  });

  // Botão Fullscreen
  const btnFullscreen = document.getElementById("btnFullscreen");
  btnFullscreen.addEventListener("click", () => {
    Sound.click();
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen().catch(() => {});
    } else {
      if (document.exitFullscreen) document.exitFullscreen();
    }
  });

  // ===================================================================
  // 2. FUNDO BRANCO COM ONDAS VERMELHAS ANIMADAS (CANVAS TOTEM SENAI)
  // ===================================================================
  const waveCanvas = document.getElementById("waveCanvas");
  const waveCtx = waveCanvas.getContext("2d");
  let wWidth, wHeight;

  function resizeWaveCanvas() {
    wWidth = window.innerWidth;
    wHeight = window.innerHeight;
    waveCanvas.width = wWidth;
    waveCanvas.height = wHeight;
  }
  window.addEventListener("resize", resizeWaveCanvas);
  resizeWaveCanvas();

  let waveStep = 0;
  const topWaveLayers = [
    { fill: "rgba(227, 6, 19, 0.04)", length: 0.0022, amplitude: 35, speed: -0.010, offset: 1.1, baseY: 0.16 },
    { fill: "rgba(227, 6, 19, 0.08)", length: 0.0032, amplitude: 28, speed: 0.012, offset: 3.3, baseY: 0.12 },
    { fill: "rgba(227, 6, 19, 0.20)", length: 0.0028, amplitude: 22, speed: -0.014, offset: 0.7, baseY: 0.08 },
    { fill: "#E30613",                length: 0.0035, amplitude: 14, speed: -0.015, offset: 4.2, baseY: 0.03 }
  ];

  const bottomWaveLayers = [
    { fill: "rgba(227, 6, 19, 0.04)", length: 0.0020, amplitude: 55, speed: 0.010, offset: 0, baseY: 0.72 },
    { fill: "rgba(227, 6, 19, 0.08)", length: 0.0030, amplitude: 45, speed: -0.013, offset: 2.1, baseY: 0.80 },
    { fill: "rgba(227, 6, 19, 0.18)", length: 0.0025, amplitude: 35, speed: 0.015, offset: 4.3, baseY: 0.86 },
    { fill: "#E30613",                length: 0.0030, amplitude: 20, speed: 0.014, offset: 3.2, baseY: 0.94 }
  ];

  function drawSineWaves(layers, isTop) {
    for (let i = 0; i < layers.length; i++) {
      const layer = layers[i];
      waveCtx.fillStyle = layer.fill;
      waveCtx.beginPath();
      const basePos = wHeight * layer.baseY;

      if (isTop) {
        waveCtx.moveTo(0, 0);
        waveCtx.lineTo(0, basePos);
        for (let x = 0; x <= wWidth; x += 15) {
          const y = basePos + Math.sin(x * layer.length + waveStep * layer.speed + layer.offset) * layer.amplitude;
          waveCtx.lineTo(x, y);
        }
        waveCtx.lineTo(wWidth, 0);
      } else {
        waveCtx.moveTo(0, wHeight);
        waveCtx.lineTo(0, basePos);
        for (let x = 0; x <= wWidth; x += 15) {
          const y = basePos + Math.sin(x * layer.length + waveStep * layer.speed + layer.offset) * layer.amplitude;
          waveCtx.lineTo(x, y);
        }
        waveCtx.lineTo(wWidth, wHeight);
      }
      waveCtx.closePath();
      waveCtx.fill();
    }
  }

  function renderWaveCanvas() {
    waveCtx.clearRect(0, 0, wWidth, wHeight);
    drawSineWaves(topWaveLayers, true);
    drawSineWaves(bottomWaveLayers, false);
    waveStep++;
    requestAnimationFrame(renderWaveCanvas);
  }
  renderWaveCanvas();

  // ===================================================================
  // 3. NAVEGAÇÃO ENTRE ABAS
  // ===================================================================
  const tabBtns = document.querySelectorAll(".tab-btn");
  const tabPanels = document.querySelectorAll(".tab-panel");
  let activeTabName = "playground";

  tabBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      const targetTab = btn.getAttribute("data-tab");
      if (targetTab === activeTabName) return;

      Sound.click();
      tabBtns.forEach(b => b.classList.remove("active"));
      tabPanels.forEach(p => p.classList.remove("active"));

      btn.classList.add("active");
      const targetPanel = document.getElementById(`tab-${targetTab}`);
      if (targetPanel) targetPanel.classList.add("active");

      activeTabName = targetTab;

      // Inicializa ou reajusta jogos ao abrir a aba
      if (targetTab === "challenges") {
        initCurrentChallenge();
      } else if (targetTab === "flappy") {
        resizeFlappyCanvas();
      } else if (targetTab === "fruit") {
        resizeFruitCanvas();
      }
    });
  });

  // ===================================================================
  // 4. ÁREA DE TESTES (PLAYGROUND DO SISTEMA)
  // ===================================================================

  // 4.1 Radar do Cursor
  const radarArea = document.getElementById("radarArea");
  const radarDot = document.getElementById("radarDot");
  const fluidityText = document.getElementById("fluidityText");
  const velocityText = document.getElementById("velocityText");

  let lastCursorX = 0, lastCursorY = 0, lastCursorTime = Date.now();
  let cursorSpeeds = [];

  window.addEventListener("mousemove", (e) => {
    const now = Date.now();
    const dt = (now - lastCursorTime) / 1000;
    if (dt > 0.005) {
      const dx = e.clientX - lastCursorX;
      const dy = e.clientY - lastCursorY;
      const dist = Math.hypot(dx, dy);
      const speed = dist / dt;

      cursorSpeeds.push(speed);
      if (cursorSpeeds.length > 12) cursorSpeeds.shift();

      const avgSpeed = cursorSpeeds.reduce((a, b) => a + b, 0) / cursorSpeeds.length;

      if (avgSpeed < 200) {
        velocityText.textContent = "Suave";
        velocityText.style.color = "#10B981";
      } else if (avgSpeed < 900) {
        velocityText.textContent = "Normal";
        velocityText.style.color = "var(--senai-red)";
      } else {
        velocityText.textContent = "Rápido";
        velocityText.style.color = "#FF2435";
      }

      // Fluidez
      const variance = cursorSpeeds.reduce((acc, val) => acc + Math.pow(val - avgSpeed, 2), 0) / cursorSpeeds.length;
      if (variance < 20000) {
        fluidityText.textContent = "Firme e Estável";
      } else {
        fluidityText.textContent = "Dinâmico";
      }

      lastCursorX = e.clientX;
      lastCursorY = e.clientY;
      lastCursorTime = now;
    }

    // Posição no Radar Virtual
    const rect = radarArea.getBoundingClientRect();
    const relX = ((e.clientX - rect.left) / rect.width) * 140;
    const relY = ((e.clientY - rect.top) / rect.height) * 140;
    const clampedX = Math.max(10, Math.min(130, relX));
    const clampedY = Math.max(10, Math.min(130, relY));

    radarDot.style.left = `${clampedX}px`;
    radarDot.style.top = `${clampedY}px`;
  });

  // 4.2 Botões Táteis com Efeito Magnético e Dwell Click
  const btnQuickClick = document.getElementById("btnQuickClick");
  const btnDwellClick = document.getElementById("btnDwellClick");
  const dwellBar = document.getElementById("dwellBar");
  const tactileFeedback = document.getElementById("tactileFeedback");

  btnQuickClick.addEventListener("click", () => {
    Sound.click();
    btnQuickClick.classList.add("triggered");
    tactileFeedback.textContent = "✓ Clique Rápido detectado com sucesso!";
    setTimeout(() => btnQuickClick.classList.remove("triggered"), 250);
  });

  // Dwell Click (Segurar 0.5s)
  let dwellTimer = null;
  let dwellStartTime = 0;
  const DWELL_DURATION = 500;

  btnDwellClick.addEventListener("mouseenter", () => {
    Sound.hover();
    dwellStartTime = Date.now();
    dwellBar.style.width = "0%";
    dwellBar.style.transition = "none";

    function updateDwell() {
      const elapsed = Date.now() - dwellStartTime;
      const pct = Math.min(100, (elapsed / DWELL_DURATION) * 100);
      dwellBar.style.width = `${pct}%`;

      if (elapsed >= DWELL_DURATION) {
        btnDwellClick.classList.add("dwell-done");
        Sound.victory();
        tactileFeedback.textContent = "✓ Gesto Dwell (0.5s) confirmado com precisão!";
        setTimeout(() => {
          btnDwellClick.classList.remove("dwell-done");
          dwellBar.style.width = "0%";
        }, 500);
      } else {
        dwellTimer = requestAnimationFrame(updateDwell);
      }
    }
    dwellTimer = requestAnimationFrame(updateDwell);
  });

  btnDwellClick.addEventListener("mouseleave", () => {
    if (dwellTimer) cancelAnimationFrame(dwellTimer);
    dwellBar.style.width = "0%";
  });

  // 4.3 Slider e Toggles
  const testSlider = document.getElementById("testSlider");
  const sliderValText = document.getElementById("sliderValText");
  testSlider.addEventListener("input", (e) => {
    sliderValText.textContent = `${e.target.value}%`;
    Sound.hover();
  });

  // 4.4 Drag and Drop de Peças Industriais
  const dragPieces = document.querySelectorAll(".drag-piece");
  const dropSlots = document.querySelectorAll(".drop-slot");

  dragPieces.forEach(piece => {
    piece.addEventListener("dragstart", (e) => {
      Sound.hover();
      e.dataTransfer.setData("text/plain", piece.getAttribute("data-type"));
      setTimeout(() => piece.style.opacity = "0.4", 0);
    });

    piece.addEventListener("dragend", () => {
      piece.style.opacity = "1";
    });
  });

  dropSlots.forEach(slot => {
    slot.addEventListener("dragover", (e) => {
      e.preventDefault();
      slot.classList.add("slot-active");
    });

    slot.addEventListener("dragleave", () => {
      slot.classList.remove("slot-active");
    });

    slot.addEventListener("drop", (e) => {
      e.preventDefault();
      slot.classList.remove("slot-active");
      const pieceType = e.dataTransfer.getData("text/plain");
      const slotType = slot.getAttribute("data-slot");

      if (pieceType === slotType) {
        Sound.victory();
        const draggedElement = document.querySelector(`.drag-piece[data-type="${pieceType}"]`);
        if (draggedElement) {
          slot.innerHTML = draggedElement.innerHTML + " ✓";
          slot.classList.add("slot-filled");
          draggedElement.style.display = "none";
        }
      } else {
        Sound.hit();
      }
    });
  });

  // 4.5 Lousa de Rabisco Neon Livre
  const freeDrawCanvas = document.getElementById("freeDrawCanvas");
  const freeDrawCtx = freeDrawCanvas.getContext("2d");
  const btnClearCanvas = document.getElementById("btnClearCanvas");
  const colorDots = document.querySelectorAll(".color-dot");
  let isDrawing = false;
  let currentColor = "#E30613";

  function resizeFreeDraw() {
    freeDrawCanvas.width = freeDrawCanvas.parentElement.clientWidth - 44;
    freeDrawCanvas.height = 180;
  }
  window.addEventListener("resize", resizeFreeDraw);
  setTimeout(resizeFreeDraw, 50);

  colorDots.forEach(dot => {
    dot.addEventListener("click", () => {
      Sound.click();
      colorDots.forEach(d => d.classList.remove("active"));
      dot.classList.add("active");
      currentColor = dot.getAttribute("data-color");
    });
  });

  btnClearCanvas.addEventListener("click", () => {
    Sound.click();
    freeDrawCtx.clearRect(0, 0, freeDrawCanvas.width, freeDrawCanvas.height);
  });

  freeDrawCanvas.addEventListener("mousedown", (e) => {
    isDrawing = true;
    const rect = freeDrawCanvas.getBoundingClientRect();
    freeDrawCtx.beginPath();
    freeDrawCtx.moveTo(e.clientX - rect.left, e.clientY - rect.top);
  });

  freeDrawCanvas.addEventListener("mousemove", (e) => {
    if (!isDrawing) return;
    const rect = freeDrawCanvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    freeDrawCtx.strokeStyle = currentColor;
    freeDrawCtx.lineWidth = 3.5;
    freeDrawCtx.lineCap = "round";
    freeDrawCtx.lineJoin = "round";
    freeDrawCtx.lineTo(x, y);
    freeDrawCtx.stroke();
  });

  window.addEventListener("mouseup", () => {
    if (isDrawing) {
      isDrawing = false;
      freeDrawCtx.closePath();
    }
  });

  // ===================================================================
  // 5. DESAFIOS DA MÃO E DO CURSOR
  // ===================================================================
  const challengeCanvas = document.getElementById("challengeCanvas");
  const chalCtx = challengeCanvas.getContext("2d");
  const challengeTabCards = document.querySelectorAll(".challenge-tab-card");
  const currentChallengeTitle = document.getElementById("currentChallengeTitle");
  const currentChallengeInstruction = document.getElementById("currentChallengeInstruction");
  const challengeStatusTag = document.getElementById("challengeStatusTag");
  const challengeWinModal = document.getElementById("challengeWinModal");
  const btnRestartChallenge = document.getElementById("btnRestartChallenge");
  const winTitle = document.getElementById("winTitle");
  const winDesc = document.getElementById("winDesc");

  let currentChallengeIdx = 1;
  let chalAnimationId = null;
  let chalState = {};

  function resizeChallengeCanvas() {
    const parent = challengeCanvas.parentElement;
    challengeCanvas.width = parent.clientWidth;
    challengeCanvas.height = parent.clientHeight;
  }
  window.addEventListener("resize", () => {
    if (activeTabName === "challenges") {
      resizeChallengeCanvas();
      initCurrentChallenge();
    }
  });

  challengeTabCards.forEach(card => {
    card.addEventListener("click", () => {
      Sound.click();
      challengeTabCards.forEach(c => c.classList.remove("active"));
      card.classList.add("active");
      currentChallengeIdx = parseInt(card.getAttribute("data-challenge"));
      initCurrentChallenge();
    });
  });

  btnRestartChallenge.addEventListener("click", () => {
    Sound.click();
    challengeWinModal.classList.remove("active");
    initCurrentChallenge();
  });

  function showChallengeWin(title, desc) {
    Sound.victory();
    winTitle.textContent = title;
    winDesc.textContent = desc;
    challengeWinModal.classList.add("active");
    challengeStatusTag.textContent = "Concluído!";
    challengeStatusTag.style.background = "#10B981";
    challengeStatusTag.style.color = "#FFFFFF";
  }

  function initCurrentChallenge() {
    resizeChallengeCanvas();
    challengeWinModal.classList.remove("active");
    challengeStatusTag.textContent = "Valendo";
    challengeStatusTag.style.background = "var(--senai-red-subtle)";
    challengeStatusTag.style.color = "var(--senai-red)";

    if (chalAnimationId) cancelAnimationFrame(chalAnimationId);

    const W = challengeCanvas.width;
    const H = challengeCanvas.height;

    if (currentChallengeIdx === 1) {
      // Desafio 1: Labirinto de Laser
      currentChallengeTitle.textContent = "Desafio 1: Labirinto de Laser";
      currentChallengeInstruction.textContent = "Guie o cursor do Ponto A até a Meta sem tocar nas paredes vermelhas.";
      chalState = {
        type: 1,
        started: false,
        points: [
          { x: 50, y: H / 2 },
          { x: W * 0.25, y: H / 2 },
          { x: W * 0.25, y: 70 },
          { x: W * 0.55, y: 70 },
          { x: W * 0.55, y: H - 70 },
          { x: W * 0.82, y: H - 70 },
          { x: W * 0.82, y: H / 2 },
          { x: W - 50, y: H / 2 }
        ],
        pathRadius: 36,
        userX: 0,
        userY: 0
      };
      runMazeChallenge();
    } else if (currentChallengeIdx === 2) {
      // Desafio 2: Reflexo Rápido
      currentChallengeTitle.textContent = "Desafio 2: Reflexo Rápido";
      currentChallengeInstruction.textContent = "Estoure 10 alvos holográficos antes que desapareçam!";
      chalState = {
        type: 2,
        targets: [],
        popped: 0,
        total: 10,
        nextSpawn: Date.now() + 400
      };
      runTargetsChallenge();
    } else if (currentChallengeIdx === 3) {
      // Desafio 3: Segurar o Foco
      currentChallengeTitle.textContent = "Desafio 3: Segurar o Foco";
      currentChallengeInstruction.textContent = "Mantenha o cursor dentro da esfera de plasma contínua por 3 segundos.";
      chalState = {
        type: 3,
        orbX: W / 2,
        orbY: H / 2,
        t: 0,
        progress: 0, // 0 a 3000ms
        inside: false,
        lastTime: Date.now()
      };
      runHoldChallenge();
    } else if (currentChallengeIdx === 4) {
      // Desafio 4: Conectar Nós do Circuito
      currentChallengeTitle.textContent = "Desafio 4: Conectar o Circuito";
      currentChallengeInstruction.textContent = "Passe o cursor pelos nós de 1 a 5 na ordem sequencial exata.";
      chalState = {
        type: 4,
        nodes: [
          { num: 1, x: W * 0.15, y: H * 0.35, connected: false },
          { num: 2, x: W * 0.35, y: H * 0.70, connected: false },
          { num: 3, x: W * 0.55, y: H * 0.25, connected: false },
          { num: 4, x: W * 0.75, y: H * 0.65, connected: false },
          { num: 5, x: W * 0.90, y: H * 0.35, connected: false }
        ],
        nextTarget: 1
      };
      runNodesChallenge();
    }
  }

  // Desafio 1 Loop: Labirinto
  function runMazeChallenge() {
    function drawMaze() {
      chalCtx.clearRect(0, 0, challengeCanvas.width, challengeCanvas.height);
      const pts = chalState.points;
      const r = chalState.pathRadius;

      // Pista Limpa
      chalCtx.beginPath();
      chalCtx.moveTo(pts[0].x, pts[0].y);
      for (let i = 1; i < pts.length; i++) {
        chalCtx.lineTo(pts[i].x, pts[i].y);
      }
      chalCtx.lineWidth = r * 2;
      chalCtx.strokeStyle = "rgba(227, 6, 19, 0.08)";
      chalCtx.lineCap = "round";
      chalCtx.lineJoin = "round";
      chalCtx.stroke();

      // Linha Central Guia
      chalCtx.lineWidth = 2;
      chalCtx.strokeStyle = "rgba(227, 6, 19, 0.3)";
      chalCtx.setLineDash([6, 6]);
      chalCtx.stroke();
      chalCtx.setLineDash([]);

      // Ponto Inicial (A)
      chalCtx.beginPath();
      chalCtx.arc(pts[0].x, pts[0].y, r * 0.8, 0, Math.PI * 2);
      chalCtx.fillStyle = "#10B981";
      chalCtx.fill();
      chalCtx.fillStyle = "#FFFFFF";
      chalCtx.font = "bold 16px Outfit";
      chalCtx.textAlign = "center";
      chalCtx.textBaseline = "middle";
      chalCtx.fillText("INÍCIO", pts[0].x, pts[0].y);

      // Meta (B)
      const last = pts[pts.length - 1];
      chalCtx.beginPath();
      chalCtx.arc(last.x, last.y, r * 0.8, 0, Math.PI * 2);
      chalCtx.fillStyle = "var(--senai-red)";
      chalCtx.fill();
      chalCtx.fillStyle = "#FFFFFF";
      chalCtx.fillText("META", last.x, last.y);

      // Verificação de Posição
      if (chalState.started) {
        let inside = false;
        // Distância do cursor até os segmentos do caminho
        for (let i = 0; i < pts.length - 1; i++) {
          const d = distToSegment({ x: chalState.userX, y: chalState.userY }, pts[i], pts[i + 1]);
          if (d <= r) {
            inside = true;
            break;
          }
        }

        if (!inside) {
          Sound.hit();
          chalState.started = false;
          challengeStatusTag.textContent = "Tocou na borda! Reinicie do Início.";
        } else {
          // Checa se alcançou a meta
          const distToGoal = Math.hypot(chalState.userX - last.x, chalState.userY - last.y);
          if (distToGoal < r) {
            showChallengeWin("Labirinto Superado!", "Excelente estabilidade e controle da mão.");
            return;
          }
        }
      }

      chalAnimationId = requestAnimationFrame(drawMaze);
    }
    chalAnimationId = requestAnimationFrame(drawMaze);
  }

  function distToSegment(p, v, w) {
    const l2 = Math.hypot(v.x - w.x, v.y - w.y) ** 2;
    if (l2 === 0) return Math.hypot(p.x - v.x, p.y - v.y);
    let t = ((p.x - v.x) * (w.x - v.x) + (p.y - v.y) * (w.y - v.y)) / l2;
    t = Math.max(0, Math.min(1, t));
    return Math.hypot(p.x - (v.x + t * (w.x - v.x)), p.y - (v.y + t * (w.y - v.y)));
  }

  // Desafio 2 Loop: Reflexo Rápido
  function runTargetsChallenge() {
    function drawTargets() {
      chalCtx.clearRect(0, 0, challengeCanvas.width, challengeCanvas.height);
      const now = Date.now();

      // Spawn de novos alvos
      if (now > chalState.nextSpawn && chalState.targets.length < 2 && (chalState.popped + chalState.targets.length < chalState.total)) {
        chalState.targets.push({
          x: 80 + Math.random() * (challengeCanvas.width - 160),
          y: 70 + Math.random() * (challengeCanvas.height - 140),
          radius: 36,
          life: 1.0,
          created: now
        });
        chalState.nextSpawn = now + 1200;
        Sound.hover();
      }

      // Desenhar Alvos
      for (let i = chalState.targets.length - 1; i >= 0; i--) {
        const tg = chalState.targets[i];
        const age = now - tg.created;
        tg.life = Math.max(0, 1.0 - (age / 2400));

        if (tg.life <= 0) {
          chalState.targets.splice(i, 1);
          continue;
        }

        // Anel Externo
        chalCtx.beginPath();
        chalCtx.arc(tg.x, tg.y, tg.radius * tg.life + 8, 0, Math.PI * 2);
        chalCtx.strokeStyle = "rgba(227, 6, 19, 0.4)";
        chalCtx.lineWidth = 2;
        chalCtx.stroke();

        // Núcleo
        chalCtx.beginPath();
        chalCtx.arc(tg.x, tg.y, tg.radius * tg.life, 0, Math.PI * 2);
        chalCtx.fillStyle = "#E30613";
        chalCtx.fill();

        chalCtx.fillStyle = "#FFFFFF";
        chalCtx.font = "bold 14px Outfit";
        chalCtx.textAlign = "center";
        chalCtx.textBaseline = "middle";
        chalCtx.fillText("MIRA", tg.x, tg.y);
      }

      challengeStatusTag.textContent = `Alvos: ${chalState.popped} / ${chalState.total}`;

      if (chalState.popped >= chalState.total) {
        showChallengeWin("Reflexo Rápido Concluído!", "Tempo de resposta e mira afiados.");
        return;
      }

      chalAnimationId = requestAnimationFrame(drawTargets);
    }
    chalAnimationId = requestAnimationFrame(drawTargets);
  }

  // Desafio 3 Loop: Segurar o Foco
  function runHoldChallenge() {
    function drawHold() {
      chalCtx.clearRect(0, 0, challengeCanvas.width, challengeCanvas.height);
      const now = Date.now();
      const dt = now - chalState.lastTime;
      chalState.lastTime = now;

      // Movimento suave Lissajous da esfera
      chalState.t += 0.018;
      const W = challengeCanvas.width;
      const H = challengeCanvas.height;
      chalState.orbX = W / 2 + Math.sin(chalState.t) * (W * 0.28);
      chalState.orbY = H / 2 + Math.cos(chalState.t * 1.4) * (H * 0.24);

      const r = 42;

      // Progresso
      if (chalState.inside) {
        chalState.progress += dt;
        if (chalState.progress % 400 < 30) Sound.hover();
      } else {
        chalState.progress = Math.max(0, chalState.progress - dt * 1.5);
      }

      const pct = Math.min(1.0, chalState.progress / 3000);

      // Halo e Esfera
      chalCtx.beginPath();
      chalCtx.arc(chalState.orbX, chalState.orbY, r + 10, 0, Math.PI * 2);
      chalCtx.fillStyle = chalState.inside ? "rgba(227, 6, 19, 0.15)" : "rgba(0, 0, 0, 0.04)";
      chalCtx.fill();

      // Anel de Carga
      chalCtx.beginPath();
      chalCtx.arc(chalState.orbX, chalState.orbY, r + 6, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * pct);
      chalCtx.strokeStyle = "#E30613";
      chalCtx.lineWidth = 5;
      chalCtx.stroke();

      // Esfera de Plasma
      chalCtx.beginPath();
      chalCtx.arc(chalState.orbX, chalState.orbY, r, 0, Math.PI * 2);
      chalCtx.fillStyle = chalState.inside ? "#E30613" : "#374151";
      chalCtx.fill();

      chalCtx.fillStyle = "#FFFFFF";
      chalCtx.font = "bold 15px Outfit";
      chalCtx.textAlign = "center";
      chalCtx.textBaseline = "middle";
      chalCtx.fillText(`${Math.round(pct * 100)}%`, chalState.orbX, chalState.orbY);

      challengeStatusTag.textContent = `Carregando: ${Math.round(pct * 100)}%`;

      if (pct >= 1.0) {
        showChallengeWin("Estabilidade Perfeita!", "Mão calibrada e foco mantido por 3 segundos.");
        return;
      }

      chalAnimationId = requestAnimationFrame(drawHold);
    }
    chalAnimationId = requestAnimationFrame(drawHold);
  }

  // Desafio 4 Loop: Conectar Nós
  function runNodesChallenge() {
    function drawNodes() {
      chalCtx.clearRect(0, 0, challengeCanvas.width, challengeCanvas.height);

      // Conexões já realizadas
      chalCtx.beginPath();
      let startedLine = false;
      for (let i = 0; i < chalState.nodes.length; i++) {
        const nd = chalState.nodes[i];
        if (nd.connected) {
          if (!startedLine) {
            chalCtx.moveTo(nd.x, nd.y);
            startedLine = true;
          } else {
            chalCtx.lineTo(nd.x, nd.y);
          }
        }
      }
      chalCtx.strokeStyle = "#E30613";
      chalCtx.lineWidth = 4;
      chalCtx.lineCap = "round";
      chalCtx.stroke();

      // Desenhar Nós
      for (let i = 0; i < chalState.nodes.length; i++) {
        const nd = chalState.nodes[i];
        chalCtx.beginPath();
        chalCtx.arc(nd.x, nd.y, 24, 0, Math.PI * 2);
        chalCtx.fillStyle = nd.connected ? "#E30613" : (nd.num === chalState.nextTarget ? "rgba(227, 6, 19, 0.2)" : "#F3F4F6");
        chalCtx.fill();
        chalCtx.strokeStyle = nd.num === chalState.nextTarget ? "#E30613" : "rgba(0,0,0,0.1)";
        chalCtx.lineWidth = 2;
        chalCtx.stroke();

        chalCtx.fillStyle = nd.connected ? "#FFFFFF" : "var(--charcoal)";
        chalCtx.font = "bold 16px Outfit";
        chalCtx.textAlign = "center";
        chalCtx.textBaseline = "middle";
        chalCtx.fillText(nd.num, nd.x, nd.y);
      }

      challengeStatusTag.textContent = `Próximo Nó: [${chalState.nextTarget}]`;

      if (chalState.nextTarget > 5) {
        showChallengeWin("Circuito Completo!", "Nós conectados com precisão geométrica.");
        return;
      }

      chalAnimationId = requestAnimationFrame(drawNodes);
    }
    chalAnimationId = requestAnimationFrame(drawNodes);
  }

  // Interação do Cursor no Canvas de Desafio
  challengeCanvas.addEventListener("mousemove", (e) => {
    const rect = challengeCanvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    if (chalState.type === 1) {
      chalState.userX = x;
      chalState.userY = y;
      const startPt = chalState.points[0];
      if (Math.hypot(x - startPt.x, y - startPt.y) < chalState.pathRadius) {
        if (!chalState.started) {
          chalState.started = true;
          Sound.click();
          challengeStatusTag.textContent = "Em percurso... Mantenha a firmeza!";
        }
      }
    } else if (chalState.type === 2) {
      // Estourar alvo ao passar ou clicar
      for (let i = chalState.targets.length - 1; i >= 0; i--) {
        const tg = chalState.targets[i];
        if (Math.hypot(x - tg.x, y - tg.y) < tg.radius) {
          Sound.point();
          chalState.popped++;
          chalState.targets.splice(i, 1);
          break;
        }
      }
    } else if (chalState.type === 3) {
      chalState.inside = Math.hypot(x - chalState.orbX, y - chalState.orbY) < 42;
    } else if (chalState.type === 4) {
      const targetNode = chalState.nodes.find(n => n.num === chalState.nextTarget);
      if (targetNode && Math.hypot(x - targetNode.x, y - targetNode.y) < 26) {
        Sound.point();
        targetNode.connected = true;
        chalState.nextTarget++;
      }
    }
  });

  // ===================================================================
  // 6. JOGO FLIP BIRD (SENAI EDITION)
  // ===================================================================
  const flappyCanvas = document.getElementById("flappyCanvas");
  const fCtx = flappyCanvas.getContext("2d");
  const flappyOverlay = document.getElementById("flappyOverlay");
  const flappyOverlayTitle = document.getElementById("flappyOverlayTitle");
  const flappyOverlayText = document.getElementById("flappyOverlayText");
  const btnStartFlappy = document.getElementById("btnStartFlappy");
  const flappyScoreEl = document.getElementById("flappyScore");
  const flappyBestEl = document.getElementById("flappyBest");

  let flappyBest = parseInt(localStorage.getItem("senai_flappy_best") || "0");
  flappyBestEl.textContent = flappyBest;

  let fW = 760, fH = 440;
  function resizeFlappyCanvas() {
    fW = flappyCanvas.parentElement.clientWidth;
    fH = 440;
    flappyCanvas.width = fW;
    flappyCanvas.height = fH;
  }
  resizeFlappyCanvas();

  let bird = { x: 90, y: 200, vy: 0, r: 18, angle: 0 };
  let pipes = [];
  let fScore = 0;
  let fGameRunning = false;
  let fGameLoopId = null;

  function resetFlappyGame() {
    bird = { x: 90, y: fH / 2, vy: 0, r: 18, angle: 0 };
    pipes = [];
    fScore = 0;
    flappyScoreEl.textContent = fScore;
  }

  function startFlappyGame() {
    resetFlappyGame();
    fGameRunning = true;
    flappyOverlay.classList.add("hidden");
    Sound.flap();

    // Primeiro cano
    pipes.push({
      x: fW + 80,
      topH: 120,
      bottomY: 260,
      w: 64,
      passed: false
    });

    if (fGameLoopId) cancelAnimationFrame(fGameLoopId);
    runFlappyLoop();
  }

  function flapBird() {
    if (!fGameRunning) return;
    bird.vy = -6.2;
    Sound.flap();
  }

  flappyCanvas.addEventListener("mousedown", flapBird);
  btnStartFlappy.addEventListener("click", startFlappyGame);
  window.addEventListener("keydown", (e) => {
    if (activeTabName === "flappy" && e.code === "Space") {
      e.preventDefault();
      if (!fGameRunning) startFlappyGame();
      else flapBird();
    }
  });

  function gameOverFlappy() {
    fGameRunning = false;
    Sound.hit();
    if (fScore > flappyBest) {
      flappyBest = fScore;
      localStorage.setItem("senai_flappy_best", flappyBest);
      flappyBestEl.textContent = flappyBest;
    }
    flappyOverlayTitle.textContent = "Fim de Voo!";
    flappyOverlayText.textContent = `Você conquistou ${fScore} pontos. Excelente pilotagem!`;
    btnStartFlappy.textContent = "Decolar Novamente";
    flappyOverlay.classList.remove("hidden");
  }

  function runFlappyLoop() {
    if (!fGameRunning) return;

    fCtx.clearRect(0, 0, fW, fH);

    // Física do Pássaro / Drone
    bird.vy += 0.32; // Gravidade
    bird.y += bird.vy;
    bird.angle = Math.min(Math.PI / 4, Math.max(-Math.PI / 4, bird.vy * 0.08));

    // Colisão Chão / Teto
    if (bird.y + bird.r > fH || bird.y - bird.r < 0) {
      gameOverFlappy();
      return;
    }

    // Gerar Canos / Torres Minimalistas
    const lastPipe = pipes[pipes.length - 1];
    if (lastPipe && lastPipe.x < fW - 240) {
      const gap = 140;
      const topH = 60 + Math.random() * (fH - gap - 120);
      pipes.push({
        x: fW,
        topH: topH,
        bottomY: topH + gap,
        w: 64,
        passed: false
      });
    }

    // Atualizar Canos
    for (let i = pipes.length - 1; i >= 0; i--) {
      const p = pipes[i];
      p.x -= 2.8;

      // Desenho do Cano Superior
      fCtx.fillStyle = "#F3F4F6";
      fCtx.fillRect(p.x, 0, p.w, p.topH);
      fCtx.strokeStyle = "rgba(227, 6, 19, 0.3)";
      fCtx.lineWidth = 2;
      fCtx.strokeRect(p.x, 0, p.w, p.topH);

      // Faixa Vermelha no Topo do Cano
      fCtx.fillStyle = "#E30613";
      fCtx.fillRect(p.x, p.topH - 12, p.w, 12);

      // Desenho do Cano Inferior
      fCtx.fillStyle = "#F3F4F6";
      fCtx.fillRect(p.x, p.bottomY, p.w, fH - p.bottomY);
      fCtx.strokeStyle = "rgba(227, 6, 19, 0.3)";
      fCtx.strokeRect(p.x, p.bottomY, p.w, fH - p.bottomY);

      // Faixa Vermelha na Base do Cano
      fCtx.fillStyle = "#E30613";
      fCtx.fillRect(p.x, p.bottomY, p.w, 12);

      // Checar Pontuação
      if (!p.passed && p.x + p.w < bird.x) {
        p.passed = true;
        fScore++;
        flappyScoreEl.textContent = fScore;
        Sound.point();
      }

      // Colisão com os Canos
      if (bird.x + bird.r > p.x && bird.x - bird.r < p.x + p.w) {
        if (bird.y - bird.r < p.topH || bird.y + bird.r > p.bottomY) {
          gameOverFlappy();
          return;
        }
      }

      // Remover canos fora da tela
      if (p.x + p.w < 0) {
        pipes.splice(i, 1);
      }
    }

    // Desenhar Drone SENAI
    fCtx.save();
    fCtx.translate(bird.x, bird.y);
    fCtx.rotate(bird.angle);

    // Corpo do Drone
    fCtx.beginPath();
    fCtx.arc(0, 0, bird.r, 0, Math.PI * 2);
    fCtx.fillStyle = "#FFFFFF";
    fCtx.fill();
    fCtx.lineWidth = 3;
    fCtx.strokeStyle = "#E30613";
    fCtx.stroke();

    // Cabine Vermelha
    fCtx.beginPath();
    fCtx.arc(4, -3, 8, 0, Math.PI * 2);
    fCtx.fillStyle = "#E30613";
    fCtx.fill();

    // Asas / Turbinas
    fCtx.fillStyle = "#111827";
    fCtx.fillRect(-bird.r - 4, -4, 6, 8);

    fCtx.restore();

    fGameLoopId = requestAnimationFrame(runFlappyLoop);
  }

  // ===================================================================
  // 7. JOGO FRUIT NINJA (SENAI EDITION)
  // ===================================================================
  const fruitCanvas = document.getElementById("fruitCanvas");
  const fruitCtx = fruitCanvas.getContext("2d");
  const fruitOverlay = document.getElementById("fruitOverlay");
  const fruitOverlayTitle = document.getElementById("fruitOverlayTitle");
  const fruitOverlayText = document.getElementById("fruitOverlayText");
  const btnStartFruit = document.getElementById("btnStartFruit");
  const fruitLivesContainer = document.getElementById("fruitLivesContainer");
  const fruitScoreText = document.getElementById("fruitScoreText");
  const fruitComboAlert = document.getElementById("fruitComboAlert");

  let frW = 980, frH = 480;
  function resizeFruitCanvas() {
    frW = fruitCanvas.parentElement.clientWidth;
    frH = 480;
    fruitCanvas.width = frW;
    fruitCanvas.height = frH;
  }
  resizeFruitCanvas();

  let fruits = [];
  let bladeTrail = [];
  let fruitScore = 0;
  let fruitLives = 3;
  let frGameRunning = false;
  let frGameLoopId = null;
  let lastSliceTime = 0;
  let currentCombo = 0;

  const FRUIT_TYPES = [
    { name: "melancia", color: "#10B981", inner: "#EF4444", radius: 34, score: 1 },
    { name: "maca", color: "#DC2626", inner: "#FEE2E2", radius: 28, score: 1 },
    { name: "laranja", color: "#F97316", inner: "#FFEDD5", radius: 30, score: 1 },
    { name: "banana", color: "#EAB308", inner: "#FEF9C3", radius: 26, score: 1 },
    { name: "bomba", color: "#1F2937", inner: "#E30613", radius: 30, isBomb: true }
  ];

  function resetFruitGame() {
    fruits = [];
    bladeTrail = [];
    fruitScore = 0;
    fruitLives = 3;
    updateFruitHUD();
  }

  function updateFruitHUD() {
    fruitScoreText.textContent = `${fruitScore} Frutas`;
    let hearts = "";
    for (let i = 0; i < fruitLives; i++) hearts += "❤️ ";
    fruitLivesContainer.innerHTML = hearts || "💀";
  }

  function startFruitGame() {
    resetFruitGame();
    frGameRunning = true;
    fruitOverlay.classList.add("hidden");
    Sound.slice();
    if (frGameLoopId) cancelAnimationFrame(frGameLoopId);
    runFruitLoop();
  }

  btnStartFruit.addEventListener("click", startFruitGame);

  function gameOverFruit(isBomb = false) {
    frGameRunning = false;
    Sound.hit();
    fruitOverlayTitle.textContent = isBomb ? "Bomba Acionada!" : "Fim de Jogo!";
    fruitOverlayText.textContent = `Você fatiou ${fruitScore} frutas com reflexo ninja!`;
    btnStartFruit.textContent = "Jogar Novamente";
    fruitOverlay.classList.remove("hidden");
  }

  // Rastreamento da Lâmina Laser
  fruitCanvas.addEventListener("mousemove", (e) => {
    if (!frGameRunning) return;
    const rect = fruitCanvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    bladeTrail.push({ x, y, time: Date.now() });
    if (bladeTrail.length > 14) bladeTrail.shift();

    // Testar Corte das Frutas
    if (bladeTrail.length >= 2) {
      const p1 = bladeTrail[bladeTrail.length - 2];
      const p2 = bladeTrail[bladeTrail.length - 1];

      for (let i = fruits.length - 1; i >= 0; i--) {
        const f = fruits[i];
        if (!f.sliced) {
          const d = distToSegment(f, p1, p2);
          if (d <= f.type.radius) {
            sliceFruit(f);
            break;
          }
        }
      }
    }
  });

  function sliceFruit(f) {
    f.sliced = true;
    Sound.slice();

    if (f.type.isBomb) {
      Sound.hit();
      gameOverFruit(true);
      return;
    }

    Sound.splat();
    fruitScore += f.type.score;

    // Detecção de Combo (cortar múltiplas frutas em menos de 350ms)
    const now = Date.now();
    if (now - lastSliceTime < 350) {
      currentCombo++;
      if (currentCombo >= 2) {
        showCombo(currentCombo);
        fruitScore += currentCombo;
      }
    } else {
      currentCombo = 1;
    }
    lastSliceTime = now;
    updateFruitHUD();

    // Dividir em duas metades físicas
    f.halves = [
      { x: f.x - 10, y: f.y, vx: f.vx - 2.5, vy: f.vy - 1.5, angle: f.angle, rotSpeed: -0.1 },
      { x: f.x + 10, y: f.y, vx: f.vx + 2.5, vy: f.vy - 1.5, angle: f.angle, rotSpeed: 0.1 }
    ];
  }

  function showCombo(combo) {
    fruitComboAlert.textContent = `COMBO x${combo}! +${combo * 5}`;
    fruitComboAlert.classList.add("show");
    setTimeout(() => fruitComboAlert.classList.remove("show"), 800);
  }

  function spawnFruit() {
    const type = FRUIT_TYPES[Math.floor(Math.random() * FRUIT_TYPES.length)];
    const startX = 100 + Math.random() * (frW - 200);
    const targetX = frW / 2 + (Math.random() - 0.5) * 200;
    const vx = (targetX - startX) * 0.015;
    const vy = -(11 + Math.random() * 3.5);

    fruits.push({
      type,
      x: startX,
      y: frH + 30,
      vx,
      vy,
      angle: 0,
      rotSpeed: (Math.random() - 0.5) * 0.08,
      sliced: false,
      halves: null
    });
  }

  let lastSpawnTime = 0;

  function runFruitLoop() {
    if (!frGameRunning) return;

    fruitCtx.clearRect(0, 0, frW, frH);
    const now = Date.now();

    // Spawn periódico
    if (now - lastSpawnTime > 1400) {
      spawnFruit();
      if (Math.random() > 0.45) spawnFruit(); // Lança em duplas
      lastSpawnTime = now;
    }

    // Atualizar & Desenhar Frutas
    for (let i = fruits.length - 1; i >= 0; i--) {
      const f = fruits[i];

      if (!f.sliced) {
        f.x += f.vx;
        f.y += f.vy;
        f.vy += 0.22; // Gravidade
        f.angle += f.rotSpeed;

        // Desenhar Fruta Inteira
        fruitCtx.save();
        fruitCtx.translate(f.x, f.y);
        fruitCtx.rotate(f.angle);

        fruitCtx.beginPath();
        fruitCtx.arc(0, 0, f.type.radius, 0, Math.PI * 2);
        fruitCtx.fillStyle = f.type.color;
        fruitCtx.fill();
        fruitCtx.lineWidth = 3;
        fruitCtx.strokeStyle = "#FFFFFF";
        fruitCtx.stroke();

        if (f.type.isBomb) {
          // Efeito de Bomba com pavio piscante
          fruitCtx.fillStyle = "#E30613";
          fruitCtx.beginPath();
          fruitCtx.arc(0, 0, 8, 0, Math.PI * 2);
          fruitCtx.fill();
        }

        fruitCtx.restore();

        // Caiu sem ser fatiada?
        if (f.y > frH + 60 && f.vy > 0) {
          if (!f.type.isBomb) {
            fruitLives--;
            Sound.hit();
            updateFruitHUD();
            if (fruitLives <= 0) {
              gameOverFruit(false);
              return;
            }
          }
          fruits.splice(i, 1);
        }
      } else {
        // Fruta Fatiada em 2 metades
        let bothGone = true;
        f.halves.forEach(h => {
          h.x += h.vx;
          h.y += h.vy;
          h.vy += 0.3;
          h.angle += h.rotSpeed;

          if (h.y < frH + 80) bothGone = false;

          fruitCtx.save();
          fruitCtx.translate(h.x, h.y);
          fruitCtx.rotate(h.angle);

          fruitCtx.beginPath();
          fruitCtx.arc(0, 0, f.type.radius, 0, Math.PI);
          fruitCtx.fillStyle = f.type.inner;
          fruitCtx.fill();
          fruitCtx.lineWidth = 3;
          fruitCtx.strokeStyle = f.type.color;
          fruitCtx.stroke();

          fruitCtx.restore();
        });

        if (bothGone) fruits.splice(i, 1);
      }
    }

    // Desenhar Rastro da Lâmina Laser (Laser Neon Vermelho)
    const trailCutoff = now - 180;
    while (bladeTrail.length && bladeTrail[0].time < trailCutoff) {
      bladeTrail.shift();
    }

    if (bladeTrail.length >= 2) {
      fruitCtx.beginPath();
      fruitCtx.moveTo(bladeTrail[0].x, bladeTrail[0].y);
      for (let i = 1; i < bladeTrail.length; i++) {
        fruitCtx.lineTo(bladeTrail[i].x, bladeTrail[i].y);
      }
      fruitCtx.strokeStyle = "#E30613";
      fruitCtx.lineWidth = 6;
      fruitCtx.lineCap = "round";
      fruitCtx.shadowColor = "rgba(227, 6, 19, 0.8)";
      fruitCtx.shadowBlur = 14;
      fruitCtx.stroke();

      // Núcleo Branco da Lâmina
      fruitCtx.beginPath();
      fruitCtx.moveTo(bladeTrail[0].x, bladeTrail[0].y);
      for (let i = 1; i < bladeTrail.length; i++) {
        fruitCtx.lineTo(bladeTrail[i].x, bladeTrail[i].y);
      }
      fruitCtx.strokeStyle = "#FFFFFF";
      fruitCtx.lineWidth = 2.5;
      fruitCtx.stroke();
      fruitCtx.shadowBlur = 0;
    }

    frGameLoopId = requestAnimationFrame(runFruitLoop);
  }

});
