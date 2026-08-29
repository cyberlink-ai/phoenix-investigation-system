"""
City Camera Graph — core of the Autonomous Investigation Path Planner.

This is the primary innovation described in docs/phoenix_master_prompt.md,
Section 3. Cameras are nodes; road connections are directed, weighted edges.
Given a "last seen at camera X" event plus a direction/appearance signal,
this module returns a RANKED list of candidate next cameras with a numeric
confidence and a human-readable list of reasons — and it is designed to be
re-run every time new evidence arrives (see InvestigationAgent).

This module has NO mock data hardcoded — it operates on whatever graph is
loaded into it (from Supabase in production, or from demo fixtures below
during scaffold/testing). This keeps it honest: it never invents cameras
or edges that were not actually supplied.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import networkx as nx


@dataclass
class CandidateCamera:
    camera_id: str
    confidence: float
    reasons: list[str] = field(default_factory=list)


class CityGraph:
    """Directed, weighted graph of the simulated camera/road network."""

    def __init__(self) -> None:
        self._graph = nx.DiGraph()

    # ------------------------------------------------------------------
    # Graph construction
    # ------------------------------------------------------------------
    def add_camera(self, camera_id: str, **attrs) -> None:
        self._graph.add_node(camera_id, **attrs)

    def add_edge(
        self,
        from_camera: str,
        to_camera: str,
        distance_meters: float,
        expected_travel_seconds: float,
        historical_flow_prob: float = 0.5,
    ) -> None:
        """historical_flow_prob: 0-1, how often vehicles historically take this edge."""
        self._graph.add_edge(
            from_camera,
            to_camera,
            distance_meters=distance_meters,
            expected_travel_seconds=expected_travel_seconds,
            historical_flow_prob=historical_flow_prob,
        )

    def neighbors(self, camera_id: str) -> list[str]:
        if camera_id not in self._graph:
            return []
        return list(self._graph.successors(camera_id))

    def list_cameras(self) -> list[dict]:
        return [{"camera_id": node, **self._graph.nodes[node]} for node in self._graph.nodes]

    # ------------------------------------------------------------------
    # Core reasoning: rank candidate next cameras given partial evidence
    # ------------------------------------------------------------------
    def rank_next_cameras(
        self,
        current_camera: str,
        elapsed_seconds: float,
        direction_hint: Optional[str] = None,
        camera_direction_map: Optional[dict[str, str]] = None,
    ) -> list[CandidateCamera]:
        """
        Returns candidate next cameras ranked by a composite score.

        Score combines three real, explainable signals:
          - historical_flow_prob   (how often vehicles take this route at all)
          - travel_time_plausibility (does elapsed_seconds fit this edge's
            expected_travel_seconds? modeled as a Gaussian-like falloff)
          - direction_match        (does the edge's destination camera match
            the last observed direction of travel, if known?)

        No neural network / LLM guessing here on purpose — this must be
        auditable arithmetic an investigator (and an SIH judge) can verify
        by hand, per the "no black box" requirement in the brief.
        """
        if current_camera not in self._graph:
            return []

        candidates: list[CandidateCamera] = []

        for neighbor in self._graph.successors(current_camera):
            edge = self._graph.edges[current_camera, neighbor]
            reasons: list[str] = []

            flow_prob = edge.get("historical_flow_prob", 0.5)
            reasons.append(f"Historical route usage probability: {flow_prob:.0%}")

            expected_time = edge.get("expected_travel_seconds", 0) or 1
            time_ratio = elapsed_seconds / expected_time if expected_time else 1
            # Plausibility peaks at ratio == 1 (elapsed time matches expectation)
            # and falls off the further elapsed time is from expected time.
            time_plausibility = max(0.0, 1 - abs(1 - time_ratio) * 0.6)
            reasons.append(
                f"Travel time plausibility: elapsed {elapsed_seconds:.0f}s vs "
                f"expected {expected_time:.0f}s ({time_plausibility:.0%} match)"
            )

            direction_score = 0.5  # neutral if no direction data available
            if direction_hint and camera_direction_map:
                neighbor_direction = camera_direction_map.get(neighbor)
                if neighbor_direction:
                    direction_score = 1.0 if neighbor_direction == direction_hint else 0.2
                    reasons.append(
                        f"Direction match: last seen heading {direction_hint}, "
                        f"this route heads {neighbor_direction} "
                        f"({'match' if direction_score == 1.0 else 'mismatch'})"
                    )

            # Weighted composite - weights are explicit and tunable, not hidden.
            confidence = round(
                0.45 * flow_prob + 0.35 * time_plausibility + 0.20 * direction_score, 3
            )

            candidates.append(
                CandidateCamera(camera_id=neighbor, confidence=confidence, reasons=reasons)
            )

        return sorted(candidates, key=lambda c: c.confidence, reverse=True)

    # ------------------------------------------------------------------
    # Demo fixture loader (Phase: scaffold only - replaced by Supabase data later)
    # ------------------------------------------------------------------
    @classmethod
    def load_demo_fixture(cls) -> "CityGraph":
        """
        Builds a small 4-camera demo graph matching the intended live-demo
        scenario in docs/phoenix_master_prompt.md (Phase 12). Used so the API
        and frontend have something real to talk to before Supabase and real
        video files are wired in.
        """
        graph = cls()
        for cam_id, label in [
            ("CAM-01", "MG Road Junction"),
            ("CAM-03", "Tonk Road Crossing"),
            ("CAM-04", "Ajmer Highway Entry"),
            ("CAM-07", "Civil Lines Circle"),
        ]:
            graph.add_camera(cam_id, label=label)

        graph.add_edge("CAM-01", "CAM-03", distance_meters=1800, expected_travel_seconds=180, historical_flow_prob=0.7)
        graph.add_edge("CAM-01", "CAM-04", distance_meters=3200, expected_travel_seconds=300, historical_flow_prob=0.3)
        graph.add_edge("CAM-03", "CAM-04", distance_meters=1500, expected_travel_seconds=150, historical_flow_prob=0.55)
        graph.add_edge("CAM-03", "CAM-07", distance_meters=2100, expected_travel_seconds=210, historical_flow_prob=0.45)
        return graph
