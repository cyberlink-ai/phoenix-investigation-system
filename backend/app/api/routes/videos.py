"""Video upload and real OpenCV processing endpoints for the prototype."""
from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import cv2
from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile

from app.agents.vision_agent import VisionAgent
from app.services.video_store import VideoStore

router = APIRouter(prefix="/videos", tags=["videos"])
_root = Path(__file__).resolve().parents[4] / "data" / "runtime"
_store = VideoStore(_root)
_allowed_extensions = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
_max_upload_bytes = 750 * 1024 * 1024


def _camera_id(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_-]", "", value).upper()[:32]
    if not cleaned:
        raise HTTPException(status_code=422, detail="Camera ID must contain letters or numbers.")
    return cleaned


def _process(video_id: str) -> None:
    record = _store.get(video_id)
    if not record:
        return
    _store.update(video_id, status="processing", error=None)
    try:
        events = VisionAgent().process_video_file(record["storage_path"], record["camera_id"], sample_every_n_frames=5)
        _store.update(video_id, status="complete", event_count=len(events), events=events[:200])
    except Exception as exc:
        _store.update(video_id, status="failed", error=str(exc), event_count=0, events=[])


@router.get("")
def list_videos():
    return {"videos": _store.list(), "note": "Events are from OpenCV motion detection; ANPR/model training is not enabled in this prototype."}


@router.get("/{video_id}")
def get_video(video_id: str):
    video = _store.get(video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found.")
    return video


@router.post("/upload", status_code=202)
async def upload_video(background_tasks: BackgroundTasks, file: UploadFile = File(...), camera_id: str = Form(...), include_in_training_dataset: bool = Form(False)):
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in _allowed_extensions:
        raise HTTPException(status_code=415, detail="Use MP4, MOV, AVI, MKV, or WebM video files.")
    camera_id = _camera_id(camera_id)
    video_id = str(uuid4())
    destination = _store.uploads / f"{video_id}{suffix}"
    written = 0
    try:
        with destination.open("wb") as output:
            while chunk := await file.read(1024 * 1024):
                written += len(chunk)
                if written > _max_upload_bytes:
                    output.close()
                    destination.unlink(missing_ok=True)
                    raise HTTPException(status_code=413, detail="Video exceeds the 750 MB prototype limit.")
                output.write(chunk)
        capture = cv2.VideoCapture(str(destination))
        if not capture.isOpened():
            destination.unlink(missing_ok=True)
            raise HTTPException(status_code=422, detail="This file could not be opened as a video.")
        metadata = {"fps": round(capture.get(cv2.CAP_PROP_FPS) or 0, 2), "frame_count": int(capture.get(cv2.CAP_PROP_FRAME_COUNT)), "width": int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)), "height": int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))}
        capture.release()
    finally:
        await file.close()
    now = datetime.now(timezone.utc).isoformat()
    record = {"id": video_id, "original_name": Path(file.filename or "recording").name, "camera_id": camera_id, "storage_path": str(destination), "bytes": written, "created_at": now, "updated_at": now, "status": "queued", "event_count": 0, "events": [], "error": None, "training_dataset": include_in_training_dataset, "metadata": metadata}
    _store.create(record)
    background_tasks.add_task(_process, video_id)
    return {"video": record, "message": "Upload accepted. OpenCV processing has started."}


@router.post("/{video_id}/process", status_code=202)
def process_again(video_id: str, background_tasks: BackgroundTasks):
    if not _store.get(video_id):
        raise HTTPException(status_code=404, detail="Video not found.")
    background_tasks.add_task(_process, video_id)
    return {"message": "Processing queued."}


@router.patch("/{video_id}/training-dataset")
def set_training_dataset(video_id: str, enabled: bool):
    video = _store.update(video_id, training_dataset=enabled)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found.")
    return {"video": video, "note": "This queues footage as a future labelled training dataset; it does not train a model."}
