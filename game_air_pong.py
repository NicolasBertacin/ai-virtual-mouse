"""
AIR PONG TOUCHLESS (ARCADE EDITION)
Jogue Pong no ar usando sua mao como raquete!
Controles:
- Mova a palma da mao para cima e para baixo para controlar a raquete.
- No modo 1 Jogador: Jogue contra a Inteligencia Artificial.
- No modo 2 Jogadores: Duas pessoas jogam na mesma camera (Mao Esquerda vs Mao Direita).
- Pressione 'm' para alternar entre 1 Jogador (vs IA) e 2 Jogadores.
- Pressione 'r' para reiniciar o placar.
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

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-4, 4)
        self.vy = random.uniform(-4, 4)
        self.color = color
        self.life = 1.0

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 0.05

    def draw(self, frame):
        if self.life > 0:
            cv2.circle(frame, (int(self.x), int(self.y)), max(1, int(4 * self.life)), self.color, -1)


def main():
    W, H = 640, 480
    cap, cam_name, cam_idx = get_usb_camera_cap(W, H)
    if not cap.isOpened():
        print(f"Erro ao abrir camera USB {cam_name}")
        return

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.7)

    # Parametros das Raquetes
    PADDLE_W = 16
    PADDLE_H = 100
    p1_y = H // 2
    p2_y = H // 2
    p1_score = 0
    p2_score = 0
    WINNING_SCORE = 5

    # Bola
    ball_radius = 12
    ball_x = W // 2
    ball_y = H // 2
    ball_speed = 7.0
    ball_vx = ball_speed if random.random() > 0.5 else -ball_speed
    ball_vy = random.uniform(-3.5, 3.5)

    mode_2players = False
    particles = []
    print("\n[AIR PONG INICIADO] Mova sua mao verticalmente para rebater a bola!")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = hands.process(rgb)
        
        detected_p1_y = None
        detected_p2_y = None

        if results.multi_hand_landmarks:
            for lms in results.multi_hand_landmarks:
                # Centro da palma
                cx = int(lms.landmark[9].x * W)
                cy = int(lms.landmark[9].y * H)
                if cx < W // 2:
                    detected_p1_y = cy
                else:
                    detected_p2_y = cy

        # Suavizacao da Raquete 1 (Esquerda)
        if detected_p1_y is not None:
            p1_y = int(0.7 * p1_y + 0.3 * detected_p1_y)
        p1_y = max(PADDLE_H // 2, min(H - PADDLE_H // 2, p1_y))

        # Raquete 2 (Direita) - Jogador 2 ou IA
        if mode_2players:
            if detected_p2_y is not None:
                p2_y = int(0.7 * p2_y + 0.3 * detected_p2_y)
        else:
            # IA inteligente com ligeira inercia
            target = ball_y
            p2_y += int(np.clip(target - p2_y, -5.5, 5.5))
        p2_y = max(PADDLE_H // 2, min(H - PADDLE_H // 2, p2_y))

        # Fisica da Bola (se ninguem venceu ainda)
        if p1_score < WINNING_SCORE and p2_score < WINNING_SCORE:
            ball_x += ball_vx
            ball_y += ball_vy

            # Colisao com Teto e Chao
            if ball_y - ball_radius <= 50 or ball_y + ball_radius >= H - 10:
                ball_vy = -ball_vy
                try:
                    winsound.Beep(500, 20)
                except Exception:
                    pass

            # Colisao Raquete 1 (Esquerda)
            p1_x = 35
            if (p1_x - PADDLE_W // 2) <= ball_x - ball_radius <= (p1_x + PADDLE_W // 2) and ball_vx < 0:
                if (p1_y - PADDLE_H // 2) <= ball_y <= (p1_y + PADDLE_H // 2):
                    offset = (ball_y - p1_y) / (PADDLE_H / 2)
                    ball_vx = abs(ball_vx) * 1.05  # Aumenta velocidade gradualmente
                    ball_vy = offset * 6.5
                    try:
                        winsound.Beep(800, 30)
                    except Exception:
                        pass
                    for _ in range(12):
                        particles.append(Particle(ball_x, ball_y, (0, 255, 120)))

            # Colisao Raquete 2 (Direita)
            p2_x = W - 35
            if (p2_x - PADDLE_W // 2) <= ball_x + ball_radius <= (p2_x + PADDLE_W // 2) and ball_vx > 0:
                if (p2_y - PADDLE_H // 2) <= ball_y <= (p2_y + PADDLE_H // 2):
                    offset = (ball_y - p2_y) / (PADDLE_H / 2)
                    ball_vx = -abs(ball_vx) * 1.05
                    ball_vy = offset * 6.5
                    try:
                        winsound.Beep(800, 30)
                    except Exception:
                        pass
                    for _ in range(12):
                        particles.append(Particle(ball_x, ball_y, (0, 200, 255)))

            # Ponto do Jogador 2 (Bola passou pela esquerda)
            if ball_x < -20:
                p2_score += 1
                try:
                    winsound.Beep(350, 100)
                except Exception:
                    pass
                ball_x, ball_y = W // 2, H // 2
                ball_vx = 7.0
                ball_vy = random.uniform(-3, 3)

            # Ponto do Jogador 1 (Bola passou pela direita)
            if ball_x > W + 20:
                p1_score += 1
                try:
                    winsound.Beep(1000, 100)
                except Exception:
                    pass
                ball_x, ball_y = W // 2, H // 2
                ball_vx = -7.0
                ball_vy = random.uniform(-3, 3)

        # Atualiza e desenha particulas
        for p in particles:
            p.update()
            p.draw(frame)
        particles = [p for p in particles if p.life > 0]

        # Desenho da Mesa / Linha Central
        for y in range(60, H, 30):
            cv2.line(frame, (W // 2, y), (W // 2, y + 15), (70, 70, 70), 2)

        # Desenho das Raquetes
        # Raquete 1 (Verde Neon)
        cv2.rectangle(frame, (35 - PADDLE_W // 2, p1_y - PADDLE_H // 2),
                      (35 + PADDLE_W // 2, p1_y + PADDLE_H // 2), (0, 255, 120), -1)
        # Raquete 2 (Ciano / Laranja)
        p2_color = (0, 200, 255) if mode_2players else (50, 100, 255)
        cv2.rectangle(frame, (W - 35 - PADDLE_W // 2, p2_y - PADDLE_H // 2),
                      (W - 35 + PADDLE_W // 2, p2_y + PADDLE_H // 2), p2_color, -1)

        # Desenho da Bola
        cv2.circle(frame, (int(ball_x), int(ball_y)), ball_radius, (255, 255, 255), -1)
        cv2.circle(frame, (int(ball_x), int(ball_y)), ball_radius + 3, (0, 255, 255), 2)

        # Placar e HUD Superior
        cv2.rectangle(frame, (0, 0), (W, 50), (18, 18, 22), -1)
        cv2.putText(frame, f"JOGADOR 1: {p1_score}", (40, 34), cv2.FONT_HERSHEY_DUPLEX, 0.65, (0, 255, 120), 2)
        p2_label = f"JOGADOR 2: {p2_score}" if mode_2players else f"IA: {p2_score}"
        cv2.putText(frame, p2_label, (W - 220, 34), cv2.FONT_HERSHEY_DUPLEX, 0.65, p2_color, 2)

        mode_str = "Modo: 2 Jogadores [M]" if mode_2players else "Modo: Vs IA [M]"
        cv2.putText(frame, mode_str, (W // 2 - 75, 34), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 180, 180), 1)

        # Tela de Vitoria
        if p1_score >= WINNING_SCORE or p2_score >= WINNING_SCORE:
            winner = "JOGADOR 1 VENCEU!" if p1_score >= WINNING_SCORE else ("JOGADOR 2 VENCEU!" if mode_2players else "IA VENCEU!")
            win_color = (0, 255, 120) if p1_score >= WINNING_SCORE else p2_color
            overlay = frame.copy()
            cv2.rectangle(overlay, (100, 170), (W - 100, 310), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)
            cv2.putText(frame, winner, (140, 230), cv2.FONT_HERSHEY_DUPLEX, 1.0, win_color, 2)
            cv2.putText(frame, "Pressione 'R' para Jogar Novamente", (145, 275), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)

        cv2.imshow("Air Pong Touchless - Pressione 'q' para sair", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('m'):
            mode_2players = not mode_2players
        elif key == ord('r'):
            p1_score = 0
            p2_score = 0
            ball_x, ball_y = W // 2, H // 2
            ball_vx = 7.0

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
