# Phoenix Backend

FastAPI service implementing:
- **Evidence Fusion Engine** (`app/agents/evidence_agent.py`) — real, working
- **Investigation Path Planner** (`app/graph/city_graph.py`) — real, working
- **Investigation Agent orchestrator + Insufficient-Evidence Guard** (`app/agents/investigation_agent.py`) — real, working
- **Vision / Trajectory Agents** — stubs, pending real video wiring (see files for exact contract)
- **Security Agent** — real basic audit logging, pending anomaly detection

## Run locally

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate   # optional but recommended
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

Visit `http://localhost:8000/docs` for interactive API docs (Swagger UI).

## Verify it's working

```bash
curl http://localhost:8000/health
curl http://localhost:8000/cameras
curl -X POST http://localhost:8000/investigations/recommend \
  -H "Content-Type: application/json" \
  -d '{"case_id":"TEST-1","last_known_camera":"CAM-01","elapsed_seconds":170,
       "direction_hint":"north","plate_match":0.75,"appearance_match":0.9,
       "color_match":0.85,"direction_match":0.9,"travel_time_match":0.8}'
```

## Deployment — important

**Do not deploy this backend to Vercel.** Vercel's serverless functions have
execution-time limits, no GPU, and don't handle large ML packages
(ultralytics/torch/easyocr) well. Once real video/YOLO processing is wired
in, this backend needs a host with persistent, long-running compute.

Recommended options (any work fine for an SIH demo):
- **Render** — free/low-cost web service, supports the included `Dockerfile`
- **Railway** — similarly simple, good free tier for hackathons
- **Fly.io** — good if you want more control over region/resources

The React frontend (deployed separately on Vercel) just needs
`VITE_API_BASE_URL` pointed at wherever this backend ends up running.

## Not yet wired in (see file-level docstrings for exact contracts)
- Real YOLO detection / ANPR OCR / ByteTrack tracking (`app/agents/vision_agent.py`)
- Cross-camera trajectory matching (`app/agents/trajectory_agent.py`)
- Supabase persistence (currently falls back to demo fixture data — see `app/db/supabase_client.py`)
