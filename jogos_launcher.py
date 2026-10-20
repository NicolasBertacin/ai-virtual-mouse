"""
CENTRAL DE JOGOS E EXPERIENCIAS TOUCHLESS - SENAI SP
Interface moderna de alta tecnologia com reconhecimento gestual e suporte a teclado.
"""

import cv2
import numpy as np
import mediapipe as mp
import subprocess
import sys
import time
import os
import winsound
import math
from camera_helper import get_usb_camera_cap, draw_glow_banner

GAMES = [
    ("1", "Fruit Ninja Holografico", "Corte frutas no ar com lamina laser", "game_fruit_ninja.py", (0, 210, 255)),
    ("2", "Iron Man: Repulsor Blaster", "Destrua drones com raios repulsores", "game_ironman_blaster.py", (0, 120, 255)),
    ("3", "Air Pong Touchless", "Ping pong no ar contra IA ou 2 jogadores", "game_air_pong.py", (0, 255, 120)),
    ("4", "Air Canvas (Pintura no Ar)", "Desenhe com luz neon e troque cores", "app_air_canvas.py", (255, 170, 0)),
    ("5", "Bateria Virtual (Air Drums)", "Toque bumbo, caixa e pratos no ar", "app_virtual_drums.py", (220, 60, 220)),
    ("6", "Jokenpo IA", "Pedra, Papel e Tesoura com IA por gestos", "game_jokenpo.py", (240, 210, 40)),
    ("7", "Simon Says (Genius)", "Memorize e reproduza sequencias luminosas", "game_simon_says.py", (40, 230, 240)),
    ("8", "Particulas Cosmicas Sci-Fi", "Manipule campos magneticos e repulsores", "app_particle_galaxy.py", (255, 110, 190))
]

def launch_game(script_name):
    try:
        winsound.Beep(1100, 70)
    except Exception:
        pass
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
    SELECTION_HOLD = 0.60
    fps = 30.0
    last_fps_t = time.time()

    print("\n" + "="*65)
    print(" SENAI TOUCHLESS LAB - CENTRAL DE JOGOS & EXPERIENCIAS")
    print(" Selecione apontando o dedo indicador ou digitando de 1 a 8!")
    print("="*65 + "\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        t_now = time.time()

        # Calculo de FPS
        dt = t_now - last_fps_t
        if dt > 0:
            fps = 0.9 * fps + 0.1 * (1.0 / dt)
        last_fps_t = t_now

        # Efeito Glassmorphism: escurece o fundo suavemente para leitura cristalina
        dark_overlay = np.zeros_like(frame)
        frame = cv2.addWeighted(frame, 0.40, dark_overlay, 0.60, 0)

        results = hands.process(rgb)
        tip_pos = None

        if results.multi_hand_landmarks:
            lms = results.multi_hand_landmarks[0].landmark
            tip_pos = (int(lms[8].x * W), int(lms[8].y * H))

        # Desenho dos 8 Cards no Layout Grid 2x4
        card_w = 284
        card_h = 74
        gap_x = 22
        gap_y = 10
        start_x = 25
        start_y = 66

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

            # Cores e efeitos do Card
            bg_alpha = 0.65 if is_hover else 0.35
            card_col = (255, 255, 255) if is_hover else col

            # Preenchimento translucido
            card_overlay = frame.copy()
            cv2.rectangle(card_overlay, (x1, y1), (x2, y2), card_col, -1)
            cv2.addWeighted(card_overlay, bg_alpha, frame, 1 - bg_alpha, 0, frame)

            # Borda com brilho neon
            border_th = 3 if is_hover else 1
            cv2.rectangle(frame, (x1, y1), (x2, y2), card_col, border_th)

            # Badge do numero
            cv2.rectangle(frame, (x1 + 8, y1 + 10), (x1 + 34, y1 + 36), col, -1)
            cv2.putText(frame, num, (x1 + 15, y1 + 30), cv2.FONT_HERSHEY_DUPLEX, 0.55, (255, 255, 255), 1)

            # Titulo e Descricao
            title_col = (255, 255, 255) if is_hover else (240, 240, 240)
            cv2.putText(frame, title, (x1 + 42, y1 + 28), cv2.FONT_HERSHEY_DUPLEX, 0.48, title_col, 1)
            cv2.putText(frame, desc, (x1 + 12, y1 + 58), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (190, 190, 190), 1)

        # Logica de Selecao Gestual por Apontamento
        if current_target is not None:
            if current_target == hover_idx:
                duration = t_now - hover_start
                pct = min(1.0, duration / SELECTION_HOLD)

                if tip_pos:
                    # Mira com anel de carregamento animado
                    r_out = int(14 + pct * 18)
                    cv2.circle(frame, tip_pos, r_out, (0, 255, 120), 2)
                    cv2.circle(frame, tip_pos, 6, (0, 255, 255), -1)

                if duration >= SELECTION_HOLD:
                    chosen_script = GAMES[current_target][3]
                    cv2.destroyAllWindows()
                    cap.release()
                    launch_game(chosen_script)
                    return main()
            else:
                hover_idx = current_target
                hover_start = t_now
                try:
                    winsound.Beep(750, 20)
                except Exception:
                    pass
        else:
            hover_idx = None
            if tip_pos:
                # Cursor normal de rastreamento
                cv2.circle(frame, tip_pos, 7, (0, 255, 255), -1)
                cv2.circle(frame, tip_pos, 11, (255, 255, 255), 1)

        # Banner Superior Tecnologico com a Logo do SENAI
        draw_glow_banner(frame, "SENAI TOUCHLESS LAB", "CENTRAL DE JOGOS", fps)

        # Rodape Informativo
        cv2.rectangle(frame, (0, H - 28), (W, H), (10, 12, 18), -1)
        cv2.putText(frame, "DICA: Digite de [1] a [8] no teclado ou aponte com o dedo indicador para abrir!",
                    (25, H - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (180, 220, 255), 1)

        cv2.imshow("SENAI Touchless Lab - Central de Jogos", frame)

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
