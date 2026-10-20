"""
VOLEI TOUCHLESS 1v1 (BEACH VOLLEYBALL VERSUS) - SENAI LAB
Partida de volei de praia 2D por cima da rede com fisica real!
Controles:
- Jogador 1 (Campo Esquerdo): Mova a mao para tocar ou cortar a bola.
- Jogador 2 (Campo Direito): Mova a mao para tocar ou cortar a bola.
- A bola tem gravidade real e nao pode tocar o chao do seu lado!
- Primeiro a fazer 5 pontos vence a partida.
- Pressione 'r' para reiniciar.
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

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-4, 4)
        self.vy = random.uniform(-5, 2)
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

    NET_W = 10
    NET_H = 140
    NET_X = W // 2
    FLOOR_Y = H - 35
    WIN_SCORE = 5

    ball_r = 16
    ball_x = float(W // 4)
    ball_y = float(H // 2)
    ball_vx = 3.5
    ball_vy = -8.0
    gravity = 0.36

    p1_pos = [W // 4, H - 100]
    p2_pos = [3 * W // 4, H - 100]
    p1_score = 0
    p2_score = 0
    particles = []

    fps = 30.0
    last_fps_t = time.time()

    def serve_ball(to_p1=True):
        nonlocal ball_x, ball_y, ball_vx, ball_vy
        ball_x = float(W // 4 if to_p1 else 3 * W // 4)
        ball_y = float(FLOOR_Y - 140)
        ball_vx = float(3.0 if to_p1 else -3.0)
        ball_vy = -8.5

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

        dark = np.zeros_like(frame)
        frame = cv2.addWeighted(frame, 0.40, dark, 0.60, 0)

        results = hands.process(rgb)

        if results.multi_hand_landmarks:
            for lms in results.multi_hand_landmarks:
                cx = int(lms.landmark[9].x * W)
                cy = int(lms.landmark[9].y * H)
                if cx < NET_X:
                    p1_pos[0] = int(np.clip(cx, 30, NET_X - 25))
                    p1_pos[1] = int(np.clip(cy, 80, FLOOR_Y - 10))
                else:
                    p2_pos[0] = int(np.clip(cx, NET_X + 25, W - 30))
                    p2_pos[1] = int(np.clip(cy, 80, FLOOR_Y - 10))

        # Fisica da bola
        if p1_score < WIN_SCORE and p2_score < WIN_SCORE:
            ball_x += ball_vx
            ball_y += ball_vy
            ball_vy += gravity

            # Paredes laterais e teto
            if ball_x - ball_r <= 10:
                ball_x = 10 + ball_r
                ball_vx = abs(ball_vx)
            elif ball_x + ball_r >= W - 10:
                ball_x = W - 10 - ball_r
                ball_vx = -abs(ball_vx)
            if ball_y - ball_r <= 55:
                ball_y = 55 + ball_r
                ball_vy = abs(ball_vy) * 0.8

            # Colisao com a Rede central (x ~ NET_X, y de FLOOR_Y - NET_H ate FLOOR_Y)
            net_top = FLOOR_Y - NET_H
            if (NET_X - NET_W // 2 - ball_r) <= ball_x <= (NET_X + NET_W // 2 + ball_r) and ball_y >= net_top:
                if ball_x < NET_X:
                    ball_x = NET_X - NET_W // 2 - ball_r
                    ball_vx = -abs(ball_vx) * 0.8
                else:
                    ball_x = NET_X + NET_W // 2 + ball_r
                    ball_vx = abs(ball_vx) * 0.8
                try: winsound.Beep(420, 20)
                except Exception: pass

            # Colisao com Jogador 1 (Mao esquerda)
            d1 = math.hypot(ball_x - p1_pos[0], ball_y - p1_pos[1])
            if d1 < (ball_r + 34):
                angle = math.atan2(ball_y - p1_pos[1], ball_x - p1_pos[0])
                ball_vx = math.cos(angle) * 7.5 + 2.0
                ball_vy = -abs(math.sin(angle) * 9.5) - 3.0
                try: winsound.Beep(850, 30)
                except Exception: pass
                for _ in range(12): particles.append(Particle(ball_x, ball_y, (0, 240, 255)))

            # Colisao com Jogador 2 (Mao direita)
            d2 = math.hypot(ball_x - p2_pos[0], ball_y - p2_pos[1])
            if d2 < (ball_r + 34):
                angle = math.atan2(ball_y - p2_pos[1], ball_x - p2_pos[0])
                ball_vx = math.cos(angle) * 7.5 - 2.0
                ball_vy = -abs(math.sin(angle) * 9.5) - 3.0
                try: winsound.Beep(850, 30)
                except Exception: pass
                for _ in range(12): particles.append(Particle(ball_x, ball_y, (0, 140, 255)))

            # Tocou o chao
            if ball_y + ball_r >= FLOOR_Y:
                if ball_x < NET_X:
                    # Caiu no campo 1 -> Ponto de P2
                    p2_score += 1
                    try: winsound.Beep(320, 120)
                    except Exception: pass
                    serve_ball(to_p1=False)
                else:
                    # Caiu no campo 2 -> Ponto de P1
                    p1_score += 1
                    try: winsound.Beep(1000, 120)
                    except Exception: pass
                    serve_ball(to_p1=True)

        # Desenho do Chao de Areia/Quadra
        cv2.rectangle(frame, (0, FLOOR_Y), (W, H), (20, 140, 200), -1)
        cv2.line(frame, (0, FLOOR_Y), (W, FLOOR_Y), (0, 220, 255), 2)

        # Desenho da Rede de Volei
        cv2.rectangle(frame, (NET_X - NET_W // 2, FLOOR_Y - NET_H), (NET_X + NET_W // 2, FLOOR_Y), (240, 240, 240), -1)
        # Borda superior da rede (fita branca)
        cv2.rectangle(frame, (NET_X - NET_W // 2 - 4, FLOOR_Y - NET_H), (NET_X + NET_W // 2 + 4, FLOOR_Y - NET_H + 8), (0, 0, 255), -1)

        # Desenho das Maos / Raquetes dos Jogadores
        cv2.circle(frame, (p1_pos[0], p1_pos[1]), 28, (0, 240, 255), 2)
        cv2.circle(frame, (p1_pos[0], p1_pos[1]), 12, (0, 240, 255), -1)

        cv2.circle(frame, (p2_pos[0], p2_pos[1]), 28, (0, 140, 255), 2)
        cv2.circle(frame, (p2_pos[0], p2_pos[1]), 12, (0, 140, 255), -1)

        # Desenho da Bola de Volei (Listrada Amarela e Azul)
        bx, by = int(ball_x), int(ball_y)
        cv2.circle(frame, (bx, by), ball_r, (0, 220, 255), -1)
        cv2.circle(frame, (bx, by), ball_r - 5, (255, 180, 0), -1)
        cv2.circle(frame, (bx, by), ball_r, (255, 255, 255), 2)

        for p in particles:
            p.update()
            p.draw(frame)
        particles = [p for p in particles if p.life > 0]

        # Header Tecnologico SENAI
        draw_glow_banner(frame, "VOLEI TOUCHLESS 1v1", f"J1: {p1_score}  x  J2: {p2_score}", fps)

        if p1_score >= WIN_SCORE or p2_score >= WIN_SCORE:
            winner = "JOGADOR 1 VENCEU!" if p1_score >= WIN_SCORE else "JOGADOR 2 VENCEU!"
            col = (0, 240, 255) if p1_score >= WIN_SCORE else (0, 140, 255)
            ov = frame.copy()
            cv2.rectangle(ov, (100, 170), (W - 100, 310), (10, 12, 20), -1)
            cv2.addWeighted(ov, 0.85, frame, 0.15, 0, frame)
            cv2.putText(frame, winner, (W // 2 - 150, 230), cv2.FONT_HERSHEY_DUPLEX, 1.0, col, 2)
            cv2.putText(frame, "Pressione [R] para Novo Jogo", (W // 2 - 140, 275), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)

        cv2.imshow("SENAI Volei Touchless 1v1 - Pressione 'q' para sair", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            p1_score = 0
            p2_score = 0
            serve_ball(True)

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
