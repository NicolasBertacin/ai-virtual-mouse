"""
CENTRAL DE JOGOS E ATIVIDADES TOUCHLESS
Hub Interativo para escolher e jogar qualquer jogo/atividade por gestos ou teclado!
Controles:
- Pressione o numero de 1 a 7 para abrir o jogo desejado:
    [1] Fruit Ninja Holografico
    [2] Iron Man: Defesa de Repulsores
    [3] Air Pong Touchless
    [4] Air Canvas (Pintura no Ar)
    [5] Bateria Virtual (Air Drums)
    [6] Jokenpo IA (Pedra, Papel e Tesoura)
    [7] Simon Says / Genius Gestual
    [8] Simulador de Particulas Cosmicas
- Ou aponte no ar com a ponta do indicador para selecionar diretamente na tela!
- Pressione 'q' para sair.
"""

import cv2
import numpy as np
import mediapipe as mp
import subprocess
import sys
import time
import os
from camera_helper import get_usb_camera_cap

GAMES = [
    ("1", "Fruit Ninja Holografico", "Corte frutas no ar com lamina laser", "game_fruit_ninja.py", (0, 200, 255)),
    ("2", "Iron Man: Repulsor Blaster", "Destrua drones com raios repulsores", "game_ironman_blaster.py", (0, 100, 255)),
    ("3", "Air Pong Touchless", "Ping pong no ar contra IA ou 2 jogadores", "game_air_pong.py", (0, 255, 120)),
    ("4", "Air Canvas (Pintura no Ar)", "Desenhe com luz neon e troque cores", "app_air_canvas.py", (255, 180, 0)),
    ("5", "Bateria Virtual (Air Drums)", "Toque bumbo, caixa e pratos no ar", "app_virtual_drums.py", (220, 50, 220)),
    ("6", "Jokenpo IA", "Pedra, Papel e Tesoura com IA por gestos", "game_jokenpo.py", (240, 200, 50)),
    ("7", "Simon Says (Genius)", "Memorize e reproduza sequencias luminosas", "game_simon_says.py", (50, 220, 240)),
    ("8", "Particulas Cosmicas Sci-Fi", "Manipule campos magneticos e repulsores", "app_particle_galaxy.py", (255, 120, 200))
]

def launch_game(script_name):
    python_exe = sys.executable
    script_path = os.path.join(os.path.dirname(__file__), script_name)
    subprocess.call([python_exe, script_path])


def main():
    W, H = 640, 480
    cap, cam_name, cam_idx = get_usb_camera_cap(W, H)
    if not cap.isOpened():
        print(f"Erro ao abrir camera USB {cam_name}")
        return

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)

    hover_idx = None
    hover_start = 0.0
    SELECTION_HOLD = 0.65

    print("\n" + "="*60)
    print(" CENTRAL DE JOGOS TOUCHLESS INICIADA")
    print(" Pressione o numero de 1 a 8 ou aponte na tela para abrir!")
    print("="*60 + "\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        t_now = time.time()

        # Fundo escuro holografico
        overlay = np.zeros_like(frame)
        frame = cv2.addWeighted(frame, 0.35, overlay, 0.65, 0)

        results = hands.process(rgb)
        tip_pos = None

        if results.multi_hand_landmarks:
            lms = results.multi_hand_landmarks[0].landmark
            tip_pos = (int(lms[8].x * W), int(lms[8].y * H))
            cv2.circle(frame, tip_pos, 8, (0, 255, 255), -1)
            cv2.circle(frame, tip_pos, 14, (255, 255, 255), 1)

        # Desenho dos 8 Botoes/Cards de Jogos (Grid 2 colunas x 4 linhas)
        card_w = 280
        card_h = 70
        gap_x = 26
        gap_y = 12
        start_x = 26
        start_y = 60

        current_target = None

        for idx, (num, title, desc, script, col) in enumerate(GAMES):
            col_idx = idx % 2
            row_idx = idx // 2
            x1 = start_x + col_idx * (card_w + gap_x)
            y1 = start_y + row_idx * (card_h + gap_y)
            x2 = x1 + card_w
            y2 = y1 + card_h

            is_hover = False
            if tip_pos and (x1 <= tip_pos[0] <= x2 and y1 <= tip_pos[1] <= y2):
                is_hover = True
                current_target = idx

            # Cor do card
            card_alpha = 0.65 if is_hover else 0.35
            card_col = (255, 255, 255) if is_hover else col

            card_overlay = frame.copy()
            cv2.rectangle(card_overlay, (x1, y1), (x2, y2), card_col, -1)
            cv2.addWeighted(card_overlay, card_alpha, frame, 1 - card_alpha, 0, frame)

            cv2.rectangle(frame, (x1, y1), (x2, y2), card_col, 2 if is_hover else 1)
            cv2.putText(frame, f"[{num}] {title}", (x1 + 10, y1 + 26), cv2.FONT_HERSHEY_DUPLEX, 0.52, (255, 255, 255), 1)
            cv2.putText(frame, desc, (x1 + 10, y1 + 52), cv2.FONT_HERSHEY_SIMPLEX, 0.36, (220, 220, 220), 1)

        # Logica de Selecao por Apontamento Touchless
        if current_target is not None:
            if current_target == hover_idx:
                duration = t_now - hover_start
                pct = min(1.0, duration / SELECTION_HOLD)
                if tip_pos:
                    cv2.circle(frame, tip_pos, int(14 + pct * 20), (0, 255, 120), 3)

                if duration >= SELECTION_HOLD:
                    chosen_script = GAMES[current_target][3]
                    cv2.destroyAllWindows()
                    cap.release()
                    launch_game(chosen_script)
                    return main()
            else:
                hover_idx = current_target
                hover_start = t_now
        else:
            hover_idx = None

        # Cabecalho do Hub
        cv2.rectangle(frame, (0, 0), (W, 46), (12, 16, 24), -1)
        cv2.line(frame, (0, 46), (W, 46), (0, 200, 255), 1)
        cv2.putText(frame, "CENTRAL TOUCHLESS: DIGITE [1-8] OU APONTE", (18, 30), cv2.FONT_HERSHEY_DUPLEX, 0.55, (0, 255, 255), 1)
        cv2.putText(frame, "[Q] Sair", (W - 85, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 180, 180), 1)

        cv2.imshow("Central de Jogos Touchless - Pressione 'q' para sair", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif ord('1') <= key <= ord('8'):
            game_idx = key - ord('1')
            chosen_script = GAMES[game_idx][3]
            cv2.destroyAllWindows()
            cap.release()
            launch_game(chosen_script)
            return main()

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
