"""
Generates a SYNTHETIC placeholder video for testing the video-ingestion and
detection pipeline before real traffic footage is available.

This is NOT real traffic footage. It draws moving colored rectangles
("vehicles") across a plain background so the CV pipeline has real pixel
data (real motion, real frames) to run against, without pretending to be an
actual detection demo. Every event this produces downstream should be
understood as a pipeline-correctness test, not a capability demo.

Usage:
    python3 generate_synthetic_video.py
"""
import os

import cv2
import numpy as np

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.normpath(
    os.path.join(SCRIPT_DIR, "..", "..", "data", "sample_videos", "synthetic_demo_camera01.mp4")
)
WIDTH, HEIGHT = 640, 360
FPS = 15
DURATION_SECONDS = 8


def generate():
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(OUTPUT_PATH, fourcc, FPS, (WIDTH, HEIGHT))
    if not writer.isOpened():
        raise RuntimeError(
            "VideoWriter failed to open. mp4v codec may be unavailable in this "
            "OpenCV build - try 'XVID' with a .avi OUTPUT_PATH instead."
        )

    total_frames = FPS * DURATION_SECONDS

    # Two "vehicles" moving at different speeds/directions across a road-like backdrop.
    vehicles = [
        {"x": -60, "y": 140, "w": 70, "h": 35, "speed": 6, "color": (40, 40, 200)},   # red-ish, left->right
        {"x": WIDTH + 60, "y": 220, "w": 60, "h": 30, "speed": -4, "color": (30, 30, 30)},  # dark, right->left
    ]

    for frame_idx in range(total_frames):
        frame = np.full((HEIGHT, WIDTH, 3), (60, 60, 60), dtype=np.uint8)  # grey "road"
        # lane markings
        for lx in range(0, WIDTH, 40):
            cv2.rectangle(frame, (lx, HEIGHT // 2 - 2), (lx + 20, HEIGHT // 2 + 2), (200, 200, 200), -1)

        for v in vehicles:
            v["x"] += v["speed"]
            cv2.rectangle(
                frame,
                (int(v["x"]), int(v["y"])),
                (int(v["x"] + v["w"]), int(v["y"] + v["h"])),
                v["color"],
                -1,
            )

        writer.write(frame)

    writer.release()
    size = os.path.getsize(OUTPUT_PATH) if os.path.exists(OUTPUT_PATH) else 0
    print(f"Synthetic video written to {OUTPUT_PATH} ({total_frames} frames, {FPS} fps, {size} bytes)")


if __name__ == "__main__":
    generate()
