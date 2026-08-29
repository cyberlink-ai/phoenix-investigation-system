"""
Video Ingest Service — reads real frames from a video file on disk.

This is the actual entry point for simulated camera feeds: each video file
in data/sample_videos/ is treated as one camera. This module knows nothing
about detection - it just yields (frame_index, timestamp_seconds, frame)
tuples for a Vision Agent to process. Kept separate so swapping in a live
RTSP stream later (real deployment, out of SIH prototype scope) only means
writing a new ingest class with the same generator interface.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator

import cv2
import numpy as np


@dataclass
class Frame:
    frame_index: int
    timestamp_seconds: float
    image: np.ndarray


class VideoFileIngestService:
    def __init__(self, video_path: str, camera_id: str) -> None:
        self.video_path = video_path
        self.camera_id = camera_id

    def frames(self, sample_every_n_frames: int = 1) -> Iterator[Frame]:
        """
        Yields frames from the video file. sample_every_n_frames > 1 skips
        frames to reduce processing load (e.g. run detection at 5fps on a
        30fps source) - a real, common technique, not a shortcut that fakes
        results.
        """
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            raise FileNotFoundError(f"Could not open video file: {self.video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        frame_index = 0

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                if frame_index % sample_every_n_frames == 0:
                    yield Frame(
                        frame_index=frame_index,
                        timestamp_seconds=frame_index / fps,
                        image=frame,
                    )
                frame_index += 1
        finally:
            cap.release()

    def get_metadata(self) -> dict:
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            raise FileNotFoundError(f"Could not open video file: {self.video_path}")
        meta = {
            "camera_id": self.camera_id,
            "video_path": self.video_path,
            "fps": cap.get(cv2.CAP_PROP_FPS),
            "frame_count": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        }
        cap.release()
        return meta
