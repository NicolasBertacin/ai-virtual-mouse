"""
Universal Hand Tracker Module (Python 3.8 - 3.13+)
Provides high-performance hand landmark detection using MediaPipe Tasks API
with automatic fallback to legacy MediaPipe Solutions API if available.
Works on Windows, Linux (Raspberry Pi 5 / x86_64), and macOS.
Includes in-memory RAM acceleration (/dev/shm) and automatic GPU/CPU delegate negotiation.
"""

import os
import cv2
import numpy as np
import mediapipe as mp
import urllib.request
from typing import List, Optional, Tuple


HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),        # Polegar
    (0, 5), (5, 6), (6, 7), (7, 8),        # Indicador
    (5, 9), (9, 10), (10, 11), (11, 12),    # Médio
    (9, 13), (13, 14), (14, 15), (15, 16), # Anelar
    (13, 17), (17, 18), (18, 19), (19, 20), (0, 17) # Mínimo e palma
]


class NormalizedLandmark:
    __slots__ = ('x', 'y', 'z')
    def __init__(self, x: float, y: float, z: float = 0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)


class SingleHandLandmarks:
    def __init__(self, landmark_list: List[NormalizedLandmark]):
        self.landmark = landmark_list

    def __getitem__(self, idx: int) -> NormalizedLandmark:
        return self.landmark[idx]

    def __len__(self) -> int:
        return len(self.landmark)


class HandDetectionResults:
    def __init__(self, multi_hand_landmarks: Optional[List[SingleHandLandmarks]] = None):
        self.multi_hand_landmarks = multi_hand_landmarks or []


class UniversalHandsDetector:
    """
    Unified Hand Landmarker compatible with both MediaPipe Tasks (Python 3.13+)
    and legacy MediaPipe Solutions (Python 3.8 - 3.12).
    """
    def __init__(
        self,
        max_num_hands: int = 2,
        min_detection_confidence: float = 0.65,
        min_tracking_confidence: float = 0.65,
        model_path: str = "hand_landmarker.task"
    ):
        self.max_hands = max_num_hands
        self.use_legacy = False
        self.legacy_detector = None
        self.tasks_detector = None

        # Check for legacy MediaPipe solutions API
        if hasattr(mp, "solutions") and hasattr(mp.solutions, "hands"):
            try:
                self.legacy_detector = mp.solutions.hands.Hands(
                    max_num_hands=max_num_hands,
                    min_detection_confidence=min_detection_confidence,
                    min_tracking_confidence=min_tracking_confidence
                )
                self.use_legacy = True
                return
            except Exception:
                pass

        # 1. Check in-memory RAM disk (/dev/shm) first for maximum performance
        shm_candidate = os.path.join("/dev/shm", os.path.basename(model_path))
        if os.path.exists(shm_candidate):
            model_path = shm_candidate
        elif not os.path.isabs(model_path):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            candidate = os.path.join(script_dir, model_path)
            if os.path.exists(candidate):
                model_path = candidate

        # 2. Download model if missing
        if not os.path.exists(model_path):
            url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
            urllib.request.urlretrieve(url, model_path)

        from mediapipe.tasks import python
        from mediapipe.tasks.python import vision

        # 3. Automatic Hardware Acceleration Delegate (GPU with CPU fallback)
        delegate = python.BaseOptions.Delegate.CPU
        if hasattr(python.BaseOptions, "Delegate"):
            try:
                test_bo = python.BaseOptions(model_asset_path=model_path, delegate=python.BaseOptions.Delegate.GPU)
                test_opts = vision.HandLandmarkerOptions(base_options=test_bo, num_hands=1)
                test_inst = vision.HandLandmarker.create_from_options(test_opts)
                test_inst.close()
                delegate = python.BaseOptions.Delegate.GPU
                print("[MediaPipe] Aceleracao por Hardware (GPU Delegate) ATIVA!")
            except Exception:
                delegate = python.BaseOptions.Delegate.CPU

        base_options = python.BaseOptions(model_asset_path=model_path, delegate=delegate)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=max_num_hands,
            min_hand_detection_confidence=min_detection_confidence,
            min_hand_presence_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        self.tasks_detector = vision.HandLandmarker.create_from_options(options)

    def process(self, rgb_frame: np.ndarray) -> HandDetectionResults:
        if self.use_legacy and self.legacy_detector:
            return self.legacy_detector.process(rgb_frame)

        if not self.tasks_detector:
            return HandDetectionResults([])

        # MediaPipe Tasks expects mp.Image
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        detection_result = self.tasks_detector.detect(mp_image)

        formatted_hands = []
        if detection_result.hand_landmarks:
            for hand in detection_result.hand_landmarks:
                lms = [NormalizedLandmark(lm.x, lm.y, lm.z) for lm in hand]
                formatted_hands.append(SingleHandLandmarks(lms))

        return HandDetectionResults(formatted_hands)


def draw_hand_skeleton(frame: np.ndarray, landmarks: SingleHandLandmarks, color: Tuple[int, int, int] = (0, 255, 120), thickness: int = 2):
    """Draws skeleton connection lines and landmark circles on frame."""
    h, w, _ = frame.shape
    coords = [(int(lm.x * w), int(lm.y * h)) for lm in landmarks.landmark]

    for p1, p2 in HAND_CONNECTIONS:
        if p1 < len(coords) and p2 < len(coords):
            cv2.line(frame, coords[p1], coords[p2], color, thickness)

    for pt in coords:
        cv2.circle(frame, pt, 3, (255, 255, 255), -1)
        cv2.circle(frame, pt, 5, color, 1)
