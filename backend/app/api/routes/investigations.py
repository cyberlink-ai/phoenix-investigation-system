from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.agents.evidence_agent import EvidenceFusionEngine
from app.agents.investigation_agent import InvestigationAgent
from app.agents.security_agent import SecurityAgent
from app.core.config import settings
from app.graph.city_graph import CityGraph

router = APIRouter(prefix="/investigations", tags=["investigations"])

# Scaffold-stage shared instances. Real implementation will build the
# CityGraph from Supabase `cameras`/`camera_edges` tables (Phase: Database).
_graph = CityGraph.load_demo_fixture()
_fusion_engine = EvidenceFusionEngine(insufficient_threshold=settings.EVIDENCE_INSUFFICIENT_THRESHOLD)
_investigation_agent = InvestigationAgent(graph=_graph, fusion_engine=_fusion_engine)
_security_agent = SecurityAgent()


class InvestigationRequest(BaseModel):
    case_id: str = Field(..., description="Investigation case identifier")
    last_known_camera: str = Field(..., description="Camera ID the vehicle was last confirmed at")
    elapsed_seconds: float = Field(..., description="Seconds since the last confirmed sighting")
    direction_hint: Optional[str] = None

    plate_match: Optional[float] = Field(None, ge=0, le=1)
    appearance_match: Optional[float] = Field(None, ge=0, le=1)
    color_match: Optional[float] = Field(None, ge=0, le=1)
    direction_match: Optional[float] = Field(None, ge=0, le=1)
    travel_time_match: Optional[float] = Field(None, ge=0, le=1)

    requested_by: str = Field(default="demo_user", description="For audit logging")


@router.post("/recommend")
def recommend_next_action(payload: InvestigationRequest):
    """
    Core endpoint: given a last known camera + whatever evidence signals are
    available (any of which may be missing/None), returns either:
      - a ranked list of candidate next cameras with confidence + reasons, or
      - an explicit "insufficient_evidence" status with what would resolve it.

    This is the live wiring of the Investigation Path Planner + Evidence
    Fusion Engine + Evidence-Insufficient Guard described in
    docs/phoenix_master_prompt.md, Section 3.
    """
    _security_agent.record_access(
        user_identifier=payload.requested_by,
        action="investigation_recommend",
        resource_accessed=f"case:{payload.case_id}",
    )

    result = _investigation_agent.investigate(
        case_id=payload.case_id,
        last_known_camera=payload.last_known_camera,
        elapsed_seconds=payload.elapsed_seconds,
        direction_hint=payload.direction_hint,
        plate_match=payload.plate_match,
        appearance_match=payload.appearance_match,
        color_match=payload.color_match,
        direction_match=payload.direction_match,
        travel_time_match=payload.travel_time_match,
    )

    return {
        "case_id": result.case_id,
        "status": result.status,
        "ranked_cameras": result.ranked_cameras,
        "evidence": result.evidence,
    }
