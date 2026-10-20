"""
SIMULADOR DE PARTICULAS SCI-FI (COSMIC GALAXY TOUCHLESS)
Manipule um campo cosmico de centenas de particulas de energia com as maos!
Controles:
- Mao Aberta: CAMPO REPULSOR (Empurra e dispersa as particulas).
- Punho Fechado: BURACO NEGRO MAGNETICO (Atrai as particulas para o centro da mao).
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
from camera_helper import get_usb_camera_cap

class Particle:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.reset()

    def reset(self):
        self.x = random.uniform(50, self.w - 50)
        self.y = random.uniform(50, self.h - 50)
        self.vx = random.uniform(-1.0, 1.0)
        self.vy = random.uniform(-1.0, 1.0)
        self.size = random.randint(2, 4)

    def update(self, hand_pos, is_attracting, is_repelling):
        # Inercia e amortecimento
        self.vx *= 0.94
        self.vy *= 0.94

        if hand_pos:
            hx, hy = hand_pos
            dx = hx - self.x
            dy = hy - self.y
            dist = math.hypot(dx, dy) + 0.001

            if is_attracting:
                # Puxa para a mao (gravidade forte + rotacao orbital)
                force = min(8.0, 350.0 / (dist + 20))
                self.vx += (dx / dist) * force - (dy / dist) * (force * 0.45)
                self.vy += (dy / dist) * force + (dx / dist) * (force * 0.45)

            elif is_repelling and dist < 220:
                # Empurra para longe da mao aberta
                force = min(12.0, 280.0 / (dist + 10))
                self.vx -= (dx / dist) * force
                self.vy -= (dy / dist) * force

        self.x += self.vx
        self.y += self.vy

        # Rebater nas bordas da tela
        if self.x < 10 or self.x > self.w - 10:
            self.vx = -self.vx
            self.x = np.clip(self.x, 10, self.w - 10)
        if self.y < 10 or self.y > self.h - 10:
            self.vy = -self.vy
            self.y = np.clip(self.y, 10, self.h - 10)


def main():
    W, H = 640, 480
    cap, cam_name, cam_idx = get_usb_camera_cap(W, H)
    if not cap.isOpened():
        print(f"Erro ao abrir camera USB {cam_name}")
        return

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)

    # 450 Particulas para otima performance a 60 FPS
    NUM_PARTICLES = 450
    particles = [Particle(W, H) for _ in range(NUM_PARTICLES)]

    palettes = [
        ("CIANO COSMICO", (255, 220, 0), (255, 255, 100)),
        ("SUPERNOVA DOURADA", (0, 190, 255), (0, 255, 255)),
        ("NEBULOSA VIOLETA", (230, 80, 220), (255, 180, 240)),
        ("FOGO SOLAR", (20, 50, 255), (0, 165, 255)),
    ]
    current_pal_idx = 0

    print("\n[PARTICULAS COSMICAS INICIADO] Abra a mao para repelir e feche para atrair!")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Efeito de escurecimento espacial translucido para realcar o brilho das particulas
        dark_overlay = np.zeros_like(frame)
        frame = cv2.addWeighted(frame, 0.45, dark_overlay, 0.55, 0)

        results = hands.process(rgb)

        hand_pos = None
        is_attracting = False
        is_repelling = False
        mode_label = "ESPERA: MOVA A MAO"

        if results.multi_hand_landmarks:
            lms = results.multi_hand_landmarks[0].landmark
            wrist = (int(lms[0].x * W), int(lms[0].y * H))
            mcp = (int(lms[9].x * W), int(lms[9].y * H))
            hand_pos = ((wrist[0] + mcp[0]) // 2, (wrist[1] + mcp[1]) // 2)

            # Checagem de dedos estendidos
            ext_fingers = sum(
                math.hypot(lms[tip].x - lms[0].x, lms[tip].y - lms[0].y) >
                math.hypot(lms[pip].x - lms[0].x, lms[pip].y - lms[0].y) * 1.15
                for tip, pip in [(8, 6), (12, 10), (16, 14), (20, 18)]
            )

            if ext_fingers >= 4:
                # Mao Aberta = Repulsor
                is_repelling = True
                mode_label = "CAMPO DE REPULSAO ATIVO"
            elif ext_fingers == 0:
                # Punho Fechado = Buraco Negro
                is_attracting = True
                mode_label = "BURACO NEGRO MAGNETICO ATIVO"
            else:
                mode_label = "VORTICE DINAMICO"

        # Atualiza particulas
        for p in particles:
            p.update(hand_pos, is_attracting, is_repelling)

        # Desenho das particulas
        col_main, col_glow = palettes[current_pal_idx][1], palettes[current_pal_idx][2]
        for p in particles:
            px, py = int(p.x), int(p.y)
            cv2.circle(frame, (px, py), p.size, col_main, -1)
            if p.size >= 3:
                cv2.circle(frame, (px, py), p.size - 1, col_glow, -1)

        # Desenho dos efeitos visuais da mao
        if hand_pos:
            hx, hy = hand_pos
            if is_attracting:
                # Nucleo de buraco negro
                cv2.circle(frame, (hx, hy), 22, (0, 0, 0), -1)
                cv2.circle(frame, (hx, hy), 28, col_glow, 2)
                cv2.circle(frame, (hx, hy), 36, col_main, 1)
            elif is_repelling:
                # Onda de choque do repulsor
                cv2.circle(frame, (hx, hy), 65, col_glow, 2)
                cv2.circle(frame, (hx, hy), 40, col_main, 2)
                cv2.circle(frame, (hx, hy), 12, (255, 255, 255), -1)
            else:
                cv2.circle(frame, (hx, hy), 16, col_glow, 2)

        # HUD Superior
        cv2.rectangle(frame, (0, 0), (W, 45), (10, 12, 18), -1)
        cv2.putText(frame, f"GALAXY: {mode_label}", (15, 30), cv2.FONT_HERSHEY_DUPLEX, 0.55, col_glow, 1)
        pal_name = palettes[current_pal_idx][0]
        cv2.putText(frame, f"Paleta [C]: {pal_name}", (W - 270, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)

        cv2.imshow("Particulas Cosmicas Touchless - Pressione 'q' para sair", frame)

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
