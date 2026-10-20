import cv2
import numpy as np
import os

_LOGO_CACHE = {}

def get_usb_camera_cap(cam_w=640, cam_h=480):
    """
    Detecta e abre exclusivamente cameras USB externas no Windows,
    excluindo cameras integradas de notebook e cameras virtuais (OBS, etc.).
    Retorna (cap, cam_name, cam_idx).
    """
    devices = []
    try:
        from pygrabber.dshow_graph import FilterGraph
        graph = FilterGraph()
        devices = graph.get_input_devices()
    except Exception:
        devices = []

    virtual_keywords = ['ivcam', 'obs', 'virtual', 'droidcam', 'iriun', 'manycam', 'vcam', 'splitcam', 'snap camera']
    internal_keywords = ['integrated', 'internal', 'built-in', 'builtin', 'integrada', 'interna', 'front camera', 'rear camera', 'ir camera']

    selected_idx = None
    selected_name = None

    if devices:
        for idx, dev_name in enumerate(devices):
            name_lower = dev_name.lower()
            if any(k in name_lower for k in virtual_keywords):
                continue
            if any(k in name_lower for k in internal_keywords):
                continue
            selected_idx = idx
            selected_name = dev_name
            break

        if selected_idx is None:
            for idx, dev_name in enumerate(devices):
                name_lower = dev_name.lower()
                if any(k in name_lower for k in virtual_keywords):
                    continue
                if any(k in name_lower for k in ['usb', 'c922', 'c920', 'logitech', 'webcam']):
                    if not any(k in name_lower for k in internal_keywords):
                        selected_idx = idx
                        selected_name = dev_name
                        break

    if selected_idx is None:
        for test_idx in [1, 2, 3, 0]:
            test_cap = cv2.VideoCapture(test_idx, cv2.CAP_DSHOW)
            if test_cap.isOpened():
                ret, _ = test_cap.read()
                test_cap.release()
                if ret:
                    selected_idx = test_idx
                    selected_name = devices[test_idx] if test_idx < len(devices) else f"Camera USB ({test_idx})"
                    break

    if selected_idx is None:
        selected_idx = 1
        selected_name = "Camera USB (Padrao)"

    cap = cv2.VideoCapture(selected_idx, cv2.CAP_DSHOW)
    if not cap.isOpened():
        cap = cv2.VideoCapture(selected_idx)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, cam_w)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cam_h)
    return cap, selected_name, selected_idx


def overlay_senai_logo(frame, x=15, y=6, target_h=34):
    """
    Desenha a logo oficial do SENAI com canal alfa perfeito sobre o frame.
    Utiliza cache em memoria para nao recalcular o resize a cada frame.
    """
    global _LOGO_CACHE
    logo_path = os.path.join(os.path.dirname(__file__), "senai_logo.png")
    
    if not os.path.exists(logo_path):
        # Fallback elegante caso a imagem nao esteja presente
        cv2.putText(frame, "SENAI", (x, y + 26), cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 70, 210), 2)
        cv2.putText(frame, "SP", (x + 95, y + 26), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1)
        return

    cache_key = (logo_path, target_h)
    if cache_key not in _LOGO_CACHE:
        raw_logo = cv2.imread(logo_path, cv2.IMREAD_UNCHANGED)
        if raw_logo is None:
            return
        orig_h, orig_w = raw_logo.shape[:2]
        scale = target_h / orig_h
        target_w = int(orig_w * scale)
        resized = cv2.resize(raw_logo, (target_w, target_h), interpolation=cv2.INTER_AREA)
        _LOGO_CACHE[cache_key] = (resized, target_w, target_h)

    logo_img, w, h = _LOGO_CACHE[cache_key]
    fh, fw = frame.shape[:2]

    # Garante limites
    if x + w > fw or y + h > fh:
        return

    # Se a logo tiver canal alfa
    if logo_img.shape[2] == 4:
        alpha = logo_img[:, :, 3] / 255.0
        # Criar fundo branco sutil translucido atras da logo para destaque maximo
        card_pad = 4
        x1 = max(0, x - card_pad)
        y1 = max(0, y - card_pad)
        x2 = min(fw, x + w + card_pad)
        y2 = min(fh, y + h + card_pad)
        
        # Placa de vidro branca suave de fundo
        bg_slice = frame[y1:y2, x1:x2].astype(np.float32)
        white_plate = np.full_like(bg_slice, 250)
        frame[y1:y2, x1:x2] = (0.85 * white_plate + 0.15 * bg_slice).astype(np.uint8)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (200, 200, 200), 1)

        # Alpha blend da logo
        roi = frame[y:y+h, x:x+w]
        for c in range(3):
            roi[:, :, c] = (alpha * logo_img[:, :, c] + (1.0 - alpha) * roi[:, :, c]).astype(np.uint8)
    else:
        frame[y:y+h, x:x+w] = logo_img[:, :, :3]


def draw_glow_banner(frame, title, subtitle="", fps=None):
    """Desenha cabecalho de alta tecnologia com a logo do SENAI e telemetria"""
    W = frame.shape[1]
    
    # Base escura com degradê suave
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (W, 52), (10, 14, 22), -1)
    cv2.addWeighted(overlay, 0.88, frame, 0.12, 0, frame)

    # Linha neon ciano/azul embaixo do banner
    cv2.line(frame, (0, 52), (W, 52), (0, 190, 255), 1)
    cv2.line(frame, (0, 53), (W, 53), (0, 80, 150), 1)

    # Logo do SENAI no canto esquerdo
    overlay_senai_logo(frame, x=14, y=8, target_h=34)

    # Titulo centralizado ou ao lado
    cv2.putText(frame, title, (170, 32), cv2.FONT_HERSHEY_DUPLEX, 0.65, (0, 240, 255), 1)
    if subtitle:
        cv2.putText(frame, f"| {subtitle}", (175 + len(title) * 11, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 180, 180), 1)

    # Telemetria no canto direito
    if fps is not None:
        cv2.circle(frame, (W - 85, 30), 4, (0, 255, 120), -1)
        cv2.putText(frame, f"{int(fps)} FPS", (W - 74, 34), cv2.FONT_HERSHEY_DUPLEX, 0.45, (200, 200, 200), 1)
