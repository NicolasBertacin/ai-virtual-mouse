"""
SIMON SAYS / GENIUS TOUCHLESS (MEMORIA GESTUAL)
Memorize a sequencia de cores e reproduza apontando com a mao no ar!
Controles:
- Observe a sequencia de cores e sons que o computador demonstrar.
- Aponte com o dedo indicador para o quadrante correspondente no ar.
- A cada acerto, uma nova cor e adicionada a sequencia!
- Pressione 'ESPACO' para comecar.
- Pressione 'q' para sair.
"""

import cv2
import numpy as np
import mediapipe as mp
import random
import time
import math
import winsound
import threading
from camera_helper import get_usb_camera_cap

def play_tone(freq, dur=180):
    def _t():
        try:
            winsound.Beep(freq, dur)
        except Exception:
            pass
    threading.Thread(target=_t, daemon=True).start()


class Quadrant:
    def __init__(self, name, x1, y1, x2, y2, color, freq):
        self.name = name
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.color = color
        self.freq = freq
        self.is_active = False
        self.active_until = 0.0

    def contains(self, px, py):
        return self.x1 <= px <= self.x2 and self.y1 <= py <= self.y2

    def flash(self, duration=0.3):
        self.is_active = True
        self.active_until = time.time() + duration
        play_tone(self.freq, int(duration * 1000))

    def update(self):
        if self.is_active and time.time() > self.active_until:
            self.is_active = False

    def draw(self, frame):
        alpha = 0.6 if self.is_active else 0.2
        col = (255, 255, 255) if self.is_active else self.color
        
        overlay = frame.copy()
        cv2.rectangle(overlay, (self.x1, self.y1), (self.x2, self.y2), col, -1)
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

        border_w = 4 if self.is_active else 1
        cv2.rectangle(frame, (self.x1, self.y1), (self.x2, self.y2), col, border_w)
        cv2.putText(frame, self.name, (self.x1 + 25, self.y1 + 45), cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), 1)


def main():
    W, H = 640, 480
    cap, cam_name, cam_idx = get_usb_camera_cap(W, H)
    if not cap.isOpened():
        print(f"Erro ao abrir camera USB {cam_name}")
        return

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)

    # 4 Quadrantes
    quads = [
        Quadrant("VERDE", 30, 60, W // 2 - 10, H // 2 - 10, (0, 220, 100), 523),      # C5 (Superior Esquerdo)
        Quadrant("VERMELHO", W // 2 + 10, 60, W - 30, H // 2 - 10, (30, 40, 240), 659), # E5 (Superior Direito)
        Quadrant("AMARELO", 30, H // 2 + 10, W // 2 - 10, H - 30, (0, 220, 240), 784),  # G5 (Inferior Esquerdo)
        Quadrant("AZUL", W // 2 + 10, H // 2 + 10, W - 30, H - 30, (240, 140, 0), 1046)  # C6 (Inferior Direito)
    ]

    sequence = []
    player_step = 0
    state = "START"  # START, COMPUTER_SHOW, PLAYER_INPUT, GAME_OVER
    level = 1

    last_show_time = 0.0
    show_index = 0
    hover_quad = None
    hover_start = 0.0
    TRIGGER_HOLD_TIME = 0.45  # Tempo apontando para confirmar selecao

    print("\n[GENIUS / SIMON SAYS INICIADO] Pressione ESPACO para iniciar!")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        t_now = time.time()

        for q in quads:
            q.update()

        results = hands.process(rgb)
        tip_pos = None

        if results.multi_hand_landmarks:
            lms = results.multi_hand_landmarks[0].landmark
            tip_pos = (int(lms[8].x * W), int(lms[8].y * H))
            # Desenha cursor na ponta do dedo
            cv2.circle(frame, tip_pos, 8, (0, 255, 255), -1)
            cv2.circle(frame, tip_pos, 14, (255, 255, 255), 1)

        # Maquina de Estados
        if state == "START":
            cv2.putText(frame, "GENIUS TOUCHLESS", (W // 2 - 150, H // 2 - 20), cv2.FONT_HERSHEY_DUPLEX, 1.0, (0, 255, 255), 2)
            cv2.putText(frame, "Pressione [ESPACO] para Comecar", (W // 2 - 170, H // 2 + 30), cv2.FONT_HERSHEY_DUPLEX, 0.65, (255, 255, 255), 1)

        elif state == "COMPUTER_SHOW":
            if t_now - last_show_time > 0.65:
                if show_index < len(sequence):
                    target_q = sequence[show_index]
                    quads[target_q].flash(0.4)
                    show_index += 1
                    last_show_time = t_now
                else:
                    # Terminou de mostrar, vez do jogador
                    state = "PLAYER_INPUT"
                    player_step = 0
                    hover_quad = None

        elif state == "PLAYER_INPUT":
            # Detecta quadrante sob a mira
            current_target = None
            if tip_pos:
                for idx, q in enumerate(quads):
                    if q.contains(tip_pos[0], tip_pos[1]):
                        current_target = idx
                        break

            if current_target is not None:
                if current_target == hover_quad:
                    # Segurando sobre o quadrante
                    hold_time = t_now - hover_start
                    pct = min(1.0, hold_time / TRIGGER_HOLD_TIME)
                    # Desenha anel de progresso
                    cv2.circle(frame, tip_pos, int(14 + pct * 16), (0, 255, 120), 2)

                    if hold_time >= TRIGGER_HOLD_TIME:
                        # Confirma escolha
                        quads[current_target].flash(0.3)
                        hover_quad = None

                        if current_target == sequence[player_step]:
                            player_step += 1
                            if player_step >= len(sequence):
                                # Rodada concluida!
                                level += 1
                                sequence.append(random.randint(0, 3))
                                state = "COMPUTER_SHOW"
                                show_index = 0
                                last_show_time = t_now + 0.5
                        else:
                            # Errou!
                            play_tone(220, 350)
                            state = "GAME_OVER"
                else:
                    hover_quad = current_target
                    hover_start = t_now
            else:
                hover_quad = None

        elif state == "GAME_OVER":
            overlay = frame.copy()
            cv2.rectangle(overlay, (80, 150), (W - 80, 330), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)
            cv2.putText(frame, "FIM DE JOGO!", (W // 2 - 130, 215), cv2.FONT_HERSHEY_DUPLEX, 1.2, (0, 0, 255), 2)
            cv2.putText(frame, f"Voce alcancou o Nivel: {level}", (W // 2 - 140, 260), cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), 1)
            cv2.putText(frame, "Pressione [ESPACO] para Reiniciar", (W // 2 - 165, 300), cv2.FONT_HERSHEY_DUPLEX, 0.6, (0, 255, 200), 1)

        # Desenha Quadrantes
        for q in quads:
            q.draw(frame)

        # HUD Superior
        cv2.rectangle(frame, (0, 0), (W, 45), (15, 15, 20), -1)
        cv2.putText(frame, f"NIVEL: {level}", (20, 30), cv2.FONT_HERSHEY_DUPLEX, 0.7, (0, 255, 255), 2)
        status_msg = "MEMORIZE A SEQUENCIA" if state == "COMPUTER_SHOW" else ("SUA VEZ (APONTE E SEGURE)" if state == "PLAYER_INPUT" else "")
        cv2.putText(frame, status_msg, (W // 2 - 130, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 120), 1)
        cv2.putText(frame, "[Q] Sair", (W - 90, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 180, 180), 1)

        cv2.imshow("Genius Simon Says Touchless - Pressione 'q' para sair", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == 32:  # Espaço
            if state in ["START", "GAME_OVER"]:
                sequence = [random.randint(0, 3)]
                level = 1
                state = "COMPUTER_SHOW"
                show_index = 0
                last_show_time = time.time() + 0.3

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
