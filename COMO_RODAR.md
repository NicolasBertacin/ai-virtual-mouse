# 🚀 Guia Completo: Como Rodar o AI Virtual Mouse & Totem SENAI

Este guia detalha o passo a passo para configurar o ambiente, instalar as dependências e executar o sistema de mouse virtual touchless e as aplicações web através de comandos Python puros.

---

## 📋 Sumário
1. [Execução Rápida em Código Python](#-execução-rápida-em-código-python)
2. [Estrutura do Projeto](#-estrutura-do-projeto)
3. [Requisitos do Sistema e Dependências](#-requisitos-do-sistema-e-dependências)
4. [Opções Detalhadas de Execução](#-opções-detalhadas-de-execução)
5. [Guia de Gestos e Controles Touchless](#-guia-de-gestos-e-controles-touchless)
6. [Resolução de Problemas Frequentes](#-resolução-de-problemas-frequentes)

---

## ⚡ Execução Rápida em Código Python

Abra o terminal (PowerShell ou CMD) na pasta do projeto e utilize o comando unificado:

```powershell
# Inicia o Mouse Virtual Touchless + abre a Área de Testes com jogos no navegador
py main.py
```

### Outras Opções com `main.py`:
```powershell
# Abre o Totem Digital institucional oficial no navegador
py main.py --totem

# Abre apenas o Laboratório de Testes Web com os 3 jogos (sem ligar câmera)
py main.py --teste

# Inicia apenas o motor do mouse virtual 60 FPS (sem abrir navegador)
py main.py --mouse-only

# Inicia o modo Jarvis / Homem de Ferro (HUD holográfico Sci-Fi)
py main.py --ironman

# Inicia a interface gráfica desktop (CustomTkinter Studio)
py main.py --gui
```

---

## 📁 Estrutura do Projeto

```
ai-virtual-mouse/
│
├── main.py                       # ⭐ Ponto de entrada unificado em Python puro
├── mac_touchless_pro.py          # Motor Touchless Principal (60 FPS, One-Euro, clique magnético)
├── ironman_touchless_pro.py      # Motor Touchless com HUD Sci-Fi holográfico
├── camera_utils.py               # Módulo de câmera otimizado (DirectShow/USB 60 FPS)
├── tracker_utils.py              # Detector universal de mãos (MediaPipe Tasks + Fallback)
├── gui_app.py                    # Aplicação Desktop CustomTkinter
├── main_gui.py                   # Ponto de entrada da aplicação desktop
├── virtual_mouse_engine.py       # Motor de background da interface desktop
├── hand_landmarker.task          # Modelo neural MediaPipe Hands
├── senai_logo.png                # Asset do logo para o Studio desktop
├── COMO_RODAR.md                 # Este guia de execução
├── README.md                     # Documentação geral do projeto
│
├── totem-senai/                  # Aplicações Web (Totem & Laboratório de Testes)
│   ├── index.html                # Totem Digital oficial (ondas a 60fps e carrossel de 20s)
│   ├── teste.html                # Laboratório de Testes (5 módulos + Flip Bird, Fruit Ninja e Hockey)
│   ├── style.css                 # Estilos visuais unificados
│   ├── script.js                 # Lógica de ondas, timer e QR codes do Totem
│   ├── INSTRUCOES.md             # Manual do Totem
│   └── assets/                   # Mídias locais e bibliotecas
│       ├── qr-thiago-masseto.png
│       ├── qr-nicolas-bertacin.png
│       ├── qr-nicolas-dalastra.png
│       ├── qrcode.min.js
│       └── senai-logo.svg
│
└── legacy/                       # Scripts históricos / didáticos
    ├── AIVirtualMouse.py         # Script didático inicial (autopy clássico)
    ├── HandTrackingModule.py     # Módulo auxiliar legado
    └── README.md                 # Nota explicativa sobre versões legadas
```

---

## 🛠️ Requisitos do Sistema e Dependências

### 1. Python
* Recomendado: **Python 3.10 ou 3.11** (compatível com a API nativa do MediaPipe).
* O projeto possui fallback automático em `tracker_utils.py` compatível com Python 3.12+.

### 2. Instalação das Dependências
Abra o terminal e execute:
```powershell
pip install opencv-python mediapipe pyautogui numpy
```
*(Opcional para a interface desktop: `pip install customtkinter pillow`)*

---

## 🎯 Opções Detalhadas de Execução

### 1. Executando os Scripts Diretamente
Você também pode rodar cada módulo diretamente pelo seu arquivo Python:

* **Modo Touchless Pro com Área de Testes:**
  ```powershell
  py mac_touchless_pro.py --web
  ```

* **Apenas o Modo Touchless Pro (Sem Navegador):**
  ```powershell
  py mac_touchless_pro.py
  ```

* **Modo Jarvis / Homem de Ferro:**
  ```powershell
  py ironman_touchless_pro.py
  ```

* **Interface Gráfica Desktop Studio:**
  ```powershell
  py main_gui.py
  ```

---

## 🖐️ Guia de Gestos e Controles Touchless

O sistema foi calibrado para resposta instantânea e **não exige pulseiras**:

* **Mover Cursor**: Aponte com o dedo indicador naturalmente. O sistema utiliza estabilização One-Euro para filtrar microtremores mantendo zero latência.
* **Trava Magnética**: Ao iniciar a aproximação dos dedos para clicar, o cursor ancora suavemente no botão para garantir que o clique não deslize.
* **Clique com Botão Esquerdo**: Junte o polegar e o dedo indicador (gesto de pinça firme).
* **Clique Duplo**: Dois toques rápidos de pinça.
* **Arrastar e Soltar (Drag & Drop)**: Segure a pinça fechada por mais de 0.3 segundos e mova o item; abra os dedos para soltar.
* **Clique com Botão Direito**: Faça a pinça entre o polegar e o dedo médio.
* **Rolagem de Página (Scroll)**: Levante o indicador e o dedo médio juntos e mova verticalmente para rolar de forma natural.
* **Encerrar**: Pressione a tecla **`q`** na janela de vídeo da câmera.

---

## ❓ Resolução de Problemas Frequentes

### 1. `AttributeError: module 'mediapipe' has no attribute 'solutions'`
* **Solução**: O sistema possui fallback nativo com `tracker_utils.py`. Caso deseje a API legacy clássica, utilize Python 3.11 com `pip install mediapipe==0.10.14`.

### 2. A webcam não abre ou fica preta
* Verifique se outros programas (Teams, Discord, Navegador) estão utilizando a webcam.
* O script seleciona automaticamente a webcam USB conectada através do `camera_utils.py`.

### 3. Tela Cheia no Totem
* Ao abrir o Totem Digital (`py main.py --totem`), pressione a tecla **`F`** no teclado para alternar para o modo tela cheia de apresentação.
