"""
AI Virtual Mouse Studio - SENAI (Edição Executiva Moderna)
- Layout limpo, contemporâneo e espaçoso com a paleta oficial do SENAI (Branco Puro, Vermelho SENAI e Slate).
- Sidebar retrátil à esquerda controlada por botão de 3 riscos (☰).
- Zero poluição visual: sem ondas e sem estatísticas/telemetrias técnicas desnecessárias.
"""

import os
import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
import cv2
import numpy as np
import time
import math
import webbrowser
from typing import Dict, Any, Optional

from virtual_mouse_engine import VirtualMouseEngine
from camera_utils import get_camera_devices, get_default_camera_index


# Configura a aparência global do CustomTkinter para Light Mode (Padrão Web SENAI)
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class ModernSenaiMouseApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configurações da Janela
        self.title("SENAI — Mouse Virtual por Visão Computacional")
        self.geometry("1280x820")
        self.minsize(1120, 720)

        # Paleta Oficial da Interface Web do SENAI
        self.c_senai_red = "#E30613"
        self.c_senai_red_hover = "#C0040F"
        self.c_senai_red_subtle = "#FFF1F2"
        self.c_senai_red_border = "#FECDD3"

        self.c_bg = "#F8FAFC"           # Slate 50 (Fundo limpo off-white)
        self.c_card = "#FFFFFF"         # Branco Puro
        self.c_card_border = "#E2E8F0"  # Borda cinza suave
        self.c_card_subtle = "#F1F5F9"  # Slate 100

        self.c_text_title = "#0F172A"   # Charcoal profundo (Slate 900)
        self.c_text_body = "#334155"    # Charcoal médio (Slate 700)
        self.c_text_muted = "#64748B"   # Slate 500

        self.c_success = "#059669"      # Verde Esmeralda
        self.c_success_bg = "#ECFDF5"
        self.c_success_border = "#A7F3D0"

        self.c_blue_tech = "#0284C7"    # Azul Tecnológico
        self.c_blue_bg = "#F0F9FF"
        self.c_blue_border = "#BAE6FD"

        self.configure(fg_color=self.c_bg)

        # Descoberta de Câmeras
        self.camera_list = get_camera_devices()
        self.camera_map = {cam["label"]: cam["index"] for cam in self.camera_list}
        self.selected_camera_index = get_default_camera_index()

        # Motor de Visão Computacional
        self.engine = VirtualMouseEngine()
        self.engine.control_system_mouse = True
        self.engine.margin_x = 85
        self.engine.margin_y = 65
        self.engine.on_frame_ready = self._on_frame_ready
        self.engine.on_telemetry_ready = self._on_telemetry_ready
        self.engine.on_action_event = self._on_engine_action

        # Estado da Aplicação
        self.is_camera_active = False
        self.last_frame: Optional[np.ndarray] = None
        self.photo_image = None
        self.photo_image_pip = None
        self.is_mini_mode = False
        self.sidebar_is_open = True
        self.current_view_key = "range"  # 'range', 'drag', 'draw', 'camera', 'settings'

        # Estado da Cobertura de Tela (4 Cantos + Centro)
        self.coverage_nodes = {
            "top_left": {"name": "Canto Sup. Esquerdo", "pos": (60, 60), "hit": False},
            "top_right": {"name": "Canto Sup. Direito", "pos": (740, 60), "hit": False},
            "bottom_left": {"name": "Canto Inf. Esquerdo", "pos": (60, 380), "hit": False},
            "bottom_right": {"name": "Canto Inf. Direito", "pos": (740, 380), "hit": False},
            "center": {"name": "Centro da Tela", "pos": (400, 220), "hit": False},
        }

        # Estado do Laboratório de Arraste (Drag & Drop)
        self.drag_items = [
            {"id": "p1", "name": "Módulo Robótico", "color": self.c_senai_red, "x": 40, "y": 90, "w": 180, "h": 54, "zone": "origem"},
            {"id": "p2", "name": "Sensor Óptico", "color": self.c_blue_tech, "x": 40, "y": 165, "w": 180, "h": 54, "zone": "origem"},
            {"id": "p3", "name": "Controlador CLP", "color": self.c_text_title, "x": 40, "y": 240, "w": 180, "h": 54, "zone": "origem"},
        ]
        self.dragged_item_idx: Optional[int] = None
        self.drag_offset = (0, 0)

        # Estado do Desenho Livre
        self.draw_color = self.c_senai_red
        self.draw_brush_size = 4
        self.last_draw_pt = None

        # Constrói o Layout Executivo
        self._build_top_navbar()
        self._build_body_layout()

        # Inicialização
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._update_loop()
        self.after(350, self._toggle_camera)

    # -------------------------------------------------------------
    # 1. TOP NAVBAR (LIMPA, ELEGANTE E MODERNA)
    # -------------------------------------------------------------
    def _build_top_navbar(self):
        """Barra superior minimalista com botão ☰, logo SENAI e controles essenciais."""
        self.navbar = ctk.CTkFrame(
            self, fg_color=self.c_card, corner_radius=18,
            border_width=1, border_color=self.c_card_border, height=68
        )
        self.navbar.pack(fill=tk.X, padx=18, pady=(16, 12))
        self.navbar.pack_propagate(False)

        # Lado Esquerdo: Botão ☰ de 3 Riscos + Logo SENAI + Título Dinâmico
        left_box = ctk.CTkFrame(self.navbar, fg_color="transparent")
        left_box.pack(side=tk.LEFT, padx=16, pady=10)

        # Botão de 3 Riscos (Hamburger ☰)
        self.btn_hamburger = ctk.CTkButton(
            left_box, text="☰", width=44, height=44, corner_radius=12,
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            fg_color=self.c_senai_red_subtle, hover_color=self.c_senai_red_border,
            text_color=self.c_senai_red,
            command=self._toggle_sidebar
        )
        self.btn_hamburger.pack(side=tk.LEFT, padx=(0, 16))

        # Logo Oficial do SENAI
        logo_path = os.path.join(os.path.dirname(__file__), "senai_logo.png")
        if os.path.exists(logo_path):
            try:
                raw_logo = Image.open(logo_path)
                w, h = raw_logo.size
                nh = 34
                nw = int(w * (nh / h))
                ctk_logo = ctk.CTkImage(light_image=raw_logo, dark_image=raw_logo, size=(nw, nh))
                logo_lbl = ctk.CTkLabel(left_box, image=ctk_logo, text="")
                logo_lbl.pack(side=tk.LEFT, padx=(0, 16))
            except Exception:
                pass

        # Divisor Vertical
        ctk.CTkFrame(left_box, width=1.5, height=32, fg_color=self.c_card_border).pack(side=tk.LEFT, padx=(0, 16))

        # Título da Seção Atual
        self.current_title_lbl = ctk.CTkLabel(
            left_box, text="🎯 TESTE DE ALCANCE DA TELA INTEIRA",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=self.c_text_title
        )
        self.current_title_lbl.pack(side=tk.LEFT)

        # Lado Direito: Apenas Status Discreto e Botão de Ação
        right_box = ctk.CTkFrame(self.navbar, fg_color="transparent")
        right_box.pack(side=tk.RIGHT, padx=16, pady=10)

        # Indicador de Status Visual Discreto
        self.status_badge = ctk.CTkLabel(
            right_box, text="● Câmera Ativa",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=self.c_success, fg_color=self.c_success_bg,
            corner_radius=10, padx=14, pady=6
        )
        self.status_badge.pack(side=tk.LEFT, padx=(0, 12))

        # Botão Principal Ligar / Parar
        self.btn_power = ctk.CTkButton(
            right_box, text="⏹ Parar Câmera",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color="#475569", hover_color="#334155",
            text_color="#FFFFFF", corner_radius=10, width=130, height=38,
            command=self._toggle_camera
        )
        self.btn_power.pack(side=tk.LEFT)

    # -------------------------------------------------------------
    # 2. BODY LAYOUT: SIDEBAR RETRÁTIL À ESQUERDA + WORKSPACE
    # -------------------------------------------------------------
    def _build_body_layout(self):
        self.body_container = ctk.CTkFrame(self, fg_color="transparent")
        self.body_container.pack(fill=tk.BOTH, expand=True, padx=18, pady=(0, 16))

        # Sidebar Retrátil
        self._build_sidebar()

        # Área de Conteúdo Principal (Card Branco)
        self.content_container = ctk.CTkFrame(
            self.body_container, fg_color=self.c_card, corner_radius=18,
            border_width=1, border_color=self.c_card_border
        )
        self.content_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Views
        self._build_view_range()
        self._build_view_drag()
        self._build_view_draw()
        self._build_view_camera()
        self._build_view_settings()

        # Inicializa na tela de Teste de Alcance
        self._navigate_to("range")

    # -------------------------------------------------------------
    # 3. SIDEBAR RETRÁTIL (ABRE E FECHA NO BOTÃO ☰)
    # -------------------------------------------------------------
    def _build_sidebar(self):
        """Menu lateral estilizado com navegação limpa e direta."""
        self.sidebar_frame = ctk.CTkFrame(
            self.body_container, fg_color=self.c_card, corner_radius=18,
            border_width=1, border_color=self.c_card_border, width=260
        )
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 12))
        self.sidebar_frame.pack_propagate(False)

        # Topo da Sidebar
        sb_header = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        sb_header.pack(fill=tk.X, padx=18, pady=(18, 14))

        ctk.CTkLabel(
            sb_header, text="MENU PRINCIPAL",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=self.c_senai_red
        ).pack(anchor="w")

        ctk.CTkLabel(
            sb_header, text="Selecione onde deseja ir:",
            font=ctk.CTkFont(family="Segoe UI", size=9),
            text_color=self.c_text_muted
        ).pack(anchor="w")

        # Divisor
        ctk.CTkFrame(self.sidebar_frame, height=1, fg_color=self.c_card_border).pack(fill=tk.X, padx=16, pady=(0, 12))

        # Botões de Navegação
        self.nav_buttons = {}
        nav_items = [
            ("range", "🎯  Alcance de Tela"),
            ("drag", "📦  Arraste de Peças"),
            ("draw", "🎨  Desenho Livre"),
            ("camera", "📷  Visão da Câmera"),
            ("settings", "⚙️  Configurações"),
        ]

        for key, title in nav_items:
            btn = ctk.CTkButton(
                self.sidebar_frame, text=f"  {title}",
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                anchor="w", corner_radius=10, height=46,
                fg_color=self.c_card_subtle, hover_color=self.c_senai_red_subtle,
                text_color=self.c_text_title,
                command=lambda k=key: self._navigate_to(k)
            )
            btn.pack(fill=tk.X, padx=14, pady=3.5)
            self.nav_buttons[key] = btn

        # Divisor
        ctk.CTkFrame(self.sidebar_frame, height=1, fg_color=self.c_card_border).pack(fill=tk.X, padx=16, pady=16)

        # Botão de Atalho para o Totem Web
        btn_totem = ctk.CTkButton(
            self.sidebar_frame, text="🌐  Abrir Totem Web SENAI",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            fg_color="#FFFFFF", hover_color=self.c_senai_red_subtle,
            text_color=self.c_senai_red, border_width=1, border_color=self.c_senai_red_border,
            corner_radius=10, height=42,
            command=self._open_totem_web
        )
        btn_totem.pack(fill=tk.X, padx=14, pady=(0, 14))

        # Guia Rápido de Gestos no Rodapé da Sidebar
        gesture_mini = ctk.CTkFrame(
            self.sidebar_frame, fg_color=self.c_card_subtle, corner_radius=12,
            border_width=1, border_color=self.c_card_border
        )
        gesture_mini.pack(fill=tk.X, padx=14, side=tk.BOTTOM, pady=16)

        ctk.CTkLabel(
            gesture_mini, text="GUIA DE GESTOS",
            font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"),
            text_color=self.c_senai_red
        ).pack(anchor="w", padx=12, pady=(10, 4))

        ctk.CTkLabel(
            gesture_mini,
            text="☝️ Indicador: Mover cursor\n🤏 Pinça: Clicar no item\n📦 Segurar: Arrastar\n✌️ 2 Dedos: Rolar página",
            font=ctk.CTkFont(family="Segoe UI", size=9),
            justify=tk.LEFT, text_color=self.c_text_body
        ).pack(anchor="w", padx=12, pady=(0, 10))

    def _toggle_sidebar(self):
        """Abre ou fecha a sidebar à esquerda ao clicar no botão hamburger (☰)."""
        if self.sidebar_is_open:
            self.sidebar_frame.pack_forget()
            self.sidebar_is_open = False
            self.btn_hamburger.configure(
                fg_color="#FFFFFF", border_width=1, border_color="#CBD5E1"
            )
        else:
            self.content_container.pack_forget()
            self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 12))
            self.content_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            self.sidebar_is_open = True
            self.btn_hamburger.configure(
                fg_color=self.c_senai_red_subtle, border_width=0
            )

    def _navigate_to(self, view_key: str):
        """Muda a tela ativa de acordo com o item selecionado na sidebar."""
        self.current_view_key = view_key

        for k, btn in self.nav_buttons.items():
            if k == view_key:
                btn.configure(
                    fg_color=self.c_senai_red,
                    hover_color=self.c_senai_red_hover,
                    text_color="#FFFFFF"
                )
            else:
                btn.configure(
                    fg_color=self.c_card_subtle,
                    hover_color=self.c_senai_red_subtle,
                    text_color=self.c_text_title
                )

        self.view_range.pack_forget()
        self.view_drag.pack_forget()
        self.view_draw.pack_forget()
        self.view_camera.pack_forget()
        self.view_settings.pack_forget()

        if view_key == "range":
            self.current_title_lbl.configure(text="🎯 TESTE DE ALCANCE DA TELA INTEIRA")
            self.view_range.pack(fill=tk.BOTH, expand=True, padx=20, pady=18)
            self._redraw_range_canvas()
        elif view_key == "drag":
            self.current_title_lbl.configure(text="📦 ARRASTE DE PEÇAS INDUSTRIAIS")
            self.view_drag.pack(fill=tk.BOTH, expand=True, padx=20, pady=18)
            self._redraw_drag_canvas()
        elif view_key == "draw":
            self.current_title_lbl.configure(text="🎨 DESENHO LIVRE & PRECISÃO")
            self.view_draw.pack(fill=tk.BOTH, expand=True, padx=20, pady=18)
        elif view_key == "camera":
            self.current_title_lbl.configure(text="📷 VISÃO DA CÂMERA & GESTOS")
            self.view_camera.pack(fill=tk.BOTH, expand=True, padx=20, pady=18)
        elif view_key == "settings":
            self.current_title_lbl.configure(text="⚙️ CONFIGURAÇÕES DO SISTEMA")
            self.view_settings.pack(fill=tk.BOTH, expand=True, padx=20, pady=18)

    def _open_totem_web(self):
        totem_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "totem-senai", "index.html"))
        if os.path.exists(totem_file):
            webbrowser.open(f"file:///{totem_file.replace(os.sep, '/')}")

    # -------------------------------------------------------------
    # VIEW 1: TESTE DE ALCANCE (4 CANTOS + CENTRO)
    # -------------------------------------------------------------
    def _build_view_range(self):
        self.view_range = ctk.CTkFrame(self.content_container, fg_color="transparent")

        # Barra Superior Limpa da View
        top_bar = ctk.CTkFrame(
            self.view_range, fg_color=self.c_card_subtle, corner_radius=12,
            border_width=1, border_color=self.c_card_border, height=52
        )
        top_bar.pack(fill=tk.X, pady=(0, 14))
        top_bar.pack_propagate(False)

        ctk.CTkLabel(
            top_bar, text="Mova o cursor com a mão até cada alvo e faça o gesto de pinça para validar o alcance.",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=self.c_text_body
        ).pack(side=tk.LEFT, padx=18)

        btn_reset = ctk.CTkButton(
            top_bar, text="↺ Reiniciar Alvos", width=130, height=34,
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            fg_color="#FFFFFF", hover_color=self.c_senai_red_subtle,
            text_color=self.c_text_title, border_width=1, border_color="#CBD5E1",
            corner_radius=8,
            command=self._reset_range_targets
        )
        btn_reset.pack(side=tk.RIGHT, padx=14)

        # Arena de Teste
        arena_frame = ctk.CTkFrame(self.view_range, fg_color="transparent")
        arena_frame.pack(fill=tk.BOTH, expand=True)

        self.range_canvas = tk.Canvas(
            arena_frame, bg="#FFFFFF", highlightthickness=1,
            highlightbackground=self.c_card_border
        )
        self.range_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.range_canvas.bind("<Configure>", lambda e: self._redraw_range_canvas())
        self.range_canvas.bind("<Button-1>", self._on_range_canvas_click)

        # Mini Câmera Picture-in-Picture
        self.pip_card = ctk.CTkFrame(
            arena_frame, fg_color=self.c_card_subtle, corner_radius=14,
            border_width=1, border_color=self.c_card_border, width=220
        )
        self.pip_card.pack(side=tk.RIGHT, fill=tk.Y, padx=(14, 0))
        self.pip_card.pack_propagate(False)

        ctk.CTkLabel(
            self.pip_card, text="MONITOR DA MÃO",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=self.c_senai_red
        ).pack(anchor="w", padx=14, pady=(12, 4))

        self.pip_canvas = tk.Canvas(
            self.pip_card, bg="#000000", width=192, height=144,
            highlightthickness=1, highlightbackground=self.c_card_border
        )
        self.pip_canvas.pack(padx=14, pady=4)

        ctk.CTkLabel(
            self.pip_card,
            text="Alcance todos os 4 cantos e o centro da tela confortavelmente com o dedo indicador.",
            font=ctk.CTkFont(family="Segoe UI", size=9),
            text_color=self.c_text_muted, wraplength=190, justify=tk.LEFT
        ).pack(padx=14, pady=12)

    def _redraw_range_canvas(self):
        self.range_canvas.delete("all")
        cw = max(400, self.range_canvas.winfo_width())
        ch = max(300, self.range_canvas.winfo_height())

        # Grade suave
        for gx in range(0, cw, 60):
            self.range_canvas.create_line(gx, 0, gx, ch, fill="#F8FAFC", width=1)
        for gy in range(0, ch, 60):
            self.range_canvas.create_line(0, gy, cw, gy, fill="#F8FAFC", width=1)

        pad = 75
        self.coverage_nodes["top_left"]["pos"] = (pad, pad)
        self.coverage_nodes["top_right"]["pos"] = (cw - pad, pad)
        self.coverage_nodes["bottom_left"]["pos"] = (pad, ch - pad)
        self.coverage_nodes["bottom_right"]["pos"] = (cw - pad, ch - pad)
        self.coverage_nodes["center"]["pos"] = (cw // 2, ch // 2)

        hit_count = 0
        for key, node in self.coverage_nodes.items():
            nx, ny = node["pos"]
            is_hit = node["hit"]
            r = 34

            if is_hit:
                hit_count += 1
                self.range_canvas.create_oval(
                    nx - r, ny - r, nx + r, ny + r,
                    fill=self.c_success_bg, outline=self.c_success, width=2.5
                )
                self.range_canvas.create_text(
                    nx, ny, text="✓", fill=self.c_success, font=("Segoe UI", 16, "bold")
                )
            else:
                self.range_canvas.create_oval(
                    nx - r, ny - r, nx + r, ny + r,
                    fill=self.c_senai_red_subtle, outline=self.c_senai_red, width=2
                )
                self.range_canvas.create_oval(
                    nx - 7, ny - 7, nx + 7, ny + 7,
                    fill=self.c_senai_red, outline=""
                )

            label_color = self.c_success if is_hit else self.c_text_body
            self.range_canvas.create_text(
                nx, ny + r + 15, text=node["name"],
                fill=label_color, font=("Segoe UI", 9, "bold")
            )

        # Celebração de 100% de cobertura
        if hit_count == 5:
            bw, bh = 460, 54
            bx1, by1 = cw // 2 - bw // 2, ch // 2 + 50
            bx2, by2 = bx1 + bw, by1 + bh
            self.range_canvas.create_rectangle(
                bx1, by1, bx2, by2,
                fill=self.c_senai_red, outline="#FFFFFF", width=2
            )
            self.range_canvas.create_text(
                cw // 2, by1 + bh // 2,
                text="🎉 100% DA TELA ALCANÇADA COM SUCESSO!",
                fill="#FFFFFF", font=("Segoe UI", 12, "bold")
            )

    def _on_range_canvas_click(self, event):
        cx, cy = event.x, event.y
        for key, node in self.coverage_nodes.items():
            nx, ny = node["pos"]
            if math.hypot(cx - nx, cy - ny) <= 38:
                node["hit"] = True
                self._redraw_range_canvas()
                break

    def _reset_range_targets(self):
        for node in self.coverage_nodes.values():
            node["hit"] = False
        self._redraw_range_canvas()

    # -------------------------------------------------------------
    # VIEW 2: ARRASTE DE PEÇAS (DRAG & DROP)
    # -------------------------------------------------------------
    def _build_view_drag(self):
        self.view_drag = ctk.CTkFrame(self.content_container, fg_color="transparent")

        top_bar = ctk.CTkFrame(
            self.view_drag, fg_color=self.c_card_subtle, corner_radius=12,
            border_width=1, border_color=self.c_card_border, height=52
        )
        top_bar.pack(fill=tk.X, pady=(0, 14))
        top_bar.pack_propagate(False)

        ctk.CTkLabel(
            top_bar,
            text="Gesto de Arraste: Segure a pinça fechada por >0.3s sobre a peça, arraste até o destino e abra os dedos.",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=self.c_text_body
        ).pack(side=tk.LEFT, padx=18)

        self.drag_canvas = tk.Canvas(
            self.view_drag, bg="#FFFFFF", highlightthickness=1,
            highlightbackground=self.c_card_border
        )
        self.drag_canvas.pack(fill=tk.BOTH, expand=True)

        self.drag_canvas.bind("<Configure>", lambda e: self._redraw_drag_canvas())
        self.drag_canvas.bind("<ButtonPress-1>", self._on_drag_press)
        self.drag_canvas.bind("<B1-Motion>", self._on_drag_motion)
        self.drag_canvas.bind("<ButtonRelease-1>", self._on_drag_release)

    def _redraw_drag_canvas(self):
        self.drag_canvas.delete("all")
        cw = max(400, self.drag_canvas.winfo_width())
        ch = max(300, self.drag_canvas.winfo_height())

        z1_w = int(cw * 0.44)
        self.drag_canvas.create_rectangle(
            20, 20, z1_w, ch - 20,
            fill="#F8FAFC", outline="#CBD5E1", width=1.5, dash=(6, 4)
        )
        self.drag_canvas.create_text(
            34, 34, text="ÁREA DE ORIGEM",
            anchor="nw", fill=self.c_text_muted, font=("Segoe UI", 10, "bold")
        )

        z2_x = int(cw * 0.56)
        self.drag_canvas.create_rectangle(
            z2_x, 20, cw - 20, ch - 20,
            fill=self.c_senai_red_subtle, outline=self.c_senai_red, width=1.5, dash=(6, 4)
        )
        self.drag_canvas.create_text(
            z2_x + 16, 34, text="ÁREA DE DESTINO (SENAI)",
            anchor="nw", fill=self.c_senai_red, font=("Segoe UI", 10, "bold")
        )

        for i, item in enumerate(self.drag_items):
            x, y, w, h = item["x"], item["y"], item["w"], item["h"]
            is_active = (self.dragged_item_idx == i)
            border_c = "#0F172A" if is_active else "#CBD5E1"
            border_w = 3 if is_active else 1.5

            self.drag_canvas.create_rectangle(
                x, y, x + w, y + h,
                fill=item["color"], outline=border_c, width=border_w
            )
            self.drag_canvas.create_text(
                x + w // 2, y + h // 2,
                text=item["name"], fill="#FFFFFF", font=("Segoe UI", 10, "bold")
            )

    def _on_drag_press(self, event):
        x, y = event.x, event.y
        for i, item in enumerate(self.drag_items):
            if item["x"] <= x <= item["x"] + item["w"] and item["y"] <= y <= item["y"] + item["h"]:
                self.dragged_item_idx = i
                self.drag_offset = (x - item["x"], y - item["y"])
                self._redraw_drag_canvas()
                break

    def _on_drag_motion(self, event):
        if self.dragged_item_idx is not None:
            item = self.drag_items[self.dragged_item_idx]
            item["x"] = event.x - self.drag_offset[0]
            item["y"] = event.y - self.drag_offset[1]
            self._redraw_drag_canvas()

    def _on_drag_release(self, event):
        if self.dragged_item_idx is not None:
            item = self.drag_items[self.dragged_item_idx]
            cw = self.drag_canvas.winfo_width()
            item["zone"] = "destino" if item["x"] >= int(cw * 0.56) - 40 else "origem"
            self.dragged_item_idx = None
            self._redraw_drag_canvas()

    # -------------------------------------------------------------
    # VIEW 3: DESENHO LIVRE
    # -------------------------------------------------------------
    def _build_view_draw(self):
        self.view_draw = ctk.CTkFrame(self.content_container, fg_color="transparent")

        top_bar = ctk.CTkFrame(
            self.view_draw, fg_color=self.c_card_subtle, corner_radius=12,
            border_width=1, border_color=self.c_card_border, height=52
        )
        top_bar.pack(fill=tk.X, pady=(0, 14))
        top_bar.pack_propagate(False)

        ctk.CTkLabel(
            top_bar, text="Paleta de Cores:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=self.c_text_body
        ).pack(side=tk.LEFT, padx=(18, 8))

        palette = [
            (self.c_senai_red, "Vermelho SENAI"),
            (self.c_blue_tech, "Azul Tech"),
            (self.c_success, "Verde"),
            (self.c_text_title, "Grafite")
        ]

        for color_hex, name in palette:
            ctk.CTkButton(
                top_bar, text="", width=26, height=26, corner_radius=7,
                fg_color=color_hex, hover_color=color_hex,
                border_width=1, border_color="#CBD5E1",
                command=lambda c=color_hex: setattr(self, "draw_color", c)
            ).pack(side=tk.LEFT, padx=3.5)

        ctk.CTkButton(
            top_bar, text="🗑️ Limpar Tela", width=120, height=34, corner_radius=8,
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            fg_color="#FFFFFF", hover_color=self.c_senai_red_subtle,
            text_color=self.c_text_title, border_width=1, border_color="#CBD5E1",
            command=lambda: self.draw_canvas.delete("all")
        ).pack(side=tk.RIGHT, padx=14)

        self.draw_canvas = tk.Canvas(
            self.view_draw, bg="#FFFFFF", highlightthickness=1,
            highlightbackground=self.c_card_border
        )
        self.draw_canvas.pack(fill=tk.BOTH, expand=True)

        self.draw_canvas.bind("<B1-Motion>", self._on_mouse_draw)
        self.draw_canvas.bind("<ButtonRelease-1>", lambda e: setattr(self, "last_draw_pt", None))

    def _on_mouse_draw(self, event):
        x, y = event.x, event.y
        if self.last_draw_pt:
            self.draw_canvas.create_line(
                self.last_draw_pt[0], self.last_draw_pt[1], x, y,
                fill=self.draw_color, width=self.draw_brush_size, capstyle=tk.ROUND, smooth=True
            )
        self.last_draw_pt = (x, y)

    # -------------------------------------------------------------
    # VIEW 4: VISÃO DA CÂMERA & GESTOS
    # -------------------------------------------------------------
    def _build_view_camera(self):
        self.view_camera = ctk.CTkFrame(self.content_container, fg_color="transparent")

        cam_top = ctk.CTkFrame(
            self.view_camera, fg_color=self.c_card_subtle, corner_radius=12,
            border_width=1, border_color=self.c_card_border, height=52
        )
        cam_top.pack(fill=tk.X, pady=(0, 14))
        cam_top.pack_propagate(False)

        ctk.CTkLabel(
            cam_top, text="Dispositivo de Vídeo:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=self.c_text_body
        ).pack(side=tk.LEFT, padx=(18, 8))

        menu_values = [cam["label"] for cam in self.camera_list] if self.camera_list else ["Câmera 0"]
        default_val = self.camera_list[0]["label"] if self.camera_list else "Câmera 0"

        self.cam_dropdown_full = ctk.CTkOptionMenu(
            cam_top, values=menu_values, command=self._on_camera_selected,
            fg_color="#FFFFFF", button_color="#F1F5F9", button_hover_color=self.c_senai_red_subtle,
            text_color=self.c_text_title, dropdown_text_color=self.c_text_title,
            corner_radius=8, height=34, width=320
        )
        self.cam_dropdown_full.set(default_val)
        self.cam_dropdown_full.pack(side=tk.LEFT, padx=6)

        cam_body = ctk.CTkFrame(self.view_camera, fg_color="transparent")
        cam_body.pack(fill=tk.BOTH, expand=True)

        self.cam_canvas_full = tk.Canvas(
            cam_body, bg="#000000", highlightthickness=1,
            highlightbackground=self.c_card_border
        )
        self.cam_canvas_full.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        cam_info = ctk.CTkFrame(
            cam_body, fg_color=self.c_card_subtle, corner_radius=14,
            border_width=1, border_color=self.c_card_border, width=280
        )
        cam_info.pack(side=tk.RIGHT, fill=tk.Y, padx=(14, 0))
        cam_info.pack_propagate(False)

        ctk.CTkLabel(
            cam_info, text="GESTOS DE OPERAÇÃO",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=self.c_senai_red
        ).pack(anchor="w", padx=16, pady=(16, 8))

        gestures_full = [
            ("☝️", "Apontar Indicador", "Mover o cursor livremente"),
            ("🤏", "Pinça Firme", "Clique com trava magnética"),
            ("⚡", "Dois Toques", "Duplo clique rápido"),
            ("📦", "Segurar Pinça", "Arrastar janelas e objetos"),
            ("✌️", "Dois Dedos", "Rolagem de página vertical"),
            ("🔒", "Pulseira Preta", "Liberação biométrica de segurança")
        ]

        for icon, title, desc in gestures_full:
            row = ctk.CTkFrame(
                cam_info, fg_color="#FFFFFF", corner_radius=8,
                border_width=1, border_color=self.c_card_border
            )
            row.pack(fill=tk.X, padx=12, pady=3.5)

            ctk.CTkLabel(
                row, text=f"{icon}  {title}",
                font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"),
                text_color=self.c_text_title
            ).pack(anchor="w", padx=10, pady=(5, 1))

            ctk.CTkLabel(
                row, text=desc,
                font=ctk.CTkFont(family="Segoe UI", size=8),
                text_color=self.c_text_muted
            ).pack(anchor="w", padx=10, pady=(0, 5))

    # -------------------------------------------------------------
    # VIEW 5: CONFIGURAÇÕES DO SISTEMA
    # -------------------------------------------------------------
    def _build_view_settings(self):
        self.view_settings = ctk.CTkFrame(self.content_container, fg_color="transparent")

        settings_box = ctk.CTkFrame(
            self.view_settings, fg_color=self.c_card_subtle, corner_radius=16,
            border_width=1, border_color=self.c_card_border
        )
        settings_box.pack(fill=tk.BOTH, expand=True, padx=24, pady=24)

        ctk.CTkLabel(
            settings_box, text="PREFERÊNCIAS & CONTROLES",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=self.c_senai_red
        ).pack(anchor="w", padx=24, pady=(24, 16))

        # Opção 1: Controle do Windows em Tela Cheia
        opt1 = ctk.CTkFrame(settings_box, fg_color="#FFFFFF", corner_radius=12, border_width=1, border_color=self.c_card_border)
        opt1.pack(fill=tk.X, padx=24, pady=8)

        c1 = ctk.CTkFrame(opt1, fg_color="transparent")
        c1.pack(side=tk.LEFT, padx=18, pady=14)

        ctk.CTkLabel(c1, text="Controle do Mouse do Windows (Tela Inteira)", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color=self.c_text_title).pack(anchor="w")
        ctk.CTkLabel(c1, text="Permite que o cursor alcance 100% dos cantos e interaja com qualquer aplicativo do computador.", font=ctk.CTkFont(family="Segoe UI", size=9), text_color=self.c_text_muted).pack(anchor="w")

        self.full_screen_switch = ctk.CTkSwitch(
            opt1, text="", command=self._on_switch_full_screen,
            progress_color=self.c_senai_red, button_color="#FFFFFF"
        )
        self.full_screen_switch.select()
        self.full_screen_switch.pack(side=tk.RIGHT, padx=18)

        # Opção 2: Modo Flutuante
        opt2 = ctk.CTkFrame(settings_box, fg_color="#FFFFFF", corner_radius=12, border_width=1, border_color=self.c_card_border)
        opt2.pack(fill=tk.X, padx=24, pady=8)

        c2 = ctk.CTkFrame(opt2, fg_color="transparent")
        c2.pack(side=tk.LEFT, padx=18, pady=14)

        ctk.CTkLabel(c2, text="Modo Flutuante / Mini Barra", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color=self.c_text_title).pack(anchor="w")
        ctk.CTkLabel(c2, text="Encolhe o aplicativo para uma mini-barra no canto da tela, liberando o monitor para navegação.", font=ctk.CTkFont(family="Segoe UI", size=9), text_color=self.c_text_muted).pack(anchor="w")

        btn_mini_view = ctk.CTkButton(
            opt2, text="🗖 Ativar Mini Modo", width=145, height=36,
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            fg_color="#FFFFFF", hover_color=self.c_senai_red_subtle,
            text_color=self.c_text_title, border_width=1, border_color="#CBD5E1",
            corner_radius=8, command=self._toggle_mini_mode
        )
        btn_mini_view.pack(side=tk.RIGHT, padx=18)

        # Opção 3: Totem Digital SENAI
        opt3 = ctk.CTkFrame(settings_box, fg_color="#FFFFFF", corner_radius=12, border_width=1, border_color=self.c_card_border)
        opt3.pack(fill=tk.X, padx=24, pady=8)

        c3 = ctk.CTkFrame(opt3, fg_color="transparent")
        c3.pack(side=tk.LEFT, padx=18, pady=14)

        ctk.CTkLabel(c3, text="Totem Digital SENAI (Interface Web)", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color=self.c_text_title).pack(anchor="w")
        ctk.CTkLabel(c3, text="Abre o painel web interativo oficial com transições automáticas de 20s.", font=ctk.CTkFont(family="Segoe UI", size=9), text_color=self.c_text_muted).pack(anchor="w")

        btn_open_web = ctk.CTkButton(
            opt3, text="🌐 Iniciar Totem", width=145, height=36,
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            fg_color=self.c_senai_red, hover_color=self.c_senai_red_hover,
            text_color="#FFFFFF", corner_radius=8, command=self._open_totem_web
        )
        btn_open_web.pack(side=tk.RIGHT, padx=18)

    # -------------------------------------------------------------
    # 4. MODO FLUTUANTE / MINI WIDGET
    # -------------------------------------------------------------
    def _toggle_mini_mode(self):
        if not self.is_mini_mode:
            self.is_mini_mode = True
            self.body_container.pack_forget()
            self.navbar.pack_forget()
            self.geometry("520x86+40+40")
            self.attributes("-topmost", True)

            self.mini_bar = ctk.CTkFrame(self, fg_color=self.c_card, corner_radius=14, border_width=1, border_color=self.c_card_border)
            self.mini_bar.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

            ctk.CTkLabel(
                self.mini_bar, text="🖱️ SENAI MOUSE VIRTUAL (ATIVO)",
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                text_color=self.c_senai_red
            ).pack(side=tk.LEFT, padx=16)

            ctk.CTkButton(
                self.mini_bar, text="🗖 Restaurar", width=100, height=30,
                font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                fg_color="#FFFFFF", hover_color=self.c_senai_red_subtle,
                text_color=self.c_text_title, border_width=1, border_color="#CBD5E1",
                corner_radius=8, command=self._toggle_mini_mode
            ).pack(side=tk.RIGHT, padx=12)
        else:
            self.is_mini_mode = False
            self.mini_bar.destroy()
            self.geometry("1280x820")
            self.attributes("-topmost", False)
            self.navbar.pack(fill=tk.X, padx=18, pady=(16, 12))
            self.body_container.pack(fill=tk.BOTH, expand=True, padx=18, pady=(0, 16))

    # -------------------------------------------------------------
    # 5. SINCRONIZAÇÃO DE CÂMERA & INTERAÇÃO
    # -------------------------------------------------------------
    def _on_switch_full_screen(self):
        val = self.full_screen_switch.get()
        self.engine.update_params(control_system_mouse=bool(val))

    def _on_frame_ready(self, frame: np.ndarray):
        self.last_frame = frame

    def _on_telemetry_ready(self, telemetry: Dict[str, Any]):
        pass  # Sem estatísticas técnicas na interface

    def _on_engine_action(self, event_name: str, payload: Dict[str, Any]):
        pass

    def _update_loop(self):
        # Atualiza apenas os feeds visuais de vídeo
        if self.last_frame is not None and not self.is_mini_mode:
            try:
                frame_rgb = cv2.cvtColor(self.last_frame, cv2.COLOR_BGR2RGB)
                fh, fw = frame_rgb.shape[:2]

                if self.current_view_key == "camera":
                    cw = max(400, self.cam_canvas_full.winfo_width())
                    ch = max(300, self.cam_canvas_full.winfo_height())
                    scale = min(cw / fw, ch / fh)
                    nw, nh = int(fw * scale), int(fh * scale)
                    resized = cv2.resize(frame_rgb, (nw, nh), interpolation=cv2.INTER_LINEAR)
                    img = Image.fromarray(resized)
                    self.photo_image = ImageTk.PhotoImage(image=img)
                    self.cam_canvas_full.delete("all")
                    self.cam_canvas_full.create_image(cw // 2, ch // 2, image=self.photo_image, anchor=tk.CENTER)

                if self.current_view_key == "range":
                    scale_pip = min(192 / fw, 144 / fh)
                    nw, nh = int(fw * scale_pip), int(fh * scale_pip)
                    resized_pip = cv2.resize(frame_rgb, (nw, nh), interpolation=cv2.INTER_LINEAR)
                    img_pip = Image.fromarray(resized_pip)
                    self.photo_image_pip = ImageTk.PhotoImage(image=img_pip)
                    self.pip_canvas.delete("all")
                    self.pip_canvas.create_image(96, 72, image=self.photo_image_pip, anchor=tk.CENTER)
            except Exception:
                pass

        self.after(33, self._update_loop)

    def _toggle_camera(self):
        if not self.is_camera_active:
            success = self.engine.start(cam_index=self.selected_camera_index)
            if success:
                self.is_camera_active = True
                self.btn_power.configure(text="⏹ Parar CÂMERA", fg_color="#475569", hover_color="#334155")
                self.status_badge.configure(text="● Câmera Ativa", text_color=self.c_success, fg_color=self.c_success_bg)
        else:
            self.engine.stop()
            self.is_camera_active = False
            self.btn_power.configure(text="▶ Ligar Câmera", fg_color=self.c_senai_red, hover_color=self.c_senai_red_hover)
            self.status_badge.configure(text="○ Câmera Pausada", text_color=self.c_text_muted, fg_color=self.c_card_subtle)

    def _on_camera_selected(self, choice: str):
        target_idx = self.camera_map.get(choice, 0)
        if target_idx == self.selected_camera_index and self.is_camera_active:
            return

        self.selected_camera_index = target_idx
        if self.is_camera_active:
            self.engine.stop()
            time.sleep(0.15)
            self.engine.start(cam_index=self.selected_camera_index)

    def _on_close(self):
        if self.is_camera_active:
            self.engine.stop()
        self.destroy()


def run_app():
    app = ModernSenaiMouseApp()
    app.mainloop()


if __name__ == "__main__":
    run_app()
