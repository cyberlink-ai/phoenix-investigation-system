# Phoenix — Autonomous Investigation Decision-Support System
### SIH26127 · Bharat Electronics Limited · Smart Automation

Full project brief and locked innovation direction: [`docs/phoenix_master_prompt.md`](docs/phoenix_master_prompt.md)

## What this is

Not a camera-monitoring dashboard. Phoenix reasons over incomplete evidence
(a partially unclear plate, a vehicle that disappeared from one camera) and
recommends **what to check next, why, and how confident to be** — updating
itself automatically as new evidence arrives.

Three real, working pieces power this (see `backend/README.md` for details):
1. **Evidence Fusion Engine** — fuses multiple weak signals into one explainable confidence score
2. **Investigation Path Planner** — ranks candidate next cameras using a real weighted graph, not a black box
3. **Evidence-Insufficient Guard** — explicitly refuses to guess when confidence is too low

## Project structure

```
phoenix/
├── backend/          FastAPI service — the reasoning engine (see backend/README.md)
├── frontend/          React + Vite dashboard (see frontend/README.md)
├── data/sample_videos/  Drop demo traffic video files here (gitignored - too large for git)
└── docs/              Locked project brief and architecture notes
```

## Deployment topology (why it's split this way)

| Piece | Where | Why |
|---|---|---|
| Frontend (React) | **Vercel** | Static/SPA hosting, exactly what Vercel is built for. Reachable from phone/laptop/any device via one URL, as requested. |
| Backend (FastAPI + eventually YOLO/OpenCV) | **Render / Railway / Fly.io** | Needs persistent, long-running compute. Vercel serverless functions can't run YOLO/OpenCV reliably (execution-time limits, no GPU, large package sizes). |
| Database | **Supabase (Postgres)** | Already planned in the brief; works fine from either host. |

The frontend talks to the backend over a plain HTTPS API call
(`VITE_API_BASE_URL`) — there's no tight coupling that requires them to be
on the same platform.

## Current build status

| Component | Status |
|---|---|
| Backend scaffold (FastAPI, routing, config) | ✅ Built and tested |
| Evidence Fusion Engine | ✅ Built and tested (real logic, no mock math) |
| Investigation Path Planner (graph) | ✅ Built and tested (real logic, demo fixture graph) |
| Insufficient-Evidence Guard | ✅ Built and tested |
| Vision Agent — video ingestion + motion detection | ✅ Built and tested against a generated synthetic video. Real OpenCV frame reads + background-subtraction detection, not mocked. |
| Vision Agent — vehicle classification + ANPR | ⏳ Placeholder (`vehicle_type: "unknown"`, `plate_text: null`) — needs YOLO + OCR, deferred until real footage justifies the PyTorch download |
| Trajectory Agent (cross-camera matching) | ⏳ Stub only — pending multiple real/labeled camera feeds |
| Supabase database | ⏳ Schema designed (`backend/app/db/schema.sql`), not yet provisioned |
| Frontend dashboard | ✅ Functional scaffold, hits real backend endpoints. Design pass pending. |
| Deployment (Vercel + Render/Railway) | ⏳ Not yet deployed |

## Testing the real video pipeline

A synthetic placeholder video is already in `data/sample_videos/` (regenerate
anytime with `python3 backend/scripts/generate_synthetic_video.py`). It's
**not real footage** — two colored rectangles moving across a plain
background — but it exercises real code: real frame reads, real
background-subtraction motion detection, real bounding boxes.

```bash
curl "http://localhost:8000/vehicles/events/from-video?camera_id=CAM-01&max_events=5"
```

Drop a real traffic video into `data/sample_videos/` and pass its filename
as `?filename=...` to run the same real pipeline against it — no code change
needed.

## Quick start (local)

```bash
# Terminal 1 — backend
cd backend
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000

# Terminal 2 — frontend
cd frontend
npm install
cp .env.example .env
npm run dev
```

Open `http://localhost:5173`.

## Uploading your own videos

The dashboard now accepts MP4, MOV, AVI, MKV, and WebM clips (up to 750 MB)
as simulated camera feeds. Choose a camera ID, upload a recorded clip, and
the backend will read its real frames with OpenCV in a background task.
The feed library refreshes automatically with the real frame metadata and
motion-event count. In a browser served over HTTPS (including Vercel), the
**Record here** button can also create and upload a WebM recording.

Files are stored locally under `data/runtime/`, which is intentionally ignored
by Git. This makes the local prototype self-contained; use object storage and
Supabase/Postgres before a shared or production deployment.

### Important honesty boundary

The current runnable pipeline performs **real OpenCV motion detection** and
rough colour/direction estimation. It does not yet perform ANPR/OCR, vehicle
identity matching, or automatic ML training. Marking a video as a "training
dataset" only retains it for a later labelled-dataset workflow; no model is
silently trained from unlabelled footage.

## Deploying the prototype

Deploy `frontend/` to Vercel and deploy `backend/` to Render, Railway, or
Fly.io. Set `VITE_API_BASE_URL` in Vercel to the HTTPS URL of the deployed
backend, and set `ALLOWED_ORIGINS` on the backend to your exact Vercel URL.
The frontend cannot perform long-running OpenCV processing by itself, so it
must remain paired with the backend service.
