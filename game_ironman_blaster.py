"""
IRON MAN: DEFESA DE REPULSORES (JARVIS TARGET BLASTER) - SENAI LAB
Defenda a cidade destruindo os drones invasores usando os repulsores do Homem de Ferro!
Controles:
- Mova a palma da mao para mirar.
- Faca uma pinca rapida ou feche o punho para DISPARAR o raio repulsor!
- Economize energia do Reator Arc.
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

class Drone:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.x = random.randint(70, w - 70)
        self.y = -35
        self.vy = random.uniform(1.8, 3.8)
        self.radius = random.randint(24, 30)
        self.dead = False
        self.rotor_angle = 0.0

    def update(self):
        self.y += self.vy
        self.rotor_angle += 0.4
        if self.y > self.h - 45:
            self.dead = True
            return True
        return False

    def draw(self, frame):
        cx, cy = int(self.x), int(self.y)
        # Helices girando
        rx = int(22 * math.cos(self.rotor_angle))
        ry = int(8 * math.sin(self.rotor_angle))
        cv2.line(frame, (cx - 25 - rx, cy - 12 - ry), (cx - 25 + rx, cy - 12 + ry), (220, 220, 220), 2)
        cv2.line(frame, (cx + 25 - rx, cy - 12 - ry), (cx + 25 + rx, cy - 12 + ry), (220, 220, 220), 2)

        # Bracos e motores
        cv2.line(frame, (cx - 25, cy - 12), (cx, cy), (100, 100, 100), 2)
        cv2.line(frame, (cx + 25, cy - 12), (cx, cy), (100, 100, 100), 2)

        # Chassi do drone
        cv2.circle(frame, (cx, cy), self.radius, (35, 45, 60), -1)
        cv2.circle(frame, (cx, cy), self.radius, (0, 140, 255), 2)
        # Olho de mira vermelho
        cv2.circle(frame, (cx, cy), 9, (0, 0, 255), -1)
        cv2.circle(frame, (cx, cy), 4, (255, 255, 255), -1)


class LaserExplosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 6
        self.max_radius = random.randint(32, 48)
        self.life = 1.0

    def update(self):
        self.radius += 3.8
        self.life -= 0.08

    def draw(self, frame):
        if self.life > 0:
            cx, cy = int(self.x), int(self.y)
            cv2.circle(frame, (cx, cy), int(self.radius), (0, 255, 255), 2)
            cv2.circle(frame, (cx, cy), max(1, int(self.radius * 0.6)), (255, 255, 255), -1)


def draw_arc_reactor_hud(frame, center, angle):
    cx, cy = center
    # Anel externo com ticks giratorios
    cv2.circle(frame, (cx, cy), 32, (0, 220, 255), 2)
    for i in range(8):
        a = angle + i * (math.pi / 4)
        x1 = int(cx + 26 * math.cos(a))
        y1 = int(cy + 26 * math.sin(a))
        x2 = int(cx + 34 * math.cos(a))
        y2 = int(cy + 34 * math.sin(a))
        cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)

    # Anel intermediario em sentido oposto
    for i in range(6):
        a = -angle * 1.5 + i * (math.pi / 3)
        x1 = int(cx + 16 * math.cos(a))
        y1 = int(cy + 16 * math.sin(a))
        x2 = int(cx + 22 * math.cos(a))
        y2 = int(cy + 22 * math.sin(a))
        cv2.line(frame, (x1, y1), (x2, y2), (255, 255, 255), 1)

    # Nucleo de energia
    cv2.circle(frame, (cx, cy), 12, (0, 255, 255), -1)
    cv2.circle(frame, (cx, cy), 5, (255, 255, 255), -1)


def main():
    W, H = 640, 480
    cap, cam_name, cam_idx = get_usb_camera_cap(W, H)
    if not cap.isOpened():
        print(f"Erro ao abrir camera USB {cam_name}")
        return

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)

    drones = []
    explosions = []
    score = 0
    base_hp = 100
    arc_energy = 100.0
    game_over = False
    last_spawn = time.time()
    last_shot_time = 0.0
    hud_angle = 0.0
    fps = 30.0
    last_fps_t = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        t_now = time.time()
        hud_angle += 0.06

        dt = t_now - last_fps_t
        if dt > 0:
            fps = 0.9 * fps + 0.1 * (1.0 / dt)
        last_fps_t = t_now

        results = hands.process(rgb)
        palm_pos = None
        is_firing = False

        if results.multi_hand_landmarks:
            lms = results.multi_hand_landmarks[0].landmark
            wrist = (int(lms[0].x * W), int(lms[0].y * H))
            mcp = (int(lms[9].x * W), int(lms[9].y * H))
            palm_pos = ((wrist[0] + mcp[0]) // 2, (wrist[1] + mcp[1]) // 2)

            tip_idx = (int(lms[8].x * W), int(lms[8].y * H))
            tip_thb = (int(lms[4].x * W), int(lms[4].y * H))
            pinch_dist = math.hypot(tip_idx[0] - tip_thb[0], tip_idx[1] - tip_thb[1])

            fingers_ext = sum(
                math.hypot(lms[tip].x - lms[0].x, lms[tip].y - lms[0].y) >
                math.hypot(lms[pip].x - lms[0].x, lms[pip].y - lms[0].y) * 1.15
                for tip, pip in [(8, 6), (12, 10), (16, 14), (20, 18)]
            )

            if (pinch_dist < 32 or fingers_ext == 0) and (t_now - last_shot_time) > 0.22 and arc_energy >= 14:
                is_firing = True
                last_shot_time = t_now
                arc_energy -= 14
                try:
                    winsound.Beep(1200, 35)
                except Exception:
                    pass

        arc_energy = min(100.0, arc_energy + 0.65)

        if not game_over and (t_now - last_spawn) > max(0.75, 1.9 - (score * 0.03)):
            drones.append(Drone(W, H))
            last_spawn = t_now

        for d in drones:
            hit_base = d.update()
            if hit_base:
                base_hp -= 15
                try:
                    winsound.Beep(280, 90)
                except Exception:
                    pass
                if base_hp <= 0:
                    base_hp = 0
                    game_over = True

        if is_firing and palm_pos and not game_over:
            target_hit = None
            closest_dist = 9999
            for d in drones:
                dx = abs(d.x - palm_pos[0])
                if dx < (d.radius + 26) and d.y < palm_pos[1]:
                    dist_to_palm = palm_pos[1] - d.y
                    if dist_to_palm < closest_dist:
                        closest_dist = dist_to_palm
                        target_hit = d

            if target_hit:
                target_hit.dead = True
                score += 10
                explosions.append(LaserExplosion(target_hit.x, target_hit.y))
                try:
                    winsound.Beep(750, 45)
                except Exception:
                    pass

        drones = [d for d in drones if not d.dead]

        for d in drones:
            d.draw(frame)

        for exp in explosions:
            exp.update()
            exp.draw(frame)
        explosions = [e for e in explosions if e.life > 0]

        if palm_pos:
            cx, cy = palm_pos
            if is_firing:
                # Raio Plasma com nucleo branco e aura ciano
                cv2.line(frame, (cx, cy), (cx, 0), (255, 200, 0), 10)
                cv2.line(frame, (cx, cy), (cx, 0), (0, 255, 255), 6)
                cv2.line(frame, (cx, cy), (cx, 0), (255, 255, 255), 2)
                cv2.circle(frame, (cx, cy), 36, (0, 255, 255), -1)

            draw_arc_reactor_hud(frame, (cx, cy), hud_angle)

        # Header Tecnologico SENAI
        draw_glow_banner(frame, "IRON MAN BLASTER", f"SCORE: {score}", fps)

        # Barras de Energia e Vida da Cidade
        cv2.putText(frame, "CIDADE:", (W - 350, 34), cv2.FONT_HERSHEY_DUPLEX, 0.45, (255, 255, 255), 1)
        hp_col = (0, 255, 120) if base_hp > 40 else (0, 0, 255)
        cv2.rectangle(frame, (W - 280, 22), (W - 190, 36), (30, 30, 30), -1)
        cv2.rectangle(frame, (W - 280, 22), (W - 280 + int(90 * (base_hp / 100)), 36), hp_col, -1)
        cv2.rectangle(frame, (W - 280, 22), (W - 190, 36), (180, 180, 180), 1)

        cv2.putText(frame, "ARC:", (W - 170, 34), cv2.FONT_HERSHEY_DUPLEX, 0.45, (0, 255, 255), 1)
        cv2.rectangle(frame, (W - 130, 22), (W - 40, 36), (30, 30, 30), -1)
        cv2.rectangle(frame, (W - 130, 22), (W - 130 + int(90 * (arc_energy / 100)), 36), (0, 240, 255), -1)
        cv2.rectangle(frame, (W - 130, 22), (W - 40, 36), (0, 255, 255), 1)

        if game_over:
            overlay = frame.copy()
            cv2.rectangle(overlay, (70, 150), (W - 70, 330), (10, 10, 25), -1)
            cv2.addWeighted(overlay, 0.85, frame, 0.15, 0, frame)
            cv2.putText(frame, "CIDADE DESTRUÍDA!", (W // 2 - 160, 210), cv2.FONT_HERSHEY_DUPLEX, 1.0, (0, 0, 255), 2)
            cv2.putText(frame, f"Pontos Defendidos: {score}", (W // 2 - 110, 255), cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), 1)
            cv2.putText(frame, "Pressione [R] para Reiniciar Jarvis", (W // 2 - 145, 295), cv2.FONT_HERSHEY_DUPLEX, 0.6, (0, 255, 200), 1)

        cv2.imshow("SENAI Iron Man Blaster - Pressione 'q' para sair", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r') and game_over:
            score = 0
            base_hp = 100
            arc_energy = 100.0
            game_over = False
            drones.clear()
            explosions.clear()

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
