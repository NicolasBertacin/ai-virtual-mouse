"""
FRUIT NINJA HOLOGRAFICO (TOUCHLESS EDITION) - SENAI LAB
Corte frutas no ar usando a ponta do seu dedo como uma lamina laser neon!
Controles:
- Aponte com o dedo indicador e faca movimentos rapidos de corte no ar.
- Desvie das bombas (pretas com caveira).
- Pressione 'r' para reiniciar quando o jogo acabar.
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

class Splatter:
    def __init__(self, x, y, color):
        self.x = int(x)
        self.y = int(y)
        self.color = color
        self.radius = random.randint(16, 28)
        self.drops = [(random.randint(-25, 25), random.randint(-25, 25), random.randint(3, 8)) for _ in range(6)]
        self.life = 1.0

    def update(self):
        self.life -= 0.025

    def draw(self, frame):
        if self.life > 0:
            alpha = max(0.0, self.life * 0.45)
            overlay = frame.copy()
            cv2.circle(overlay, (self.x, self.y), self.radius, self.color, -1)
            for dx, dy, r in self.drops:
                cv2.circle(overlay, (self.x + dx, self.y + dy), r, self.color, -1)
            cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)


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
        self.life -= 0.04

    def draw(self, frame):
        if self.life > 0:
            radius = max(1, int(self.size * self.life))
            cv2.circle(frame, (int(self.x), int(self.y)), radius, self.color, -1)
            cv2.circle(frame, (int(self.x), int(self.y)), max(1, radius - 1), (255, 255, 255), -1)


class Fruit:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.radius = 32
        self.x = random.randint(90, w - 90)
        self.y = h + 25
        self.vx = (w / 2 - self.x) * random.uniform(0.015, 0.032) + random.uniform(-1.5, 1.5)
        self.vy = random.uniform(-19, -14)
        self.gravity = 0.44
        self.is_bomb = random.random() < 0.22

        types = [
            ("Melancia", (35, 180, 45), (45, 55, 230), (255, 255, 255)),
            ("Laranja", (0, 130, 255), (0, 190, 255), (200, 255, 255)),
            ("Maca", (35, 35, 235), (220, 245, 230), (255, 255, 255)),
            ("Limao", (0, 220, 220), (180, 255, 190), (255, 255, 255)),
            ("Uva", (160, 40, 180), (200, 70, 220), (255, 255, 255))
        ]
        chosen = random.choice(types)
        self.name = chosen[0]
        self.skin_color = (25, 25, 25) if self.is_bomb else chosen[1]
        self.pulp_color = (0, 0, 255) if self.is_bomb else chosen[2]

        self.sliced = False
        self.halves = []
        self.dead = False
        self.angle = 0.0
        self.rot_speed = random.uniform(-0.08, 0.08)

    def update(self):
        self.angle += self.rot_speed
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

    def slice(self):
        if not self.sliced:
            self.sliced = True
            self.halves = [
                {'x': self.x - 10, 'y': self.y, 'vx': self.vx - 5.0, 'vy': self.vy - 2.5},
                {'x': self.x + 10, 'y': self.y, 'vx': self.vx + 5.0, 'vy': self.vy - 1.5}
            ]

    def draw(self, frame):
        if not self.sliced:
            cx, cy = int(self.x), int(self.y)
            if self.is_bomb:
                # Bomba com pavio e fogo
                cv2.circle(frame, (cx, cy), self.radius, (20, 20, 20), -1)
                cv2.circle(frame, (cx, cy), self.radius, (0, 0, 255), 2)
                cv2.putText(frame, "X", (cx - 10, cy + 11), cv2.FONT_HERSHEY_DUPLEX, 1.0, (0, 0, 255), 3)
                # Pavio faiscante
                fx = cx + int(14 * math.cos(self.angle * 4))
                fy = cy - 20 + int(4 * math.sin(self.angle * 4))
                cv2.circle(frame, (fx, fy), 5, (0, 165, 255), -1)
                cv2.circle(frame, (fx, fy), 2, (255, 255, 255), -1)
            else:
                # Efeito 3D com Casca e Polpa
                cv2.circle(frame, (cx, cy), self.radius, self.skin_color, -1)
                cv2.circle(frame, (cx, cy), self.radius - 6, self.pulp_color, -1)
                # Brilho de reflexo especular
                cv2.circle(frame, (cx - 9, cy - 9), 6, (255, 255, 255), -1)
                cv2.circle(frame, (cx, cy), self.radius, (255, 255, 255), 1)
        else:
            for h in self.halves:
                hx, hy = int(h['x']), int(h['y'])
                cv2.circle(frame, (hx, hy), self.radius - 5, self.skin_color, -1)
                cv2.circle(frame, (hx, hy), self.radius - 11, self.pulp_color, -1)
                cv2.circle(frame, (hx, hy), self.radius - 5, (255, 255, 255), 1)


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
    hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)

    fruits = []
    particles = []
    splatters = []
    trail = []
    score = 0
    combo_count = 0
    combo_text = ""
    combo_time = 0.0
    lives = 3
    game_over = False
    last_spawn = time.time()
    spawn_interval = 1.3
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
        blade_point = None

        if results.multi_hand_landmarks:
            lms = results.multi_hand_landmarks[0].landmark
            tip_x = int(lms[8].x * W)
            tip_y = int(lms[8].y * H)
            blade_point = (tip_x, tip_y)
            trail.append((t_now, tip_x, tip_y))

        trail = [p for p in trail if t_now - p[0] < 0.22]

        if not game_over and (t_now - last_spawn) > spawn_interval:
            count = random.choices([1, 2, 3], weights=[0.55, 0.35, 0.1])[0]
            for _ in range(count):
                fruits.append(Fruit(W, H))
            last_spawn = t_now
            spawn_interval = max(0.65, 1.4 - (score * 0.02))

        # Deteccao de corte com pontuacao e combos
        slice_this_frame = 0
        for fruit in fruits:
            fruit.update()
            if not fruit.sliced and not game_over and len(trail) >= 2:
                p1 = (trail[-2][1], trail[-2][2])
                p2 = (trail[-1][1], trail[-1][2])
                dist_moved = math.hypot(p2[0] - p1[0], p2[1] - p1[1])

                if dist_moved > 14 and line_intersects_circle(p1, p2, (fruit.x, fruit.y), fruit.radius + 8):
                    fruit.slice()
                    if fruit.is_bomb:
                        lives -= 1
                        try:
                            winsound.Beep(260, 240)
                        except Exception:
                            pass
                        for _ in range(30):
                            particles.append(Particle(fruit.x, fruit.y, (0, 0, 255)))
                        if lives <= 0:
                            game_over = True
                    else:
                        slice_this_frame += 1
                        score += 1
                        splatters.append(Splatter(fruit.x, fruit.y, fruit.pulp_color))
                        for _ in range(22):
                            particles.append(Particle(fruit.x, fruit.y, fruit.pulp_color))
                        try:
                            winsound.Beep(900 + min(score * 25, 750), 40)
                        except Exception:
                            pass

        if slice_this_frame > 1:
            score += slice_this_frame  # Bonus de combo!
            combo_text = f"COMBO x{slice_this_frame}! +{slice_this_frame}"
            combo_time = t_now

        fruits = [f for f in fruits if not f.dead]

        # Desenha manchas de suco
        for sp in splatters:
            sp.update()
            sp.draw(frame)
        splatters = [s for s in splatters if s.life > 0]

        # Desenha frutas
        for fruit in fruits:
            fruit.draw(frame)

        # Desenha particulas com brilho
        for p in particles:
            p.update()
            p.draw(frame)
        particles = [p for p in particles if p.life > 0]

        # Desenho da Lamina Laser Neon
        if len(trail) >= 2:
            for i in range(len(trail) - 1):
                pt1 = (trail[i][1], trail[i][2])
                pt2 = (trail[i + 1][1], trail[i + 1][2])
                prog = i / len(trail)
                th = max(2, int(prog * 11))
                cv2.line(frame, pt1, pt2, (255, 200, 0), th + 4)     # Halo externo ciano
                cv2.line(frame, pt1, pt2, (255, 255, 120), th)       # Corpo luminoso
                cv2.line(frame, pt1, pt2, (255, 255, 255), max(1, th - 3)) # Nucleo branco puro
            if blade_point:
                cv2.circle(frame, blade_point, 9, (0, 255, 255), -1)
                cv2.circle(frame, blade_point, 5, (255, 255, 255), -1)

        # Exibe texto de Combo
        if t_now - combo_time < 0.8:
            cv2.putText(frame, combo_text, (W // 2 - 110, H // 2 - 40), cv2.FONT_HERSHEY_DUPLEX, 1.1, (0, 255, 255), 3)

        # Cabecalho Moderno SENAI
        draw_glow_banner(frame, "FRUIT NINJA", f"PONTOS: {score}", fps)

        # Indicador de Vidas
        lives_str = "VIDAS: " + ("<3 " * max(0, lives))
        cv2.putText(frame, lives_str, (W - 210, 34), cv2.FONT_HERSHEY_DUPLEX, 0.65, (0, 0, 255), 2)

        # Tela de Game Over
        if game_over:
            overlay = frame.copy()
            cv2.rectangle(overlay, (70, 150), (W - 70, 330), (10, 10, 20), -1)
            cv2.addWeighted(overlay, 0.85, frame, 0.15, 0, frame)
            cv2.putText(frame, "GAME OVER!", (W // 2 - 130, 210), cv2.FONT_HERSHEY_DUPLEX, 1.2, (0, 0, 255), 3)
            cv2.putText(frame, f"Pontuacao Final: {score}", (W // 2 - 110, 255), cv2.FONT_HERSHEY_DUPLEX, 0.75, (255, 255, 255), 1)
            cv2.putText(frame, "Pressione [R] para Reiniciar", (W // 2 - 140, 295), cv2.FONT_HERSHEY_DUPLEX, 0.65, (0, 255, 200), 1)

        cv2.imshow("SENAI Fruit Ninja Touchless - Pressione 'q' para sair", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r') and game_over:
            score = 0
            lives = 3
            game_over = False
            fruits.clear()
            particles.clear()
            splatters.clear()
            trail.clear()

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
