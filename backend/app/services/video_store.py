"""Small local persistence layer for uploaded demo videos."""
from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class VideoStore:
    """Stores processing metadata without requiring a database service."""
    def __init__(self, root: Path) -> None:
        self.root = root
        self.uploads = root / "uploads"
        self.index_path = root / "videos.json"
        self._lock = threading.Lock()
        self.uploads.mkdir(parents=True, exist_ok=True)

    def _read(self) -> dict[str, Any]:
        if not self.index_path.exists():
            return {}
        return json.loads(self.index_path.read_text(encoding="utf-8"))

    def _write(self, videos: dict[str, Any]) -> None:
        temporary = self.index_path.with_suffix(".tmp")
        temporary.write_text(json.dumps(videos, indent=2), encoding="utf-8")
        temporary.replace(self.index_path)

    def create(self, video: dict[str, Any]) -> None:
        with self._lock:
            videos = self._read()
            videos[video["id"]] = video
            self._write(videos)

    def get(self, video_id: str) -> dict[str, Any] | None:
        with self._lock:
            return self._read().get(video_id)

    def update(self, video_id: str, **values: Any) -> dict[str, Any] | None:
        with self._lock:
            videos = self._read()
            video = videos.get(video_id)
            if video is None:
                return None
            video.update(values)
            video["updated_at"] = datetime.now(timezone.utc).isoformat()
            self._write(videos)
            return video

    def list(self) -> list[dict[str, Any]]:
        with self._lock:
            return sorted(self._read().values(), key=lambda item: item["created_at"], reverse=True)
