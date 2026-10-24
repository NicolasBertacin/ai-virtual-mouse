#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI Virtual Mouse & Flappy Bird SENAI - Unified Launcher
=========================================================
Ponto de entrada unificado em 100% Python para inicializar o sistema
de mouse virtual touchless em conjunto com o jogo Flappy Bird (Pygame).

Uso:
  py main.py                 -> Inicia Touchless Mouse + Jogo Flappy Bird em Python (Padrão 100% Python)
  py main.py --flappy        -> Executa apenas o Jogo Flappy Bird (Pygame)
  py main.py --mouse-only    -> Executa apenas o Mouse Touchless 60 FPS
  py main.py --teste         -> Abre o Laboratório de Calibração/Testes Web
  py main.py --totem         -> Abre o Totem Digital oficial SENAI no navegador
  py main.py --ironman       -> Executa o modo HUD Jarvis / Homem de Ferro
  py main.py --gui           -> Executa a interface desktop CustomTkinter
"""

import sys
import os
import argparse
import webbrowser
import subprocess

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
TOTEM_INDEX = os.path.join(ROOT_DIR, "totem-senai", "index.html")
TESTE_INDEX = os.path.join(ROOT_DIR, "totem-senai", "teste.html")
FLAPPY_SCRIPT = os.path.join(ROOT_DIR, "flappy_mouse.py")


def open_in_browser(file_path: str, title: str):
    """Abre uma página HTML local no navegador padrão."""
    if os.path.exists(file_path):
        print(f"[Navegador] Abrindo {title}: {file_path}")
        webbrowser.open(f"file:///{os.path.abspath(file_path)}")
    else:
        print(f"[Erro] Arquivo não encontrado: {file_path}")


def print_banner():
    print("=" * 64)
    print("       AI VIRTUAL MOUSE & FLAPPY BIRD - 100% PYTHON (SENAI)")
    print("=" * 64)
    print(" - Mover Pássaro / Cursor: Aponte com o indicador naturalmente")
    print(" - Trava Magnética: Ao iniciar a pinça, o cursor ancora")
    print(" - Clique / Reiniciar Jogo: Junte polegar + indicador (pinça)")
    print(" - Clique Duplo: Dois toques rápidos de pinça")
    print(" - Arrastar & Soltar: Segure a pinça fechada (> 0.3s)")
    print(" - Clique Direito: Pinça entre polegar + dedo médio")
    print(" - Rolagem (Scroll): Levante indicador + médio juntos")
    print(" - Tela Cheia no Jogo: Pressione 'F' ou 'F11' na janela do jogo")
    print(" - Sair: Pressione 'q' na janela de vídeo ou jogo")
    print("=" * 64)


def main():
    parser = argparse.ArgumentParser(
        description="Sistema de Mouse Virtual Touchless e Jogo Flappy Bird SENAI (100% Python)",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "--flappy", "-f",
        action="store_true",
        help="Executa apenas o jogo desktop Flappy Bird (Pygame)."
    )
    parser.add_argument(
        "--mouse-only", "-m",
        action="store_true",
        help="Executa apenas o motor touchless de 60 FPS (sem abrir o jogo)."
    )
    parser.add_argument(
        "--teste", "-l", "--web", "-w",
        dest="teste",
        action="store_true",
        help="Abre o Laboratório de Calibração e Testes no navegador."
    )
    parser.add_argument(
        "--totem", "-t",
        action="store_true",
        help="Abre o Totem Digital institucional SENAI no navegador."
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

    # Opção: Jogo Flappy Bird Standalone
    if args.flappy:
        print_banner()
        if os.path.exists(FLAPPY_SCRIPT):
            print("\n[Inicializando] Jogo Flappy Bird (Pygame)...")
            subprocess.call([sys.executable, FLAPPY_SCRIPT])
        else:
            print(f"[Erro] Arquivo não encontrado: {FLAPPY_SCRIPT}")
        return

    # Opção: Apenas Mouse Touchless
    if args.mouse_only:
        print_banner()
        print("\n[Inicializando] Motor Touchless Pro 60 FPS...")
        from mac_touchless_pro import main as run_touchless
        run_touchless()
        return

    # Opção: Totem Digital no Navegador
    if args.totem:
        print_banner()
        open_in_browser(TOTEM_INDEX, "Totem Digital SENAI")
        print("\nPressione 'F' no teclado do navegador para Tela Cheia.")
        return

    # Opção: Área de Calibração / Testes Web
    if args.teste:
        print_banner()
        open_in_browser(TESTE_INDEX, "Área de Testes e Calibração SENAI")
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

    # Modo Padrão: 100% PYTHON (Jogo Flappy Bird Pygame + Motor Touchless 60 FPS)
    print_banner()
    print("\n[1/2] Executando Jogo Flappy Bird em Python (Pygame)...")
    flappy_proc = None
    if os.path.exists(FLAPPY_SCRIPT):
        try:
            flappy_proc = subprocess.Popen([sys.executable, FLAPPY_SCRIPT])
        except Exception as e:
            print(f"[Aviso] Não foi possível iniciar flappy_mouse.py: {e}")

    print("\n[2/2] Inicializando Sistema Touchless Pro (60 FPS)...")
    from mac_touchless_pro import main as run_touchless
    try:
        run_touchless()
    finally:
        if flappy_proc and flappy_proc.poll() is None:
            try:
                flappy_proc.terminate()
            except Exception:
                pass


if __name__ == "__main__":
    main()
