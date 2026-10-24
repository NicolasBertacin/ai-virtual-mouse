#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI Virtual Mouse & Área de Testes SENAI - Launcher Unificado
============================================================
Inicializa o mouse virtual touchless (60 FPS) integrado à Área de
Testes Web e ao jogo Flappy Bird em Python puro (Pygame).

Uso:
  py main.py                 -> Abre Área de Testes Web + Motor Touchless 60 FPS
                                (Pressione 'G' na página web para abrir o Flappy Bird em Python no PC)
  py main.py --flappy        -> Executa diretamente o Jogo Flappy Bird (Pygame)
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

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
TOTEM_INDEX = os.path.join(ROOT_DIR, "totem-senai", "index.html")
TESTE_INDEX = os.path.join(ROOT_DIR, "totem-senai", "teste.html")
FLAPPY_SCRIPT = os.path.join(ROOT_DIR, "flappy_mouse.py")

# Processo global do jogo Flappy Bird
FLAPPY_PROC = None
FLAPPY_LOCK = threading.Lock()


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
                return True
            except Exception as e:
                print(f"[Erro] Falha ao iniciar flappy_mouse.py: {e}")
                return False
        else:
            print(f"[Erro] Script do jogo não encontrado: {FLAPPY_SCRIPT}")
            return False


class AppRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Servidor HTTP local para fornecer a interface web e receber o comando 'G'."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT_DIR, **kwargs)

    def do_GET(self):
        # Endpoint de acionamento do Flappy Bird em Python
        if self.path == "/api/launch-flappy":
            launched = launch_flappy_game()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            status = "launched" if launched else "already_running"
            self.wfile.write(f'{{"status": "{status}"}}'.encode("utf-8"))
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
    for port in range(preferred_port, preferred_port + 20):
        try:
            server = http.server.HTTPServer(("127.0.0.1", port), AppRequestHandler)
            t = threading.Thread(target=server.serve_forever, daemon=True)
            t.start()
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
    print("      AI VIRTUAL MOUSE & ÁREA DE TESTES SENAI - 60 FPS")
    print("=" * 64)
    print(" - Mover Cursor: Aponte com o indicador naturalmente")
    print(" - Trava Magnética: Ao iniciar a pinça, o cursor ancora")
    print(" - Clique Esquerdo: Junte polegar + indicador (pinça)")
    print(" - Clique Duplo: Dois toques rápidos de pinça")
    print(" - Arrastar & Soltar: Segure a pinça fechada (> 0.3s)")
    print(" - Clique Direito: Pinça entre polegar + dedo médio")
    print(" - Rolagem (Scroll): Levante indicador + médio juntos")
    print(" - Atalho Flappy Bird: Pressione 'G' na página web para abrir o jogo no PC")
    print(" - Tela Cheia Web: Pressione 'F' no navegador")
    print(" - Sair: Pressione 'q' na janela de vídeo da câmera")
    if server_port:
        print(f" - Servidor Local Ativo: http://127.0.0.1:{server_port}")
    print("=" * 64)


def main():
    parser = argparse.ArgumentParser(
        description="Sistema de Mouse Virtual Touchless e Totem Digital SENAI",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "--flappy", "-f",
        action="store_true",
        help="Executa diretamente o jogo desktop Flappy Bird (Pygame)."
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

    # Inicia o Servidor Local HTTP para servir a aplicação web e a API do Flappy
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
    # O Flappy Bird em Python é acionado ao pressionar 'G' ou clicar no botão na web
    print_banner(port)
    url = f"http://127.0.0.1:{port}/totem-senai/teste.html"
    print("\n[1/2] Abrindo Área de Testes Web no Navegador...")
    print(f"      URL: {url}")
    print("      (Dica: Pressione 'G' na página web para abrir o Flappy Bird em Python)")
    open_in_browser(url, "Área de Testes Web SENAI")

    print("\n[2/2] Inicializando Sistema Touchless Pro (60 FPS)...")
    from mac_touchless_pro import main as run_touchless
    try:
        run_touchless()
    finally:
        # Encerramento limpo do Flappy Bird e do servidor HTTP
        if FLAPPY_PROC and FLAPPY_PROC.poll() is None:
            try:
                FLAPPY_PROC.terminate()
            except Exception:
                pass
        try:
            server.shutdown()
        except Exception:
            pass


if __name__ == "__main__":
    main()
