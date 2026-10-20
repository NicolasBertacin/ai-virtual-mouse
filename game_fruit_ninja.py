"""
FRUIT NINJA HOLOGRAFICO (TOUCHLESS EDITION)
Corte frutas no ar usando a ponta do seu dedo como uma lamina laser!
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
from camera_helper import get_usb_camera_cap

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-6, 6)
        self.vy = random.uniform(-8, 3)
        self.color = color
        self.size = random.randint(3, 6)
        self.life = 1.0

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.35  # gravidade
        self.life -= 0.04

    def draw(self, frame):
        if self.life > 0:
            alpha = max(0.0, self.life)
            radius = max(1, int(self.size * alpha))
            cv2.circle(frame, (int(self.x), int(self.y)), radius, self.color, -1)

class Fruit:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.radius = 28
        self.x = random.randint(80, w - 80)
        self.y = h + 20
        # Velocidades iniciais para arco parabolico
        self.vx = (w / 2 - self.x) * random.uniform(0.015, 0.035) + random.uniform(-1.5, 1.5)
        self.vy = random.uniform(-18, -13)
        self.gravity = 0.42
        self.is_bomb = random.random() < 0.22
        
        types = [
            ("Melancia", (30, 200, 40), (40, 50, 220)),   # casca verde, polpa vermelha
            ("Laranja", (0, 140, 255), (0, 180, 255)),
            ("Maca", (40, 40, 230), (50, 200, 50)),
            ("Limao", (0, 230, 230), (200, 255, 200)),
        ]
        chosen = random.choice(types)
        self.name = chosen[0]
        self.color = (30, 30, 30) if self.is_bomb else chosen[1]
        self.inner_color = (0, 0, 255) if self.is_bomb else chosen[2]

        self.sliced = False
        self.halves = []
        self.dead = False

    def update(self):
        if not self.sliced:
            self.x += self.vx
            self.y += self.vy
            self.vy += self.gravity
            if self.y > self.h + 60 and self.vy > 0:
                self.dead = True
        else:
            # Atualiza as duas metades cortadas
            for h in self.halves:
                h['x'] += h['vx']
                h['y'] += h['vy']
                h['vy'] += self.gravity
            if all(h['y'] > self.h + 60 for h in self.halves):
                self.dead = True

    def slice(self):
        if not self.sliced:
            self.sliced = True
            # Cria duas metades voando para direcoes opostas
            self.halves = [
                {'x': self.x - 8, 'y': self.y, 'vx': self.vx - 4.5, 'vy': self.vy - 2.0},
                {'x': self.x + 8, 'y': self.y, 'vx': self.vx + 4.5, 'vy': self.vy - 1.0}
            ]

    def draw(self, frame):
        if not self.sliced:
            cx, cy = int(self.x), int(self.y)
            if self.is_bomb:
                # Bomba preta com pavio vermelho piscante
                cv2.circle(frame, (cx, cy), self.radius, (25, 25, 25), -1)
                cv2.circle(frame, (cx, cy), self.radius, (0, 0, 255), 2)
                cv2.putText(frame, "X", (cx - 9, cy + 9), cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 0, 255), 2)
                # Fagulha do pavio
                cv2.circle(frame, (cx + 12, cy - 18), 4, (0, 165, 255), -1)
            else:
                cv2.circle(frame, (cx, cy), self.radius, self.color, -1)
                cv2.circle(frame, (cx, cy), self.radius - 6, self.inner_color, -1)
                cv2.circle(frame, (cx - 7, cy - 7), 5, (255, 255, 255), -1)
        else:
            # Desenha metades
            for h in self.halves:
                hx, hy = int(h['x']), int(h['y'])
                cv2.circle(frame, (hx, hy), self.radius - 6, self.color, -1)
                cv2.circle(frame, (hx, hy), self.radius - 12, self.inner_color, -1)


def line_intersects_circle(p1, p2, circle_center, radius):
    """Calcula se o segmento de reta do corte atingiu a fruta"""
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
    trail = []  # rastro da lamina
    score = 0
    lives = 3
    game_over = False
    last_spawn = time.time()
    spawn_interval = 1.3

    print("\n[FRUIT NINJA INICIADO] Use seu dedo indicador para cortar as frutas!")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        t_now = time.time()

        # Deteccao da mao e dedo
        results = hands.process(rgb)
        blade_point = None

        if results.multi_hand_landmarks:
            lms = results.multi_hand_landmarks[0].landmark
            # Ponta do indicador (Landmark 8)
            tip_x = int(lms[8].x * W)
            tip_y = int(lms[8].y * H)
            blade_point = (tip_x, tip_y)
            trail.append((t_now, tip_x, tip_y))

        # Manter apenas os ultimos 0.22s no rastro da lamina
        trail = [p for p in trail if t_now - p[0] < 0.22]

        # Spawner de frutas
        if not game_over and (t_now - last_spawn) > spawn_interval:
            count = random.choices([1, 2, 3], weights=[0.6, 0.3, 0.1])[0]
            for _ in range(count):
                fruits.append(Fruit(W, H))
            last_spawn = t_now
            spawn_interval = max(0.7, 1.4 - (score * 0.02))

        # Atualizacao das frutas e colisao com a lamina
        for fruit in fruits:
            fruit.update()
            if not fruit.sliced and not game_over and len(trail) >= 2:
                # Verifica colisao com o segmento recente do corte
                p1 = (trail[-2][1], trail[-2][2])
                p2 = (trail[-1][1], trail[-1][2])
                dist_moved = math.hypot(p2[0] - p1[0], p2[1] - p1[1])

                # Exige uma velocidade minima de corte
                if dist_moved > 14 and line_intersects_circle(p1, p2, (fruit.x, fruit.y), fruit.radius + 8):
                    fruit.slice()
                    if fruit.is_bomb:
                        lives -= 1
                        try:
                            winsound.Beep(280, 220)
                        except Exception:
                            pass
                        for _ in range(25):
                            particles.append(Particle(fruit.x, fruit.y, (0, 0, 255)))
                        if lives <= 0:
                            game_over = True
                    else:
                        score += 1
                        try:
                            winsound.Beep(850 + min(score * 20, 800), 45)
                        except Exception:
                            pass
                        for _ in range(18):
                            particles.append(Particle(fruit.x, fruit.y, fruit.inner_color))

        fruits = [f for f in fruits if not f.dead]

        # Atualiza e desenha particulas
        for p in particles:
            p.update()
            p.draw(frame)
        particles = [p for p in particles if p.life > 0]

        # Desenha as frutas
        for fruit in fruits:
            fruit.draw(frame)

        # Desenha a Lamina Laser Neon
        if len(trail) >= 2:
            for i in range(len(trail) - 1):
                pt1 = (trail[i][1], trail[i][2])
                pt2 = (trail[i + 1][1], trail[i + 1][2])
                prog = i / len(trail)
                thickness = max(2, int(prog * 9))
                # Glow ciano/neon
                cv2.line(frame, pt1, pt2, (255, 255, 0), thickness)
                cv2.line(frame, pt1, pt2, (255, 255, 255), max(1, thickness - 3))
            if blade_point:
                cv2.circle(frame, blade_point, 7, (0, 255, 255), -1)
                cv2.circle(frame, blade_point, 11, (255, 255, 255), 1)

        # HUD Superior
        cv2.rectangle(frame, (0, 0), (W, 45), (15, 15, 20), -1)
        cv2.putText(frame, f"PONTOS: {score}", (15, 30), cv2.FONT_HERSHEY_DUPLEX, 0.7, (0, 255, 255), 2)
        
        # Coracoes de vidas
        lives_str = "VIDAS: " + ("<3 " * max(0, lives))
        cv2.putText(frame, lives_str, (W - 200, 30), cv2.FONT_HERSHEY_DUPLEX, 0.65, (0, 0, 255), 2)

        # Tela de Game Over
        if game_over:
            overlay = frame.copy()
            cv2.rectangle(overlay, (80, 150), (W - 80, 330), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)
            cv2.putText(frame, "GAME OVER!", (190, 210), cv2.FONT_HERSHEY_DUPLEX, 1.2, (0, 0, 255), 3)
            cv2.putText(frame, f"Pontuacao Final: {score}", (200, 255), cv2.FONT_HERSHEY_DUPLEX, 0.75, (255, 255, 255), 1)
            cv2.putText(frame, "Pressione 'R' para Jogar Novamente", (135, 295), cv2.FONT_HERSHEY_DUPLEX, 0.6, (0, 255, 200), 1)

        cv2.imshow("Fruit Ninja Touchless - Pressione 'q' para sair", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r') and game_over:
            score = 0
            lives = 3
            game_over = False
            fruits.clear()
            particles.clear()
            trail.clear()

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
