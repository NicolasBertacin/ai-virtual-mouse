"""
====================================================================
      FRUIT NINJA TOUCHLESS - EDIÇÃO ESPECIAL SENAI (PYGAME)
====================================================================
Jogo interativo em Python puro com controle por Mouse Virtual Touchless.
Mova a mão no ar como uma lâmina laser para cortar as frutas que sobem
pela tela. Desvie das bombas vermelhas!

Comandos:
  - Lâmina Laser: Mova a mão no ar com velocidade para cortar
  - Alternar Janela / Tela Cheia: Pressione 'F' ou 'F11'
  - Reiniciar: Clique com o mouse (pinça no ar) ou pressione ESPAÇO
  - Sair: Pressione 'Q' ou 'ESC'
====================================================================
"""

import pygame
import random
import sys
import math
import time
from collections import deque

# Inicialização do Pygame e mixer de áudio
pygame.init()
try:
    pygame.mixer.init(44100, -16, 2, 512)
    AUDIO_DISPONIVEL = True
except Exception:
    AUDIO_DISPONIVEL = False

# Resolução padrão
LARGURA_PADRAO = 1024
ALTURA_PADRAO = 720

# INICIALIZA DIRETAMENTE EM TELA CHEIA (Fullscreen)
is_fullscreen = True
try:
    tela = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
except Exception:
    tela = pygame.display.set_mode((LARGURA_PADRAO, ALTURA_PADRAO), pygame.RESIZABLE)
    is_fullscreen = False

pygame.display.set_caption("SENAI Fruit Ninja - Corte Touchless")

relogio = pygame.time.Clock()

# Cores Principais (Tema Claro com Identidade SENAI)
COR_SENAI_VERMELHO = (227, 6, 19)
COR_SENAI_AZUL     = (0, 71, 143)

# Fundo Claro e Moderno (Tábua de corte clara estilo Dojo / Sala Tecnológica)
COR_FUNDO_CLARO    = (246, 244, 238)
COR_FUNDO_TABUA    = (226, 222, 212)
COR_SOMBRA_FRUTA   = (190, 184, 172)

COR_BRANCO         = (255, 255, 255)
COR_PRETO          = (15, 17, 22)
COR_OURO           = (255, 195, 0)
COR_LASER_EXTERNO  = (0, 185, 255)
COR_LASER_INTERNO  = (255, 255, 255)
COR_LASER_SENAI    = (227, 6, 19)

# Fontes seguras do sistema
def obter_fontes():
    try:
        f_grande = pygame.font.SysFont("Arial", 46, bold=True)
        f_media  = pygame.font.SysFont("Arial", 28, bold=True)
        f_pequena = pygame.font.SysFont("Arial", 18, bold=True)
        f_hud    = pygame.font.SysFont("Arial", 22, bold=True)
        f_combo  = pygame.font.SysFont("Arial", 34, bold=True)
    except Exception:
        f_grande = pygame.font.Font(None, 52)
        f_media  = pygame.font.Font(None, 32)
        f_pequena = pygame.font.Font(None, 20)
        f_hud    = pygame.font.Font(None, 24)
        f_combo  = pygame.font.Font(None, 38)
    return f_grande, f_media, f_pequena, f_hud, f_combo

fonte_grande, fonte_media, fonte_pequena, fonte_hud, fonte_combo = obter_fontes()

# Geração de Efeitos Sonoros Sintéticos com NumPy (Zero arquivos externos)
sons = {}
if AUDIO_DISPONIVEL:
    try:
        import numpy as np

        def criar_som_corte():
            dur = 0.12
            sr = 44100
            t = np.linspace(0, dur, int(sr * dur), False)
            freq = np.linspace(1200, 300, len(t))
            env = np.sin(np.pi * t / dur) ** 2
            wave = np.sin(2 * np.pi * freq * t) * env * 0.4
            noise = (np.random.rand(len(t)) * 2 - 1) * 0.15 * env
            final = wave + noise
            stereo = np.ascontiguousarray(np.vstack((final, final)).T * 32767, dtype=np.int16)
            return pygame.sndarray.make_sound(stereo)

        def criar_som_splat():
            dur = 0.18
            sr = 44100
            t = np.linspace(0, dur, int(sr * dur), False)
            freq = np.linspace(480, 160, len(t))
            env = np.exp(-14 * t)
            wave = np.sin(2 * np.pi * freq * t) * env * 0.5
            noise = (np.random.rand(len(t)) * 2 - 1) * 0.25 * env
            final = wave + noise
            stereo = np.ascontiguousarray(np.vstack((final, final)).T * 32767, dtype=np.int16)
            return pygame.sndarray.make_sound(stereo)

        def criar_som_explosao():
            dur = 0.55
            sr = 44100
            t = np.linspace(0, dur, int(sr * dur), False)
            env = np.exp(-5.5 * t)
            sub = np.sin(2 * np.pi * 75 * t) * env * 0.7
            noise = (np.random.rand(len(t)) * 2 - 1) * 0.6 * env
            final = sub + noise
            stereo = np.ascontiguousarray(np.vstack((final, final)).T * 32767, dtype=np.int16)
            return pygame.sndarray.make_sound(stereo)

        def criar_som_combo():
            dur = 0.35
            sr = 44100
            t = np.linspace(0, dur, int(sr * dur), False)
            env = np.exp(-6 * t)
            c = np.sin(2 * np.pi * 523.25 * t)
            e = np.sin(2 * np.pi * 659.25 * t)
            g = np.sin(2 * np.pi * 783.99 * t)
            c2 = np.sin(2 * np.pi * 1046.50 * t)
            final = (c + e + g + c2) * 0.2 * env
            stereo = np.ascontiguousarray(np.vstack((final, final)).T * 32767, dtype=np.int16)
            return pygame.sndarray.make_sound(stereo)

        sons["corte"] = criar_som_corte()
        sons["splat"] = criar_som_splat()
        sons["explosao"] = criar_som_explosao()
        sons["combo"] = criar_som_combo()
    except Exception as e:
        print(f"[Aviso] Áudio sintético indisponível: {e}")
        AUDIO_DISPONIVEL = False

def tocar_som(nome):
    if AUDIO_DISPONIVEL and nome in sons:
        try:
            sons[nome].play()
        except Exception:
            pass

# Tipos de Frutas e Propriedades Gráficas
TIPOS_FRUTA = {
    "melancia": {
        "nome": "Melancia",
        "raio": 40,
        "cor_casca": (32, 138, 55),
        "cor_polpa": (228, 26, 46),
        "cor_juice": (225, 20, 50),
        "pontos": 1
    },
    "laranja": {
        "nome": "Laranja",
        "raio": 34,
        "cor_casca": (255, 140, 0),
        "cor_polpa": (255, 180, 40),
        "cor_juice": (255, 145, 20),
        "pontos": 1
    },
    "maca": {
        "nome": "Maçã",
        "raio": 32,
        "cor_casca": (215, 22, 32),
        "cor_polpa": (245, 240, 210),
        "cor_juice": (228, 35, 35),
        "pontos": 1
    },
    "banana": {
        "nome": "Banana",
        "raio": 30,
        "cor_casca": (255, 220, 25),
        "cor_polpa": (255, 248, 195),
        "cor_juice": (245, 215, 50),
        "pontos": 2
    },
    "coco": {
        "nome": "Coco",
        "raio": 36,
        "cor_casca": (115, 68, 38),
        "cor_polpa": (245, 245, 250),
        "cor_juice": (140, 150, 160),
        "pontos": 3
    },
    "morango": {
        "nome": "Morango",
        "raio": 26,
        "cor_casca": (230, 18, 55),
        "cor_polpa": (255, 115, 125),
        "cor_juice": (230, 20, 50),
        "pontos": 2
    },
    "bomba": {
        "nome": "Bomba",
        "raio": 34,
        "cor_casca": (24, 26, 32),
        "cor_polpa": (180, 20, 20),
        "cor_juice": (255, 80, 0),
        "pontos": 0
    }
}

# ==================== CLASSES DO JOGO ====================

class Fruta:
    """Representa uma fruta ou bomba lançada alto em arco gravitacional majestoso."""
    def __init__(self, tipo_nome, largura_tela, altura_tela):
        self.tipo_nome = tipo_nome
        self.tipo = TIPOS_FRUTA[tipo_nome]
        self.raio = self.tipo["raio"]
        self.is_bomba = (tipo_nome == "bomba")

        # Posição de lançamento na parte inferior
        self.x = random.randint(int(largura_tela * 0.12), int(largura_tela * 0.88))
        self.y = altura_tela + self.raio + random.randint(15, 45)

        # Gravidade suave para dar tempo de corte
        self.gravidade = 0.26

        # FÓRMULA DE VOO ALTO: O ápice do salto alcança entre 8% e 20% do topo da tela!
        altura_alvo_topo = random.uniform(altura_tela * 0.08, altura_tela * 0.20)
        distancia_subida = max(100.0, self.y - altura_alvo_topo)

        # v^2 = 2 * g * h => vy = -sqrt(2 * g * h)
        self.vy = -math.sqrt(2.0 * self.gravidade * distancia_subida)

        # Velocidade horizontal com leve curvatura em direção ao centro
        margem_centro = (largura_tela / 2 - self.x) * 0.002
        self.vx = random.uniform(-2.2, 2.2) + margem_centro

        self.angulo = random.uniform(0, 360)
        self.v_rotacao = random.uniform(-3.5, 3.5)

        self.cortada = False
        self.ativa = True
        self.perdeu_ponto = False

    def atualizar(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravidade
        self.angulo += self.v_rotacao

    def desenhar(self, superficie):
        px, py = int(self.x), int(self.y)

        if self.is_bomba:
            # Sombra suave da bomba
            pygame.draw.circle(superficie, COR_SOMBRA_FRUTA, (px + 4, py + 6), self.raio)

            # Corpo esférico negro metálico
            pygame.draw.circle(superficie, (26, 28, 35), (px, py), self.raio)
            pygame.draw.circle(superficie, (75, 80, 92), (px - 8, py - 8), self.raio // 3)
            pygame.draw.circle(superficie, COR_SENAI_VERMELHO, (px, py), self.raio, 3)

            # Pavio e faíscas animadas
            pavio_x = px + int(math.cos(math.radians(self.angulo)) * self.raio)
            pavio_y = py - int(math.sin(math.radians(self.angulo)) * self.raio)
            pygame.draw.line(superficie, (160, 120, 70), (px, py), (pavio_x, pavio_y), 4)

            # Faísca brilhante
            faica_cor = random.choice([(255, 230, 50), (255, 80, 20), (255, 255, 255)])
            pygame.draw.circle(superficie, faica_cor, (pavio_x, pavio_y), random.randint(4, 8))

            # Ícone de perigo SENAI no centro
            txt_x = fonte_pequena.render("X", True, COR_SENAI_VERMELHO)
            superficie.blit(txt_x, (px - txt_x.get_width() // 2, py - txt_x.get_height() // 2))

        else:
            r = self.raio
            casca = self.tipo["cor_casca"]
            polpa = self.tipo["cor_polpa"]

            # Sombra suave no fundo claro
            pygame.draw.circle(superficie, COR_SOMBRA_FRUTA, (px + 4, py + 6), r)

            # Casca da fruta
            pygame.draw.circle(superficie, casca, (px, py), r)

            # Detalhes específicos de cada fruta
            if self.tipo_nome == "melancia":
                # Listras verde-escuras da melancia
                for ang in range(0, 360, 45):
                    rad = math.radians(ang + self.angulo)
                    p1 = (px + math.cos(rad) * (r * 0.4), py + math.sin(rad) * (r * 0.4))
                    p2 = (px + math.cos(rad) * r, py + math.sin(rad) * r)
                    pygame.draw.line(superficie, (18, 85, 32), p1, p2, 4)

            elif self.tipo_nome == "laranja":
                pygame.draw.circle(superficie, (255, 110, 0), (px, py), r - 4)
                pygame.draw.circle(superficie, (255, 180, 50), (px - 6, py - 6), r // 3)

            elif self.tipo_nome == "maca":
                rad = math.radians(self.angulo - 90)
                cab_fim = (px + math.cos(rad) * (r + 9), py + math.sin(rad) * (r + 9))
                pygame.draw.line(superficie, (90, 50, 20), (px, py), cab_fim, 3)
                pygame.draw.circle(superficie, (255, 90, 90), (px - 6, py - 6), r // 4)

            elif self.tipo_nome == "banana":
                pygame.draw.ellipse(superficie, casca, (px - r, py - r // 2, r * 2, r))
                pygame.draw.circle(superficie, (110, 75, 20), (px + r - 3, py), 4)

            elif self.tipo_nome == "coco":
                pygame.draw.circle(superficie, (75, 40, 20), (px, py), r, 3)

            elif self.tipo_nome == "morango":
                for sx, sy in [(-6, -4), (6, -2), (0, 4), (-5, 6), (4, 7)]:
                    pygame.draw.circle(superficie, (150, 10, 30), (px + sx, py + sy), 2)
                pygame.draw.circle(superficie, (40, 160, 60), (px, py - r + 3), 6)


class MetadeFruta:
    """Representa uma das duas metades de uma fruta cortada."""
    def __init__(self, tipo_nome, x, y, vx, vy, angulo, v_rot, lado):
        self.tipo_nome = tipo_nome
        self.tipo = TIPOS_FRUTA[tipo_nome]
        self.x = x
        self.y = y
        self.vx = vx + (3.8 if lado == 1 else -3.8)
        self.vy = vy + random.uniform(-2.5, 0.5)
        self.angulo = angulo
        self.v_rot = v_rot * 1.8 + (4.0 if lado == 1 else -4.0)
        self.lado = lado
        self.raio = self.tipo["raio"]
        self.ativa = True

    def atualizar(self, gravidade=0.38):
        self.x += self.vx
        self.y += self.vy
        self.vy += gravidade
        self.angulo += self.v_rot

    def desenhar(self, superficie):
        px, py = int(self.x), int(self.y)
        r = self.raio
        casca = self.tipo["cor_casca"]
        polpa = self.tipo["cor_polpa"]

        surf_metade = pygame.Surface((r * 2 + 10, r * 2 + 10), pygame.SRCALPHA)
        cx, cy = r + 5, r + 5

        pygame.draw.circle(surf_metade, casca, (cx, cy), r)
        pygame.draw.circle(surf_metade, polpa, (cx, cy), r - 5)

        # Corta a metade oposta
        if self.lado == 1:
            pygame.draw.rect(surf_metade, (0, 0, 0, 0), (0, cy, r * 2 + 10, r + 5))
        else:
            pygame.draw.rect(surf_metade, (0, 0, 0, 0), (0, 0, r * 2 + 10, cy))

        rotacionada = pygame.transform.rotate(surf_metade, self.angulo)
        superficie.blit(rotacionada, (px - rotacionada.get_width() // 2, py - rotacionada.get_height() // 2))


class ParticulaJuice:
    """Gotas e respingos de suco e faíscas."""
    def __init__(self, x, y, cor, vel_max=7.5, vida_max=36):
        self.x = x
        self.y = y
        ang = random.uniform(0, math.pi * 2)
        v = random.uniform(1.8, vel_max)
        self.vx = math.cos(ang) * v
        self.vy = math.sin(ang) * v
        self.cor = cor
        self.vida = vida_max
        self.vida_total = vida_max
        self.raio = random.uniform(3.5, 7.5)

    def atualizar(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.28
        self.vida -= 1

    def desenhar(self, superficie):
        if self.vida > 0:
            alpha = int((self.vida / self.vida_total) * 230)
            r = max(1, int(self.raio * (self.vida / self.vida_total)))
            surf_p = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(surf_p, (*self.cor[:3], alpha), (r + 1, r + 1), r)
            superficie.blit(surf_p, (int(self.x) - r, int(self.y) - r))


class NotificacaoTexto:
    """Textos flutuantes de Combo e Bônus com sombra de alto contraste."""
    def __init__(self, texto, x, y, cor=(255, 140, 0), duracao=48):
        self.texto = texto
        self.x = x
        self.y = y
        self.cor = cor
        self.vida = duracao
        self.vida_total = duracao

    def atualizar(self):
        self.y -= 1.8
        self.vida -= 1

    def desenhar(self, superficie):
        if self.vida > 0:
            alpha = int((self.vida / self.vida_total) * 255)
            surf_t = fonte_combo.render(self.texto, True, self.cor)
            surf_sombra = fonte_combo.render(self.texto, True, (15, 23, 42))

            surf_t.set_alpha(alpha)
            surf_sombra.set_alpha(alpha)

            superficie.blit(surf_sombra, (int(self.x) - surf_t.get_width() // 2 + 2, int(self.y) + 2))
            superficie.blit(surf_t, (int(self.x) - surf_t.get_width() // 2, int(self.y)))


# ==================== FUNÇÕES MATEMÁTICAS DE CORTE ====================

def distancia_ponto_segmento(px, py, x1, y1, x2, y2):
    """Calcula a menor distância entre um ponto e um segmento de reta."""
    dx = x2 - x1
    dy = y2 - y1
    if dx == 0 and dy == 0:
        return math.hypot(px - x1, py - y1)

    t = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))
    proj_x = x1 + t * dx
    proj_y = y1 + t * dy
    return math.hypot(px - proj_x, py - proj_y)


# ==================== ESTADO DO JOGO ====================

pontuacao = 0
recorde = 0
vidas = 3
game_over = False

frutas = []
metades = []
particulas = []
notificacoes = []
manchas_fundo = []

# Rastro da Lâmina Laser
rastro_lamina = deque(maxlen=16)

# Controle de Lançamento
tempo_ultimo_spawn = time.time()
intervalo_spawn = 2.1

# Temporizador de Combos
tempo_ultimo_corte = 0
frutas_no_corte_atual = 0

def reiniciar():
    global pontuacao, vidas, game_over, frutas, metades, particulas, notificacoes, manchas_fundo, rastro_lamina
    pontuacao = 0
    vidas = 3
    game_over = False
    frutas.clear()
    metades.clear()
    particulas.clear()
    notificacoes.clear()
    manchas_fundo.clear()
    rastro_lamina.clear()

def spawn_onda(largura, altura):
    """Lança uma nova remessa de frutas altas e eventuais bombas."""
    global intervalo_spawn

    if pontuacao > 40:
        qtd = random.randint(3, 5)
        chance_bomba = 0.32
    elif pontuacao > 20:
        qtd = random.randint(2, 4)
        chance_bomba = 0.22
    else:
        qtd = random.randint(1, 3)
        chance_bomba = 0.12

    tipos_disponiveis = ["melancia", "laranja", "maca", "banana", "coco", "morango"]

    for _ in range(qtd):
        if random.random() < chance_bomba and len(frutas) > 0 and pontuacao >= 5:
            frutas.append(Fruta("bomba", largura, altura))
        else:
            tipo = random.choice(tipos_disponiveis)
            frutas.append(Fruta(tipo, largura, altura))

# Inicialização
reiniciar()

# ==================== LOOP PRINCIPAL ====================
executando = True
while executando:
    dt = relogio.tick(60) / 1000.0
    largura_atual, altura_atual = tela.get_size()
    agora = time.time()

    # Leitura do mouse / touchless
    mouse_x, mouse_y = pygame.mouse.get_pos()
    rastro_lamina.append({"x": mouse_x, "y": mouse_y, "t": agora})

    # Velocidade instantânea do corte
    velocidade_corte = 0.0
    if len(rastro_lamina) >= 2:
        p_ant = rastro_lamina[-2]
        p_atual = rastro_lamina[-1]
        velocidade_corte = math.hypot(p_atual["x"] - p_ant["x"], p_atual["y"] - p_ant["y"])

    # Reset do combo se a lâmina parar por mais de 0.28s
    if agora - tempo_ultimo_corte > 0.28:
        if frutas_no_corte_atual >= 3:
            bonus = frutas_no_corte_atual
            pontuacao += bonus
            notificacoes.append(NotificacaoTexto(f"COMBO x{frutas_no_corte_atual}! +{bonus}", mouse_x, mouse_y - 20, COR_OURO))
            tocar_som("combo")
        elif frutas_no_corte_atual == 2:
            pontuacao += 1
            notificacoes.append(NotificacaoTexto("COMBO x2! +1", mouse_x, mouse_y - 20, (255, 140, 20)))
            tocar_som("combo")
        frutas_no_corte_atual = 0

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

            # Reiniciar partida
            elif evento.key in (pygame.K_SPACE, pygame.K_RETURN) and game_over:
                reiniciar()

            # Sair
            elif evento.key in (pygame.K_q, pygame.K_ESCAPE):
                executando = False

        elif evento.type == pygame.VIDEORESIZE:
            if not is_fullscreen:
                tela = pygame.display.set_mode((evento.w, evento.h), pygame.RESIZABLE)

        elif evento.type == pygame.MOUSEBUTTONDOWN and game_over:
            reiniciar()

    # ==================== LÓGICA DO JOGO ====================
    if not game_over:
        # Lançar novas frutas periodicamente
        if agora - tempo_ultimo_spawn > intervalo_spawn:
            spawn_onda(largura_atual, altura_atual)
            tempo_ultimo_spawn = agora
            intervalo_spawn = max(1.2, 2.3 - (pontuacao * 0.02))

        # Verificação de Corte (Colisão da Lâmina com as Frutas)
        LIMIAR_VELOCIDADE = 5.5
        if len(rastro_lamina) >= 2 and velocidade_corte >= LIMIAR_VELOCIDADE:
            p1 = rastro_lamina[-2]
            p2 = rastro_lamina[-1]

            for fruta in frutas:
                if not fruta.cortada:
                    dist = distancia_ponto_segmento(fruta.x, fruta.y, p1["x"], p1["y"], p2["x"], p2["y"])

                    if dist <= fruta.raio:
                        # CORTOU A FRUTA!
                        fruta.cortada = True
                        fruta.ativa = False

                        if fruta.is_bomba:
                            # CORTOU A BOMBA!
                            tocar_som("explosao")
                            vidas -= 1
                            notificacoes.append(NotificacaoTexto("💥 BOMBA! -1 VIDA", fruta.x, fruta.y, (227, 6, 19)))

                            for _ in range(40):
                                particulas.append(ParticulaJuice(fruta.x, fruta.y, (255, 80, 20), vel_max=12.0, vida_max=45))

                            if vidas <= 0:
                                game_over = True
                                recorde = max(recorde, pontuacao)

                        else:
                            # FRUTA LEGÍTIMA CORTADA
                            tocar_som("splat")
                            tocar_som("corte")
                            pontos_ganhos = fruta.tipo["pontos"]
                            pontuacao += pontos_ganhos
                            recorde = max(recorde, pontuacao)

                            tempo_ultimo_corte = agora
                            frutas_no_corte_atual += 1

                            # Cria as duas metades separadas
                            metades.append(MetadeFruta(fruta.tipo_nome, fruta.x, fruta.y, fruta.vx, fruta.vy, fruta.angulo, fruta.v_rotacao, lado=1))
                            metades.append(MetadeFruta(fruta.tipo_nome, fruta.x, fruta.y, fruta.vx, fruta.vy, fruta.angulo, fruta.v_rotacao, lado=2))

                            # Respingos de suco no fundo claro (aquarela vibrante)
                            manchas_fundo.append({
                                "x": fruta.x, "y": fruta.y,
                                "r": random.randint(fruta.raio - 2, fruta.raio + 14),
                                "cor": fruta.tipo["cor_juice"],
                                "alpha": 160
                            })
                            if len(manchas_fundo) > 22:
                                manchas_fundo.pop(0)

                            # Partículas de suco explodindo
                            for _ in range(24):
                                particulas.append(ParticulaJuice(fruta.x, fruta.y, fruta.tipo["cor_juice"]))

        # Atualização das Frutas Ativas
        for fruta in frutas:
            fruta.atualizar()

            # Fruta caiu abaixo da tela sem ser cortada
            if not fruta.cortada and fruta.y > altura_atual + 60 and fruta.vy > 0:
                fruta.ativa = False
                if not fruta.is_bomba and not fruta.perdeu_ponto:
                    fruta.perdeu_ponto = True
                    vidas -= 1
                    notificacoes.append(NotificacaoTexto("❌ ERROU!", min(max(50, fruta.x), largura_atual - 50), altura_atual - 40, (227, 6, 19)))
                    if vidas <= 0:
                        game_over = True
                        recorde = max(recorde, pontuacao)

        frutas = [f for f in frutas if f.ativa and f.y < altura_atual + 120]

        # Atualização das Metades de Fruta
        for m in metades:
            m.atualizar()
        metades = [m for m in metades if m.y < altura_atual + 100]

    # Atualização de Partículas
    for p in particulas:
        p.atualizar()
    particulas = [p for p in particulas if p.vida > 0]

    # Atualização de Notificações
    for n in notificacoes:
        n.atualizar()
    notificacoes = [n for n in notificacoes if n.vida > 0]

    # ==================== RENDERIZAÇÃO GRÁFICA ====================

    # 1. Fundo Claro Elegante (Tábua Limpa SENAI)
    tela.fill(COR_FUNDO_CLARO)

    # Textura sutil de tábua com ranhuras horizontais
    for y_line in range(0, altura_atual, 60):
        pygame.draw.line(tela, COR_FUNDO_TABUA, (0, y_line), (largura_atual, y_line), 2)

    # 2. Manchas de Suco no Fundo Claro (Aquarela translúcida)
    for mancha in manchas_fundo:
        surf_mancha = pygame.Surface((mancha["r"] * 2 + 4, mancha["r"] * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(surf_mancha, (*mancha["cor"][:3], int(mancha["alpha"])), (mancha["r"] + 2, mancha["r"] + 2), mancha["r"])
        tela.blit(surf_mancha, (int(mancha["x"]) - mancha["r"], int(mancha["y"]) - mancha["r"]))
        # Desbota muito suavemente
        mancha["alpha"] = max(20, mancha["alpha"] - 0.08)

    # 3. Metades de Fruta
    for m in metades:
        m.desenhar(tela)

    # 4. Frutas Inteiras
    for f in frutas:
        f.desenhar(tela)

    # 5. Gotas e Respingos de Suco
    for p in particulas:
        p.desenhar(tela)

    # 6. Rastro da Lâmina Laser (Efeito Sabre de Luz Neon de Alto Contraste)
    if len(rastro_lamina) >= 2:
        pontos = list(rastro_lamina)
        total_pts = len(pontos)

        for i in range(1, total_pts):
            p_ini = (pontos[i - 1]["x"], pontos[i - 1]["y"])
            p_fim = (pontos[i]["x"], pontos[i]["y"])

            frac = i / float(total_pts)
            espessura_externa = int(frac * 12) + 2
            espessura_interna = int(frac * 4) + 1

            cor_externa = COR_LASER_SENAI if frac > 0.55 else COR_LASER_EXTERNO
            pygame.draw.line(tela, cor_externa, p_ini, p_fim, espessura_externa)
            pygame.draw.line(tela, COR_LASER_INTERNO, p_ini, p_fim, espessura_interna)

        # Faísca no bico da lâmina
        ponta = pontos[-1]
        pygame.draw.circle(tela, COR_BRANCO, (ponta["x"], ponta["y"]), 5)
        pygame.draw.circle(tela, COR_LASER_EXTERNO, (ponta["x"], ponta["y"]), 9, 2)

    # 7. Textos Flutuantes de Combo
    for n in notificacoes:
        n.desenhar(tela)

    # 8. HUD Superior Oficial SENAI (Barra escura translúcida para legibilidade máxima)
    hud_surf = pygame.Surface((largura_atual, 60), pygame.SRCALPHA)
    hud_surf.fill((15, 23, 42, 220))
    tela.blit(hud_surf, (0, 0))
    pygame.draw.rect(tela, COR_SENAI_VERMELHO, (0, 57, largura_atual, 3))

    # Logo / Título
    txt_logo = fonte_hud.render("SENAI", True, COR_SENAI_VERMELHO)
    txt_titulo = fonte_pequena.render("FRUIT NINJA TOUCHLESS", True, COR_BRANCO)
    tela.blit(txt_logo, (24, 16))
    tela.blit(txt_titulo, (96, 19))

    # Pontuação Central
    txt_pts = fonte_grande.render(str(pontuacao), True, COR_BRANCO)
    txt_pts_sombra = fonte_grande.render(str(pontuacao), True, (15, 23, 42))
    cx = largura_atual // 2 - txt_pts.get_width() // 2
    tela.blit(txt_pts_sombra, (cx + 2, 8))
    tela.blit(txt_pts, (cx, 6))

    # Vidas (Corações Vermelhos)
    vidas_str = "♥ " * vidas + "♡ " * (3 - vidas)
    txt_vidas = fonte_media.render(vidas_str.strip(), True, COR_SENAI_VERMELHO)
    tela.blit(txt_vidas, (largura_atual - txt_vidas.get_width() - 24, 14))

    # Recorde
    txt_rec = fonte_pequena.render(f"RECORDE: {recorde}", True, COR_OURO)
    tela.blit(txt_rec, (largura_atual - txt_vidas.get_width() - txt_rec.get_width() - 48, 21))

    # Rodapé de Instrução
    txt_guia = fonte_pequena.render("Corte com a mão no ar  |  [F] Alternar Tela Cheia  |  [Q] Sair", True, (90, 100, 115))
    tela.blit(txt_guia, (largura_atual // 2 - txt_guia.get_width() // 2, altura_atual - 26))

    # 9. Tela de Game Over
    if game_over:
        overlay = pygame.Surface((largura_atual, altura_atual), pygame.SRCALPHA)
        overlay.fill((15, 23, 42, 210))
        tela.blit(overlay, (0, 0))

        card_w = min(540, largura_atual - 40)
        card_h = 300
        card_x = largura_atual // 2 - card_w // 2
        card_y = altura_atual // 2 - card_h // 2

        pygame.draw.rect(tela, (255, 255, 255), (card_x, card_y, card_w, card_h), border_radius=14)
        pygame.draw.rect(tela, COR_SENAI_VERMELHO, (card_x, card_y, card_w, 8), border_top_left_radius=14, border_top_right_radius=14)
        pygame.draw.rect(tela, (203, 213, 225), (card_x, card_y, card_w, card_h), 2, border_radius=14)

        txt_fim = fonte_grande.render("FIM DE JOGO", True, COR_SENAI_VERMELHO)
        tela.blit(txt_fim, (largura_atual // 2 - txt_fim.get_width() // 2, card_y + 30))

        txt_stats = fonte_media.render(f"Pontuação: {pontuacao}   •   Recorde: {recorde}", True, COR_PRETO)
        tela.blit(txt_stats, (largura_atual // 2 - txt_stats.get_width() // 2, card_y + 100))

        btn_box = pygame.Rect(largura_atual // 2 - 160, card_y + 165, 320, 50)
        pygame.draw.rect(tela, COR_SENAI_VERMELHO, btn_box, border_radius=25)
        txt_reiniciar = fonte_hud.render("FAÇA A PINÇA OU CLIQUE", True, COR_BRANCO)
        tela.blit(txt_reiniciar, (btn_box.centerx - txt_reiniciar.get_width() // 2, btn_box.centery - txt_reiniciar.get_height() // 2))

        txt_ajuda = fonte_pequena.render("Pressione [ESPAÇO] para jogar novamente | [Q] para Sair", True, (100, 116, 139))
        tela.blit(txt_ajuda, (largura_atual // 2 - txt_ajuda.get_width() // 2, card_y + 245))

    pygame.display.flip()

pygame.quit()
sys.exit()
