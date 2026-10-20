"""
JOKENPO IA (PEDRA, PAPEL E TESOURA TOUCHLESS)
Jogue Pedra, Papel e Tesoura contra a Inteligencia Artificial usando as maos!
Controles:
- Feche o punho = PEDRA
- Abra a palma inteira = PAPEL
- Levante Indicador + Medio = TESOURA
- Pressione 'ESPACO' para iniciar uma rodada com contagem regressiva!
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
from camera_helper import get_usb_camera_cap

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
    return "INDEFINIDO"


def determine_winner(player, ai):
    if player == ai:
        return "EMPATE!"
    if (player == "PEDRA" and ai == "TESOURA") or \
       (player == "PAPEL" and ai == "PEDRA") or \
       (player == "TESOURA" and ai == "PAPEL"):
        return "VOCE VENCEU!"
    return "IA VENCEU!"


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

    state = "WAITING"  # WAITING, COUNTDOWN, RESULT
    countdown_start = 0.0
    countdown_val = 3
    ai_choice = None
    player_choice = None
    round_result = None

    print("\n[JOKENPO INICIADO] Pressione ESPACO para iniciar a rodada!")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        t_now = time.time()

        results = hands.process(rgb)
        current_gesture = "NENHUMA MAO"

        if results.multi_hand_landmarks:
            lms = results.multi_hand_landmarks[0].landmark
            current_gesture = classify_hand(lms, W, H)
            # Desenha contorno na mao
            wrist_x = int(lms[0].x * W)
            wrist_y = int(lms[0].y * H)
            cv2.circle(frame, (wrist_x, wrist_y), 8, (0, 255, 255), -1)

        # Maquina de Estados
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
                # Hora do disparo!
                state = "RESULT"
                ai_choice = random.choice(choices)
                player_choice = current_gesture if current_gesture in choices else "PEDRA"
                round_result = determine_winner(player_choice, ai_choice)
                if round_result == "VOCE VENCEU!":
                    player_score += 1
                    try:
                        winsound.Beep(900, 150)
                    except Exception:
                        pass
                elif round_result == "IA VENCEU!":
                    ai_score += 1
                    try:
                        winsound.Beep(320, 150)
                    except Exception:
                        pass
                else:
                    draws += 1
                    try:
                        winsound.Beep(600, 100)
                    except Exception:
                        pass

        # HUD Superior
        cv2.rectangle(frame, (0, 0), (W, 55), (15, 18, 25), -1)
        cv2.putText(frame, f"VOCE: {player_score}", (20, 36), cv2.FONT_HERSHEY_DUPLEX, 0.7, (0, 255, 120), 2)
        cv2.putText(frame, f"IA: {ai_score}", (W - 130, 36), cv2.FONT_HERSHEY_DUPLEX, 0.7, (0, 100, 255), 2)
        cv2.putText(frame, f"Empates: {draws}", (W // 2 - 50, 36), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        # Exibicao Central
        if state == "WAITING":
            cv2.putText(frame, f"Seu Gesto: {current_gesture}", (W // 2 - 130, H - 70), cv2.FONT_HERSHEY_DUPLEX, 0.7, (0, 255, 255), 2)
            cv2.putText(frame, "Pressione [ESPACO] para Jogar", (W // 2 - 165, H - 30), cv2.FONT_HERSHEY_DUPLEX, 0.65, (255, 255, 255), 1)

        elif state == "COUNTDOWN":
            cv2.putText(frame, str(countdown_val), (W // 2 - 30, H // 2 + 30), cv2.FONT_HERSHEY_DUPLEX, 3.5, (0, 255, 255), 6)
            cv2.putText(frame, f"Seu Gesto: {current_gesture}", (W // 2 - 130, H - 40), cv2.FONT_HERSHEY_DUPLEX, 0.7, (200, 200, 200), 2)

        elif state == "RESULT":
            overlay = frame.copy()
            cv2.rectangle(overlay, (40, 130), (W - 40, 360), (10, 10, 20), -1)
            cv2.addWeighted(overlay, 0.85, frame, 0.15, 0, frame)

            res_color = (0, 255, 120) if round_result == "VOCE VENCEU!" else ((0, 100, 255) if round_result == "IA VENCEU!" else (255, 255, 0))
            cv2.putText(frame, round_result, (W // 2 - 130, 190), cv2.FONT_HERSHEY_DUPLEX, 1.1, res_color, 2)
            cv2.putText(frame, f"Voce jogou: {player_choice}", (80, 245), cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), 1)
            cv2.putText(frame, f"A IA jogou:  {ai_choice}", (80, 285), cv2.FONT_HERSHEY_DUPLEX, 0.7, (0, 200, 255), 1)
            cv2.putText(frame, "Pressione [ESPACO] para Proxima Rodada", (100, 335), cv2.FONT_HERSHEY_DUPLEX, 0.6, (0, 255, 200), 1)

        cv2.imshow("Jokenpo AI Touchless - Pressione 'q' para sair", frame)

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
