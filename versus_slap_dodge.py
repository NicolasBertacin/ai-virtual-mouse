"""
JOGO DA MAOZINHA / TAPA E ESQUIVA 1v1 (SLAP DODGE TOUCHLESS) - SENAI LAB
Classico duelo escolar de reflexo, agora 100% sem contato fisico!
Regras:
- Um jogador e o ATACANTE e o outro e o DEFENSOR.
- O Defensor deve posicionar a mao dentro do Circulo de Perigo no centro.
- O Atacante posiciona a mao na sua Base lateral.
- Quando a rodada iniciar:
  * O Atacante pode dar o bote (avancar a mao rapidamente ate o centro)!
  * O Defensor deve retirar a mao no exato momento do bote para se esquivar!
  * Se o Defensor tirar a mao ANTES do atacante se mover: FALSA ESQUIVA (Ponto pro atacante!).
  * Se o Atacante alcancar o centro antes do defensor fugir: TAPA CONECTOU! (Ponto pro atacante!).
  * Se o Defensor escapar a tempo para sua base: ESQUIVA COM SUCESSO! (Ponto pro defensor!).
- A cada ponto, os papeis se invertem (quem atacou agora defende).
- Primeiro a fazer 5 pontos vence o trofeu!
- Pressione 'r' para reiniciar ou 'q' para sair.
"""

import cv2
import numpy as np
import mediapipe as mp
import time
import math
import winsound
import threading
from camera_helper import get_usb_camera_cap, draw_glow_banner

def play_sound(freq, duration):
    def _beep():
        try:
            winsound.Beep(freq, duration)
        except Exception:
            pass
    threading.Thread(target=_beep, daemon=True).start()

def main():
    W, H = 640, 480
    cap, cam_name, cam_idx = get_usb_camera_cap(W, H)
    if not cap.isOpened():
        print(f"Erro ao abrir camera USB {cam_name}")
        return

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.7)

    # Zonas
    CENTER_POS = (W // 2, 280)
    DANGER_RADIUS = 75
    P1_BASE_X = 180  # Esquerda
    P2_BASE_X = 460  # Direita

    p1_score = 0
    p2_score = 0
    MAX_SCORE = 5

    # 1 = P1 Ataca, P2 Defende; 2 = P2 Ataca, P1 Defende
    attacker = 1
    state = "GET_READY"  # GET_READY, IN_POSITION, ATTACK_ACTIVE, RESULT_PAUSE, GAME_OVER
    result_text = ""
    result_color = (255, 255, 255)
    pause_until = 0.0

    particles = []

    fps = 30.0
    last_fps_t = time.time()

    def spawn_sparks(pos, color, count=25):
        for _ in range(count):
            angle = np.random.uniform(0, 2 * np.pi)
            speed = np.random.uniform(4, 12)
            particles.append({
                'x': float(pos[0]),
                'y': float(pos[1]),
                'vx': np.cos(angle) * speed,
                'vy': np.sin(angle) * speed,
                'life': 1.0,
                'color': color
            })

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

        p1_pos = None
        p2_pos = None

        if results.multi_hand_landmarks:
            for lms in results.multi_hand_landmarks:
                # Usar centro da palma / base do dedo medio
                cx = int(lms.landmark[9].x * W)
                cy = int(lms.landmark[9].y * H)
                if cx < W // 2:
                    p1_pos = (cx, cy)
                else:
                    p2_pos = (cx, cy)

        # Desenhar visual das bases e area de perigo
        # Base P1 (Ciano)
        cv2.line(frame, (P1_BASE_X, 100), (P1_BASE_X, H - 20), (255, 200, 0), 2)
        cv2.putText(frame, "BASE P1", (20, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 200, 0), 2)

        # Base P2 (Laranja)
        cv2.line(frame, (P2_BASE_X, 100), (P2_BASE_X, H - 20), (0, 160, 255), 2)
        cv2.putText(frame, "BASE P2", (W - 120, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 160, 255), 2)

        # Circulo de Perigo no Centro
        danger_color = (0, 0, 255) if state == "ATTACK_ACTIVE" else (0, 255, 255)
        cv2.circle(frame, CENTER_POS, DANGER_RADIUS, danger_color, 2)
        cv2.circle(frame, CENTER_POS, 8, danger_color, -1)
        cv2.putText(frame, "ZONA DE TAPA", (CENTER_POS[0] - 70, CENTER_POS[1] - DANGER_RADIUS - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, danger_color, 2)

        # Logica do jogo
        if state != "GAME_OVER":
            defender = 2 if attacker == 1 else 1

            # Checar posicoes
            def dist(p_a, p_b):
                return math.hypot(p_a[0] - p_b[0], p_a[1] - p_b[1])

            # Posicao do atacante e defensor
            att_pos = p1_pos if attacker == 1 else p2_pos
            def_pos = p2_pos if attacker == 1 else p1_pos

            # Flags de posicao
            att_in_base = False
            if att_pos is not None:
                if attacker == 1 and att_pos[0] < P1_BASE_X:
                    att_in_base = True
                elif attacker == 2 and att_pos[0] > P2_BASE_X:
                    att_in_base = True

            def_in_danger = (def_pos is not None and dist(def_pos, CENTER_POS) < DANGER_RADIUS)

            # Maquina de estados
            if state == "GET_READY":
                status_msg = f"Aguardando: P{attacker} na BASE | P{defender} no CENTRO"
                cv2.putText(frame, status_msg, (W // 2 - 200, 110),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 2)

                if att_in_base and def_in_danger:
                    state = "IN_POSITION"
                    play_sound(700, 100)

            elif state == "IN_POSITION":
                cv2.putText(frame, "ATENCAO! VALENDO O BOTE!", (W // 2 - 140, 110),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2)

                # Defensor tirou a mao antes do atacante sair da base? (Falsa Esquiva / Tremeu!)
                if not def_in_danger:
                    # Falha do defensor
                    result_text = f"P{defender} TREMEU! Ponto para P{attacker}!"
                    result_color = (0, 255, 255)
                    if attacker == 1: p1_score += 1
                    else: p2_score += 1
                    spawn_sparks(CENTER_POS, (0, 255, 255), 30)
                    play_sound(400, 300)
                    state = "RESULT_PAUSE"
                    pause_until = t_now + 2.0
                    attacker = 2 if attacker == 1 else 1

                # Atacante saiu da base? (Inicia ataque!)
                elif not att_in_base:
                    state = "ATTACK_ACTIVE"
                    play_sound(1000, 60)

            elif state == "ATTACK_ACTIVE":
                cv2.putText(frame, "GOLPE DESFERIDO!", (W // 2 - 100, 110),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                # Checa se atacante chegou ao centro
                att_reached_center = (att_pos is not None and dist(att_pos, CENTER_POS) < (DANGER_RADIUS + 20))
                def_escaped = False
                if def_pos is not None:
                    if defender == 1 and def_pos[0] < P1_BASE_X:
                        def_escaped = True
                    elif defender == 2 and def_pos[0] > P2_BASE_X:
                        def_escaped = True
                    elif dist(def_pos, CENTER_POS) > DANGER_RADIUS + 30:
                        def_escaped = True

                # Condicao 1: Defensor escapou antes do atacante alcancar o centro
                if def_escaped and not att_reached_center:
                    result_text = f"ESQUIVOU! P{defender} SALVO! (+1 Ponto)"
                    result_color = (0, 255, 0)
                    if defender == 1: p1_score += 1
                    else: p2_score += 1
                    spawn_sparks(def_pos if def_pos else CENTER_POS, (0, 255, 0), 25)
                    play_sound(1200, 150)
                    state = "RESULT_PAUSE"
                    pause_until = t_now + 2.0
                    attacker = 2 if attacker == 1 else 1

                # Condicao 2: Atacante alcancou e defensor ainda esta perto/na zona
                elif att_reached_center:
                    if def_in_danger or (def_pos and dist(att_pos, def_pos) < 60):
                        result_text = f"TAPA CONECTADO! P{attacker} ACERTOU! (+1 Ponto)"
                        result_color = (0, 0, 255)
                        if attacker == 1: p1_score += 1
                        else: p2_score += 1
                        spawn_sparks(CENTER_POS, (0, 0, 255), 40)
                        play_sound(250, 250)
                    else:
                        result_text = f"GOLPE NO VAZIO! P{defender} ESQUIVOU!"
                        result_color = (0, 255, 0)
                        if defender == 1: p1_score += 1
                        else: p2_score += 1
                        spawn_sparks(CENTER_POS, (0, 255, 0), 25)
                        play_sound(1100, 150)

                    state = "RESULT_PAUSE"
                    pause_until = t_now + 2.0
                    attacker = 2 if attacker == 1 else 1

            elif state == "RESULT_PAUSE":
                cv2.putText(frame, result_text, (W // 2 - 180, 110),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.65, result_color, 2)
                if t_now > pause_until:
                    if p1_score >= MAX_SCORE or p2_score >= MAX_SCORE:
                        state = "GAME_OVER"
                    else:
                        state = "GET_READY"

        else: # GAME_OVER
            winner = 1 if p1_score >= MAX_SCORE else 2
            win_color = (255, 200, 0) if winner == 1 else (0, 160, 255)
            cv2.rectangle(frame, (W // 2 - 200, 180), (W // 2 + 200, 320), (20, 20, 20), -1)
            cv2.rectangle(frame, (W // 2 - 200, 180), (W // 2 + 200, 320), win_color, 3)
            cv2.putText(frame, f"CAMPEAO: JOGADOR {winner}!", (W // 2 - 170, 235),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, win_color, 3)
            cv2.putText(frame, "Pressione 'r' para Reiniciar", (W // 2 - 140, 280),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)

        # Renderizar maos
        if p1_pos:
            cv2.circle(frame, p1_pos, 16, (255, 200, 0), -1)
            role1 = "ATACANTE" if attacker == 1 else "DEFENSOR"
            cv2.putText(frame, f"P1 ({role1})", (p1_pos[0] - 40, p1_pos[1] - 22),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 200, 0), 2)

        if p2_pos:
            cv2.circle(frame, p2_pos, 16, (0, 160, 255), -1)
            role2 = "ATACANTE" if attacker == 2 else "DEFENSOR"
            cv2.putText(frame, f"P2 ({role2})", (p2_pos[0] - 40, p2_pos[1] - 22),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 160, 255), 2)

        # Atualizar particulas
        for p in particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= 0.05
            if p['life'] <= 0:
                particles.remove(p)
            else:
                alpha = int(p['life'] * 255)
                color = tuple(min(255, int(c * p['life'])) for c in p['color'])
                cv2.circle(frame, (int(p['x']), int(p['y'])), int(4 * p['life']), color, -1)

        # Banner Superior SENAI
        hud_info = f"P1: {p1_score} | P2: {p2_score} (Meta: {MAX_SCORE})"
        draw_glow_banner(frame, "TAPA E ESQUIVA 1v1", hud_info)

        cv2.imshow("SENAI LAB - Tapa e Esquiva 1v1", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            p1_score = 0
            p2_score = 0
            attacker = 1
            state = "GET_READY"
            particles.clear()

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
