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

### Outras Opções de Execução:
```bash
python main.py --totem       # Abre o Totem Digital SENAI no navegador
python main.py --teste       # Abre o Laboratório de Testes Web com os jogos
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

### 🎮 Laboratório de Testes Web & Jogos Touchless
- Contém 5 módulos interativos de calibração (Alcance de Tela, Arraste de Peças, Desenho Livre, Teclado Virtual, Teste de Reflexo).
- Inclui 3 Jogos Touchless:
  - **Flip Bird**: Pilote o Drone Tecnológico SENAI no ar.
  - **Fruit Ninja**: Fatie frutas no ar com a lâmina laser e desvie de bombas.
  - **Air Hockey 1x1**: Disputa esportiva ágil contra a inteligência artificial.

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
