# AI Virtual Mouse 🖱️🤖

> Controle de mouse por gestos e inteligência artificial usando Python, OpenCV e MediaPipe em tempo real através da webcam.

Para um guia passo a passo detalhado em português com resolução de erros, consulte o **[COMO_RODAR.md](COMO_RODAR.md)**.

---

## 🌟 Versões Disponíveis

1. **`ironman_touchless_pro.py` (Modo Jarvis / Sci-Fi)**:
   - Interface HUD holográfica estilo reator Arc do Homem de Ferro.
   - Gestos de produtividade com a palma (trocar áreas de trabalho virtuais, `Win+Tab`, `Win+D`).
   - Zoom holográfico com as duas mãos e escudo repulsor.
   - Estabilização avançada com filtro One Euro.

2. **`mac_touchless_pro.py` (Modo MacBook / Vision Pro)**:
   - Trava magnética pré-clique (evita que o cursor escorregue na colisão dos dedos).
   - Rolagem natural estilo trackpad do Mac com dois dedos.
   - Suporte a arrastar e soltar (drag & drop) e clique com botão direito.

3. **`AIVirtualMouse.py` (Modo Clássico Básico)**:
   - Versão inicial simples de rastreamento com dedos indicador e médio.

---

## ⚡ Início Rápido

### 1. Pré-requisitos
* **Python 3.10 ou 3.11** *(Importante: Não use Python 3.13 para evitar incompatibilidade com a API de soluções do MediaPipe)*.
* **Webcam** conectada e funcional.

### 2. Instalação

```powershell
# Criação do ambiente virtual com Python 3.11
py -3.11 -m venv venv

# Ativação do ambiente (PowerShell)
.\venv\Scripts\Activate.ps1

# Instalação das dependências compatíveis
pip install opencv-python mediapipe==0.10.14 pyautogui numpy
```

*(Opcional: caso queira executar o `AIVirtualMouse.py`, instale também `pip install autopy`).*

### 3. Como Rodar

```powershell
# Versão Jarvis (Recomendada)
python ironman_touchless_pro.py

# Ou Versão MacBook Touchless Pro
python mac_touchless_pro.py

# Ou Versão Clássica
python AIVirtualMouse.py
```

Para encerrar qualquer script, foque na janela da webcam e pressione a tecla **`q`**.

---

Para mais detalhes sobre gestos suportados, solução de problemas (`mediapipe.solutions`) e permissões do PowerShell, veja o arquivo **[COMO_RODAR.md](COMO_RODAR.md)**.
