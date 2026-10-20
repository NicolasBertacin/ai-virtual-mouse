"""
JOKENPO IA (PEDRA, PAPEL E TESOURA TOUCHLESS) - SENAI LAB
Jogue Pedra, Papel e Tesoura contra a Inteligencia Artificial usando as maos!
Controles:
- Feche o punho = PEDRA
- Abra a palma inteira = PAPEL
- Levante Indicador + Medio = TESOURA
- Pressione 'ESPACO' para iniciar a rodada com contagem regressiva!
- Pressione 'r' para zerar o placar.
- Pressione 'q' para sair.
"""

import cv2
import numpy as np
import mediapipe as mp
import random
import time
import math
import winsound
from camera_helper import get_usb_camera_cap, draw_glow_banner

def classify_hand(lms, W, H):
    wrist = (int(lms[0].x * W), int(lms[0].y * H))
    
    def is_ext(tip_idx, pip_idx):
        tip = (int(lms[tip_idx].x * W), int(lms[tip_idx].y * H))
        pip = (int(lms[pip_idx].x * W), int(lms[pip_idx].y * H))
        return math.hypot(tip[0] - wrist[0], tip[1] - wrist[1]) > math.hypot(pip[0] - wrist[0], pip[1] - wrist[1]) * 1.15

    idx_ext = is_ext(8, 6)
    mid_ext = is_ext(12, 10)
    rng_ext = is_ext(16, 14)
    pnk_ext = is_ext(20, 18)

    ext_count = sum([idx_ext, mid_ext, rng_ext, pnk_ext])

    if ext_count == 0:
        return "PEDRA"
    elif ext_count >= 4:
        return "PAPEL"
    elif idx_ext and mid_ext and not rng_ext and not pnk_ext:
        return "TESOURA"
    return "AGUARDANDO GESTO"


def determine_winner(player, ai):
    if player == ai:
        return "EMPATE!"
    if (player == "PEDRA" and ai == "TESOURA") or \
       (player == "PAPEL" and ai == "PEDRA") or \
       (player == "TESOURA" and ai == "PAPEL"):
        return "VOCE VENCEU!"
    return "IA VENCEU!"


def draw_gesture_card(frame, x, y, title, gesture, color):
    w, h = 180, 150
    overlay = frame.copy()
    cv2.rectangle(overlay, (x, y), (x + w, y + h), (15, 20, 30), -1)
    cv2.addWeighted(overlay, 0.85, frame, 0.15, 0, frame)

    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
    cv2.putText(frame, title, (x + 20, y + 30), cv2.FONT_HERSHEY_DUPLEX, 0.55, (200, 200, 200), 1)

    # Simbolo do gesto
    icon_text = "[ # ]" if gesture == "PEDRA" else ("[---]" if gesture == "PAPEL" else "[ X ]")
    cv2.putText(frame, icon_text, (x + 45, y + 78), cv2.FONT_HERSHEY_DUPLEX, 0.9, color, 2)
    cv2.putText(frame, gesture, (x + 24, y + 120), cv2.FONT_HERSHEY_DUPLEX, 0.65, (255, 255, 255), 1)


def main():
    W, H = 640, 480
    cap, cam_name, cam_idx = get_usb_camera_cap(W, H)
    if not cap.isOpened():
        print(f"Erro ao abrir camera USB {cam_name}")
        return

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)

    choices = ["PEDRA", "PAPEL", "TESOURA"]
    player_score = 0
    ai_score = 0
    draws = 0

    state = "WAITING"
    countdown_start = 0.0
    countdown_val = 3
    ai_choice = None
    player_choice = None
    round_result = None
    fps = 30.0
    last_fps_t = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        t_now = time.time()

        dt = t_now - last_fps_t
        if dt > 0:
            fps = 0.9 * fps + 0.1 * (1.0 / dt)
        last_fps_t = t_now

        results = hands.process(rgb)
        current_gesture = "NENHUMA MAO"

        if results.multi_hand_landmarks:
            lms = results.multi_hand_landmarks[0].landmark
            current_gesture = classify_hand(lms, W, H)
            wrist_x = int(lms[0].x * W)
            wrist_y = int(lms[0].y * H)
            cv2.circle(frame, (wrist_x, wrist_y), 9, (0, 255, 255), -1)

        if state == "COUNTDOWN":
            elapsed = t_now - countdown_start
            remaining = 3.2 - elapsed

            if remaining > 2.0:
                countdown_val = 3
            elif remaining > 1.0:
                countdown_val = 2
            elif remaining > 0.0:
                countdown_val = 1
            else:
                state = "RESULT"
                ai_choice = random.choice(choices)
                player_choice = current_gesture if current_gesture in choices else "PEDRA"
                round_result = determine_winner(player_choice, ai_choice)
                if round_result == "VOCE VENCEU!":
                    player_score += 1
                    try:
                        winsound.Beep(920, 140)
                    except Exception:
                        pass
                elif round_result == "IA VENCEU!":
                    ai_score += 1
                    try:
                        winsound.Beep(320, 140)
                    except Exception:
                        pass
                else:
                    draws += 1
                    try:
                        winsound.Beep(600, 90)
                    except Exception:
                        pass

        # Header Tecnologico SENAI
        draw_glow_banner(frame, "JOKENPO IA", f"VOCE: {player_score} | IA: {ai_score} | EMPATES: {draws}", fps)

        if state == "WAITING":
            overlay = frame.copy()
            cv2.rectangle(overlay, (W // 2 - 180, H - 90), (W // 2 + 180, H - 20), (10, 14, 22), -1)
            cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)
            cv2.rectangle(frame, (W // 2 - 180, H - 90), (W // 2 + 180, H - 20), (0, 200, 255), 1)

            cv2.putText(frame, f"Seu Gesto: {current_gesture}", (W // 2 - 150, H - 60), cv2.FONT_HERSHEY_DUPLEX, 0.65, (0, 255, 255), 1)
            cv2.putText(frame, "Pressione [ESPACO] para Jogar", (W // 2 - 150, H - 34), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (255, 255, 255), 1)

        elif state == "COUNTDOWN":
            # Circulos de contagem regressiva pulsantes
            pulse = int((t_now * 8) % 25)
            cv2.circle(frame, (W // 2, H // 2), 70 + pulse, (0, 255, 255), 2)
            cv2.circle(frame, (W // 2, H // 2), 55, (10, 14, 25), -1)
            cv2.circle(frame, (W // 2, H // 2), 55, (0, 200, 255), 2)
            cv2.putText(frame, str(countdown_val), (W // 2 - 18, H // 2 + 20), cv2.FONT_HERSHEY_DUPLEX, 2.2, (0, 255, 255), 4)

            cv2.putText(frame, f"Gesto Atual: {current_gesture}", (W // 2 - 120, H - 40), cv2.FONT_HERSHEY_DUPLEX, 0.65, (255, 255, 255), 1)

        elif state == "RESULT":
            # Cards dos dois jogadores
            draw_gesture_card(frame, 90, 150, "VOCE JOGOU", player_choice, (0, 255, 120))
            draw_gesture_card(frame, W - 270, 150, "A IA JOGOU", ai_choice, (0, 140, 255))

            # VS no centro
            cv2.putText(frame, "VS", (W // 2 - 20, 230), cv2.FONT_HERSHEY_DUPLEX, 1.2, (200, 200, 200), 2)

            # Banner do Vencedor
            res_col = (0, 255, 120) if round_result == "VOCE VENCEU!" else ((0, 100, 255) if round_result == "IA VENCEU!" else (255, 255, 0))
            overlay = frame.copy()
            cv2.rectangle(overlay, (W // 2 - 190, 330), (W // 2 + 190, 420), (10, 10, 20), -1)
            cv2.addWeighted(overlay, 0.85, frame, 0.15, 0, frame)
            cv2.rectangle(frame, (W // 2 - 190, 330), (W // 2 + 190, 420), res_col, 2)

            cv2.putText(frame, round_result, (W // 2 - 120, 368), cv2.FONT_HERSHEY_DUPLEX, 0.95, res_col, 2)
            cv2.putText(frame, "Pressione [ESPACO] para Nova Rodada", (W // 2 - 165, 402), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)

        cv2.imshow("SENAI Jokenpo AI Touchless - Pressione 'q' para sair", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == 32:  # Barra de espaço
            state = "COUNTDOWN"
            countdown_start = time.time()
        elif key == ord('r'):
            player_score = 0
            ai_score = 0
            draws = 0
            state = "WAITING"

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
