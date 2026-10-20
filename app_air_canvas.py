"""
AIR CANVAS HOLOGRAFICO (PINTURA NO AR) - SENAI LAB
Desenhe no ar usando a ponta do seu dedo com cores neon fluidas e glow estelar!
Controles:
- 1 Dedo levantado (Indicador): MODO PINTURA (Desenha no ar).
- 2 Dedos levantados (Indicador + Medio): MODO SELECAO (Mova para selecionar cores no topo).
- Mao Aberta (5 Dedos): LIMPAR TELA (Apaga todo o desenho).
- Pressione 's' para salvar o desenho como imagem PNG.
- Pressione 'c' para limpar o quadro.
- Pressione 'q' para sair.
"""

import cv2
import numpy as np
import mediapipe as mp
import math
import time
from camera_helper import get_usb_camera_cap, draw_glow_banner

def main():
    W, H = 640, 480
    cap, cam_name, cam_idx = get_usb_camera_cap(W, H)
    if not cap.isOpened():
        print(f"Erro ao abrir camera USB {cam_name}")
        return

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.75, min_tracking_confidence=0.75)

    canvas = np.zeros((H, W, 3), dtype=np.uint8)

    colors = [
        ("Azul Neon", (255, 190, 0)),
        ("Verde Neon", (0, 255, 120)),
        ("Vermelho", (40, 40, 245)),
        ("Amarelo Ouro", (0, 230, 255)),
        ("Violeta", (230, 60, 210)),
        ("Borracha", (0, 0, 0))
    ]
    current_color_idx = 0
    brush_thickness = 7
    eraser_thickness = 34

    prev_pt = None
    status_label = "Modo Selecao"
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

        results = hands.process(rgb)

        if results.multi_hand_landmarks:
            lms = results.multi_hand_landmarks[0].landmark
            wrist = (int(lms[0].x * W), int(lms[0].y * H))
            idx_tip = (int(lms[8].x * W), int(lms[8].y * H))
            idx_pip = (int(lms[6].x * W), int(lms[6].y * H))
            mid_tip = (int(lms[12].x * W), int(lms[12].y * H))
            mid_pip = (int(lms[10].x * W), int(lms[10].y * H))

            def is_ext(tip, pip):
                return math.hypot(tip[0] - wrist[0], tip[1] - wrist[1]) > math.hypot(pip[0] - wrist[0], pip[1] - wrist[1]) * 1.15

            idx_up = is_ext(idx_tip, idx_pip)
            mid_up = is_ext(mid_tip, mid_pip)
            ring_up = is_ext((int(lms[16].x * W), int(lms[16].y * H)), (int(lms[14].x * W), int(lms[14].y * H)))
            pinky_up = is_ext((int(lms[20].x * W), int(lms[20].y * H)), (int(lms[18].x * W), int(lms[18].y * H)))

            open_count = sum([idx_up, mid_up, ring_up, pinky_up])

            # 1. GESTO: LIMPAR QUADRO (Palma totalmente aberta)
            if open_count == 4:
                status_label = "LIMPANDO TELA"
                prev_pt = None
                cv2.circle(frame, idx_tip, 24, (0, 0, 255), 2)
                canvas = np.zeros((H, W, 3), dtype=np.uint8)

            # 2. GESTO: SELECAO DE CORES (Indicador + Medio levantados)
            elif idx_up and mid_up and not ring_up and not pinky_up:
                status_label = "SELECIONAR COR"
                prev_pt = None
                mid_x = (idx_tip[0] + mid_tip[0]) // 2
                mid_y = (idx_tip[1] + mid_tip[1]) // 2
                cv2.circle(frame, (mid_x, mid_y), 14, (255, 255, 255), 2)
                cv2.circle(frame, (mid_x, mid_y), 4, (0, 255, 255), -1)

                if 55 <= mid_y <= 105:
                    btn_w = W // len(colors)
                    clicked_idx = mid_x // btn_w
                    if 0 <= clicked_idx < len(colors):
                        current_color_idx = clicked_idx

            # 3. GESTO: DESENHAR (Apenas Indicador levantado)
            elif idx_up and not mid_up and not ring_up and not pinky_up:
                status_label = "DESENHANDO"
                cur_color = colors[current_color_idx][1]
                thick = eraser_thickness if colors[current_color_idx][0] == "Borracha" else brush_thickness

                # Efeito de caneta de luz neon
                cv2.circle(frame, idx_tip, thick // 2 + 2, (255, 255, 255), -1)
                cv2.circle(frame, idx_tip, thick + 4, cur_color, 2)

                if prev_pt is not None:
                    # Traço no canvas com efeito de glow
                    cv2.line(canvas, prev_pt, idx_tip, cur_color, thick)
                prev_pt = idx_tip
            else:
                prev_pt = None
                status_label = "MAO EM ESPERA"
        else:
            prev_pt = None
            status_label = "APONTE A MAO"

        # Mescla o canvas brilhante sobre a webcam
        gray_canvas = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
        _, mask_inv = cv2.threshold(gray_canvas, 10, 255, cv2.THRESH_BINARY_INV)
        frame_bg = cv2.bitwise_and(frame, frame, mask=mask_inv)
        frame = cv2.add(frame_bg, canvas)

        # Paleta de Cores Flutuante no Topo (y de 55 a 95)
        btn_w = W // len(colors)
        for i, (name, col) in enumerate(colors):
            x1 = i * btn_w + 4
            x2 = (i + 1) * btn_w - 4
            y1 = 58
            y2 = 94
            is_active = (i == current_color_idx)

            # Sombra e preenchimento
            cv2.rectangle(frame, (x1, y1), (x2, y2), col, -1)
            border_col = (255, 255, 255) if is_active else (80, 80, 80)
            border_th = 3 if is_active else 1
            cv2.rectangle(frame, (x1, y1), (x2, y2), border_col, border_th)

            text_col = (0, 0, 0) if (col[0] + col[1] + col[2]) > 380 else (255, 255, 255)
            cv2.putText(frame, name, (x1 + 6, y1 + 24), cv2.FONT_HERSHEY_DUPLEX, 0.40, text_col, 1)

        # Header Tecnologico SENAI
        draw_glow_banner(frame, "AIR CANVAS", f"MODO: {status_label}", fps)

        # Rodape com atalhos
        cv2.rectangle(frame, (0, H - 26), (W, H), (12, 14, 20), -1)
        cv2.putText(frame, "[1 Dedo] Pintar  •  [2 Dedos] Paleta  •  [Mao Aberta] Limpar  •  [S] Salvar PNG",
                    (20, H - 9), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (190, 220, 255), 1)

        cv2.imshow("SENAI Air Canvas Touchless - Pressione 'q' para sair", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('c'):
            canvas = np.zeros((H, W, 3), dtype=np.uint8)
        elif key == ord('s'):
            filename = f"desenho_senai_canvas_{int(time.time())}.png"
            cv2.imwrite(filename, frame)
            print(f"[SALVO] Imagem salva como '{filename}'!")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
