"""
IRON MAN: DEFESA DE REPULSORES (JARVIS TARGET BLASTER)
Defenda a cidade destruindo os drones invasores usando os repulsores do Homem de Ferro!
Controles:
- Mova a palma da mao para mirar.
- Feche o punho ou abra a palma virada para a camera para DISPARAR o raio repulsor!
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
from camera_helper import get_usb_camera_cap

class Drone:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.x = random.randint(60, w - 60)
        self.y = -30
        self.vy = random.uniform(1.8, 3.8)
        self.radius = random.randint(22, 28)
        self.hp = 1
        self.dead = False
        self.color = (0, 100, 255)  # Laranja/Inimigo

    def update(self):
        self.y += self.vy
        if self.y > self.h - 40:
            self.dead = True
            return True  # Atingiu a base
        return False

    def draw(self, frame):
        cx, cy = int(self.x), int(self.y)
        # Corpo do drone
        cv2.circle(frame, (cx, cy), self.radius, self.color, -1)
        cv2.circle(frame, (cx, cy), self.radius + 3, (0, 200, 255), 1)
        # Olho do drone
        cv2.circle(frame, (cx, cy), 8, (0, 0, 255), -1)
        # Helices / Asas
        cv2.line(frame, (cx - self.radius - 8, cy), (cx + self.radius + 8, cy), (200, 200, 200), 2)


class LaserExplosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 6
        self.max_radius = random.randint(28, 42)
        self.life = 1.0

    def update(self):
        self.radius += 3.5
        self.life -= 0.08

    def draw(self, frame):
        if self.life > 0:
            cx, cy = int(self.x), int(self.y)
            cv2.circle(frame, (cx, cy), int(self.radius), (0, 255, 255), 2)
            cv2.circle(frame, (cx, cy), max(1, int(self.radius * 0.6)), (255, 255, 255), -1)


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

    print("\n[IRON MAN BLASTER INICIADO] Mire com a mao e atire fechando ou empurrando a palma!")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        t_now = time.time()

        results = hands.process(rgb)
        palm_pos = None
        is_firing = False

        if results.multi_hand_landmarks:
            lms = results.multi_hand_landmarks[0].landmark
            wrist = (int(lms[0].x * W), int(lms[0].y * H))
            mcp = (int(lms[9].x * W), int(lms[9].y * H))
            palm_pos = ((wrist[0] + mcp[0]) // 2, (wrist[1] + mcp[1]) // 2)

            # Deteccao de disparo:
            # Gesto de tiro: Pinca rapida entre polegar e indicador OU punho fechado
            tip_idx = (int(lms[8].x * W), int(lms[8].y * H))
            tip_thb = (int(lms[4].x * W), int(lms[4].y * H))
            pinch_dist = math.hypot(tip_idx[0] - tip_thb[0], tip_idx[1] - tip_thb[1])

            # Contagem de dedos estendidos
            fingers_ext = sum(
                math.hypot(lms[tip].x - lms[0].x, lms[tip].y - lms[0].y) >
                math.hypot(lms[pip].x - lms[0].x, lms[pip].y - lms[0].y) * 1.15
                for tip, pip in [(8, 6), (12, 10), (16, 14), (20, 18)]
            )

            # Disparo acionado com a pinca ou punho fechado
            if (pinch_dist < 32 or fingers_ext == 0) and (t_now - last_shot_time) > 0.22 and arc_energy >= 14:
                is_firing = True
                last_shot_time = t_now
                arc_energy -= 14
                try:
                    winsound.Beep(1200, 40)
                except Exception:
                    pass

        # Recarga passiva de energia do Arc Reactor
        arc_energy = min(100.0, arc_energy + 0.6)

        # Spawner de drones inimigos
        if not game_over and (t_now - last_spawn) > max(0.8, 2.0 - (score * 0.04)):
            drones.append(Drone(W, H))
            last_spawn = t_now

        # Atualiza drones
        for d in drones:
            hit_base = d.update()
            if hit_base:
                base_hp -= 15
                try:
                    winsound.Beep(300, 100)
                except Exception:
                    pass
                if base_hp <= 0:
                    base_hp = 0
                    game_over = True

        # Logica de Tiro e Colisao
        if is_firing and palm_pos and not game_over:
            target_hit = None
            closest_dist = 9999
            for d in drones:
                # Verifica raio laser vertical para cima da mira
                dx = abs(d.x - palm_pos[0])
                if dx < (d.radius + 24) and d.y < palm_pos[1]:
                    dist_to_palm = palm_pos[1] - d.y
                    if dist_to_palm < closest_dist:
                        closest_dist = dist_to_palm
                        target_hit = d

            if target_hit:
                target_hit.dead = True
                score += 10
                explosions.append(LaserExplosion(target_hit.x, target_hit.y))
                try:
                    winsound.Beep(700, 50)
                except Exception:
                    pass

        drones = [d for d in drones if not d.dead]

        # Desenha drones
        for d in drones:
            d.draw(frame)

        # Atualiza e desenha explosoes
        for exp in explosions:
            exp.update()
            exp.draw(frame)
        explosions = [e for e in explosions if e.life > 0]

        # Desenha Mira e Feixe do Homem de Ferro
        if palm_pos:
            cx, cy = palm_pos
            # Feixe laser quando atira
            if is_firing:
                cv2.line(frame, (cx, cy), (cx, 0), (0, 255, 255), 6)
                cv2.line(frame, (cx, cy), (cx, 0), (255, 255, 255), 2)
                cv2.circle(frame, (cx, cy), 32, (0, 255, 255), -1)

            # Reator Arc Holografico / Mira na palma
            cv2.circle(frame, (cx, cy), 26, (0, 220, 255), 2)
            cv2.circle(frame, (cx, cy), 12, (0, 255, 255), -1)
            cv2.circle(frame, (cx, cy), 4, (255, 255, 255), -1)
            # Linhas da mira
            cv2.line(frame, (cx - 36, cy), (cx - 16, cy), (0, 240, 255), 2)
            cv2.line(frame, (cx + 16, cy), (cx + 36, cy), (0, 240, 255), 2)
            cv2.line(frame, (cx, cy - 36), (cx, cy - 16), (0, 240, 255), 2)
            cv2.line(frame, (cx, cy + 16), (cx, cy + 36), (0, 240, 255), 2)

        # HUD Jarvis Superior
        hud_bg = frame.copy()
        cv2.rectangle(hud_bg, (0, 0), (W, 55), (10, 15, 22), -1)
        cv2.addWeighted(hud_bg, 0.85, frame, 0.15, 0, frame)
        cv2.line(frame, (0, 55), (W, 55), (0, 200, 255), 1)

        cv2.putText(frame, f"SCORE: {score}", (15, 36), cv2.FONT_HERSHEY_DUPLEX, 0.65, (0, 255, 255), 1)

        # Barra de HP da Base
        cv2.putText(frame, "CIDADE:", (180, 36), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1)
        hp_color = (0, 255, 100) if base_hp > 40 else (0, 0, 255)
        cv2.rectangle(frame, (250, 22), (370, 40), (40, 40, 40), -1)
        cv2.rectangle(frame, (250, 22), (250 + int(120 * (base_hp / 100)), 40), hp_color, -1)
        cv2.rectangle(frame, (250, 22), (370, 40), (200, 200, 200), 1)

        # Barra do Reator Arc
        cv2.putText(frame, "ARC CORE:", (390, 36), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 255, 255), 1)
        cv2.rectangle(frame, (485, 22), (615, 40), (40, 40, 40), -1)
        cv2.rectangle(frame, (485, 22), (485 + int(130 * (arc_energy / 100)), 40), (0, 230, 255), -1)
        cv2.rectangle(frame, (485, 22), (615, 40), (0, 255, 255), 1)

        # Game Over
        if game_over:
            overlay = frame.copy()
            cv2.rectangle(overlay, (80, 160), (W - 80, 340), (10, 10, 30), -1)
            cv2.addWeighted(overlay, 0.85, frame, 0.15, 0, frame)
            cv2.putText(frame, "CIDADE DESTRUÍDA!", (150, 220), cv2.FONT_HERSHEY_DUPLEX, 1.0, (0, 0, 255), 2)
            cv2.putText(frame, f"Pontos Defendidos: {score}", (200, 265), cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), 1)
            cv2.putText(frame, "Pressione 'R' para Reiniciar Jarvis", (145, 305), cv2.FONT_HERSHEY_DUPLEX, 0.6, (0, 255, 200), 1)

        cv2.imshow("Iron Man Repulsor Blaster - Pressione 'q' para sair", frame)

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
