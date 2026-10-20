"""
BATERIA VIRTUAL HOLOGRAFICA (AIR DRUMS) - SENAI LAB
Toque bateria no ar com as duas maos e visual de pads iluminados!
Controles:
- Mova as maos e bata para baixo nos pads virtuais flutuantes.
- Suporta as duas maos simultaneas (baquetas virtuais).
- Pressione 'q' para sair.
"""

import cv2
import numpy as np
import mediapipe as mp
import threading
import winsound
import time
from camera_helper import get_usb_camera_cap, draw_glow_banner

def play_drum_sound(freq, duration):
    def _beep():
        try:
            winsound.Beep(freq, duration)
        except Exception:
            pass
    threading.Thread(target=_beep, daemon=True).start()


class DrumPad:
    def __init__(self, name, cx, cy, radius, color, freq, dur):
        self.name = name
        self.cx = cx
        self.cy = cy
        self.radius = radius
        self.color = color
        self.freq = freq
        self.dur = dur
        self.hit_time = 0.0

    def contains(self, px, py):
        return (px - self.cx)**2 + (py - self.cy)**2 <= self.radius**2

    def trigger(self):
        self.hit_time = time.time()
        play_drum_sound(self.freq, self.dur)

    def draw(self, frame):
        t_now = time.time()
        is_hit = (t_now - self.hit_time) < 0.18
        
        # Efeito de expansao e brilho de impacto
        col = (255, 255, 255) if is_hit else self.color
        cur_radius = self.radius + (8 if is_hit else 0)
        alpha = 0.55 if is_hit else 0.22

        overlay = frame.copy()
        cv2.circle(overlay, (self.cx, self.cy), cur_radius, col, -1)
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

        # Anel externo neon
        cv2.circle(frame, (self.cx, self.cy), cur_radius, col, 3 if is_hit else 2)
        cv2.circle(frame, (self.cx, self.cy), cur_radius - 8, (255, 255, 255), 1)

        # Onda de choque quando bate
        if is_hit:
            shock_r = int(cur_radius + (t_now - self.hit_time) * 110)
            cv2.circle(frame, (self.cx, self.cy), shock_r, col, 1)

        # Nome do pad
        text_size = cv2.getTextSize(self.name, cv2.FONT_HERSHEY_DUPLEX, 0.48, 1)[0]
        tx = self.cx - text_size[0] // 2
        ty = self.cy + text_size[1] // 2
        cv2.putText(frame, self.name, (tx, ty), cv2.FONT_HERSHEY_DUPLEX, 0.48, (255, 255, 255), 1)


def main():
    W, H = 640, 480
    cap, cam_name, cam_idx = get_usb_camera_cap(W, H)
    if not cap.isOpened():
        print(f"Erro ao abrir camera USB {cam_name}")
        return

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.7)

    # 5 Pads de Bateria em formato circular moderno
    pads = [
        DrumPad("PRATO CRASH", 110, 140, 58, (0, 220, 255), 1400, 70),
        DrumPad("HI-HAT", 280, 130, 54, (255, 190, 0), 1000, 40),
        DrumPad("TOM-TOM", 440, 130, 54, (220, 60, 220), 450, 70),
        DrumPad("RIDE / PRATO", 555, 140, 54, (0, 240, 200), 1250, 60),
        DrumPad("CAIXA SNARE", 190, 320, 68, (0, 255, 120), 750, 60),
        DrumPad("BUMBO BASS", 450, 320, 74, (40, 50, 240), 220, 100),
    ]

    prev_tips = {}
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

        # Fundo escurecido estilo estudio
        dark_overlay = np.zeros_like(frame)
        frame = cv2.addWeighted(frame, 0.40, dark_overlay, 0.60, 0)

        results = hands.process(rgb)

        if results.multi_hand_landmarks:
            for hand_idx, lms in enumerate(results.multi_hand_landmarks):
                tip_x = int(lms.landmark[8].x * W)
                tip_y = int(lms.landmark[8].y * H)

                # Baqueta Virtual com halo neon
                cv2.circle(frame, (tip_x, tip_y), 14, (0, 255, 255), 2)
                cv2.circle(frame, (tip_x, tip_y), 8, (255, 255, 255), -1)

                if hand_idx in prev_tips:
                    old_x, old_y = prev_tips[hand_idx]
                    dy = tip_y - old_y
                    if dy > 5:
                        for pad in pads:
                            if pad.contains(tip_x, tip_y) and not pad.contains(old_x, old_y):
                                pad.trigger()

                prev_tips[hand_idx] = (tip_x, tip_y)

        for pad in pads:
            pad.draw(frame)

        # Header Tecnologico SENAI
        draw_glow_banner(frame, "AIR DRUMS", "BATERIA HOLOGRAFICA", fps)

        # Rodape Informativo
        cv2.rectangle(frame, (0, H - 26), (W, H), (12, 14, 20), -1)
        cv2.putText(frame, "Bata para baixo nos pratos e tambores para disparar o som percussivo!",
                    (35, H - 9), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (190, 220, 255), 1)

        cv2.imshow("SENAI Air Drums Touchless - Pressione 'q' para sair", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
