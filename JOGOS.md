# 🎮 Central de Jogos e Experiências Touchless - SENAI Lab

Coleção completa com **16 jogos e experiências interativas sem toque (*touchless*)**, desenvolvida com visão computacional, OpenCV e MediaPipe.

Todos os jogos contam com integração com a câmera USB dedicada (Logitech C922), identidade visual com a logomarca oficial do SENAI, efeitos sonoros sintetizados e feedback visual neon/cyber.

---

## 🚀 Como Iniciar

Abra a central interativa com o comando:

```powershell
.\.venv\Scripts\python.exe jogos_launcher.py
```

### 🧭 Como Navegar na Central:
* **Alternar Abas**: Pressione `[TAB]` no teclado ou aponte com o dedo indicador sobre os botões de abas no topo (`MODO SOLO` e `MODO 1v1 VERSUS`).
* **Iniciar Jogo**: Digite o número de `[1]` a `[8]` no teclado correspondente à aba ativa, ou **aponte e segure a mira com o dedo indicador** sobre o card do jogo por 0.6 segundo!
* **Sair**: Pressione `q`.

---

## 🕹️ ABA 1: MODO SOLO / ARCADE (8 Jogos)

### 1. Fruit Ninja Holográfico
* **Comando direto**: `.\.venv\Scripts\python.exe game_fruit_ninja.py`
* **Como jogar**: Use a ponta do seu dedo indicador como uma lâmina laser neon para fatiar as frutas no ar. Cuidado com as bombas!

### 2. Iron Man: Defesa de Repulsores (Target Blaster)
* **Comando direto**: `.\.venv\Scripts\python.exe game_ironman_blaster.py`
* **Como jogar**: Mire na tela com a palma da mão e feche o punho ou faça a pinça para disparar raios repulsores e explodir drones invasores.

### 3. Air Pong Touchless
* **Comando direto**: `.\.venv\Scripts\python.exe game_air_pong.py`
* **Como jogar**: Controle a raquete com a palma da mão na vertical. Pressione `M` para alternar entre jogar contra a Inteligência Artificial ou contra um amigo (2 jogadores locais na mesma câmera).

### 4. Air Canvas (Pintura no Ar)
* **Comando direto**: `.\.venv\Scripts\python.exe app_air_canvas.py`
* **Como usar**:
  * 1 Dedo (Indicador): Modo Pintura (desenha com cores neon).
  * 2 Dedos (Indicador + Médio): Modo Seleção (escolhe cores no topo sem pintar).
  * 5 Dedos (Mão Aberta): Limpar o quadro.
  * Pressione `S` para salvar seu desenho como imagem PNG.

### 5. Bateria Virtual (Air Drums)
* **Comando direto**: `.\.venv\Scripts\python.exe app_virtual_drums.py`
* **Como tocar**: Bata para baixo nos tambores e pratos flutuantes no ar com uma ou duas mãos para acionar os sons percussivos instantaneamente.

### 6. Jokenpô IA (Pedra, Papel e Tesoura)
* **Comando direto**: `.\.venv\Scripts\python.exe game_jokenpo.py`
* **Como jogar**: Pressione `ESPAÇO` para iniciar a contagem regressiva e faça o gesto (Punho = Pedra, Palma aberta = Papel, Dois dedos = Tesoura).

### 7. Simon Says / Genius Gestual
* **Comando direto**: `.\.venv\Scripts\python.exe game_simon_says.py`
* **Como jogar**: Memorize a sequência de cores e tons musicais demonstrada e repita apontando no ar para os quadrantes na ordem certa.

### 8. Simulador de Partículas Cósmicas
* **Comando direto**: `.\.venv\Scripts\python.exe app_particle_galaxy.py`
* **Como interagir**: Centenas de partículas físicas na tela. Abra a mão para emitir ondas de choque de repulsão; feche o punho para criar um buraco negro magnético atrator. Pressione `C` para trocar as cores.

---

## ⚔️ ABA 2: MODO 1 CONTRA 1 LOCAL (8 Duelos)

Todos os jogos 1v1 dividem o campo de visão da câmera USB para 2 jogadores lado a lado (Jogador 1 na Esquerda / Jogador 2 na Direita).

### 1. Air Hockey Cyber 1v1
* **Comando direto**: `.\.venv\Scripts\python.exe versus_air_hockey.py`
* **Mecânica**: Cada jogador controla um batedor circular neon com a palma da mão. A mesa possui gols laterais e física realista de ricochete. Vence quem fizer 5 gols!

### 2. Duelo de Sabres de Luz 1v1 (Laser Sabers)
* **Comando direto**: `.\.venv\Scripts\python.exe versus_laser_sabers.py`
* **Mecânica**: O ângulo do seu punho e indicador projeta uma lâmina de plasma luminosa (Azul vs Vermelho). Ao cruzar as lâminas, faíscas neon saltam e sons de choque de sabre tocam! Encoste a lâmina no corpo/área do oponente para marcar pontos.

### 3. Cabo de Guerra de Plasma 1v1 (Tug of War)
* **Comando direto**: `.\.venv\Scripts\python.exe versus_tug_of_war.py`
* **Mecânica**: Um feixe de plasma com uma orbe de energia no centro. Cada jogador deve puxar a mão repetidamente da linha central em direção ao seu lado. Quem puxar com mais velocidade arrasta a energia para sua base e vence!

### 4. Duelo de Faroeste / Quick Draw 1v1
* **Comando direto**: `.\.venv\Scripts\python.exe versus_quick_draw.py`
* **Mecânica**: Ambos colocam a mão no "coldre" (abaixo da linha). Aguarde a tensão do comando... Se sacar a mão antes, queima a largada! Ao soar o "FOGO!", saque a mão no ar o mais rápido possível. O sistema mede o tempo de reação em milissegundos exatos!

### 5. Batalha de Frutas 1v1 (Fruit Slicer Battle)
* **Comando direto**: `.\.venv\Scripts\python.exe versus_fruit_battle.py`
* **Mecânica**: Frutas voam pela tela e ambos os jogadores fatiam com lâminas simultâneas (Ciano vs Laranja). Cronômetro de 45 segundos e placar ao vivo. Cuidado: quem cortar bomba perde 3 pontos!

### 6. Batalha Espacial 1v1 (Space Battle)
* **Comando direto**: `.\.venv\Scripts\python.exe versus_space_battle.py`
* **Mecânica**: Cada jogador pilota uma nave espacial com o movimento da mão. Levante o indicador para disparar torpedos laser. Abra a mão inteira para erguer um escudo defletor de energia! 5 vidas para cada nave.

### 7. Vôlei Touchless 1v1
* **Comando direto**: `.\.venv\Scripts\python.exe versus_volleyball.py`
* **Mecânica**: Vista lateral 2D com uma rede central alta. A bola sofre gravidade. Use as mãos para cortar, amortecer e jogar a bola por cima da rede para o chão do adversário. Primeiro a 5 pontos vence.

### 8. Tapa e Esquiva / Jogo da Mãozinha 1v1 (Slap & Dodge)
* **Comando direto**: `.\.venv\Scripts\python.exe versus_slap_dodge.py`
* **Mecânica**: O clássico duelo de reflexos de escola, 100% higiênico e sem encostar! Um jogador é o Atacante (na base) e o outro é o Defensor (mão no círculo central de perigo). O atacante pode dar o bote rápido; o defensor deve puxar a mão para a base no instante exato. Se o defensor tremer antes do bote, comete falta! A cada ponto, os papéis se alternam.
