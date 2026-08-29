import os

from fastapi import APIRouter, HTTPException

from app.agents.vision_agent import VisionAgent

router = APIRouter(prefix="/vehicles", tags=["vehicles"])

_vision_agent = VisionAgent()

# Resolved relative to the backend/ directory (where uvicorn is normally run from).
_SAMPLE_VIDEO_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "data", "sample_videos"))


@router.get("/events/mock")
def get_mock_events(camera_id: str = "CAM-01"):
    """
    Returns clearly-labeled mock detection events (source: 'mock') for
    frontend development when no video file is available at all.
    """
    return {"events": _vision_agent.get_mock_events(camera_id)}


@router.get("/events/from-video")
def get_events_from_video(camera_id: str = "CAM-01", filename: str = "synthetic_demo_camera01.mp4", max_events: int = 30):
    """
    Runs the REAL video ingestion + motion detection pipeline against a video
    file in data/sample_videos/ and returns real detection events
    (source: 'motion_detector_real_video'). Works with the synthetic
    placeholder video now, and with real traffic footage later - no code
    change needed, just drop the real file into data/sample_videos/.
    """
    video_path = os.path.join(_SAMPLE_VIDEO_DIR, filename)
    if not os.path.exists(video_path):
        raise HTTPException(
            status_code=404,
            detail=f"Video file not found: {filename}. Run backend/scripts/generate_synthetic_video.py "
            "or drop a real video file into data/sample_videos/.",
        )

    events = _vision_agent.process_video_file(video_path=video_path, camera_id=camera_id, sample_every_n_frames=2)
    return {"camera_id": camera_id, "source_file": filename, "event_count": len(events), "events": events[:max_events]}
