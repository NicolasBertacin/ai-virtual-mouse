"""
DUELO DE FAROESTE 1v1 (QUICK DRAW TOUCHLESS) - SENAI LAB
Teste seus reflexos no clássico duelo de gatilho mais rápido do oeste!
Controles:
- Fase 1: Mantenha as maos ABAIXO da linha pontilhada (No Coldre).
- Fase 2: Aguarde o comando em tensao... Se levantar antes, queima a largada!
- Fase 3: Ao surgir 'FOGO!', saque a mao o mais rapido possivel!
- O sistema mede o tempo de reacao exato em milissegundos!
- Melhor de 5 rodadas.
- Pressione 'ESPACO' para iniciar a rodada.
- Pressione 'q' para sair.
"""

import cv2
import numpy as np
import mediapipe as mp
import random
import time
import winsound
from camera_helper import get_usb_camera_cap, draw_glow_banner

def main():
    W, H = 640, 480
    cap, cam_name, cam_idx = get_usb_camera_cap(W, H)
    if not cap.isOpened():
        print(f"Erro ao abrir camera USB {cam_name}")
        return

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.7)

    HOLSTER_Y = 320  # Linha do coldre
    p1_score = 0
    p2_score = 0
    MAX_SCORE = 3

    state = "READY_PROMPT"  # READY_PROMPT, HOLSTER_WAIT, WAITING_FIRE, FIRED, ROUND_OVER, GAME_OVER
    fire_trigger_time = 0.0
    fire_start_timestamp = 0.0
    winner_round = None
    reaction_ms = 0
    foul_player = None

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

        p1_hand_y = None
        p2_hand_y = None

        if results.multi_hand_landmarks:
            for lms in results.multi_hand_landmarks:
                cx = int(lms.landmark[9].x * W)
                cy = int(lms.landmark[9].y * H)
                if cx < W // 2:
                    p1_hand_y = cy
                    cv2.circle(frame, (cx, cy), 14, (0, 240, 255), 2)
                else:
                    p2_hand_y = cy
                    cv2.circle(frame, (cx, cy), 14, (0, 180, 255), 2)

        # Maquina de Estados
        if state == "HOLSTER_WAIT":
            # Aguarda ambos os jogadores colocarem as maos no coldre (y > HOLSTER_Y)
            p1_in_holster = (p1_hand_y is not None and p1_hand_y > HOLSTER_Y)
            p2_in_holster = (p2_hand_y is not None and p2_hand_y > HOLSTER_Y)

            if p1_in_holster and p2_in_holster:
                state = "WAITING_FIRE"
                # Tempo aleatorio entre 2.2 e 5.5 segundos para o disparo
                fire_trigger_time = t_now + random.uniform(2.2, 5.5)

        elif state == "WAITING_FIRE":
            # Checagem de queima de largada (Foul)
            if p1_hand_y is not None and p1_hand_y < HOLSTER_Y:
                foul_player = 1
                p2_score += 1
                state = "ROUND_OVER"
                try: winsound.Beep(250, 250)
                except Exception: pass
            elif p2_hand_y is not None and p2_hand_y < HOLSTER_Y:
                foul_player = 2
                p1_score += 1
                state = "ROUND_OVER"
                try: winsound.Beep(250, 250)
                except Exception: pass
            elif t_now >= fire_trigger_time:
                # HORA DO DISPARO!
                state = "FIRED"
                fire_start_timestamp = t_now
                try: winsound.Beep(1400, 80)
                except Exception: pass

        elif state == "FIRED":
            # Primeiro a sacar acima da linha de coldre vence
            if p1_hand_y is not None and p1_hand_y < HOLSTER_Y:
                winner_round = 1
                reaction_ms = int((t_now - fire_start_timestamp) * 1000)
                p1_score += 1
                state = "ROUND_OVER"
                try: winsound.Beep(950, 120)
                except Exception: pass
            elif p2_hand_y is not None and p2_hand_y < HOLSTER_Y:
                winner_round = 2
                reaction_ms = int((t_now - fire_start_timestamp) * 1000)
                p2_score += 1
                state = "ROUND_OVER"
                try: winsound.Beep(950, 120)
                except Exception: pass

        # Linha pontilhada do Coldre
        for x in range(20, W - 20, 30):
            cv2.line(frame, (x, HOLSTER_Y), (x + 16, HOLSTER_Y), (0, 180, 255), 2)
        cv2.putText(frame, "--- LINHA DO COLDRE (MAOS ABAIXO) ---", (W // 2 - 150, HOLSTER_Y + 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 220, 255), 1)

        # Divisao central
        cv2.line(frame, (W // 2, 60), (W // 2, H), (60, 60, 60), 1)

        # Header Tecnologico SENAI
        draw_glow_banner(frame, "DUELO DE FAROESTE 1v1", f"J1: {p1_score}  x  J2: {p2_score}", fps)

        # Exibicoes de Status e Banners
        if state == "READY_PROMPT":
            ov = frame.copy()
            cv2.rectangle(ov, (110, 160), (W - 110, 280), (10, 12, 20), -1)
            cv2.addWeighted(ov, 0.85, frame, 0.15, 0, frame)
            cv2.putText(frame, "DUELO DE GATILHO RAPIDO", (W // 2 - 175, 205), cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 240, 255), 2)
            cv2.putText(frame, "Pressione [ESPACO] para Iniciar a Rodada", (W // 2 - 180, 245), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (255, 255, 255), 1)

        elif state == "HOLSTER_WAIT":
            cv2.putText(frame, "COLOQUEM AS MAOS NO COLDRE (ABAIXO DA LINHA)",
                        (W // 2 - 230, 180), cv2.FONT_HERSHEY_DUPLEX, 0.65, (0, 255, 255), 2)

        elif state == "WAITING_FIRE":
            # Tensao...
            cv2.putText(frame, "AGUARDE...", (W // 2 - 70, 190), cv2.FONT_HERSHEY_DUPLEX, 1.2, (255, 255, 0), 2)
            cv2.putText(frame, "Nao saque antes da hora!", (W // 2 - 100, 230), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        elif state == "FIRED":
            # Efeito flash vermelho de disparo
            red_flash = np.full_like(frame, (0, 0, 200))
            frame = cv2.addWeighted(frame, 0.65, red_flash, 0.35, 0)
            cv2.putText(frame, "FOGO! SAQUE!", (W // 2 - 150, 210), cv2.FONT_HERSHEY_DUPLEX, 1.6, (255, 255, 255), 4)

        elif state == "ROUND_OVER":
            ov = frame.copy()
            cv2.rectangle(ov, (80, 150), (W - 80, 290), (10, 12, 20), -1)
            cv2.addWeighted(ov, 0.85, frame, 0.15, 0, frame)

            if foul_player:
                cv2.putText(frame, f"QUEIMOU A LARGADA! PONTO P/ JOGADOR {2 if foul_player==1 else 1}!",
                            (W // 2 - 240, 205), cv2.FONT_HERSHEY_DUPLEX, 0.68, (0, 0, 255), 2)
            else:
                w_col = (0, 240, 255) if winner_round == 1 else (0, 180, 255)
                cv2.putText(frame, f"JOGADOR {winner_round} DISPAROU PRIMEIRO!", (W // 2 - 200, 200),
                            cv2.FONT_HERSHEY_DUPLEX, 0.75, w_col, 2)
                cv2.putText(frame, f"Tempo de Reacao: {reaction_ms} ms", (W // 2 - 110, 235),
                            cv2.FONT_HERSHEY_DUPLEX, 0.62, (255, 255, 255), 1)

            if p1_score >= MAX_SCORE or p2_score >= MAX_SCORE:
                final_w = 1 if p1_score >= MAX_SCORE else 2
                cv2.putText(frame, f"JOGADOR {final_w} VENCEU O DUELO!", (W // 2 - 165, 268), cv2.FONT_HERSHEY_DUPLEX, 0.75, (0, 255, 120), 2)
            else:
                cv2.putText(frame, "Pressione [ESPACO] para Proxima Rodada", (W // 2 - 165, 268), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 200), 1)

        cv2.imshow("SENAI Duelo de Faroeste 1v1 - Pressione 'q' para sair", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == 32:  # Barra de espaço
            if p1_score >= MAX_SCORE or p2_score >= MAX_SCORE:
                p1_score = 0
                p2_score = 0
            state = "HOLSTER_WAIT"
            foul_player = None
            winner_round = None

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
