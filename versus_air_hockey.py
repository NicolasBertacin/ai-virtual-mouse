"""
AIR HOCKEY TOUCHLESS 1v1 (VERSUS LOCAL) - SENAI LAB
Partida competitiva de Air Hockey para 2 jogadores na mesma camera!
Controles:
- Jogador 1 (Esquerda - Taco Ciano): Mova a mao esquerda no seu campo.
- Jogador 2 (Direita - Taco Laranja): Mova a mao direita no seu campo.
- Rebata o disco com forca no gol adversario!
- Primeiro a fazer 5 gols vence a partida.
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
        self.vx = random.uniform(-6, 6)
        self.vy = random.uniform(-6, 6)
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

    PADDLE_R = 30
    PUCK_R = 16
    GOAL_H = 150
    WIN_SCORE = 5

    p1_pos = [100, H // 2]
    p2_pos = [W - 100, H // 2]
    p1_score = 0
    p2_score = 0

    puck_x = float(W // 2)
    puck_y = float(H // 2)
    puck_vx = 0.0
    puck_vy = 0.0
    puck_trail = []
    particles = []

    fps = 30.0
    last_fps_t = time.time()

    def reset_puck(to_player=1):
        nonlocal puck_x, puck_y, puck_vx, puck_vy
        puck_x = float(W // 2)
        puck_y = float(H // 2)
        puck_vx = -5.5 if to_player == 1 else 5.5
        puck_vy = random.uniform(-2.5, 2.5)
        puck_trail.clear()

    reset_puck(random.choice([1, 2]))

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

        # Fundo mesa de hockey escura
        dark = np.zeros_like(frame)
        frame = cv2.addWeighted(frame, 0.35, dark, 0.65, 0)

        results = hands.process(rgb)

        # Atualiza posicoes dos tacos
        if results.multi_hand_landmarks:
            for lms in results.multi_hand_landmarks:
                cx = int(lms.landmark[9].x * W)
                cy = int(lms.landmark[9].y * H)
                if cx < W // 2:
                    p1_pos[0] = int(np.clip(cx, PADDLE_R + 10, W // 2 - PADDLE_R - 5))
                    p1_pos[1] = int(np.clip(cy, PADDLE_R + 60, H - PADDLE_R - 10))
                else:
                    p2_pos[0] = int(np.clip(cx, W // 2 + PADDLE_R + 5, W - PADDLE_R - 10))
                    p2_pos[1] = int(np.clip(cy, PADDLE_R + 60, H - PADDLE_R - 10))

        # Fisica do Disco
        if p1_score < WIN_SCORE and p2_score < WIN_SCORE:
            puck_x += puck_vx
            puck_y += puck_vy
            puck_vx *= 0.992
            puck_vy *= 0.992

            puck_trail.append((int(puck_x), int(puck_y)))
            if len(puck_trail) > 8:
                puck_trail.pop(0)

            # Rebote superior e inferior
            if puck_y - PUCK_R <= 58:
                puck_y = 58 + PUCK_R
                puck_vy = abs(puck_vy)
                try: winsound.Beep(450, 15)
                except Exception: pass
            elif puck_y + PUCK_R >= H - 12:
                puck_y = H - 12 - PUCK_R
                puck_vy = -abs(puck_vy)
                try: winsound.Beep(450, 15)
                except Exception: pass

            # Colisao com Taco 1 (Ciano)
            d1 = math.hypot(puck_x - p1_pos[0], puck_y - p1_pos[1])
            if d1 < (PUCK_R + PADDLE_R):
                overlap = (PUCK_R + PADDLE_R) - d1
                angle = math.atan2(puck_y - p1_pos[1], puck_x - p1_pos[0])
                puck_x += math.cos(angle) * overlap
                puck_y += math.sin(angle) * overlap
                speed = math.hypot(puck_vx, puck_vy) + 1.2
                speed = np.clip(speed, 6.0, 16.0)
                puck_vx = math.cos(angle) * speed
                puck_vy = math.sin(angle) * speed
                try: winsound.Beep(850, 20)
                except Exception: pass
                for _ in range(12): particles.append(Particle(puck_x, puck_y, (0, 255, 255)))

            # Colisao com Taco 2 (Laranja)
            d2 = math.hypot(puck_x - p2_pos[0], puck_y - p2_pos[1])
            if d2 < (PUCK_R + PADDLE_R):
                overlap = (PUCK_R + PADDLE_R) - d2
                angle = math.atan2(puck_y - p2_pos[1], puck_x - p2_pos[0])
                puck_x += math.cos(angle) * overlap
                puck_y += math.sin(angle) * overlap
                speed = math.hypot(puck_vx, puck_vy) + 1.2
                speed = np.clip(speed, 6.0, 16.0)
                puck_vx = math.cos(angle) * speed
                puck_vy = math.sin(angle) * speed
                try: winsound.Beep(850, 20)
                except Exception: pass
                for _ in range(12): particles.append(Particle(puck_x, puck_y, (0, 140, 255)))

            # Gol Esquerdo (Ponto de P2)
            goal_top = H // 2 - GOAL_H // 2
            goal_bot = H // 2 + GOAL_H // 2
            if puck_x - PUCK_R <= 15:
                if goal_top <= puck_y <= goal_bot:
                    p2_score += 1
                    try: winsound.Beep(300, 120)
                    except Exception: pass
                    reset_puck(to_player=1)
                else:
                    puck_x = 15 + PUCK_R
                    puck_vx = abs(puck_vx)

            # Gol Direito (Ponto de P1)
            if puck_x + PUCK_R >= W - 15:
                if goal_top <= puck_y <= goal_bot:
                    p1_score += 1
                    try: winsound.Beep(1000, 120)
                    except Exception: pass
                    reset_puck(to_player=2)
                else:
                    puck_x = W - 15 - PUCK_R
                    puck_vx = -abs(puck_vx)

        # Desenho da Mesa de Hockey
        # Linha e circulo central
        cv2.line(frame, (W // 2, 58), (W // 2, H - 12), (0, 180, 255), 2)
        cv2.circle(frame, (W // 2, H // 2), 65, (0, 180, 255), 2)

        # Gols (Aberturas vermelha e azul)
        cv2.line(frame, (15, H // 2 - GOAL_H // 2), (15, H // 2 + GOAL_H // 2), (0, 0, 255), 6)
        cv2.line(frame, (W - 15, H // 2 - GOAL_H // 2), (W - 15, H // 2 + GOAL_H // 2), (0, 255, 0), 6)

        # Tacos dos Jogadores
        cv2.circle(frame, (p1_pos[0], p1_pos[1]), PADDLE_R, (0, 240, 255), -1)
        cv2.circle(frame, (p1_pos[0], p1_pos[1]), PADDLE_R, (255, 255, 255), 2)
        cv2.circle(frame, (p1_pos[0], p1_pos[1]), 8, (255, 255, 255), -1)

        cv2.circle(frame, (p2_pos[0], p2_pos[1]), PADDLE_R, (0, 120, 255), -1)
        cv2.circle(frame, (p2_pos[0], p2_pos[1]), PADDLE_R, (255, 255, 255), 2)
        cv2.circle(frame, (p2_pos[0], p2_pos[1]), 8, (255, 255, 255), -1)

        # Rastro e Disco
        for tx, ty in puck_trail:
            cv2.circle(frame, (tx, ty), PUCK_R - 6, (0, 255, 120), -1)
        cv2.circle(frame, (int(puck_x), int(puck_y)), PUCK_R, (255, 255, 255), -1)
        cv2.circle(frame, (int(puck_x), int(puck_y)), PUCK_R + 2, (0, 255, 120), 2)

        # Particulas
        for p in particles:
            p.update()
            p.draw(frame)
        particles = [p for p in particles if p.life > 0]

        # Header Tecnologico SENAI
        draw_glow_banner(frame, "AIR HOCKEY 1v1", f"J1: {p1_score}  x  J2: {p2_score}", fps)

        # Vitoria
        if p1_score >= WIN_SCORE or p2_score >= WIN_SCORE:
            winner = "JOGADOR 1 VENCEU!" if p1_score >= WIN_SCORE else "JOGADOR 2 VENCEU!"
            col = (0, 240, 255) if p1_score >= WIN_SCORE else (0, 120, 255)
            ov = frame.copy()
            cv2.rectangle(ov, (100, 170), (W - 100, 310), (10, 12, 20), -1)
            cv2.addWeighted(ov, 0.85, frame, 0.15, 0, frame)
            cv2.putText(frame, winner, (W // 2 - 150, 230), cv2.FONT_HERSHEY_DUPLEX, 1.0, col, 2)
            cv2.putText(frame, "Pressione [R] para Reiniciar", (W // 2 - 145, 275), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)

        cv2.imshow("SENAI Air Hockey 1v1 - Pressione 'q' para sair", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            p1_score = 0
            p2_score = 0
            reset_puck()

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
