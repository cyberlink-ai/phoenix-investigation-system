"""
Investigation Agent — orchestrates CityGraph (Path Planner) + EvidenceFusionEngine,
and enforces the Evidence-Insufficient Guard (docs/phoenix_master_prompt.md,
Section 3, "Supporting pillar 2").

This is the module the /investigations API route calls. It never fabricates
a recommendation: if fused confidence is below threshold, it explicitly
returns "insufficient evidence" plus what would resolve it, instead of
forcing a ranked answer.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from app.agents.evidence_agent import EvidenceFusionEngine, FusionResult
from app.graph.city_graph import CandidateCamera, CityGraph


@dataclass
class InvestigationRecommendation:
    case_id: str
    status: str  # "recommendation" | "insufficient_evidence"
    ranked_cameras: list[dict] = field(default_factory=list)
    evidence: Optional[dict] = None


class InvestigationAgent:
    def __init__(self, graph: CityGraph, fusion_engine: EvidenceFusionEngine) -> None:
        self.graph = graph
        self.fusion_engine = fusion_engine

    def investigate(
        self,
        case_id: str,
        last_known_camera: str,
        elapsed_seconds: float,
        direction_hint: Optional[str] = None,
        camera_direction_map: Optional[dict[str, str]] = None,
        plate_match: Optional[float] = None,
        appearance_match: Optional[float] = None,
        color_match: Optional[float] = None,
        direction_match: Optional[float] = None,
        travel_time_match: Optional[float] = None,
    ) -> InvestigationRecommendation:
        fusion: FusionResult = self.fusion_engine.fuse(
            plate_match=plate_match,
            appearance_match=appearance_match,
            color_match=color_match,
            direction_match=direction_match,
            travel_time_match=travel_time_match,
        )

        evidence_payload = {
            "fused_confidence": fusion.fused_confidence,
            "sub_scores": fusion.sub_scores,
            "reasoning": fusion.reasoning,
        }

        if not fusion.sufficient:
            return InvestigationRecommendation(
                case_id=case_id,
                status="insufficient_evidence",
                ranked_cameras=[],
                evidence=evidence_payload,
            )

        candidates: list[CandidateCamera] = self.graph.rank_next_cameras(
            current_camera=last_known_camera,
            elapsed_seconds=elapsed_seconds,
            direction_hint=direction_hint,
            camera_direction_map=camera_direction_map,
        )

        ranked = [
            {
                "rank": i + 1,
                "camera_id": c.camera_id,
                "confidence": c.confidence,
                "reasons": c.reasons,
            }
            for i, c in enumerate(candidates)
        ]

        return InvestigationRecommendation(
            case_id=case_id,
            status="recommendation",
            ranked_cameras=ranked,
            evidence=evidence_payload,
        )
