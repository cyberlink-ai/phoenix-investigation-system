from fastapi import APIRouter

from app.graph.city_graph import CityGraph

router = APIRouter(prefix="/cameras", tags=["cameras"])

# Scaffold-stage: served from the demo fixture graph until Supabase is wired
# in (Phase: Database). Real implementation will query the `cameras` table.
_graph = CityGraph.load_demo_fixture()


@router.get("")
def list_cameras():
    return {"source": "demo_fixture", "cameras": _graph.list_cameras()}


@router.get("/{camera_id}/neighbors")
def get_camera_neighbors(camera_id: str):
    return {"camera_id": camera_id, "neighbors": _graph.neighbors(camera_id)}
