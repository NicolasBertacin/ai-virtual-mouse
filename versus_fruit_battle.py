"""
FRUIT NINJA VERSUS 1v1 (BATALHA DE FRUTAS) - SENAI LAB
Competicao direta entre 2 jogadores para ver quem fatia mais frutas em 45 segundos!
Controles:
- Jogador 1 (Esquerda - Lamina Ciano): Use o indicador esquerdo para fatiar.
- Jogador 2 (Direita - Lamina Laranja): Use o indicador direito para fatiar.
- Quem cortar a fruta primeiro ganha o ponto!
- Cuidado com as bombas (perde 3 pontos!).
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
        self.vx = random.uniform(-7, 7)
        self.vy = random.uniform(-9, 4)
        self.color = color
        self.size = random.randint(3, 7)
        self.life = 1.0

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.38
        self.life -= 0.045

    def draw(self, frame):
        if self.life > 0:
            radius = max(1, int(self.size * self.life))
            cv2.circle(frame, (int(self.x), int(self.y)), radius, self.color, -1)


class Fruit:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.radius = 32
        self.x = random.randint(110, w - 110)
        self.y = h + 25
        self.vx = (w / 2 - self.x) * random.uniform(0.015, 0.032) + random.uniform(-1.5, 1.5)
        self.vy = random.uniform(-19, -14)
        self.gravity = 0.44
        self.is_bomb = random.random() < 0.22

        types = [
            ("Melancia", (35, 180, 45), (45, 55, 230)),
            ("Laranja", (0, 130, 255), (0, 190, 255)),
            ("Maca", (35, 35, 235), (220, 245, 230)),
            ("Limao", (0, 220, 220), (180, 255, 190))
        ]
        chosen = random.choice(types)
        self.skin_color = (25, 25, 25) if self.is_bomb else chosen[1]
        self.pulp_color = (0, 0, 255) if self.is_bomb else chosen[2]

        self.sliced = False
        self.halves = []
        self.dead = False
        self.cutter = None

    def update(self):
        if not self.sliced:
            self.x += self.vx
            self.y += self.vy
            self.vy += self.gravity
            if self.y > self.h + 70 and self.vy > 0:
                self.dead = True
        else:
            for h in self.halves:
                h['x'] += h['vx']
                h['y'] += h['vy']
                h['vy'] += self.gravity
            if all(h['y'] > self.h + 70 for h in self.halves):
                self.dead = True

    def slice(self, player):
        if not self.sliced:
            self.sliced = True
            self.cutter = player
            self.halves = [
                {'x': self.x - 10, 'y': self.y, 'vx': self.vx - 5.0, 'vy': self.vy - 2.5},
                {'x': self.x + 10, 'y': self.y, 'vx': self.vx + 5.0, 'vy': self.vy - 1.5}
            ]

    def draw(self, frame):
        if not self.sliced:
            cx, cy = int(self.x), int(self.y)
            if self.is_bomb:
                cv2.circle(frame, (cx, cy), self.radius, (20, 20, 20), -1)
                cv2.circle(frame, (cx, cy), self.radius, (0, 0, 255), 2)
                cv2.putText(frame, "X", (cx - 10, cy + 11), cv2.FONT_HERSHEY_DUPLEX, 1.0, (0, 0, 255), 3)
            else:
                cv2.circle(frame, (cx, cy), self.radius, self.skin_color, -1)
                cv2.circle(frame, (cx, cy), self.radius - 6, self.pulp_color, -1)
                cv2.circle(frame, (cx - 9, cy - 9), 6, (255, 255, 255), -1)
                cv2.circle(frame, (cx, cy), self.radius, (255, 255, 255), 1)
        else:
            for h in self.halves:
                hx, hy = int(h['x']), int(h['y'])
                cv2.circle(frame, (hx, hy), self.radius - 5, self.skin_color, -1)
                cv2.circle(frame, (hx, hy), self.radius - 11, self.pulp_color, -1)


def line_intersects_circle(p1, p2, circle_center, radius):
    x1, y1 = p1
    x2, y2 = p2
    cx, cy = circle_center
    dx = x2 - x1
    dy = y2 - y1
    if dx == 0 and dy == 0:
        return math.hypot(cx - x1, cy - y1) <= radius
    t = max(0.0, min(1.0, ((cx - x1) * dx + (cy - y1) * dy) / (dx * dx + dy * dy)))
    closest_x = x1 + t * dx
    closest_y = y1 + t * dy
    return math.hypot(cx - closest_x, cy - closest_y) <= radius


def main():
    W, H = 640, 480
    cap, cam_name, cam_idx = get_usb_camera_cap(W, H)
    if not cap.isOpened():
        print(f"Erro ao abrir camera USB {cam_name}")
        return

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.7)

    fruits = []
    particles = []
    trail1 = []
    trail2 = []
    p1_score = 0
    p2_score = 0

    MATCH_DURATION = 45.0
    start_time = time.time()
    last_spawn = time.time()
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

        time_left = max(0.0, MATCH_DURATION - (t_now - start_time))
        game_over = (time_left <= 0.0)

        results = hands.process(rgb)

        if results.multi_hand_landmarks:
            for lms in results.multi_hand_landmarks:
                tip_x = int(lms.landmark[8].x * W)
                tip_y = int(lms.landmark[8].y * H)
                if tip_x < W // 2:
                    trail1.append((t_now, tip_x, tip_y))
                else:
                    trail2.append((t_now, tip_x, tip_y))

        trail1 = [p for p in trail1 if t_now - p[0] < 0.20]
        trail2 = [p for p in trail2 if t_now - p[0] < 0.20]

        if not game_over and (t_now - last_spawn) > 1.1:
            count = random.choices([1, 2, 3], weights=[0.55, 0.35, 0.1])[0]
            for _ in range(count):
                fruits.append(Fruit(W, H))
            last_spawn = t_now

        # Colisoes de corte
        for fruit in fruits:
            fruit.update()
            if not fruit.sliced and not game_over:
                # Checa corte do Jogador 1 (Ciano)
                if len(trail1) >= 2:
                    p1 = (trail1[-2][1], trail1[-2][2])
                    p2 = (trail1[-1][1], trail1[-1][2])
                    if math.hypot(p2[0]-p1[0], p2[1]-p1[1]) > 14 and line_intersects_circle(p1, p2, (fruit.x, fruit.y), fruit.radius + 8):
                        fruit.slice(1)
                        if fruit.is_bomb:
                            p1_score = max(0, p1_score - 3)
                            try: winsound.Beep(260, 150)
                            except Exception: pass
                            for _ in range(25): particles.append(Particle(fruit.x, fruit.y, (0, 0, 255)))
                        else:
                            p1_score += 1
                            try: winsound.Beep(1000, 35)
                            except Exception: pass
                            for _ in range(20): particles.append(Particle(fruit.x, fruit.y, (0, 240, 255)))

                # Checa corte do Jogador 2 (Laranja) se ainda nao fatiada
                if not fruit.sliced and len(trail2) >= 2:
                    p1 = (trail2[-2][1], trail2[-2][2])
                    p2 = (trail2[-1][1], trail2[-1][2])
                    if math.hypot(p2[0]-p1[0], p2[1]-p1[1]) > 14 and line_intersects_circle(p1, p2, (fruit.x, fruit.y), fruit.radius + 8):
                        fruit.slice(2)
                        if fruit.is_bomb:
                            p2_score = max(0, p2_score - 3)
                            try: winsound.Beep(260, 150)
                            except Exception: pass
                            for _ in range(25): particles.append(Particle(fruit.x, fruit.y, (0, 0, 255)))
                        else:
                            p2_score += 1
                            try: winsound.Beep(1100, 35)
                            except Exception: pass
                            for _ in range(20): particles.append(Particle(fruit.x, fruit.y, (0, 140, 255)))

        fruits = [f for f in fruits if not f.dead]

        for fruit in fruits:
            fruit.draw(frame)

        for p in particles:
            p.update()
            p.draw(frame)
        particles = [p for p in particles if p.life > 0]

        # Desenho das laminas
        # Lamina 1 (Ciano)
        if len(trail1) >= 2:
            for i in range(len(trail1) - 1):
                pt1 = (trail1[i][1], trail1[i][2])
                pt2 = (trail1[i+1][1], trail1[i+1][2])
                cv2.line(frame, pt1, pt2, (0, 240, 255), 8)
                cv2.line(frame, pt1, pt2, (255, 255, 255), 2)

        # Lamina 2 (Laranja)
        if len(trail2) >= 2:
            for i in range(len(trail2) - 1):
                pt1 = (trail2[i][1], trail2[i][2])
                pt2 = (trail2[i+1][1], trail2[i+1][2])
                cv2.line(frame, pt1, pt2, (0, 140, 255), 8)
                cv2.line(frame, pt1, pt2, (255, 255, 255), 2)

        # Divisao central suave
        cv2.line(frame, (W // 2, 55), (W // 2, H), (45, 45, 45), 1)

        # Header Tecnologico SENAI
        draw_glow_banner(frame, "FRUIT BATTLE 1v1", f"J1: {p1_score}  x  J2: {p2_score}  |  TEMPO: {int(time_left)}s", fps)

        if game_over:
            winner = "EMPATE!" if p1_score == p2_score else ("JOGADOR 1 VENCEU!" if p1_score > p2_score else "JOGADOR 2 VENCEU!")
            col = (0, 240, 255) if p1_score > p2_score else ((0, 140, 255) if p2_score > p1_score else (255, 255, 255))
            ov = frame.copy()
            cv2.rectangle(ov, (100, 170), (W - 100, 310), (10, 12, 20), -1)
            cv2.addWeighted(ov, 0.85, frame, 0.15, 0, frame)
            cv2.putText(frame, winner, (W // 2 - 145, 230), cv2.FONT_HERSHEY_DUPLEX, 1.0, col, 2)
            cv2.putText(frame, f"Placar Final: {p1_score} x {p2_score}", (W // 2 - 100, 265), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)
            cv2.putText(frame, "Pressione [R] para Nova Batalha", (W // 2 - 140, 295), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 200), 1)

        cv2.imshow("SENAI Fruit Battle 1v1 - Pressione 'q' para sair", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            p1_score = 0
            p2_score = 0
            start_time = time.time()
            fruits.clear()

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
