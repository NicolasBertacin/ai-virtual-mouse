"""
SIMULADOR DE PARTICULAS SCI-FI (COSMIC GALAXY TOUCHLESS) - SENAI LAB
Manipule um campo cosmico de centenas de particulas de energia com as maos!
Controles:
- Mao Aberta: CAMPO REPULSOR (Empurra e dispersa as particulas).
- Punho Fechado: BURACO NEGRO MAGNETICO (Atrai as particulas em espiral para o centro da mao).
- Mova a mao no ar para criar um rastro/vortice cosmico fluido.
- Pressione 'c' para alternar a paleta de cores (Ciano, Dourado, Violeta, Fogo).
- Pressione 'r' para resetar a posicao das particulas.
- Pressione 'q' para sair.
"""

import cv2
import numpy as np
import mediapipe as mp
import random
import math
import time
from camera_helper import get_usb_camera_cap, draw_glow_banner

class Particle:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.reset()

    def reset(self):
        self.x = random.uniform(50, self.w - 50)
        self.y = random.uniform(60, self.h - 50)
        self.vx = random.uniform(-1.0, 1.0)
        self.vy = random.uniform(-1.0, 1.0)
        self.size = random.randint(2, 4)

    def update(self, hand_pos, is_attracting, is_repelling):
        self.vx *= 0.94
        self.vy *= 0.94

        if hand_pos:
            hx, hy = hand_pos
            dx = hx - self.x
            dy = hy - self.y
            dist = math.hypot(dx, dy) + 0.001

            if is_attracting:
                # Forca atratora em espiral
                force = min(8.5, 360.0 / (dist + 18))
                self.vx += (dx / dist) * force - (dy / dist) * (force * 0.48)
                self.vy += (dy / dist) * force + (dx / dist) * (force * 0.48)

            elif is_repelling and dist < 230:
                # Forca repulsora de choque
                force = min(12.5, 300.0 / (dist + 10))
                self.vx -= (dx / dist) * force
                self.vy -= (dy / dist) * force

        self.x += self.vx
        self.y += self.vy

        if self.x < 10 or self.x > self.w - 10:
            self.vx = -self.vx
            self.x = np.clip(self.x, 10, self.w - 10)
        if self.y < 55 or self.y > self.h - 10:
            self.vy = -self.vy
            self.y = np.clip(self.y, 55, self.h - 10)


def main():
    W, H = 640, 480
    cap, cam_name, cam_idx = get_usb_camera_cap(W, H)
    if not cap.isOpened():
        print(f"Erro ao abrir camera USB {cam_name}")
        return

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)

    NUM_PARTICLES = 480
    particles = [Particle(W, H) for _ in range(NUM_PARTICLES)]

    palettes = [
        ("CIANO COSMICO", (255, 220, 0), (255, 255, 120)),
        ("SUPERNOVA DOURADA", (0, 190, 255), (0, 255, 255)),
        ("NEBULOSA VIOLETA", (230, 80, 220), (255, 180, 240)),
        ("FOGO SOLAR", (20, 60, 255), (0, 180, 255)),
    ]
    current_pal_idx = 0
    vortex_angle = 0.0
    fps = 30.0
    last_fps_t = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        t_now = time.time()
        vortex_angle += 0.08

        dt = t_now - last_fps_t
        if dt > 0:
            fps = 0.9 * fps + 0.1 * (1.0 / dt)
        last_fps_t = t_now

        # Fundo escuro espacial translucido
        dark_overlay = np.zeros_like(frame)
        frame = cv2.addWeighted(frame, 0.40, dark_overlay, 0.60, 0)

        results = hands.process(rgb)

        hand_pos = None
        is_attracting = False
        is_repelling = False
        mode_label = "MOVA A MAO"

        if results.multi_hand_landmarks:
            lms = results.multi_hand_landmarks[0].landmark
            wrist = (int(lms[0].x * W), int(lms[0].y * H))
            mcp = (int(lms[9].x * W), int(lms[9].y * H))
            hand_pos = ((wrist[0] + mcp[0]) // 2, (wrist[1] + mcp[1]) // 2)

            ext_fingers = sum(
                math.hypot(lms[tip].x - lms[0].x, lms[tip].y - lms[0].y) >
                math.hypot(lms[pip].x - lms[0].x, lms[pip].y - lms[0].y) * 1.15
                for tip, pip in [(8, 6), (12, 10), (16, 14), (20, 18)]
            )

            if ext_fingers >= 4:
                is_repelling = True
                mode_label = "ONDA DE CHOQUE REPULSORA"
            elif ext_fingers == 0:
                is_attracting = True
                mode_label = "BURACO NEGRO MAGNETICO"
            else:
                mode_label = "VORTICE DINAMICO"

        for p in particles:
            p.update(hand_pos, is_attracting, is_repelling)

        col_main, col_glow = palettes[current_pal_idx][1], palettes[current_pal_idx][2]
        for p in particles:
            px, py = int(p.x), int(p.y)
            cv2.circle(frame, (px, py), p.size, col_main, -1)
            if p.size >= 3:
                cv2.circle(frame, (px, py), p.size - 1, col_glow, -1)

        # Efeitos visuais do campo gravitacional na mao
        if hand_pos:
            hx, hy = hand_pos
            if is_attracting:
                cv2.circle(frame, (hx, hy), 24, (10, 10, 10), -1)
                # Anéis espirais girando
                for i in range(4):
                    a = vortex_angle + i * (math.pi / 2)
                    rx = int(32 * math.cos(a))
                    ry = int(32 * math.sin(a))
                    cv2.line(frame, (hx, hy), (hx + rx, hy + ry), col_glow, 2)
                cv2.circle(frame, (hx, hy), 36, col_main, 1)

            elif is_repelling:
                wave_r = int(50 + 20 * math.sin(vortex_angle * 3))
                cv2.circle(frame, (hx, hy), wave_r, col_glow, 2)
                cv2.circle(frame, (hx, hy), max(10, wave_r - 20), col_main, 2)
                cv2.circle(frame, (hx, hy), 12, (255, 255, 255), -1)
            else:
                cv2.circle(frame, (hx, hy), 18, col_glow, 2)

        # Header Tecnologico SENAI
        pal_name = palettes[current_pal_idx][0]
        draw_glow_banner(frame, "PARTICULAS COSMICAS", f"{mode_label}  |  Paleta [C]: {pal_name}", fps)

        cv2.imshow("SENAI Particulas Cosmicas Touchless - Pressione 'q' para sair", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('c'):
            current_pal_idx = (current_pal_idx + 1) % len(palettes)
        elif key == ord('r'):
            for p in particles:
                p.reset()

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
