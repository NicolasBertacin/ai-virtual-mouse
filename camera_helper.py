import cv2

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
        # 1. Primeira prioridade: dispositivo fisico externo (nem virtual, nem integrado)
        for idx, dev_name in enumerate(devices):
            name_lower = dev_name.lower()
            if any(k in name_lower for k in virtual_keywords):
                continue
            if any(k in name_lower for k in internal_keywords):
                continue
            selected_idx = idx
            selected_name = dev_name
            break

        # 2. Busca por termos especificos de USB/Webcam externa
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

    # 3. Fallback: testa o indice 1 primeiro (geralmente a camera externa quando o notebook usa o 0)
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
