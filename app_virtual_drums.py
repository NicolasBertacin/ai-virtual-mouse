"""
BATERIA VIRTUAL HOLOGRAFICA (AIR DRUMS)
Toque bateria no ar com as duas maos!
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
from camera_helper import get_usb_camera_cap

# Reproducao de som sem travar o video
def play_drum_sound(freq, duration):
    def _beep():
        try:
            winsound.Beep(freq, duration)
        except Exception:
            pass
    threading.Thread(target=_beep, daemon=True).start()


class DrumPad:
    def __init__(self, name, x1, y1, x2, y2, color, freq, dur):
        self.name = name
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.color = color
        self.freq = freq
        self.dur = dur
        self.hit_time = 0.0

    def contains(self, px, py):
        return self.x1 <= px <= self.x2 and self.y1 <= py <= self.y2

    def trigger(self):
        self.hit_time = time.time()
        play_drum_sound(self.freq, self.dur)

    def draw(self, frame):
        t_now = time.time()
        is_hit = (t_now - self.hit_time) < 0.15
        
        # Efeito de brilho quando atingido
        col = (255, 255, 255) if is_hit else self.color
        alpha = 0.45 if is_hit else 0.25
        
        # Desenha pad translucido
        overlay = frame.copy()
        cv2.rectangle(overlay, (self.x1, self.y1), (self.x2, self.y2), col, -1)
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

        # Borda
        border_th = 4 if is_hit else 2
        cv2.rectangle(frame, (self.x1, self.y1), (self.x2, self.y2), col, border_th)

        # Nome do instrumento
        text_size = cv2.getTextSize(self.name, cv2.FONT_HERSHEY_DUPLEX, 0.6, 1)[0]
        tx = (self.x1 + self.x2 - text_size[0]) // 2
        ty = (self.y1 + self.y2 + text_size[1]) // 2
        cv2.putText(frame, self.name, (tx, ty), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)


def main():
    W, H = 640, 480
    cap, cam_name, cam_idx = get_usb_camera_cap(W, H)
    if not cap.isOpened():
        print(f"Erro ao abrir camera USB {cam_name}")
        return

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.7)

    # Definicao dos Pads de Bateria
    pads = [
        DrumPad("PRATO (CRASH)", 30, 70, 180, 190, (0, 220, 255), 1400, 70),
        DrumPad("HI-HAT", 220, 70, 370, 190, (255, 180, 0), 1000, 40),
        DrumPad("TOM-TOM", 410, 70, 610, 190, (200, 50, 220), 450, 70),
        DrumPad("CAIXA (SNARE)", 80, 260, 280, 420, (0, 255, 100), 750, 60),
        DrumPad("BUMBO (BASS)", 360, 260, 560, 420, (40, 50, 240), 220, 100),
    ]

    # Historico das pontas dos dedos indicadores de cada mao para detectar batida descendente
    prev_tips = {}

    print("\n[BATERIA VIRTUAL INICIADA] Bata para baixo nos tambores e pratos com as maos!")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = hands.process(rgb)

        current_tips = []
        if results.multi_hand_landmarks:
            for hand_idx, lms in enumerate(results.multi_hand_landmarks):
                # Ponta do indicador (8) e dedo medio (12)
                tip_x = int(lms.landmark[8].x * W)
                tip_y = int(lms.landmark[8].y * H)
                current_tips.append((hand_idx, tip_x, tip_y))

                # Desenha baqueta virtual na ponta do dedo
                cv2.circle(frame, (tip_x, tip_y), 10, (0, 255, 255), -1)
                cv2.circle(frame, (tip_x, tip_y), 14, (255, 255, 255), 2)

                # Verifica se houve movimento descendente para dentro de um pad
                if hand_idx in prev_tips:
                    old_x, old_y = prev_tips[hand_idx]
                    dy = tip_y - old_y
                    # Se desceu mais de 6 pixels rapidamente
                    if dy > 6:
                        for pad in pads:
                            if pad.contains(tip_x, tip_y) and not pad.contains(old_x, old_y):
                                pad.trigger()

                prev_tips[hand_idx] = (tip_x, tip_y)

        # Desenha os Pads
        for pad in pads:
            pad.draw(frame)

        # HUD Superior
        cv2.rectangle(frame, (0, 0), (W, 40), (15, 15, 20), -1)
        cv2.putText(frame, "AIR DRUMS: BATA PARA BAIXO NOS PADS", (15, 26), cv2.FONT_HERSHEY_DUPLEX, 0.55, (0, 255, 255), 1)
        cv2.putText(frame, "[Q] Sair", (W - 90, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 180, 180), 1)

        cv2.imshow("Air Drums Touchless - Pressione 'q' para sair", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
