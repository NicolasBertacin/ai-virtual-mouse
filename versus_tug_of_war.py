"""
CABO DE GUERRA DE ENERGIA 1v1 (PLASMA TUG OF WAR) - SENAI LAB
Disputa frenetica de forca e velocidade de gestos entre 2 jogadores!
Controles:
- Jogador 1 (Esquerda - Energia Ciano): Mova e bombe a mao rapidamente.
- Jogador 2 (Direita - Energia Dourada): Mova e bombe a mao rapidamente.
- Quanto mais rapido voce mover sua mao no ar, mais forca empurra a esfera de plasma para o campo do adversario!
- Empurre a esfera alem da linha limite adversaria para vencer!
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

class EnergyParticle:
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
        self.life -= 0.06

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

    sphere_x = float(W // 2)
    sphere_y = float(H // 2 + 20)
    sphere_vx = 0.0

    p1_prev_pos = None
    p2_prev_pos = None
    p1_power = 0.0
    p2_power = 0.0

    particles = []
    game_over = False
    winner_text = ""
    win_color = (255, 255, 255)
    fps = 30.0
    last_fps_t = time.time()
    last_beep_t = 0.0

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
        frame = cv2.addWeighted(frame, 0.35, dark, 0.65, 0)

        results = hands.process(rgb)

        p1_cur_pos = None
        p2_cur_pos = None

        if results.multi_hand_landmarks:
            for lms in results.multi_hand_landmarks:
                cx = int(lms.landmark[9].x * W)
                cy = int(lms.landmark[9].y * H)
                if cx < W // 2:
                    p1_cur_pos = (cx, cy)
                else:
                    p2_cur_pos = (cx, cy)

        # Calculo de velocidade de agitacao / bombeamento dos jogadores
        if p1_cur_pos and p1_prev_pos:
            d = math.hypot(p1_cur_pos[0] - p1_prev_pos[0], p1_cur_pos[1] - p1_prev_pos[1])
            p1_power = 0.85 * p1_power + 0.15 * min(45.0, d * 2.8)
        else:
            p1_power *= 0.92
        p1_prev_pos = p1_cur_pos

        if p2_cur_pos and p2_prev_pos:
            d = math.hypot(p2_cur_pos[0] - p2_prev_pos[0], p2_cur_pos[1] - p2_prev_pos[1])
            p2_power = 0.85 * p2_power + 0.15 * min(45.0, d * 2.8)
        else:
            p2_power *= 0.92
        p2_prev_pos = p2_cur_pos

        # Deslocamento da Esfera de Plasma
        if not game_over:
            diff_power = (p1_power - p2_power) * 0.18
            sphere_vx = 0.88 * sphere_vx + 0.12 * diff_power
            sphere_x += sphere_vx

            # Beep de tensao
            if t_now - last_beep_t > 0.35:
                freq = int(np.clip(600 + (sphere_x - W // 2) * 2, 350, 1100))
                try: winsound.Beep(freq, 25)
                except Exception: pass
                last_beep_t = t_now

            # Limites de Vitoria
            if sphere_x > (W - 90):
                game_over = True
                winner_text = "JOGADOR 1 VENCEU!"
                win_color = (0, 240, 255)
                try: winsound.Beep(1200, 250)
                except Exception: pass
            elif sphere_x < 90:
                game_over = True
                winner_text = "JOGADOR 2 VENCEU!"
                win_color = (0, 180, 255)
                try: winsound.Beep(1200, 250)
                except Exception: pass

        # Linhas de Limite de Campo
        cv2.line(frame, (90, 60), (90, H - 20), (0, 0, 255), 2)
        cv2.line(frame, (W - 90, 60), (W - 90, H - 20), (0, 0, 255), 2)
        cv2.line(frame, (W // 2, 60), (W // 2, H - 20), (70, 70, 70), 1)

        # Raios de Energia conectando as maos a esfera
        sx, sy = int(sphere_x), int(sphere_y)
        if p1_cur_pos:
            # Raio de P1 (Ciano)
            cv2.line(frame, p1_cur_pos, (sx, sy), (255, 200, 0), 4)
            cv2.line(frame, p1_cur_pos, (sx, sy), (255, 255, 255), 1)
            cv2.circle(frame, p1_cur_pos, 16, (0, 240, 255), 2)
        if p2_cur_pos:
            # Raio de P2 (Dourado/Laranja)
            cv2.line(frame, p2_cur_pos, (sx, sy), (0, 140, 255), 4)
            cv2.line(frame, p2_cur_pos, (sx, sy), (255, 255, 255), 1)
            cv2.circle(frame, p2_cur_pos, 16, (0, 180, 255), 2)

        # Particulas espirais saindo da esfera
        for _ in range(4):
            col = (0, 240, 255) if random.random() > 0.5 else (0, 180, 255)
            particles.append(EnergyParticle(sx, sy, col))

        for p in particles:
            p.update()
            p.draw(frame)
        particles = [p for p in particles if p.life > 0]

        # Esfera Central de Plasma
        cv2.circle(frame, (sx, sy), 38, (0, 255, 255), 2)
        cv2.circle(frame, (sx, sy), 26, (255, 220, 0), -1)
        cv2.circle(frame, (sx, sy), 14, (255, 255, 255), -1)

        # Barras de Forca Instantanea
        cv2.putText(frame, f"FORCA J1: {int(p1_power * 3)}%", (30, H - 35), cv2.FONT_HERSHEY_DUPLEX, 0.45, (0, 240, 255), 1)
        cv2.rectangle(frame, (30, H - 25), (200, H - 12), (30, 30, 30), -1)
        cv2.rectangle(frame, (30, H - 25), (30 + int(170 * (p1_power / 45.0)), H - 12), (0, 240, 255), -1)

        cv2.putText(frame, f"FORCA J2: {int(p2_power * 3)}%", (W - 200, H - 35), cv2.FONT_HERSHEY_DUPLEX, 0.45, (0, 180, 255), 1)
        cv2.rectangle(frame, (W - 200, H - 25), (W - 30, H - 12), (30, 30, 30), -1)
        cv2.rectangle(frame, (W - 200, H - 25), (W - 200 + int(170 * (p2_power / 45.0)), H - 12), (0, 180, 255), -1)

        # Header Tecnologico SENAI
        draw_glow_banner(frame, "CABO DE GUERRA 1v1", "BOMBEIE A MAO RAPIDO!", fps)

        if game_over:
            ov = frame.copy()
            cv2.rectangle(ov, (100, 170), (W - 100, 310), (10, 12, 20), -1)
            cv2.addWeighted(ov, 0.85, frame, 0.15, 0, frame)
            cv2.putText(frame, winner_text, (W // 2 - 150, 230), cv2.FONT_HERSHEY_DUPLEX, 1.0, win_color, 2)
            cv2.putText(frame, "Pressione [R] para Novo Duelo", (W // 2 - 145, 275), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)

        cv2.imshow("SENAI Cabo de Guerra 1v1 - Pressione 'q' para sair", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            sphere_x = float(W // 2)
            sphere_vx = 0.0
            game_over = False

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
