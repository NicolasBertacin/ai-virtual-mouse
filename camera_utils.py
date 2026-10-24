"""   
####
Camera Management and Auto-Detection Utilities for AI Virtual Mouse.
Detects USB webcams, integrated webcams, and virtual cameras.
Prioritizes physical external USB webcams.
Cross-plat form support: Windows (DirectShow), Linux / Raspberry Pi (V4L2), and macOS.
"""

import sys
import os
import cv2
from typing import List, Dict, Any, Tuple, Optional


VIRTUAL_KEYWORDS = [
    'virtual', 'obs', 'ivcam', 'droidcam', 'iriun',
    'manycam', 'vcam', 'epoccam', 'splitcam', 'ndi', 'unity'
]

INTEGRATED_KEYWORDS = [
    'integrated', 'internal', 'built-in', 'builtin',
    'laptop', 'facetime', 'front camera', 'rear camera', 'câmera frontal'
]




def _get_platform_backend() -> int:
    """Retorna o backend ideal de captura para o sistema operacional atual."""
    if sys.platform == "win32":
        return cv2.CAP_DSHOW
    elif sys.platform.startswith("linux"):
        return cv2.CAP_V4L2
    return 0


def get_camera_devices() -> List[Dict[str, Any]]:
    """
    Detects all video capture devices on the system.
    Identifies external USB webcams vs integrated laptop cameras vs virtual cameras.
    Returns list of device dictionaries sorted by priority (USB webcams first).
    """
    device_names: List[str] = []

    # 1. No Windows, tenta pygrabber para obter os nomes reais DirectShow
    if sys.platform == "win32":
        try:
            from pygrabber.dshow_graph import FilterGraph
            graph = FilterGraph()
            device_names = graph.get_input_devices()
        except Exception:
            device_names = []

    # 2. No Linux / Raspberry Pi, verifica nós /sys ou /dev/video se disponíveis
    if not device_names and sys.platform.startswith("linux"):
        try:
            # Lista dispositivos /sys/class/video4linux
            v4l_dir = "/sys/class/video4linux"
            if os.path.isdir(v4l_dir):
                nodes = sorted([d for d in os.listdir(v4l_dir) if d.startswith("video")])
                for node in nodes:
                    name_file = os.path.join(v4l_dir, node, "name")
                    idx_str = node.replace("video", "")
                    if idx_str.isdigit():
                        idx = int(idx_str)
                        c_name = f"V4L2 Camera {idx}"
                        if os.path.exists(name_file):
                            try:
                                with open(name_file, "r", encoding="utf-8") as f:
                                    c_name = f.read().strip()
                            except Exception:
                                pass
                        # Testa apenas índices pares ou válidos para captura de vídeo
                        cap = cv2.VideoCapture(idx, cv2.CAP_V4L2)
                        if cap.isOpened():
                            ret, _ = cap.read()
                            if ret:
                                device_names.append(c_name)
                            cap.release()
        except Exception:
            device_names = []

    # 3. Fallback universal: probe via índices OpenCV
    if not device_names:
        backend = _get_platform_backend()
        for idx in range(6):
            cap = cv2.VideoCapture(idx, backend) if backend != 0 else cv2.VideoCapture(idx)
            if not cap.isOpened():
                cap = cv2.VideoCapture(idx)
            if cap.isOpened():
                ret, _ = cap.read()
                if ret:
                    device_names.append(f"Câmera de Vídeo {idx}")
                cap.release()
            else:
                break

    devices_info: List[Dict[str, Any]] = []

    for idx, name in enumerate(device_names):
        nl = name.lower()
        is_virt = any(k in nl for k in VIRTUAL_KEYWORDS)
        is_integ = any(k in nl for k in INTEGRATED_KEYWORDS)
        is_usb_ext = (not is_virt) and (not is_integ)

        if is_usb_ext:
            score = 100
            label = f"{name} (USB Externa)"
        elif is_integ:
            score = 50
            label = f"{name} (Integrada)"
        elif is_virt:
            score = 10
            label = f"{name} (Virtual)"
        else:
            score = 40
            label = f"{name}"

        devices_info.append({
            "index": idx,
            "name": name,
            "label": label,
            "score": score,
            "is_usb_external": is_usb_ext,
            "is_integrated": is_integ,
            "is_virtual": is_virt
        })

    # Sort so that highest score (external USB webcam) is first
    devices_info.sort(key=lambda d: d["score"], reverse=True)
    return devices_info


def get_default_camera_index() -> int:
    """
    Returns the camera index of the best physical USB webcam available.
    Falls back to 0 if no preferred camera is found.
    """
    cams = get_camera_devices()
    if cams:
        return cams[0]["index"]
    return 0


def get_default_camera_name() -> str:
    """
    Returns the friendly name of the preferred USB webcam.
    """
    cams = get_camera_devices()
    if cams:
        return cams[0]["name"]
    return "Câmera Padrão"


def open_camera(cam_index: int, cam_w: int = 640, cam_h: int = 480) -> Tuple[Optional[cv2.VideoCapture], str, int]:
    """
    Opens the camera at the given index with the optimal platform backend:
    - DirectShow on Windows
    - V4L2 on Linux / Raspberry Pi 5
    - Default on other platforms
    Sets preferred resolution (MJPG 60 FPS) and validates capture.
    Returns (cap, cam_name, cam_index).
    """
    cams = get_camera_devices()
    cam_name = f"Camera {cam_index}"
    for c in cams:
        if c["index"] == cam_index:
            cam_name = c["name"]
            break

    backend = _get_platform_backend()
    cap = cv2.VideoCapture(cam_index, backend) if backend != 0 else cv2.VideoCapture(cam_index)
    if not cap.isOpened():
        cap = cv2.VideoCapture(cam_index)

    if cap.isOpened():
        # High-FPS MJPG configuration & zero-latency buffer
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, cam_w)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cam_h)
        cap.set(cv2.CAP_PROP_FPS, 60)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        # Test read
        ret, _ = cap.read()
        if not ret:
            # If reading failed with accelerated backend, try default backend
            cap.release()
            cap = cv2.VideoCapture(cam_index)
            if cap.isOpened():
                cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, cam_w)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cam_h)
                cap.set(cv2.CAP_PROP_FPS, 60)
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    return cap, cam_name, cam_index
