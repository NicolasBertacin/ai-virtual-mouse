"""
DUELO DE SABRES DE LUZ 1v1 (LASER SWORD DUEL) - SENAI LAB
Duele com sabres de energia no ar contra seu amigo!
Controles:
- Jogador 1 (Esquerda - Sabre Azul): Empunhe com a mao esquerda.
- Jogador 2 (Direita - Sabre Vermelho): Empunhe com a mao direita.
- Cruze as laminas para colidir (CLASH com faiscas!).
- Atinja o campo adversario para reduzir a energia do escudo.
- Pressione 'r' para reiniciar o duelo.
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

class Spark:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-8, 8)
        self.vy = random.uniform(-8, 8)
        self.life = 1.0

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 0.08

    def draw(self, frame):
        if self.life > 0:
            cv2.circle(frame, (int(self.x), int(self.y)), max(1, int(3 * self.life)), (255, 255, 200), -1)


def segments_intersect(p1, p2, p3, p4):
    """Verifica interseccao entre segmento p1-p2 e p3-p4"""
    def ccw(A, B, C):
        return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])
    return (ccw(p1, p3, p4) != ccw(p2, p3, p4)) and (ccw(p1, p2, p3) != ccw(p1, p2, p4))


def main():
    W, H = 640, 480
    cap, cam_name, cam_idx = get_usb_camera_cap(W, H)
    if not cap.isOpened():
        print(f"Erro ao abrir camera USB {cam_name}")
        return

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.7)

    p1_hp = 100.0
    p2_hp = 100.0
    sparks = []
    last_clash_t = 0.0
    last_hit_t1 = 0.0
    last_hit_t2 = 0.0
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

        # Fundo escuro de arena estelar
        dark = np.zeros_like(frame)
        frame = cv2.addWeighted(frame, 0.40, dark, 0.60, 0)

        results = hands.process(rgb)

        saber1 = None  # (hilt, tip)
        saber2 = None

        if results.multi_hand_landmarks:
            for lms in results.multi_hand_landmarks:
                wrist = (int(lms.landmark[0].x * W), int(lms.landmark[0].y * H))
                tip = (int(lms.landmark[8].x * W), int(lms.landmark[8].y * H))
                # Vetor de projecao da lamina do sabre (comprimento ~130px)
                dx = tip[0] - wrist[0]
                dy = tip[1] - wrist[1]
                dist = math.hypot(dx, dy) + 0.001
                blade_len = 135
                blade_tip = (int(tip[0] + (dx / dist) * blade_len), int(tip[1] + (dy / dist) * blade_len))

                if wrist[0] < W // 2:
                    saber1 = (tip, blade_tip)
                else:
                    saber2 = (tip, blade_tip)

        # Colisao entre sabres (CLASH!)
        is_clashing = False
        if saber1 and saber2 and p1_hp > 0 and p2_hp > 0:
            if segments_intersect(saber1[0], saber1[1], saber2[0], saber2[1]):
                is_clashing = True
                clash_x = (saber1[1][0] + saber2[1][0]) // 2
                clash_y = (saber1[1][1] + saber2[1][1]) // 2
                if t_now - last_clash_t > 0.12:
                    last_clash_t = t_now
                    try: winsound.Beep(1200, 30)
                    except Exception: pass
                    for _ in range(25):
                        sparks.append(Spark(clash_x, clash_y))

        # Ataque no campo adversario (se nao estiver em clash)
        if not is_clashing and p1_hp > 0 and p2_hp > 0:
            # Sabre 1 ataca campo 2 (x > W - 140)
            if saber1 and saber1[1][0] > (W - 160) and (t_now - last_hit_t2) > 0.35:
                p2_hp = max(0.0, p2_hp - 12.0)
                last_hit_t2 = t_now
                try: winsound.Beep(350, 60)
                except Exception: pass
                for _ in range(20): sparks.append(Spark(saber1[1][0], saber1[1][1]))

            # Sabre 2 ataca campo 1 (x < 140)
            if saber2 and saber2[1][0] < 160 and (t_now - last_hit_t1) > 0.35:
                p1_hp = max(0.0, p1_hp - 12.0)
                last_hit_t1 = t_now
                try: winsound.Beep(350, 60)
                except Exception: pass
                for _ in range(20): sparks.append(Spark(saber2[1][0], saber2[1][1]))

        # Desenho dos Sabres de Luz
        # Sabre 1 (Azul / Ciano)
        if saber1:
            h, t = saber1
            cv2.line(frame, h, t, (255, 180, 0), 12)       # Aura externa
            cv2.line(frame, h, t, (255, 255, 100), 7)      # Brilho
            cv2.line(frame, h, t, (255, 255, 255), 2)      # Nucleo branco
            cv2.circle(frame, h, 8, (180, 180, 180), -1)   # Empunhadura

        # Sabre 2 (Vermelho / Carmim)
        if saber2:
            h, t = saber2
            cv2.line(frame, h, t, (0, 0, 255), 12)
            cv2.line(frame, h, t, (0, 140, 255), 7)
            cv2.line(frame, h, t, (255, 255, 255), 2)
            cv2.circle(frame, h, 8, (180, 180, 180), -1)

        # Faiscas
        for sp in sparks:
            sp.update()
            sp.draw(frame)
        sparks = [s for s in sparks if s.life > 0]

        # Header Tecnologico SENAI
        draw_glow_banner(frame, "DUELO DE SABRES 1v1", "CRUZE AS LAMINAS!", fps)

        # Barras de Escudo dos Jogadores
        # Jogador 1 (Azul)
        cv2.putText(frame, "JOGADOR 1 (AZUL):", (25, H - 36), cv2.FONT_HERSHEY_DUPLEX, 0.48, (255, 200, 0), 1)
        cv2.rectangle(frame, (25, H - 26), (225, H - 12), (30, 30, 30), -1)
        cv2.rectangle(frame, (25, H - 26), (25 + int(200 * (p1_hp / 100)), H - 12), (255, 180, 0), -1)
        cv2.rectangle(frame, (25, H - 26), (225, H - 12), (255, 255, 255), 1)

        # Jogador 2 (Vermelho)
        cv2.putText(frame, "JOGADOR 2 (VERMELHO):", (W - 240, H - 36), cv2.FONT_HERSHEY_DUPLEX, 0.48, (0, 80, 255), 1)
        cv2.rectangle(frame, (W - 240, H - 26), (W - 40, H - 12), (30, 30, 30), -1)
        cv2.rectangle(frame, (W - 240, H - 26), (W - 240 + int(200 * (p2_hp / 100)), H - 12), (0, 60, 255), -1)
        cv2.rectangle(frame, (W - 240, H - 26), (W - 40, H - 12), (255, 255, 255), 1)

        # Vitoria
        if p1_hp <= 0 or p2_hp <= 0:
            winner = "SABRE AZUL VENCEU!" if p2_hp <= 0 else "SABRE VERMELHO VENCEU!"
            col = (255, 200, 0) if p2_hp <= 0 else (0, 80, 255)
            ov = frame.copy()
            cv2.rectangle(ov, (100, 170), (W - 100, 310), (10, 10, 20), -1)
            cv2.addWeighted(ov, 0.85, frame, 0.15, 0, frame)
            cv2.putText(frame, winner, (W // 2 - 165, 230), cv2.FONT_HERSHEY_DUPLEX, 1.0, col, 2)
            cv2.putText(frame, "Pressione [R] para Novo Duelo", (W // 2 - 145, 275), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)

        cv2.imshow("SENAI Duelo de Sabres 1v1 - Pressione 'q' para sair", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            p1_hp = 100.0
            p2_hp = 100.0

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
