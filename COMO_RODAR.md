# 🚀 Guia Completo: Como Rodar o AI Virtual Mouse & Totem SENAI

Este guia detalha o passo a passo completo para configurar o ambiente, instalar as dependências e executar o sistema de **Mouse Virtual Touchless** e as aplicações do **Totem Digital SENAI**, tanto no **Windows** quanto no **Raspberry Pi 5**.

---

## 📋 Sumário
1. [Execução Rápida via Python](#-execução-rápida-via-python)
2. [Dependências e Requisitos do Sistema](#-dependências-e-requisitos-do-sistema)
3. [Instalação e Execução no Windows](#-instalação-e-execução-no-windows)
4. [🍓 Guia Completo: Como Rodar no Raspberry Pi 5](#-guia-completo-como-rodar-no-raspberry-pi-5)
5. [Opções de Execução do `main.py` e Módulos](#-opções-de-execução-do-mainpy-e-módulos)
6. [🖐️ Guia de Gestos e Controles Touchless](#️-guia-de-gestos-e-controles-touchless)
7. [❓ Resolução de Problemas Frequentes](#-resolução-de-problemas-frequentes)

---

## ⚡ Execução Rápida via Python

Abra o terminal na pasta do projeto e execute o comando principal:

```bash
# Windows
py main.py

# Linux / Raspberry Pi 5
python3 main.py
```

> **O que esse comando faz?**
> 1. Abre automaticamente a **Área de Testes Web com Jogos** (Flip Bird, Fruit Ninja e Air Hockey) no navegador padrão.
> 2. Inicializa o motor do **Mouse Virtual Touchless a 60 FPS**, detectando automaticamente sua webcam USB e permitindo controlar todo o monitor com a mão no ar.

---

## 🛠️ Dependências e Requisitos do Sistema

### 1. Versão do Python
* **Recomendado**: **Python 3.10 ou 3.11** (64-bit).
* **Python 3.12 / 3.13**: Totalmente suportado via `tracker_utils.py` com o modelo neural MediaPipe Tasks (`hand_landmarker.task`).

### 2. Pacotes Python (`requirements.txt`)
O projeto conta com o arquivo [`requirements.txt`](file:///c:/Users/Aluno/Desktop/ai-virtual-mouse/requirements.txt):

| Pacote | Função |
| :--- | :--- |
| **`opencv-python`** | Captura de vídeo de alta taxa de quadros (MJPG 60 FPS) e processamento de imagem |
| **`mediapipe`** | Rastreamento neural de 21 pontos tridimensionais da mão |
| **`numpy`** | Cálculos vetoriais, interpolação e matrizes |
| **`pyautogui`** | Injeção de eventos de mouse (movimento, cliques, scroll, arraste) |
| **`pillow`** | Processamento de imagens e assets visuais |
| **`customtkinter`** | Interface gráfica moderna em Dark Mode (para o modo `--gui`) |
| **`pygame`** | Execução de minijogos desktop interativos (ex: `flappy_mouse.py`) |
| **`pygrabber` / `comtypes`** | *(Windows)* Detecção de nomes reais de webcams via DirectShow |

---

## 💻 Instalação e Execução no Windows

### Passo 1: Criar e Ativar o Ambiente Virtual
Abra o **PowerShell** ou **CMD** na pasta `ai-virtual-mouse`:

```powershell
# Cria o ambiente virtual
py -3.11 -m venv .venv

# Ativa o ambiente virtual
.\.venv\Scripts\activate
```

### Passo 2: Instalar as Dependências
```powershell
pip install -r requirements.txt
```

### Passo 3: Executar
```powershell
py main.py
```

---

## 🍓 Guia Completo: Como Rodar no Raspberry Pi 5

O **Raspberry Pi 5** possui poder de processamento excelente (processador quad-core Cortex-A76 de 2.4 GHz) e roda o MediaPipe Hands a **25-40+ FPS reais** a 640x480.

### 1. Requisitos de Hardware para o Raspberry Pi 5
* **Raspberry Pi 5** (modelos de 4GB ou 8GB de RAM recomendados).
* **Fonte Oficial Raspberry Pi 27W USB-C PD** (essencial para evitar *undervoltage* e perdas de FPS).
* **Cooler Ativo Oficial (Active Cooler)** ou gabinete com ventoinha (evita estrangulamento térmico durante visão computacional contínua).
* **Webcam USB padrão (UVC)** conectada a uma das portas USB 3.0 (azuis), como Logitech C920, C922 ou câmeras USB genéricas 1080p/720p.
* **Sistema Operacional**: **Raspberry Pi OS (64-bit)** Bookworm ou Ubuntu Desktop 24.04 ARM64.

---

### 2. ⚠️ Configuração Crítica de Display: Trocar Wayland por X11
Por padrão, o Raspberry Pi OS Bookworm utiliza o compositor **Wayland** (Wayfire/Labwc). Por regras de segurança, o Wayland **bloqueia** que softwares de terceiros (como `pyautogui`) injetem cliques e controlem o cursor em janelas de outros programas.

Para permitir que o mouse virtual controle livremente toda a tela do Raspberry Pi, alterne para o servidor gráfico **X11**:

1. No terminal do Raspberry Pi, abra a ferramenta de configuração:
   ```bash
   sudo raspi-config
   ```
2. Navegue até: **`6 Advanced Options`** e pressione Enter.
3. Selecione: **`A6 Wayland`** e pressione Enter.
4. Escolha a opção: **`W1 X11 (Openbox)`** e confirme.
5. Selecione **`<Finish>`** e escolha **`<Yes>`** para reiniciar o Raspberry Pi:
   ```bash
   sudo reboot
   ```

---

### 3. Instalação das Bibliotecas do Sistema (apt)
Após reiniciar com o X11 ativo, abra o terminal e instale as dependências nativas necessárias para o OpenCV, MediaPipe e PyAutoGUI:

```bash
sudo apt update && sudo apt upgrade -y

# Instala suporte gráfico, dependências do OpenCV, Tkinter, Pygame e captura X11
sudo apt install -y python3-pip python3-venv libgl1 libglib2.0-0 libcap-dev scrot python3-tk libxcb-cursor0 v4l-utils
```

---

### 4. Configuração do Projeto e Instalação no Raspberry Pi 5
No terminal, clone ou transfira o repositório para o Raspberry Pi:

```bash
cd ~/ai-virtual-mouse

# No Debian Bookworm (PEP 668), crie sempre um ambiente virtual:
python3 -m venv .venv

# Ative o ambiente
source .venv/bin/activate

# Atualize o pip
pip install --upgrade pip

# Instale os pacotes necessários
pip install -r requirements.txt
```

> **💡 Dica sobre o MediaPipe no Raspberry Pi 5**:
> O `pip` baixa automaticamente a roda pré-compilada oficial para Linux ARM64 (`mediapipe-0.10.14-cp311-cp311-manylinux_2_17_aarch64.whl`). **Não é necessário compilar o MediaPipe do zero!**

---

### 5. Executando no Raspberry Pi 5

Com o ambiente virtual ativado (`source .venv/bin/activate`):

```bash
# Modo Recomendado: Mouse Virtual Touchless + Área de Testes no Chromium
python3 main.py

# Apenas o Mouse Virtual Touchless (sem navegador)
python3 main.py --mouse-only

# Modo Totem Digital Institucional do SENAI
python3 main.py --totem

# Modo Jarvis / Homem de Ferro (HUD Holográfico)
python3 main.py --ironman

# Jogo Flappy Mouse Standalone (Pygame)
python3 flappy_mouse.py
```

---

### 6. Modo Totem Kiosk Automático (Tela Cheia) no Raspberry Pi 5
Para totens físicos e exposições onde o sistema deve abrir em tela cheia sem barras de navegação ou bordas de janela:

```bash
# Abre o Totem Digital SENAI em tela cheia Kiosk no Chromium:
chromium-browser --kiosk --noerrdialogs --disable-infobars file://$(pwd)/totem-senai/index.html &

# Inicia o mouse virtual touchless em segundo plano:
python3 main.py --mouse-only
```

---

### 7. Dicas de Otimização e FPS no Raspberry Pi 5
* **Resolução da Câmera**: O projeto já vem configurado em `640x480` com compressão `MJPG` (`camera_utils.py`), garantindo excelente taxa de quadros e menor uso de CPU.
* **Permissão de Câmera**: Caso a câmera USB não abra, garanta que seu usuário pertença ao grupo `video`:
  ```bash
  sudo usermod -a -G video $USER
  ```
* **Câmera Oficial Raspberry Pi (CSI via cabo flat)**: Se estiver utilizando a câmera nativa do Raspberry Pi (Camera Module 3) em vez de webcam USB, utilize o comando `libcamerify`:
  ```bash
  libcamerify python3 main.py
  ```

---

## 🎯 Opções de Execução do `main.py` e Módulos

O arquivo [`main.py`](file:///c:/Users/Aluno/Desktop/ai-virtual-mouse/main.py) é o ponto de entrada unificado do sistema. Confira todos os parâmetros:

| Comando | Descrição |
| :--- | :--- |
| `python main.py` | **Padrão**: Inicia o Mouse Virtual 60 FPS + abre a Área de Testes com jogos no navegador |
| `python main.py --totem` (ou `-t`) | Abre o Totem Institucional oficial do SENAI no navegador |
| `python main.py --teste` (ou `-l`) | Abre apenas a Área de Testes Web com os jogos (sem ligar a câmera) |
| `python main.py --mouse-only` (ou `-m`) | Inicia apenas o motor do mouse virtual touchless (sem abrir navegador) |
| `python main.py --ironman` (ou `-i`) | Inicia a versão futurista Jarvis com HUD holográfico do Homem de Ferro |
| `python main.py --gui` (ou `-g`) | Inicia a interface gráfica desktop desenvolvida em CustomTkinter |

### Executando Módulos Específicos Diretamente:
* **Flappy Mouse Standalone (Pygame)**: `python flappy_mouse.py`
* **Interface Desktop Studio**: `python main_gui.py`
* **Motor Touchless Pro Direto**: `python mac_touchless_pro.py`
* **Modo Jarvis Direto**: `python ironman_touchless_pro.py`

---

## 🖐️ Guia de Gestos e Controles Touchless

O sistema foi calibrado para controle confortável de **100% da tela** sem necessidade de encostar no monitor:

| Gesto | Ação | Como Executar |
| :--- | :--- | :--- |
| **Mover Cursor** | Navegação por toda a tela | Aponte com o dedo indicador naturalmente. O Filtro One-Euro elimina tremores mantendo resposta imediata. |
| **Trava Magnética** | Precisão absoluta de clique | Ao aproximar os dedos para clicar, o cursor ancora para não deslizar fora do botão. |
| **Clique Esquerdo** | Clicar em botões e links | Junte o polegar e o dedo indicador (pinça firme rápida). |
| **Clique Duplo** | Abrir pastas e itens | Dois toques rápidos de pinça. |
| **Arrastar e Soltar** | Mover janelas e peças | Segure a pinça fechada por mais de 0.3 segundos e mova; abra a mão para soltar. |
| **Clique Direito** | Menu de contexto | Faça a pinça entre o polegar e o dedo médio. |
| **Rolagem (Scroll)** | Rolar páginas e feeds | Levante o indicador e o dedo médio juntos e mova para cima ou para baixo. |
| **Encerrar** | Fechar aplicação | Pressione a tecla **`q`** na janela de vídeo da câmera. |

---

## ❓ Resolução de Problemas Frequentes

### 1. `error: externally-managed-environment` (no Raspberry Pi 5 / Debian Bookworm)
* **Causa**: O Debian 12 impede a instalação de pacotes pip globais fora de um ambiente virtual (norma PEP 668).
* **Solução**: Crie e use o ambiente virtual:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  ```

### 2. O cursor move na janela da câmera mas não clica no sistema (no Raspberry Pi 5)
* **Causa**: O Raspberry Pi está rodando o compositor gráfico Wayland, que impede a injeção de eventos de mouse pelo `pyautogui`.
* **Solução**: Alterne para X11 usando `sudo raspi-config` -> `Advanced Options` -> `Wayland` -> `X11 (Openbox)` e reinicie com `sudo reboot`.

### 3. `AttributeError: module 'mediapipe' has no attribute 'solutions'`
* **Solução**: O projeto possui fallback automático em `tracker_utils.py` com `hand_landmarker.task`. Se desejar a API legacy clássica, utilize Python 3.11 com `pip install mediapipe==0.10.14`.

### 4. A webcam não abre ou a janela fica preta
* Verifique se outro aplicativo (Navegador, Teams, Discord) está utilizando a webcam.
* O sistema seleciona automaticamente a webcam física USB conectada (`camera_utils.py`).

### 5. Modo de Apresentação em Tela Cheia no Totem
* Ao abrir o Totem Digital (`python main.py --totem`), pressione a tecla **`F`** no teclado do navegador para alternar para a tela cheia.
