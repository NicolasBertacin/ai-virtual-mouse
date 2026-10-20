"""
CENTRAL DE JOGOS E EXPERIENCIAS TOUCHLESS - SENAI SP
Interface moderna de alta tecnologia com reconhecimento gestual e suporte a teclado.
Possui abas para MODO SOLO / ARCADE (8 jogos) e MODO BATALHA 1v1 VERSUS (8 jogos).
Total: 16 experiencias touchless!
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

SOLO_GAMES = [
    ("1", "Fruit Ninja Holografico", "Corte frutas no ar com lamina laser", "game_fruit_ninja.py", (0, 210, 255)),
    ("2", "Iron Man: Repulsor Blaster", "Destrua drones com raios repulsores", "game_ironman_blaster.py", (0, 120, 255)),
    ("3", "Air Pong Touchless", "Ping pong no ar contra IA ou 2 jogadores", "game_air_pong.py", (0, 255, 120)),
    ("4", "Air Canvas (Pintura no Ar)", "Desenhe com luz neon e troque cores", "app_air_canvas.py", (255, 170, 0)),
    ("5", "Bateria Virtual (Air Drums)", "Toque bumbo, caixa e pratos no ar", "app_virtual_drums.py", (220, 60, 220)),
    ("6", "Jokenpo IA", "Pedra, Papel e Tesoura com IA por gestos", "game_jokenpo.py", (240, 210, 40)),
    ("7", "Simon Says (Genius)", "Memorize e reproduza sequencias luminosas", "game_simon_says.py", (40, 230, 240)),
    ("8", "Particulas Cosmicas Sci-Fi", "Manipule campos magneticos e repulsores", "app_particle_galaxy.py", (255, 110, 190))
]

VERSUS_GAMES = [
    ("1", "Air Hockey 1v1", "Dispute gols no disco em alta velocidade", "versus_air_hockey.py", (0, 230, 255)),
    ("2", "Duelo de Sabres 1v1", "Lute com espadas laser e choque laminas", "versus_laser_sabers.py", (0, 100, 255)),
    ("3", "Cabo de Guerra 1v1", "Puxe o feixe de plasma com gestos rapidos", "versus_tug_of_war.py", (0, 255, 150)),
    ("4", "Duelo Faroeste 1v1", "Reflexo puro no coldre com medicao em ms", "versus_quick_draw.py", (255, 180, 0)),
    ("5", "Batalha de Frutas 1v1", "Corte mais frutas e fatie combos simultaneos", "versus_fruit_battle.py", (240, 60, 240)),
    ("6", "Guerra Espacial 1v1", "Pilote naves espaciais com tiros e escudos", "versus_space_battle.py", (255, 220, 40)),
    ("7", "Volei Touchless 1v1", "Corte a bola por cima da rede no ar", "versus_volleyball.py", (40, 240, 200)),
    ("8", "Tapa e Esquiva 1v1", "Classico jogo da maozinha sem encostar", "versus_slap_dodge.py", (50, 130, 255))
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

    active_tab = 0  # 0: SOLO / ARCADE, 1: VERSUS 1v1
    hover_target = None  # ('tab', 0/1) ou ('game', idx)
    hover_start = 0.0
    SELECTION_HOLD = 0.60
    fps = 30.0
    last_fps_t = time.time()

    print("\n" + "="*65)
    print(" SENAI TOUCHLESS LAB - CENTRAL DE JOGOS & EXPERIENCIAS")
    print(" 16 Jogos: 8 Solo/Arcade + 8 Duelos 1v1")
    print(" Selecione apontando o dedo indicador ou digitando de 1 a 8!")
    print(" Pressione [TAB] para alternar entre Solo e 1v1 Versus!")
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

        # --- BOTOES DE ABAS NO TOPO ---
        tab1_rect = (25, 58, 305, 84)
        tab2_rect = (335, 58, 615, 84)

        current_detected_target = None

        # Checar hover nas abas
        if tip_pos:
            if tab1_rect[0] <= tip_pos[0] <= tab1_rect[2] and tab1_rect[1] <= tip_pos[1] <= tab1_rect[3]:
                current_detected_target = ('tab', 0)
            elif tab2_rect[0] <= tip_pos[0] <= tab2_rect[2] and tab2_rect[1] <= tip_pos[1] <= tab2_rect[3]:
                current_detected_target = ('tab', 1)

        # Desenhar Aba 1
        t1_active = (active_tab == 0)
        t1_col = (0, 220, 255) if t1_active else (80, 80, 80)
        t1_bg = 0.6 if t1_active else 0.25
        overlay1 = frame.copy()
        cv2.rectangle(overlay1, (tab1_rect[0], tab1_rect[1]), (tab1_rect[2], tab1_rect[3]), t1_col, -1)
        cv2.addWeighted(overlay1, t1_bg, frame, 1 - t1_bg, 0, frame)
        cv2.rectangle(frame, (tab1_rect[0], tab1_rect[1]), (tab1_rect[2], tab1_rect[3]), t1_col, 2 if t1_active else 1)
        cv2.putText(frame, "[1-8] MODO SOLO / ARCADE (8)", (tab1_rect[0] + 16, tab1_rect[1] + 18),
                    cv2.FONT_HERSHEY_DUPLEX, 0.46, (255, 255, 255) if t1_active else (180, 180, 180), 1)

        # Desenhar Aba 2
        t2_active = (active_tab == 1)
        t2_col = (0, 140, 255) if t2_active else (80, 80, 80)
        t2_bg = 0.6 if t2_active else 0.25
        overlay2 = frame.copy()
        cv2.rectangle(overlay2, (tab2_rect[0], tab2_rect[1]), (tab2_rect[2], tab2_rect[3]), t2_col, -1)
        cv2.addWeighted(overlay2, t2_bg, frame, 1 - t2_bg, 0, frame)
        cv2.rectangle(frame, (tab2_rect[0], tab2_rect[1]), (tab2_rect[2], tab2_rect[3]), t2_col, 2 if t2_active else 1)
        cv2.putText(frame, "[1-8] MODO 1v1 VERSUS (8)", (tab2_rect[0] + 28, tab2_rect[1] + 18),
                    cv2.FONT_HERSHEY_DUPLEX, 0.46, (255, 255, 255) if t2_active else (180, 180, 180), 1)

        # --- GRID DE CARDS DOS JOGOS DA ABA ATIVA ---
        active_list = SOLO_GAMES if active_tab == 0 else VERSUS_GAMES

        card_w = 284
        card_h = 70
        gap_x = 22
        gap_y = 10
        start_x = 25
        start_y = 96

        for idx, (num, title, desc, script, col) in enumerate(active_list):
            col_idx = idx % 2
            row_idx = idx // 2
            x1 = start_x + col_idx * (card_w + gap_x)
            y1 = start_y + row_idx * (card_h + gap_y)
            x2 = x1 + card_w
            y2 = y1 + card_h

            is_hover = False
            if tip_pos and (x1 <= tip_pos[0] <= x2 and y1 <= tip_pos[1] <= y2):
                is_hover = True
                current_detected_target = ('game', idx)

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
            cv2.rectangle(frame, (x1 + 8, y1 + 8), (x1 + 34, y1 + 34), col, -1)
            cv2.putText(frame, num, (x1 + 15, y1 + 27), cv2.FONT_HERSHEY_DUPLEX, 0.55, (255, 255, 255), 1)

            # Titulo e Descricao
            title_col = (255, 255, 255) if is_hover else (240, 240, 240)
            cv2.putText(frame, title, (x1 + 42, y1 + 26), cv2.FONT_HERSHEY_DUPLEX, 0.46, title_col, 1)
            cv2.putText(frame, desc, (x1 + 12, y1 + 54), cv2.FONT_HERSHEY_SIMPLEX, 0.33, (190, 190, 190), 1)

        # --- LOGICA DE SELECAO GESTUAL POR APONTAMENTO ---
        if current_detected_target is not None:
            if current_detected_target == hover_target:
                duration = t_now - hover_start
                pct = min(1.0, duration / SELECTION_HOLD)

                if tip_pos:
                    # Mira com anel de carregamento animado
                    r_out = int(14 + pct * 18)
                    cv2.circle(frame, tip_pos, r_out, (0, 255, 120), 2)
                    cv2.circle(frame, tip_pos, 6, (0, 255, 255), -1)

                if duration >= SELECTION_HOLD:
                    t_type, t_val = current_detected_target
                    if t_type == 'tab':
                        if active_tab != t_val:
                            active_tab = t_val
                            try:
                                winsound.Beep(900, 50)
                            except Exception:
                                pass
                        hover_target = None
                    elif t_type == 'game':
                        chosen_script = active_list[t_val][3]
                        cv2.destroyAllWindows()
                        cap.release()
                        launch_game(chosen_script)
                        return main()
            else:
                hover_target = current_detected_target
                hover_start = t_now
                try:
                    winsound.Beep(750, 20)
                except Exception:
                    pass
        else:
            hover_target = None
            if tip_pos:
                # Cursor normal de rastreamento
                cv2.circle(frame, tip_pos, 7, (0, 255, 255), -1)
                cv2.circle(frame, tip_pos, 11, (255, 255, 255), 1)

        # Banner Superior Tecnologico com a Logo do SENAI
        hud_mode = "SOLO / ARCADE" if active_tab == 0 else "1v1 VERSUS"
        draw_glow_banner(frame, "SENAI TOUCHLESS LAB", f"MODO {hud_mode}", fps)

        # Rodape Informativo
        cv2.rectangle(frame, (0, H - 28), (W, H), (10, 12, 18), -1)
        cv2.putText(frame, "[TAB] Alternar Modo | Digite [1-8] ou Aponte para Escolher | [q] Sair",
                    (25, H - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (180, 220, 255), 1)

        cv2.imshow("SENAI Touchless Lab - Central de Jogos", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == 9:  # TAB key
            active_tab = 1 if active_tab == 0 else 0
            try: winsound.Beep(900, 50)
            except Exception: pass
        elif key == ord('t') or key == ord('T'):
            active_tab = 1 if active_tab == 0 else 0
            try: winsound.Beep(900, 50)
            except Exception: pass
        elif key == ord('s') or key == ord('S'):
            active_tab = 0
            try: winsound.Beep(900, 50)
            except Exception: pass
        elif key == ord('v') or key == ord('V'):
            active_tab = 1
            try: winsound.Beep(900, 50)
            except Exception: pass
        elif ord('1') <= key <= ord('8'):
            game_idx = key - ord('1')
            chosen_script = active_list[game_idx][3]
            cv2.destroyAllWindows()
            cap.release()
            launch_game(chosen_script)
            return main()

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
