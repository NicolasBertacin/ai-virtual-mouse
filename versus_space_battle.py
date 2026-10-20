"""
GUERRA DE NAVES 1v1 (SPACE BATTLE VERSUS) - SENAI LAB
Batalha espacial futurista entre 2 naves comandadas por gestos!
Controles:
- Jogador 1 (Esquerda - Nave Ciano): Mova a mao verticalmente para esquivar.
  Faca pinca ou feche o punho para DISPARAR lasers!
- Jogador 2 (Direita - Nave Vermelha): Mova a mao verticalmente para esquivar.
  Faca pinca ou feche o punho para DISPARAR lasers!
- Destrua o escudo de 100 HP do oponente para vencer!
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

class LaserShot:
    def __init__(self, x, y, direction, color):
        self.x = float(x)
        self.y = float(y)
        self.vx = 14.0 * direction
        self.color = color
        self.dead = False

    def update(self):
        self.x += self.vx
        if self.x < -30 or self.x > 670:
            self.dead = True

    def draw(self, frame):
        cx, cy = int(self.x), int(self.y)
        cv2.line(frame, (cx - int(self.vx * 1.5), cy), (cx, cy), self.color, 4)
        cv2.line(frame, (cx - int(self.vx * 1.5), cy), (cx, cy), (255, 255, 255), 1)


class Explosion:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.radius = 6
        self.life = 1.0

    def update(self):
        self.radius += 3.2
        self.life -= 0.08

    def draw(self, frame):
        if self.life > 0:
            cv2.circle(frame, (int(self.x), int(self.y)), int(self.radius), self.color, 2)
            cv2.circle(frame, (int(self.x), int(self.y)), max(1, int(self.radius * 0.5)), (255, 255, 255), -1)


def draw_spaceship(frame, x, y, direction, color):
    # direction: 1 para direita, -1 para esquerda
    pts = np.array([
        [x + 28 * direction, y],
        [x - 18 * direction, y - 20],
        [x - 8 * direction, y],
        [x - 18 * direction, y + 20]
    ], np.int32)
    cv2.fillPoly(frame, [pts], (25, 30, 45))
    cv2.polylines(frame, [pts], True, color, 2)
    # Fogo do propulsor
    fx = x - 22 * direction
    cv2.circle(frame, (fx, y), 6, (0, 180, 255), -1)
    cv2.circle(frame, (fx, y), 3, (255, 255, 255), -1)


def main():
    W, H = 640, 480
    cap, cam_name, cam_idx = get_usb_camera_cap(W, H)
    if not cap.isOpened():
        print(f"Erro ao abrir camera USB {cam_name}")
        return

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.7)

    p1_y = H // 2
    p2_y = H // 2
    p1_hp = 100.0
    p2_hp = 100.0
    p1_last_shot = 0.0
    p2_last_shot = 0.0

    lasers = []
    explosions = []
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

        # Espaco sideral escuro
        dark = np.zeros_like(frame)
        frame = cv2.addWeighted(frame, 0.35, dark, 0.65, 0)

        results = hands.process(rgb)

        if results.multi_hand_landmarks:
            for lms in results.multi_hand_landmarks:
                wrist = (int(lms.landmark[0].x * W), int(lms.landmark[0].y * H))
                tip_idx = (int(lms.landmark[8].x * W), int(lms.landmark[8].y * H))
                tip_thb = (int(lms.landmark[4].x * W), int(lms.landmark[4].y * H))
                pinch = math.hypot(tip_idx[0] - tip_thb[0], tip_idx[1] - tip_thb[1])

                ext = sum(
                    math.hypot(lms.landmark[tip].x - lms.landmark[0].x, lms.landmark[tip].y - lms.landmark[0].y) >
                    math.hypot(lms.landmark[pip].x - lms.landmark[0].x, lms.landmark[pip].y - lms.landmark[0].y) * 1.15
                    for tip, pip in [(8, 6), (12, 10), (16, 14), (20, 18)]
                )

                cy = int(lms.landmark[9].y * H)
                if wrist[0] < W // 2:
                    p1_y = int(0.7 * p1_y + 0.3 * cy)
                    # Disparo Jogador 1 (Direcao +1)
                    if (pinch < 32 or ext == 0) and (t_now - p1_last_shot) > 0.28 and p1_hp > 0 and p2_hp > 0:
                        lasers.append(LaserShot(65, p1_y, 1, (0, 240, 255)))
                        p1_last_shot = t_now
                        try: winsound.Beep(980, 25)
                        except Exception: pass
                else:
                    p2_y = int(0.7 * p2_y + 0.3 * cy)
                    # Disparo Jogador 2 (Direcao -1)
                    if (pinch < 32 or ext == 0) and (t_now - p2_last_shot) > 0.28 and p1_hp > 0 and p2_hp > 0:
                        lasers.append(LaserShot(W - 65, p2_y, -1, (0, 80, 255)))
                        p2_last_shot = t_now
                        try: winsound.Beep(1150, 25)
                        except Exception: pass

        p1_y = int(np.clip(p1_y, 80, H - 35))
        p2_y = int(np.clip(p2_y, 80, H - 35))

        # Atualiza lasers e colisoes com naves
        p1_x = 45
        p2_x = W - 45

        for shot in lasers:
            shot.update()
            # Laser de P2 atinge P1
            if shot.vx < 0 and abs(shot.x - p1_x) < 26 and abs(shot.y - p1_y) < 28 and p1_hp > 0:
                shot.dead = True
                p1_hp = max(0.0, p1_hp - 15.0)
                explosions.append(Explosion(p1_x, p1_y, (0, 240, 255)))
                try: winsound.Beep(280, 70)
                except Exception: pass

            # Laser de P1 atinge P2
            if shot.vx > 0 and abs(shot.x - p2_x) < 26 and abs(shot.y - p2_y) < 28 and p2_hp > 0:
                shot.dead = True
                p2_hp = max(0.0, p2_hp - 15.0)
                explosions.append(Explosion(p2_x, p2_y, (0, 80, 255)))
                try: winsound.Beep(280, 70)
                except Exception: pass

        lasers = [s for s in lasers if not s.dead]

        # Desenho
        for s in lasers:
            s.draw(frame)

        for exp in explosions:
            exp.update()
            exp.draw(frame)
        explosions = [e for e in explosions if e.life > 0]

        # Desenha Naves
        if p1_hp > 0:
            draw_spaceship(frame, p1_x, p1_y, 1, (0, 240, 255))
        if p2_hp > 0:
            draw_spaceship(frame, p2_x, p2_y, -1, (0, 80, 255))

        # Header Tecnologico SENAI
        draw_glow_banner(frame, "SPACE BATTLE 1v1", "DISPARE COM PINCA OU PUNHO", fps)

        # Barras de Escudo
        cv2.putText(frame, "ESCUDO J1:", (30, H - 28), cv2.FONT_HERSHEY_DUPLEX, 0.45, (0, 240, 255), 1)
        cv2.rectangle(frame, (120, H - 38), (240, H - 22), (30, 30, 30), -1)
        cv2.rectangle(frame, (120, H - 38), (120 + int(120 * (p1_hp / 100)), H - 22), (0, 240, 255), -1)

        cv2.putText(frame, "ESCUDO J2:", (W - 240, H - 28), cv2.FONT_HERSHEY_DUPLEX, 0.45, (0, 80, 255), 1)
        cv2.rectangle(frame, (W - 140, H - 38), (W - 20, H - 22), (30, 30, 30), -1)
        cv2.rectangle(frame, (W - 140, H - 38), (W - 140 + int(120 * (p2_hp / 100)), H - 22), (0, 80, 255), -1)

        # Fim de Jogo
        if p1_hp <= 0 or p2_hp <= 0:
            winner = "NAVE CIANO VENCEU!" if p2_hp <= 0 else "NAVE VERMELHA VENCEU!"
            col = (0, 240, 255) if p2_hp <= 0 else (0, 80, 255)
            ov = frame.copy()
            cv2.rectangle(ov, (100, 170), (W - 100, 310), (10, 10, 20), -1)
            cv2.addWeighted(ov, 0.85, frame, 0.15, 0, frame)
            cv2.putText(frame, winner, (W // 2 - 160, 230), cv2.FONT_HERSHEY_DUPLEX, 1.0, col, 2)
            cv2.putText(frame, "Pressione [R] para Nova Batalha", (W // 2 - 145, 275), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)

        cv2.imshow("SENAI Guerra de Naves 1v1 - Pressione 'q' para sair", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            p1_hp = 100.0
            p2_hp = 100.0
            lasers.clear()
            explosions.clear()

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
