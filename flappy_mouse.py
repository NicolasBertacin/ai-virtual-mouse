"""
====================================================================
      FLAPPY BIRD TOUCHLESS - EDIÇÃO ESPECIAL SENAI (PYGAME)
====================================================================
Jogo interativo em Python puro com controle por Mouse Virtual Touchless.
O pássaro segue a mão do usuário suavemente pelo ar.

Comandos:
  - Mover: Aponte com o indicador (o pássaro segue o cursor)
  - Reiniciar: Clique com o mouse (pinça no ar) ou pressione ESPAÇO
  - Alternar Janela / Tela Cheia: Pressione 'F' ou 'F11'
  - Sair: Pressione 'Q' ou 'ESC'
====================================================================
"""

import pygame
import random
import sys
import math
import os

# Inicialização do Pygame
pygame.init()

# Cores Oficiais e Temáticas
COR_SENAI_VERMELHO = (227, 6, 19)
COR_SENAI_AZUL     = (0, 71, 143)
COR_FUNDO_CEU      = (100, 180, 245)
COR_BRANCO         = (255, 255, 255)
COR_PRETO          = (20, 24, 30)
COR_AMARELO        = (255, 215, 0)
COR_LARANJA        = (255, 140, 0)
COR_CANO_CORPO     = (34, 160, 68)
COR_CANO_BORDA     = (18, 115, 45)
COR_CANO_TOPO      = (227, 6, 19)      # Detalhe SENAI Vermelho
COR_CINZA_CLARO    = (240, 244, 248)
COR_SOMBRA         = (30, 41, 59, 160)

# Resolução padrão
LARGURA_PADRAO = 1024
ALTURA_PADRAO = 720

# Inicializa DIRETAMENTE EM TELA CHEIA (Fullscreen)
is_fullscreen = True
try:
    tela = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
except Exception:
    tela = pygame.display.set_mode((LARGURA_PADRAO, ALTURA_PADRAO), pygame.RESIZABLE)
    is_fullscreen = False

pygame.display.set_caption("SENAI Flappy Bird - Controle Touchless")

# Ícone da janela (se disponível)
logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "senai_logo.png")
if os.path.exists(logo_path):
    try:
        icone = pygame.image.load(logo_path)
        pygame.display.set_icon(icone)
    except Exception:
        pass

relogio = pygame.time.Clock()

# Fontes seguras do sistema
def obter_fontes():
    try:
        f_grande = pygame.font.SysFont("Arial", 46, bold=True)
        f_media = pygame.font.SysFont("Arial", 28, bold=True)
        f_pequena = pygame.font.SysFont("Arial", 18)
        f_hud = pygame.font.SysFont("Arial", 22, bold=True)
    except Exception:
        f_grande = pygame.font.Font(None, 52)
        f_media = pygame.font.Font(None, 32)
        f_pequena = pygame.font.Font(None, 20)
        f_hud = pygame.font.Font(None, 24)
    return f_grande, f_media, f_pequena, f_hud

fonte_grande, fonte_media, fonte_pequena, fonte_hud = obter_fontes()

# Parâmetros da Física do Jogo
LARGURA_BARREIRA = 88
ESPACO_PADRAO = 210
VELOCIDADE_CANO = 4.2
VELOCIDADE_SEGUIMENTO = 0.14
RAIO_PASSARO = 20

# Estado Global do Jogo
passaro_x = 180.0
passaro_y = ALTURA_PADRAO / 2
asa_fase = 0.0

barreiras = []
pontuacao = 0
recorde = 0
game_over = False

def criar_barreira(pos_x, largura_tela, altura_tela):
    margem = 80
    espaco = max(200, int(altura_tela * 0.26))
    topo = random.randint(margem, max(margem + 10, int(altura_tela - espaco - margem)))
    return {
        "x": float(pos_x),
        "topo": topo,
        "espaco": espaco,
        "passou": False
    }

def reiniciar():
    global passaro_x, passaro_y, barreiras, pontuacao, game_over
    w, h = tela.get_size()
    passaro_x = min(220.0, w * 0.22)
    passaro_y = h / 2
    dist_barreira = max(360, int(w * 0.28))
    barreiras = [
        criar_barreira(w + 100, w, h),
        criar_barreira(w + 100 + dist_barreira, w, h)
    ]
    pontuacao = 0
    game_over = False

# Nuvens decorativas de fundo
nuvens = [
    {"x": 120, "y": 80, "vel": 0.4, "t": 28},
    {"x": 450, "y": 140, "vel": 0.3, "t": 36},
    {"x": 800, "y": 95, "vel": 0.5, "t": 24},
    {"x": 1150, "y": 160, "vel": 0.35, "t": 32},
    {"x": 1500, "y": 110, "vel": 0.45, "t": 30}
]

# Inicializa jogo
reiniciar()

# Loop Principal
executando = True
while executando:
    relogio.tick(60)
    largura_atual, altura_atual = tela.get_size()

    # Processamento de Eventos
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            executando = False

        elif evento.type == pygame.KEYDOWN:
            # Alternar Tela Cheia (F ou F11)
            if evento.key in (pygame.K_f, pygame.K_F11):
                is_fullscreen = not is_fullscreen
                if is_fullscreen:
                    tela = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                else:
                    tela = pygame.display.set_mode((LARGURA_PADRAO, ALTURA_PADRAO), pygame.RESIZABLE)
                reiniciar()

            # Reiniciar partida pelo teclado (Espaço ou Enter)
            elif evento.key in (pygame.K_SPACE, pygame.K_RETURN) and game_over:
                reiniciar()

            # Sair (Q ou ESC)
            elif evento.key in (pygame.K_q, pygame.K_ESCAPE):
                executando = False

        elif evento.type == pygame.VIDEORESIZE:
            if not is_fullscreen:
                tela = pygame.display.set_mode((evento.w, evento.h), pygame.RESIZABLE)

        # Reiniciar partida com clique do mouse (ou pinça touchless)
        elif evento.type == pygame.MOUSEBUTTONDOWN and game_over:
            reiniciar()

    # Atualização da Lógica do Jogo
    if not game_over:
        # Pássaro segue suavemente a posição do cursor (Touchless)
        mouse_x, mouse_y = pygame.mouse.get_pos()
        alvo_y = float(mouse_y)

        # Suavização com interpolação
        passaro_y += (alvo_y - passaro_y) * VELOCIDADE_SEGUIMENTO

        # Limitar dentro dos limites da tela com margem de segurança
        passaro_y = max(RAIO_PASSARO + 10, min(altura_atual - RAIO_PASSARO - 10, passaro_y))
        passaro_x = min(220.0, largura_atual * 0.22)

        # Bater de asas animado
        velocidade_vertical = alvo_y - passaro_y
        asa_fase += 0.2 + abs(velocidade_vertical) * 0.01

        # Mover barreiras
        for barreira in barreiras:
            barreira["x"] -= VELOCIDADE_CANO

            # Contabilizar pontuação ao ultrapassar
            if not barreira["passou"] and barreira["x"] + LARGURA_BARREIRA < passaro_x:
                pontuacao += 1
                barreira["passou"] = True

        # Gerar novas barreiras à frente
        dist_prox = max(360, int(largura_atual * 0.28))
        if len(barreiras) == 0 or barreiras[-1]["x"] < largura_atual - 300:
            pos_nova = largura_atual + 50 if len(barreiras) == 0 else barreiras[-1]["x"] + dist_prox
            barreiras.append(criar_barreira(pos_nova, largura_atual, altura_atual))

        # Descartar barreiras que saíram da tela
        barreiras = [b for b in barreiras if b["x"] + LARGURA_BARREIRA > -20]

        # Caixa de colisão do pássaro
        passaro_rect = pygame.Rect(
            int(passaro_x - RAIO_PASSARO),
            int(passaro_y - RAIO_PASSARO),
            RAIO_PASSARO * 2,
            RAIO_PASSARO * 2
        )

        # Detecção de Colisão com as Barreiras
        for barreira in barreiras:
            bx = int(barreira["x"])
            topo = barreira["topo"]
            espaco = barreira.get("espaco", ESPACO_PADRAO)
            base = topo + espaco

            rect_sup = pygame.Rect(bx, 0, LARGURA_BARREIRA, topo)
            rect_inf = pygame.Rect(bx, base, LARGURA_BARREIRA, altura_atual - base)

            if passaro_rect.colliderect(rect_sup) or passaro_rect.colliderect(rect_inf):
                game_over = True
                recorde = max(recorde, pontuacao)

        # Colisão com o teto ou o chão
        if passaro_y - RAIO_PASSARO <= 5 or passaro_y + RAIO_PASSARO >= altura_atual - 5:
            game_over = True
            recorde = max(recorde, pontuacao)

    # ==================== RENDERIZAÇÃO GRÁFICA ====================

    # 1. Fundo Gradiente (Céu)
    tela.fill(COR_FUNDO_CEU)

    # 2. Nuvens em Movimento Suave
    for n in nuvens:
        n["x"] -= n["vel"]
        if n["x"] < -120:
            n["x"] = largura_atual + 80
            n["y"] = random.randint(50, max(60, altura_atual // 3))
        # Desenho composto de nuvem
        nx, ny, nt = int(n["x"]), int(n["y"]), n["t"]
        pygame.draw.circle(tela, (255, 255, 255, 210), (nx, ny), nt)
        pygame.draw.circle(tela, (255, 255, 255, 210), (nx + int(nt * 0.7), ny - int(nt * 0.2)), int(nt * 0.8))
        pygame.draw.circle(tela, (255, 255, 255, 210), (nx - int(nt * 0.7), ny + int(nt * 0.1)), int(nt * 0.7))

    # 3. Desenho das Barreiras (Estilo Industrial SENAI)
    for barreira in barreiras:
        bx = int(barreira["x"])
        topo = barreira["topo"]
        espaco = barreira.get("espaco", ESPACO_PADRAO)
        base = topo + espaco

        # Cano Superior
        pygame.draw.rect(tela, COR_CANO_CORPO, (bx, 0, LARGURA_BARREIRA, topo))
        pygame.draw.rect(tela, COR_CANO_BORDA, (bx, 0, LARGURA_BARREIRA, topo), 3)
        pygame.draw.rect(tela, COR_CANO_CORPO, (bx - 6, topo - 26, LARGURA_BARREIRA + 12, 26))
        pygame.draw.rect(tela, COR_CANO_BORDA, (bx - 6, topo - 26, LARGURA_BARREIRA + 12, 26), 3)
        pygame.draw.rect(tela, COR_SENAI_VERMELHO, (bx - 6, topo - 6, LARGURA_BARREIRA + 12, 6))

        # Cano Inferior
        pygame.draw.rect(tela, COR_CANO_CORPO, (bx, base, LARGURA_BARREIRA, altura_atual - base))
        pygame.draw.rect(tela, COR_CANO_BORDA, (bx, base, LARGURA_BARREIRA, altura_atual - base), 3)
        pygame.draw.rect(tela, COR_CANO_CORPO, (bx - 6, base, LARGURA_BARREIRA + 12, 26))
        pygame.draw.rect(tela, COR_CANO_BORDA, (bx - 6, base, LARGURA_BARREIRA + 12, 26), 3)
        pygame.draw.rect(tela, COR_SENAI_VERMELHO, (bx - 6, base, LARGURA_BARREIRA + 12, 6))

    # 4. Desenho do Pássaro / Drone Tecnológico
    px = int(passaro_x)
    py = int(passaro_y)

    # Sombra do pássaro
    pygame.draw.ellipse(tela, (60, 90, 120, 80), (px - RAIO_PASSARO + 4, py + RAIO_PASSARO - 4, RAIO_PASSARO * 2, 8))

    # Corpo Amarelo / Dourado
    pygame.draw.circle(tela, COR_LARANJA, (px, py + 2), RAIO_PASSARO)
    pygame.draw.circle(tela, COR_AMARELO, (px, py), RAIO_PASSARO)
    pygame.draw.circle(tela, COR_PRETO, (px, py), RAIO_PASSARO, 2)

    # Asa Batendo (Oscilação senoidal)
    asa_offset_y = math.sin(asa_fase) * 6
    asa_rect = pygame.Rect(px - 14, int(py - 4 + asa_offset_y), 18, 13)
    pygame.draw.ellipse(tela, COR_BRANCO, asa_rect)
    pygame.draw.ellipse(tela, COR_SENAI_VERMELHO, asa_rect, 2)

    # Olho do Pássaro
    pygame.draw.circle(tela, COR_BRANCO, (px + 7, py - 5), 6)
    pygame.draw.circle(tela, COR_PRETO, (px + 9, py - 5), 3)
    pygame.draw.circle(tela, COR_BRANCO, (px + 10, py - 7), 1)

    # Bico Laranja
    bico_pts = [(px + 15, py - 3), (px + 28, py + 2), (px + 15, py + 7)]
    pygame.draw.polygon(tela, COR_LARANJA, bico_pts)
    pygame.draw.polygon(tela, COR_PRETO, bico_pts, 2)

    # 5. Barra Superior HUD & SENAI Branding
    hud_bg = pygame.Surface((largura_atual, 58), pygame.SRCALPHA)
    hud_bg.fill((15, 23, 42, 210))
    tela.blit(hud_bg, (0, 0))

    # Friso vermelho SENAI na base do HUD
    pygame.draw.rect(tela, COR_SENAI_VERMELHO, (0, 55, largura_atual, 3))

    # Logo / Texto SENAI
    txt_logo = fonte_hud.render("SENAI", True, COR_SENAI_VERMELHO)
    txt_sub = fonte_pequena.render("FLAPPY BIRD TOUCHLESS", True, COR_BRANCO)
    tela.blit(txt_logo, (24, 16))
    tela.blit(txt_sub, (98, 19))

    # Pontuação no Centro com Sombra
    txt_score_sombra = fonte_grande.render(str(pontuacao), True, (15, 23, 42))
    txt_score = fonte_grande.render(str(pontuacao), True, COR_BRANCO)
    cx = largura_atual // 2 - txt_score.get_width() // 2
    tela.blit(txt_score_sombra, (cx + 2, 7))
    tela.blit(txt_score, (cx, 5))

    # Recorde à Direita
    txt_rec = fonte_hud.render(f"RECORDE: {recorde}", True, COR_AMARELO)
    tela.blit(txt_rec, (largura_atual - txt_rec.get_width() - 24, 17))

    # 6. Dica no Rodapé
    txt_dica = fonte_pequena.render("Mova a mão no ar para pilotar  |  [F] Alternar Tela Cheia  |  [Q] Sair", True, (245, 245, 245))
    sombra_dica = fonte_pequena.render("Mova a mão no ar para pilotar  |  [F] Alternar Tela Cheia  |  [Q] Sair", True, (20, 20, 20))
    dx = largura_atual // 2 - txt_dica.get_width() // 2
    tela.blit(sombra_dica, (dx + 1, altura_atual - 27))
    tela.blit(txt_dica, (dx, altura_atual - 28))

    # 7. Tela de Game Over
    if game_over:
        overlay = pygame.Surface((largura_atual, altura_atual), pygame.SRCALPHA)
        overlay.fill((15, 23, 42, 210))
        tela.blit(overlay, (0, 0))

        # Caixa do Card de Game Over
        card_w = min(540, largura_atual - 40)
        card_h = 280
        card_x = largura_atual // 2 - card_w // 2
        card_y = altura_atual // 2 - card_h // 2

        pygame.draw.rect(tela, (255, 255, 255), (card_x, card_y, card_w, card_h), border_radius=14)
        pygame.draw.rect(tela, COR_SENAI_VERMELHO, (card_x, card_y, card_w, 8), border_top_left_radius=14, border_top_right_radius=14)
        pygame.draw.rect(tela, (203, 213, 225), (card_x, card_y, card_w, card_h), 2, border_radius=14)

        # Título
        txt_fim = fonte_grande.render("FIM DE VOO", True, COR_SENAI_VERMELHO)
        tela.blit(txt_fim, (largura_atual // 2 - txt_fim.get_width() // 2, card_y + 30))

        # Estatísticas
        txt_resumo = fonte_media.render(f"Pontos: {pontuacao}    •    Recorde: {recorde}", True, COR_PRETO)
        tela.blit(txt_resumo, (largura_atual // 2 - txt_resumo.get_width() // 2, card_y + 95))

        # Botão / Dica de Reiniciar
        btn_reiniciar_rect = pygame.Rect(largura_atual // 2 - 160, card_y + 155, 320, 48)
        pygame.draw.rect(tela, COR_SENAI_VERMELHO, btn_reiniciar_rect, border_radius=24)
        txt_btn = fonte_hud.render("FAÇA A PINÇA OU CLIQUE", True, COR_BRANCO)
        tela.blit(txt_btn, (btn_reiniciar_rect.centerx - txt_btn.get_width() // 2, btn_reiniciar_rect.centery - txt_btn.get_height() // 2))

        txt_instrucao = fonte_pequena.render("Pressione [ESPAÇO] ou clique na tela para tentar de novo", True, (100, 116, 139))
        tela.blit(txt_instrucao, (largura_atual // 2 - txt_instrucao.get_width() // 2, card_y + 225))

    pygame.display.flip()

pygame.quit()
sys.exit()
