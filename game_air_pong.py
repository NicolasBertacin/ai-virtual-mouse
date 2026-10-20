"""
AIR PONG TOUCHLESS (CYBER ARCADE EDITION) - SENAI LAB
Jogue Pong no ar usando sua mao como raquete com visual Tron Neon!
Controles:
- Mova a palma da mao para cima e para baixo para controlar a raquete.
- Pressione 'M' para alternar entre 1 Jogador (vs IA) e 2 Jogadores na mesma camera.
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
from camera_helper import get_usb_camera_cap, draw_glow_banner

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-5, 5)
        self.vy = random.uniform(-5, 5)
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

    PADDLE_W = 18
    PADDLE_H = 105
    p1_y = H // 2
    p2_y = H // 2
    p1_score = 0
    p2_score = 0
    WINNING_SCORE = 5

    ball_radius = 12
    ball_x = W // 2
    ball_y = H // 2
    ball_speed = 7.0
    ball_vx = ball_speed if random.random() > 0.5 else -ball_speed
    ball_vy = random.uniform(-3.5, 3.5)
    ball_trail = []

    mode_2players = False
    particles = []
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

        # Efeito mesa Tron escurecida
        dark_overlay = np.zeros_like(frame)
        frame = cv2.addWeighted(frame, 0.40, dark_overlay, 0.60, 0)

        results = hands.process(rgb)
        detected_p1_y = None
        detected_p2_y = None

        if results.multi_hand_landmarks:
            for lms in results.multi_hand_landmarks:
                cx = int(lms.landmark[9].x * W)
                cy = int(lms.landmark[9].y * H)
                if cx < W // 2:
                    detected_p1_y = cy
                else:
                    detected_p2_y = cy

        if detected_p1_y is not None:
            p1_y = int(0.7 * p1_y + 0.3 * detected_p1_y)
        p1_y = max(PADDLE_H // 2 + 55, min(H - PADDLE_H // 2 - 10, p1_y))

        if mode_2players:
            if detected_p2_y is not None:
                p2_y = int(0.7 * p2_y + 0.3 * detected_p2_y)
        else:
            target = ball_y
            p2_y += int(np.clip(target - p2_y, -5.5, 5.5))
        p2_y = max(PADDLE_H // 2 + 55, min(H - PADDLE_H // 2 - 10, p2_y))

        # Fisica da bola
        if p1_score < WINNING_SCORE and p2_score < WINNING_SCORE:
            ball_x += ball_vx
            ball_y += ball_vy
            ball_trail.append((ball_x, ball_y))
            if len(ball_trail) > 10:
                ball_trail.pop(0)

            # Colisao teto e chao
            if ball_y - ball_radius <= 56 or ball_y + ball_radius >= H - 12:
                ball_vy = -ball_vy
                try:
                    winsound.Beep(520, 20)
                except Exception:
                    pass

            # Colisao Raquete 1
            p1_x = 35
            if (p1_x - PADDLE_W // 2) <= ball_x - ball_radius <= (p1_x + PADDLE_W // 2) and ball_vx < 0:
                if (p1_y - PADDLE_H // 2) <= ball_y <= (p1_y + PADDLE_H // 2):
                    offset = (ball_y - p1_y) / (PADDLE_H / 2)
                    ball_vx = abs(ball_vx) * 1.05
                    ball_vy = offset * 6.5
                    try:
                        winsound.Beep(850, 25)
                    except Exception:
                        pass
                    for _ in range(14):
                        particles.append(Particle(ball_x, ball_y, (0, 255, 120)))

            # Colisao Raquete 2
            p2_x = W - 35
            if (p2_x - PADDLE_W // 2) <= ball_x + ball_radius <= (p2_x + PADDLE_W // 2) and ball_vx > 0:
                if (p2_y - PADDLE_H // 2) <= ball_y <= (p2_y + PADDLE_H // 2):
                    offset = (ball_y - p2_y) / (PADDLE_H / 2)
                    ball_vx = -abs(ball_vx) * 1.05
                    ball_vy = offset * 6.5
                    try:
                        winsound.Beep(850, 25)
                    except Exception:
                        pass
                    for _ in range(14):
                        particles.append(Particle(ball_x, ball_y, (0, 200, 255)))

            if ball_x < -20:
                p2_score += 1
                try:
                    winsound.Beep(320, 90)
                except Exception:
                    pass
                ball_x, ball_y = W // 2, H // 2
                ball_vx = 7.0
                ball_vy = random.uniform(-3, 3)
                ball_trail.clear()

            if ball_x > W + 20:
                p1_score += 1
                try:
                    winsound.Beep(980, 90)
                except Exception:
                    pass
                ball_x, ball_y = W // 2, H // 2
                ball_vx = -7.0
                ball_vy = random.uniform(-3, 3)
                ball_trail.clear()

        # Desenho da linha central pontilhada
        for y in range(65, H - 10, 26):
            cv2.line(frame, (W // 2, y), (W // 2, y + 14), (0, 180, 255), 1)

        # Placar gigante de fundo translucido
        score_overlay = frame.copy()
        cv2.putText(score_overlay, str(p1_score), (W // 4 - 30, H // 2 + 50), cv2.FONT_HERSHEY_DUPLEX, 3.5, (0, 255, 120), 4)
        cv2.putText(score_overlay, str(p2_score), (3 * W // 4 - 30, H // 2 + 50), cv2.FONT_HERSHEY_DUPLEX, 3.5, (0, 200, 255), 4)
        cv2.addWeighted(score_overlay, 0.25, frame, 0.75, 0, frame)

        # Rastro luminoso da bola
        for i, (tx, ty) in enumerate(ball_trail):
            prog = (i + 1) / len(ball_trail)
            r = max(2, int(ball_radius * prog * 0.75))
            cv2.circle(frame, (int(tx), int(ty)), r, (255, 255, 100), -1)

        # Bola com glow
        cv2.circle(frame, (int(ball_x), int(ball_y)), ball_radius + 4, (0, 255, 255), 2)
        cv2.circle(frame, (int(ball_x), int(ball_y)), ball_radius, (255, 255, 255), -1)

        # Raquetes com efeito Neon
        # Raquete 1
        cv2.rectangle(frame, (35 - PADDLE_W // 2, p1_y - PADDLE_H // 2),
                      (35 + PADDLE_W // 2, p1_y + PADDLE_H // 2), (0, 255, 120), -1)
        cv2.rectangle(frame, (35 - PADDLE_W // 2 - 2, p1_y - PADDLE_H // 2 - 2),
                      (35 + PADDLE_W // 2 + 2, p1_y + PADDLE_H // 2 + 2), (255, 255, 255), 1)

        # Raquete 2
        p2_color = (0, 200, 255) if mode_2players else (50, 100, 255)
        cv2.rectangle(frame, (W - 35 - PADDLE_W // 2, p2_y - PADDLE_H // 2),
                      (W - 35 + PADDLE_W // 2, p2_y + PADDLE_H // 2), p2_color, -1)
        cv2.rectangle(frame, (W - 35 - PADDLE_W // 2 - 2, p2_y - PADDLE_H // 2 - 2),
                      (W - 35 + PADDLE_W // 2 + 2, p2_y + PADDLE_H // 2 + 2), (255, 255, 255), 1)

        # Particulas
        for p in particles:
            p.update()
            p.draw(frame)
        particles = [p for p in particles if p.life > 0]

        # Header Tecnologico SENAI
        mode_str = "2 JOGADORES" if mode_2players else "VS IA"
        draw_glow_banner(frame, "AIR PONG CYBER", f"MODO: {mode_str} [M]", fps)

        if p1_score >= WINNING_SCORE or p2_score >= WINNING_SCORE:
            winner = "JOGADOR 1 VENCEU!" if p1_score >= WINNING_SCORE else ("JOGADOR 2 VENCEU!" if mode_2players else "IA VENCEU!")
            win_color = (0, 255, 120) if p1_score >= WINNING_SCORE else p2_color
            overlay = frame.copy()
            cv2.rectangle(overlay, (90, 170), (W - 90, 310), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.85, frame, 0.15, 0, frame)
            cv2.putText(frame, winner, (W // 2 - 150, 230), cv2.FONT_HERSHEY_DUPLEX, 1.0, win_color, 2)
            cv2.putText(frame, "Pressione [R] para Jogar Novamente", (W // 2 - 160, 275), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)

        cv2.imshow("SENAI Air Pong Touchless - Pressione 'q' para sair", frame)

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
            ball_trail.clear()

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
