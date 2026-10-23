# AI Virtual Mouse — Edição SENAI (Alcance de Tela Inteira)

Sistema moderno de controle de mouse sem contato (Touchless Mouse) por Visão Computacional em tempo real, desenvolvido com a identidade visual do **SENAI** e interface em **CustomTkinter**.

---

## 🚀 Como Iniciar via Código

Execute no terminal dentro da pasta do projeto:

```powershell
# Modo Recomendado: Mouse Virtual Touchless + Área de Testes com Jogos
py main.py
```

### Outras Opções em Código:
```powershell
py main.py --totem       # Abre o Totem Digital SENAI no navegador
py main.py --teste       # Abre o Laboratório de Testes Web com os jogos
py main.py --mouse-only  # Executa apenas o motor touchless (sem navegador)
py main.py --ironman     # Executa a versão com HUD futurista Jarvis Ironman
py main.py --gui         # Executa a interface desktop Studio CustomTkinter
```

---

## ✨ Principais Destaques do Sistema

### 🖥️ Controle Real por Toda a Tela (100% de Alcance)
- O mouse virtual controla diretamente a tela inteira do computador (1920x1080) com alcance total nos cantos e centro.
- Mapeamento calibrado com margens adaptativas permitindo alcançar os 4 cantos da tela e o centro com movimentos confortáveis da mão sobre a mesa, sem cansar o braço.

### 📷 Seleção Automática de Webcam USB em 60 FPS
- **Detecção Inteligente**: Identifica automaticamente webcams externas conectadas via USB (ex: Logitech C922) com prioridade máxima sobre a câmera integrada.
- Configuração de baixa latência em DirectShow (`CAP_PROP_BUFFERSIZE = 1`).

### 🎮 Laboratório de Testes Web & Jogos Touchless
- Contém 5 módulos interativos de calibração (Alcance de Tela, Arraste de Peças, Desenho Livre, Teclado Virtual, Teste de Reflexo).
- Inclui 3 Jogos Touchless:
  - **Flip Bird**: Pilote o Drone Tecnológico SENAI no ar.
  - **Fruit Ninja**: Fatie frutas no ar com a lâmina laser e desvie de bombas.
  - **Air Hockey 1x1**: Disputa esportiva ágil contra a inteligência artificial.

### 🎨 Visual Moderno & Tema SENAI
- Fundo contínuo com 10 ondas senoidais vermelhas a 60 FPS no padrão institucional do SENAI.
- Tipografia limpa, despoluída e sem emojis ou botões redundantes.

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
