#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI Virtual Mouse & Jogos Touchless SENAI - Launcher Unificado
=============================================================
Inicializa o mouse virtual touchless (60 FPS) integrado à Área de
Testes Web e aos jogos Flappy Bird e Fruit Ninja em Python puro (Pygame).

Uso:
  py main.py                 -> Abre Área de Testes Web + Motor Touchless 60 FPS
                                (Atalho 'G' abre Flappy Bird | Atalho 'N' abre Fruit Ninja)
  py main.py --flappy        -> Executa diretamente o Jogo Flappy Bird (Pygame)
  py main.py --fruit         -> Executa diretamente o Jogo Fruit Ninja (Pygame)
  py main.py --mouse-only    -> Executa apenas o Mouse Touchless sem navegador
  py main.py --totem         -> Abre o Totem Digital institucional no navegador
  py main.py --ironman       -> Executa o modo HUD Jarvis / Homem de Ferro
  py main.py --gui           -> Executa a interface desktop CustomTkinter
"""

import sys
import os
import argparse
import webbrowser
import subprocess
import threading
import http.server
import time

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
TOTEM_INDEX = os.path.join(ROOT_DIR, "totem-senai", "index.html")
TESTE_INDEX = os.path.join(ROOT_DIR, "totem-senai", "teste.html")
FLAPPY_SCRIPT = os.path.join(ROOT_DIR, "flappy_mouse.py")
FRUIT_SCRIPT = os.path.join(ROOT_DIR, "fruit_ninja.py")

CURRENT_SERVER_PORT = 8765

# Processos globais dos jogos
FLAPPY_PROC = None
FLAPPY_LOCK = threading.Lock()

FRUIT_PROC = None
FRUIT_LOCK = threading.Lock()


def start_game_monitor(proc):
    """Monitora o processo do jogo em segundo plano. Ao fechar, restaura a web em tela cheia."""
    def _run():
        proc.wait()
        print("\n[Sistema] Jogo encerrado pelo usuário. Restaurando Área de Testes Web em Tela Cheia...")
        url = f"http://127.0.0.1:{CURRENT_SERVER_PORT}/totem-senai/teste.html"
        try:
            webbrowser.open(url)
        except Exception:
            pass

        # Aguarda brevemente para o navegador recuperar o foco do sistema operacional
        time.sleep(0.4)
        try:
            import pyautogui
            # F11 ativa tela cheia nativa no navegador (Chrome/Edge/Firefox)
            pyautogui.press('f11')
        except Exception:
            pass

    t = threading.Thread(target=_run, daemon=True)
    t.start()


def launch_flappy_game():
    """Inicia o jogo flappy_mouse.py em processo independente se não estiver em execução."""
    global FLAPPY_PROC
    with FLAPPY_LOCK:
        if FLAPPY_PROC and FLAPPY_PROC.poll() is None:
            print("[Flappy] Jogo já está em execução no PC.")
            return False

        if os.path.exists(FLAPPY_SCRIPT):
            print("\n[Flappy] Iniciando Jogo Flappy Bird em Python (Pygame)...")
            try:
                FLAPPY_PROC = subprocess.Popen([sys.executable, FLAPPY_SCRIPT])
                start_game_monitor(FLAPPY_PROC)
                return True
            except Exception as e:
                print(f"[Erro] Falha ao iniciar flappy_mouse.py: {e}")
                return False
        else:
            print(f"[Erro] Script do jogo não encontrado: {FLAPPY_SCRIPT}")
            return False


def launch_fruit_game():
    """Inicia o jogo fruit_ninja.py em processo independente se não estiver em execução."""
    global FRUIT_PROC
    with FRUIT_LOCK:
        if FRUIT_PROC and FRUIT_PROC.poll() is None:
            print("[Fruit Ninja] Jogo já está em execução no PC.")
            return False

        if os.path.exists(FRUIT_SCRIPT):
            print("\n[Fruit Ninja] Iniciando Jogo Fruit Ninja em Python (Pygame)...")
            try:
                FRUIT_PROC = subprocess.Popen([sys.executable, FRUIT_SCRIPT])
                start_game_monitor(FRUIT_PROC)
                return True
            except Exception as e:
                print(f"[Erro] Falha ao iniciar fruit_ninja.py: {e}")
                return False
        else:
            print(f"[Erro] Script do jogo não encontrado: {FRUIT_SCRIPT}")
            return False


class AppRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Servidor HTTP local para fornecer a interface web e receber comandos dos jogos."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT_DIR, **kwargs)

    def do_GET(self):
        # Endpoint: Flappy Bird
        if self.path == "/api/launch-flappy":
            launched = launch_flappy_game()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            status = "launched" if launched else "already_running"
            self.wfile.write(f'{{"status": "{status}"}}'.encode("utf-8"))
            return

        # Endpoint: Fruit Ninja
        elif self.path == "/api/launch-fruit":
            launched = launch_fruit_game()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            status = "launched" if launched else "already_running"
            self.wfile.write(f'{{"status": "{status}"}}'.encode("utf-8"))
            return

        # Endpoint: Status dos jogos (para a web detectar quando fechou e restaurar tela cheia)
        elif self.path == "/api/game-status":
            flappy_on = bool(FLAPPY_PROC and FLAPPY_PROC.poll() is None)
            fruit_on = bool(FRUIT_PROC and FRUIT_PROC.poll() is None)
            any_on = flappy_on or fruit_on
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(f'{{"active": {str(any_on).lower()}}}'.encode("utf-8"))
            return

        # Redirecionamentos amigáveis
        elif self.path in ("/", "/teste", "/teste.html"):
            self.send_response(302)
            self.send_header("Location", "/totem-senai/teste.html")
            self.end_headers()
            return
        elif self.path in ("/totem", "/totem.html"):
            self.send_response(302)
            self.send_header("Location", "/totem-senai/index.html")
            self.end_headers()
            return

        super().do_GET()

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def log_message(self, format, *args):
        # Silencia logs comuns de requisições HTTP para manter o console limpo
        pass


def start_local_server(preferred_port=8765):
    """Inicia o servidor local em uma porta livre em segundo plano."""
    global CURRENT_SERVER_PORT
    for port in range(preferred_port, preferred_port + 20):
        try:
            server = http.server.HTTPServer(("127.0.0.1", port), AppRequestHandler)
            t = threading.Thread(target=server.serve_forever, daemon=True)
            t.start()
            CURRENT_SERVER_PORT = port
            return server, port
        except OSError:
            continue
    raise RuntimeError("Não foi possível iniciar o servidor HTTP local.")


def open_in_browser(url: str, title: str):
    """Abre uma URL ou arquivo local no navegador padrão."""
    print(f"[Navegador] Abrindo {title}: {url}")
    webbrowser.open(url)


def print_banner(server_port=None):
    print("=" * 64)
    print("      AI VIRTUAL MOUSE & JOGOS TOUCHLESS SENAI - 60 FPS")
    print("=" * 64)
    print(" - Mover Cursor / Lâmina: Aponte com o indicador naturalmente")
    print(" - Trava Magnética: Ao iniciar a pinça, o cursor ancora")
    print(" - Clique Esquerdo: Junte polegar + indicador (pinça)")
    print(" - Clique Duplo: Dois toques rápidos de pinça")
    print(" - Arrastar & Soltar: Segure a pinça fechada (> 0.3s)")
    print(" - Clique Direito: Pinça entre polegar + dedo médio")
    print(" - Rolagem (Scroll): Levante indicador + médio juntos")
    print(" - Atalho Flappy Bird: Pressione 'G' na página web para abrir")
    print(" - Atalho Fruit Ninja: Pressione 'N' na página web para abrir")
    print(" - Tela Cheia: Pressione 'F' no navegador ou nos jogos")
    print(" - Sair: Pressione 'q' na janela de vídeo ou jogo")
    if server_port:
        print(f" - Servidor Local Ativo: http://127.0.0.1:{server_port}")
    print("=" * 64)


def main():
    parser = argparse.ArgumentParser(
        description="Sistema de Mouse Virtual Touchless e Jogos SENAI (Python)",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "--flappy", "-f",
        action="store_true",
        help="Executa diretamente o jogo desktop Flappy Bird (Pygame)."
    )
    parser.add_argument(
        "--fruit", "-n",
        action="store_true",
        help="Executa diretamente o jogo desktop Fruit Ninja (Pygame)."
    )
    parser.add_argument(
        "--mouse-only", "-m",
        action="store_true",
        help="Executa apenas o motor touchless de 60 FPS (sem navegador)."
    )
    parser.add_argument(
        "--totem", "-t",
        action="store_true",
        help="Abre o Totem Digital institucional SENAI no navegador."
    )
    parser.add_argument(
        "--teste", "-l",
        action="store_true",
        help="Abre apenas a Área de Testes Web."
    )
    parser.add_argument(
        "--ironman", "-i",
        action="store_true",
        help="Inicia a versão com HUD futurista Jarvis / Homem de Ferro."
    )
    parser.add_argument(
        "--gui", "-g",
        action="store_true",
        help="Inicia a interface gráfica desktop CustomTkinter."
    )

    args = parser.parse_args()

    # Opção: Jogo Flappy Bird Direto
    if args.flappy:
        print_banner()
        launch_flappy_game()
        if FLAPPY_PROC:
            FLAPPY_PROC.wait()
        return

    # Opção: Jogo Fruit Ninja Direto
    if args.fruit:
        print_banner()
        launch_fruit_game()
        if FRUIT_PROC:
            FRUIT_PROC.wait()
        return

    # Opção: Apenas Mouse Touchless
    if args.mouse_only:
        print_banner()
        print("\n[Inicializando] Motor Touchless Pro 60 FPS...")
        from mac_touchless_pro import main as run_touchless
        run_touchless()
        return

    # Opção: Modo Jarvis / Ironman
    if args.ironman:
        print_banner()
        print("\n[Inicializando] Modo HUD Jarvis / Homem de Ferro...")
        from ironman_touchless_pro import main as run_ironman
        run_ironman()
        return

    # Opção: Interface Desktop CustomTkinter
    if args.gui:
        print_banner()
        print("\n[Inicializando] Interface Gráfica Studio CustomTkinter...")
        from gui_app import run_app
        run_app()
        return

    # Inicia o Servidor Local HTTP para servir a aplicação web e as APIs dos jogos
    server, port = start_local_server()

    # Opção: Totem Digital no Navegador
    if args.totem:
        print_banner(port)
        url = f"http://127.0.0.1:{port}/totem-senai/index.html"
        open_in_browser(url, "Totem Digital SENAI")
        print("\nPressione 'F' no teclado do navegador para Tela Cheia.")
        from mac_touchless_pro import main as run_touchless
        try:
            run_touchless()
        finally:
            server.shutdown()
        return

    # Modo Padrão (py main.py): Abre a Área de Testes Web + Inicia Motor Touchless
    print_banner(port)
    url = f"http://127.0.0.1:{port}/totem-senai/teste.html"
    print("\n[1/2] Abrindo Área de Testes Web no Navegador...")
    print(f"      URL: {url}")
    print("      (Atalhos: 'G' para Flappy Bird | 'N' para Fruit Ninja)")
    open_in_browser(url, "Área de Testes Web SENAI")

    print("\n[2/2] Inicializando Sistema Touchless Pro (60 FPS)...")
    from mac_touchless_pro import main as run_touchless
    try:
        run_touchless()
    finally:
        # Encerramento limpo dos jogos e do servidor HTTP
        if FLAPPY_PROC and FLAPPY_PROC.poll() is None:
            try:
                FLAPPY_PROC.terminate()
            except Exception:
                pass
        if FRUIT_PROC and FRUIT_PROC.poll() is None:
            try:
                FRUIT_PROC.terminate()
            except Exception:
                pass
        try:
            server.shutdown()
        except Exception:
            pass


if __name__ == "__main__":
    main()
