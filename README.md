# AI Virtual Mouse — Edição SENAI (Alcance de Tela Inteira)

Sistema moderno de controle de mouse sem contato (Touchless Mouse) por Visão Computacional em tempo real, desenvolvido com a identidade visual do **SENAI** e compatível com **Windows** e **Raspberry Pi 5**.

---

## 🚀 Como Iniciar

### 1. Instalação das Dependências
Crie o ambiente virtual e instale os pacotes necessários:

```bash
# Windows
py -3.11 -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt

# Linux / Raspberry Pi 5
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Execução Unificada
```bash
# Windows
py main.py

# Linux / Raspberry Pi 5
python3 main.py
```

> 🎮 **Atalhos dos Jogos**: Ao executar `py main.py`, a Área de Testes Web é aberta junto ao Mouse Touchless:
> - Pressione **`G`** no teclado ou clique em **Flappy Bird [G]** para abrir o jogo Flappy Bird em Python no PC!
> - Pressione **`N`** no teclado ou clique em **Fruit Ninja [N]** para abrir o jogo Fruit Ninja em Python no PC!

### Outras Opções de Execução:
```bash
python main.py --fruit       # Executa diretamente o jogo desktop Fruit Ninja (Pygame)
python main.py --flappy      # Executa diretamente o jogo desktop Flappy Bird (Pygame)
python main.py --totem       # Abre o Totem Digital SENAI no navegador
python main.py --mouse-only  # Executa apenas o motor touchless (sem navegador)
python main.py --ironman     # Executa a versão com HUD futurista Jarvis Ironman
python main.py --gui         # Executa a interface desktop Studio CustomTkinter
```

> 📖 **Guia Passo a Passo Completo**:
> Consulte o arquivo [`COMO_RODAR.md`](COMO_RODAR.md) para o manual detalhado de instalação, configuração no **Raspberry Pi 5** (troca de Wayland para X11, modo Kiosk), guia de gestos e resolução de problemas.

---

## ✨ Principais Destaques do Sistema

### 🖥️ Controle Real por Toda a Tela (100% de Alcance)
- O mouse virtual controla diretamente a tela inteira do computador (1920x1080) com alcance total nos 4 cantos e no centro.
- Mapeamento calibrado com margens adaptativas permitindo alcançar toda a tela com movimentos confortáveis da mão sobre a mesa, sem cansar o braço.

### 📷 Seleção Automática de Webcam USB em 60 FPS
- **Detecção Inteligente**: Identifica automaticamente webcams externas conectadas via USB (ex: Logitech C922) com prioridade máxima sobre a câmera integrada.
- Configuração de baixa latência em DirectShow no Windows e V4L2 no Linux / Raspberry Pi (`CAP_PROP_BUFFERSIZE = 1`).

### 🍓 Compatibilidade com Raspberry Pi 5
- Totalmente otimizado para a arquitetura ARM64 do Raspberry Pi 5.
- Taxa de quadros fluida (25-40+ FPS) utilizando compressão MJPG 640x480.
- Suporte a modo Kiosk em tela cheia para totens interativos.

### 🎮 Jogos 100% Python Touchless & Área de Calibração
- **Fruit Ninja Touchless (`fruit_ninja.py`)**: Fatie melancias, laranjas, maçãs, bananas e cocos cortando o ar com a mão! Efeito de lâmina laser neon com física de divisão de frutas, partículas de suco, combos e bombas para desviar.
- **Flappy Bird Touchless (`flappy_mouse.py`)**: Jogo clássico onde o pássaro segue os movimentos da sua mão no ar com física suave, suporte a tela cheia (`F`), reinício por pinça e recorde.
- **Área de Calibração Web**: 4 módulos interativos para testar e calibrar a precisão e o alcance do mouse virtual (Alcance de Tela Inteira, Arraste de Peças, Desenho Livre e Teste de Reflexo).

### 🎨 Visual Moderno & Tema SENAI
- Fundo contínuo com 10 ondas senoidais vermelhas a 60 FPS no padrão institucional do SENAI.
- Tipografia limpa, despoluída e sem poluição visual.

---

## 🖐️ Guia de Gestos

| Gesto | Ação | Como Fazer |
| :--- | :--- | :--- |
| **Mover Cursor** | Navegação por toda a tela | Aponte com o dedo indicador naturalmente |
| **Trava Magnética** | Evita deslizar o clique | Ao iniciar a pinça, o cursor ancora no botão |
| **Clique Esquerdo** | Clicar em qualquer botão | Junte o polegar e o indicador (pinça firme) |
| **Duplo Clique** | Abrir pastas e programas | Dois toques rápidos de pinça |
| **Arrastar e Soltar** | Mover janelas e peças | Segure a pinça fechada por mais de 0.3s |
| **Clique Direito** | Menu de contexto | Pinça entre polegar e dedo médio |
| **Rolagem (Scroll)** | Rolar páginas e feeds | Levante os dedos indicador e médio juntos |
