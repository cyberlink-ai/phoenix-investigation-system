from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.agents.evidence_agent import EvidenceFusionEngine
from app.core.config import settings

router = APIRouter(prefix="/evidence", tags=["evidence"])

_fusion_engine = EvidenceFusionEngine(insufficient_threshold=settings.EVIDENCE_INSUFFICIENT_THRESHOLD)


class FuseRequest(BaseModel):
    plate_match: Optional[float] = Field(None, ge=0, le=1)
    appearance_match: Optional[float] = Field(None, ge=0, le=1)
    color_match: Optional[float] = Field(None, ge=0, le=1)
    direction_match: Optional[float] = Field(None, ge=0, le=1)
    travel_time_match: Optional[float] = Field(None, ge=0, le=1)


@router.post("/fuse")
def fuse_evidence(payload: FuseRequest):
    """Standalone access to the Evidence Fusion Engine - useful for building
    and testing the frontend's confidence-explanation UI independent of a
    full investigation flow."""
    result = _fusion_engine.fuse(**payload.model_dump())
    return {
        "fused_confidence": result.fused_confidence,
        "sub_scores": result.sub_scores,
        "reasoning": result.reasoning,
        "sufficient": result.sufficient,
    }
