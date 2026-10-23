#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MacBook-Tier Touchless Mouse System - Ultra-Fluid High FPS Edition
==================================================================
Otimizações de Baixíssima Latência:
- Movimento contínuo 1:1 sem travamento ou delay artificial.
- Filtro One-Euro calibrado para alta velocidade (beta 0.45, sem arrasto).
- Chamadas Win32 nativas (ctypes.user32) com 0ms de overhead.
- Clique por pinça instantâneo (polegar + indicador) e suporte a Arrastar & Soltar.
- Rolagem suave com dois dedos (indicador + médio).
- Clique com o botão direito via pinça (polegar + médio).
"""

import sys
import os
import math
import time
import ctypes
import webbrowser
import cv2
import numpy as np

# ---------------------------------------------------------
# 1. Funções de Mouse de Baixíssima Latência (Win32 API pura)
# ---------------------------------------------------------
try:
    user32 = ctypes.windll.user32
    MOUSEEVENTF_LEFTDOWN = 0x0002
    MOUSEEVENTF_LEFTUP = 0x0004
    MOUSEEVENTF_RIGHTDOWN = 0x0008
    MOUSEEVENTF_RIGHTUP = 0x0010
    MOUSEEVENTF_WHEEL = 0x0800

    def fast_set_cursor(x: int, y: int):
        user32.SetCursorPos(int(x), int(y))

    def fast_click():
        user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

    def fast_double_click():
        user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        time.sleep(0.02)
        user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

    def fast_mouse_down():
        user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)

    def fast_mouse_up():
        user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

    def fast_right_click():
        user32.mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
        user32.mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)

    def fast_scroll(amount: int):
        user32.mouse_event(MOUSEEVENTF_WHEEL, 0, 0, int(amount), 0)

    SCREEN_W = user32.GetSystemMetrics(0)
    SCREEN_H = user32.GetSystemMetrics(1)

except Exception:
    import pyautogui
    pyautogui.FAILSAFE = False
    pyautogui.PAUSE = 0.0

    def fast_set_cursor(x: int, y: int):
        pyautogui.moveTo(int(x), int(y))

    def fast_click():
        pyautogui.click()

    def fast_double_click():
        pyautogui.doubleClick()

    def fast_mouse_down():
        pyautogui.mouseDown()

    def fast_mouse_up():
        pyautogui.mouseUp()

    def fast_right_click():
        pyautogui.rightClick()

    def fast_scroll(amount: int):
        pyautogui.scroll(int(amount))

    SCREEN_W, SCREEN_H = pyautogui.size()


# ---------------------------------------------------------
# 2. Filtro One-Euro Tunado para Fluidez Máxima
# ---------------------------------------------------------
class OneEuroFilter:
    def __init__(self, t0, x0, dx0=0.0, min_cutoff=1.6, beta=0.45, d_cutoff=1.0):
        self.min_cutoff = float(min_cutoff)  # Estabilidade quando parado
        self.beta = float(beta)              # Resposta instantânea em movimento
        self.d_cutoff = float(d_cutoff)
        self.x_prev = float(x0)
        self.dx_prev = float(dx0)
        self.t_prev = float(t0)

    def _smoothing_factor(self, t_e, cutoff):
        r = 2 * math.pi * cutoff * t_e
        return r / (r + 1)

    def _exp_smoothing(self, a, x, x_prev):
        return a * x + (1 - a) * x_prev

    def filter(self, t, x):
        t_e = t - self.t_prev
        if t_e <= 0.0001:
            return self.x_prev

        a_d = self._smoothing_factor(t_e, self.d_cutoff)
        dx = (x - self.x_prev) / t_e
        dx_hat = self._exp_smoothing(a_d, dx, self.dx_prev)

        cutoff = self.min_cutoff + self.beta * abs(dx_hat)
        a = self._smoothing_factor(t_e, cutoff)
        x_hat = self._exp_smoothing(a, x, self.x_prev)

        self.x_prev = x_hat
        self.dx_prev = dx_hat
        self.t_prev = t
        return x_hat


from camera_utils import open_camera, get_default_camera_index


def get_usb_camera_cap(cam_w=640, cam_h=480):
    idx = get_default_camera_index()
    return open_camera(idx, cam_w, cam_h)


# ---------------------------------------------------------
# 3. Loop Principal de Alta Precisão e Baixo Delay
# ---------------------------------------------------------
def main():
    CAM_W, CAM_H = 640, 480
    cap, cam_name, cam_idx = get_usb_camera_cap(CAM_W, CAM_H)

    if not cap or not cap.isOpened():
        print(f"[Erro] Nao foi possivel acessar a camera USB '{cam_name}' (Indice {cam_idx}).")
        return

    # Margens de rastreamento ativas (alcance total confortável de 100% da tela)
    MARGIN_X = 65
    MARGIN_Y = 55

    from tracker_utils import UniversalHandsDetector, draw_hand_skeleton
    hands = UniversalHandsDetector(
        max_num_hands=1,
        min_detection_confidence=0.50,
        min_tracking_confidence=0.50
    )

    t_now = time.time()
    filter_x = OneEuroFilter(t_now, SCREEN_W / 2, min_cutoff=1.6, beta=0.45)
    filter_y = OneEuroFilter(t_now, SCREEN_H / 2, min_cutoff=1.6, beta=0.45)

    # Estados de Ação
    is_pinched = False
    pinch_start_time = 0.0
    last_click_time = 0.0
    is_dragging = False
    is_scrolling = False
    prev_scroll_y = None

    # Right click
    is_right_pinching = False
    right_pinch_start = 0.0

    current_action_label = "Controle Fluido Ativo"
    label_color = (0, 255, 120)
    fps_time = time.time()
    fps = 60.0

    print("\n" + "=" * 60)
    print(" TOUCHLESS MOUSE PRO (ALTA VELOCIDADE & SEM DELAY)")
    print("=" * 60)
    print(" - Mover Cursor: Aponte com o dedo indicador (fluido e continuo)")
    print(" - Clique Esquerdo: Pinca rapida entre polegar e indicador")
    print(" - Clique Duplo: Dois toques rapidos de pinca")
    print(" - Arrastar & Soltar: Aperte a pinca e segure (> 0.28s)")
    print(" - Clique Direito: Pinca de polegar + dedo medio")
    print(" - Rolagem (Scroll): Levante indicador + medio juntos")
    print(" - Sair: Pressione 'q' na janela de video")
    print("=" * 60 + "\n")

    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            break

        if frame.shape[1] != CAM_W or frame.shape[0] != CAM_H:
            frame = cv2.resize(frame, (CAM_W, CAM_H), interpolation=cv2.INTER_NEAREST)

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        t_current = time.time()

        dt_fps = t_current - fps_time
        if dt_fps > 0:
            fps = 0.9 * fps + 0.1 * (1.0 / dt_fps)
        fps_time = t_current

        results = hands.process(rgb_frame)

        # Retângulo guia da área de alcance
        cv2.rectangle(frame, (MARGIN_X, MARGIN_Y), (CAM_W - MARGIN_X, CAM_H - MARGIN_Y),
                      (60, 60, 60), 1)

        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            draw_hand_skeleton(frame, hand_landmarks, CAM_W, CAM_H)
            landmarks = hand_landmarks.landmark

            def get_px(idx):
                return int(landmarks[idx].x * CAM_W), int(landmarks[idx].y * CAM_H)

            wrist_px = get_px(0)
            thumb_px = get_px(4)        # Ponta do Polegar
            index_px = get_px(8)        # Ponta do Indicador
            middle_px = get_px(12)      # Ponta do Médio
            ring_px = get_px(16)        # Ponta do Anelar
            pinky_px = get_px(20)       # Ponta do Mínimo

            index_pip = get_px(6)
            middle_pip = get_px(10)
            ring_pip = get_px(14)
            pinky_pip = get_px(18)

            index_up = index_px[1] < index_pip[1]
            middle_up = middle_px[1] < middle_pip[1]
            ring_up = ring_px[1] < ring_pip[1]
            pinky_up = pinky_px[1] < pinky_pip[1]

            hand_scale = max(60, math.hypot(wrist_px[0] - middle_pip[0], wrist_px[1] - middle_pip[1]))
            scale_ratio = hand_scale / 120.0

            dist_thumb_index = math.hypot(thumb_px[0] - index_px[0], thumb_px[1] - index_px[1])
            dist_thumb_middle = math.hypot(thumb_px[0] - middle_px[0], thumb_px[1] - middle_px[1])

            PINCH_CLICK_DIST = int(36 * scale_ratio)
            RELEASE_DIST = int(48 * scale_ratio)

            # -------------------------------------------------------------
            # MODO 1: ROLAGEM COM DOIS DEDOS (Indicador + Médio juntos)
            # -------------------------------------------------------------
            two_finger_mode = index_up and middle_up and not ring_up and not pinky_up and dist_thumb_index > (50 * scale_ratio)

            if two_finger_mode:
                is_scrolling = True
                avg_y = (index_px[1] + middle_px[1]) / 2.0
                if prev_scroll_y is not None:
                    dy = avg_y - prev_scroll_y
                    if abs(dy) > 1.2:
                        fast_scroll(-int(dy * 22))
                prev_scroll_y = avg_y
                current_action_label = "Rolagem com 2 Dedos"
                label_color = (0, 215, 255)
                cv2.line(frame, index_px, middle_px, (0, 215, 255), 3)

            else:
                is_scrolling = False
                prev_scroll_y = None

                # ---------------------------------------------------------
                # MODO 2: RASTREAMENTO CONTÍNUO & FLUIDO (Sem congelamento)
                # ---------------------------------------------------------
                raw_x = np.interp(index_px[0], [MARGIN_X, CAM_W - MARGIN_X], [0, SCREEN_W])
                raw_y = np.interp(index_px[1], [MARGIN_Y, CAM_H - MARGIN_Y], [0, SCREEN_H])

                smooth_x = filter_x.filter(t_current, raw_x)
                smooth_y = filter_y.filter(t_current, raw_y)
                smooth_x = max(0, min(SCREEN_W - 1, smooth_x))
                smooth_y = max(0, min(SCREEN_H - 1, smooth_y))

                # Atualização contínua do cursor no Windows em tempo real
                fast_set_cursor(smooth_x, smooth_y)

                # ---------------------------------------------------------
                # MODO 3: CLIQUE RÁPIDO & ARRASTAR (PINÇA POLEGAR + INDICADOR)
                # ---------------------------------------------------------
                if not is_right_pinching:
                    if dist_thumb_index < PINCH_CLICK_DIST:
                        if not is_pinched:
                            is_pinched = True
                            pinch_start_time = t_current

                            # Detecta duplo clique
                            if (t_current - last_click_time) < 0.38:
                                fast_double_click()
                                current_action_label = "Duplo Clique!"
                                label_color = (255, 0, 255)
                                last_click_time = 0.0
                            else:
                                fast_click()
                                current_action_label = "Clique!"
                                label_color = (0, 255, 0)
                                last_click_time = t_current

                        # Transição para Arraste após segurar
                        elif not is_dragging and (t_current - pinch_start_time) > 0.28:
                            is_dragging = True
                            fast_mouse_down()
                            current_action_label = "Arrastando..."
                            label_color = (255, 120, 0)

                    elif dist_thumb_index > RELEASE_DIST:
                        if is_dragging:
                            fast_mouse_up()
                            is_dragging = False
                            current_action_label = "Solto"
                            label_color = (200, 200, 200)
                        is_pinched = False

                if not is_pinched and not is_dragging and not is_scrolling:
                    current_action_label = "Movendo Cursor"
                    label_color = (220, 220, 220)

                # ---------------------------------------------------------
                # MODO 4: CLIQUE DIREITO (PINÇA POLEGAR + MÉDIO)
                # ---------------------------------------------------------
                if not is_pinched and not is_dragging:
                    if not is_right_pinching:
                        if dist_thumb_middle < (30 * scale_ratio) and dist_thumb_index > (45 * scale_ratio):
                            is_right_pinching = True
                            right_pinch_start = t_current
                            fast_right_click()
                            current_action_label = "Clique Direito"
                            label_color = (0, 120, 255)
                    else:
                        if dist_thumb_middle > (45 * scale_ratio):
                            is_right_pinching = False

            # Mira e feedback visual de toque
            ring_color = (0, 255, 0) if is_pinched else ((0, 120, 255) if is_right_pinching else (0, 255, 255))
            cv2.line(frame, thumb_px, index_px, (160, 160, 160), 1)
            cv2.circle(frame, index_px, 6, (0, 255, 255), -1)
            cv2.circle(frame, thumb_px, 5, (255, 120, 0), -1)

            mid_x = int((thumb_px[0] + index_px[0]) / 2)
            mid_y = int((thumb_px[1] + index_px[1]) / 2)
            cv2.circle(frame, (mid_x, mid_y), 8 if is_pinched else 14, ring_color, 2)

        else:
            if is_dragging:
                fast_mouse_up()
                is_dragging = False
            is_pinched = False
            is_scrolling = False
            current_action_label = "Aguardando Mao..."
            label_color = (130, 130, 130)

        # HUD Superior Limpo e Otimizado
        cv2.rectangle(frame, (0, 0), (CAM_W, 40), (16, 16, 16), -1)
        cv2.putText(frame, "TOUCHLESS PRO 60FPS", (14, 26),
                    cv2.FONT_HERSHEY_DUPLEX, 0.52, (255, 255, 255), 1)
        cv2.putText(frame, current_action_label, (230, 26),
                    cv2.FONT_HERSHEY_DUPLEX, 0.50, label_color, 1)
        cv2.putText(frame, f"{int(fps)} FPS", (CAM_W - 85, 26),
                    cv2.FONT_HERSHEY_DUPLEX, 0.48, (0, 255, 120) if fps >= 30 else (160, 160, 160), 1)

        cv2.imshow("Touchless Mouse Pro - Pressione 'q' para sair", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    if is_dragging:
        fast_mouse_up()

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    if "--web" in sys.argv:
        test_html = os.path.join(os.path.dirname(os.path.abspath(__file__)), "totem-senai", "teste.html")
        if os.path.exists(test_html):
            print(f"[Navegador] Abrindo Area de Testes: {test_html}")
            webbrowser.open(f"file:///{test_html}")
    main()
