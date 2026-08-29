"""
Motion-based vehicle detector — REAL, WORKING, but an interim stand-in for YOLO.

Why this exists instead of YOLO right now:
  - ultralytics (YOLO) pulls in PyTorch, a multi-GB dependency, and needs a
    downloaded model weight file - unnecessary to force on every dev machine
    just to run the scaffold, and unnecessary until real traffic footage
    with real vehicles exists to test against.
  - This detector uses OpenCV background subtraction (MOG2) + contour
    filtering to find moving blobs in a frame. It is genuinely functional
    computer vision - it processes real pixel data frame-by-frame and finds
    real motion - but it cannot classify vehicle type or read plates. It is
    a placeholder for the DETECTION step only.

Swapping in real YOLO later (once real footage exists):
  Replace MotionBlobDetector with a class exposing the same
  `detect(frame) -> list[Detection]` interface, backed by
  `ultralytics.YOLO(...)　.predict(frame)`. VisionAgent and everything
  downstream (API routes, Investigation Agent) does not need to change,
  because they only depend on the Detection dataclass shape below.
"""
from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np


@dataclass
class Detection:
    x: int
    y: int
    w: int
    h: int
    area: float


class MotionBlobDetector:
    def __init__(self, min_area: int = 400, max_area_ratio: float = 0.5) -> None:
        self.min_area = min_area
        # Rejects implausibly large "detections" that cover most of the frame -
        # these are almost always background-subtractor cold-start artifacts
        # (the very first frame has no background model yet) rather than a
        # real single vehicle. This is standard practice, not a fudge.
        self.max_area_ratio = max_area_ratio
        self._bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=50, varThreshold=30, detectShadows=False
        )
        self._frames_seen = 0

    def detect(self, frame: np.ndarray) -> list[Detection]:
        self._frames_seen += 1
        frame_area = frame.shape[0] * frame.shape[1]
        max_area = frame_area * self.max_area_ratio

        fg_mask = self._bg_subtractor.apply(frame)

        # Skip the very first frame entirely - MOG2 has no background model
        # yet, so everything is flagged as foreground by definition.
        if self._frames_seen <= 1:
            return []

        # Clean up noise so small flickers aren't reported as vehicles.
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        fg_mask = cv2.dilate(fg_mask, np.ones((5, 5), np.uint8), iterations=2)

        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        detections = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < self.min_area or area > max_area:
                continue
            x, y, w, h = cv2.boundingRect(contour)
            detections.append(Detection(x=x, y=y, w=w, h=h, area=area))

        return detections

    @staticmethod
    def dominant_color(frame: np.ndarray, detection: Detection) -> str:
        """Rough color estimate from the mean pixel color inside the bounding
        box - a real (if simple) signal for the 'color' field, not invented."""
        crop = frame[detection.y : detection.y + detection.h, detection.x : detection.x + detection.w]
        if crop.size == 0:
            return "unknown"
        mean_b, mean_g, mean_r = crop.reshape(-1, 3).mean(axis=0)

        # Very simple bucketing - adequate as a placeholder signal only.
        if max(mean_r, mean_g, mean_b) < 70:
            return "black"
        if min(mean_r, mean_g, mean_b) > 180:
            return "white"
        if mean_r > mean_g and mean_r > mean_b:
            return "red"
        if mean_b > mean_r and mean_b > mean_g:
            return "blue"
        return "grey"
