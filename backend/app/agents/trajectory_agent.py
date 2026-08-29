"""
Trajectory Agent — STUB. Real implementation pending (build phase: Trajectory Assembly).

Responsibilities when wired in for real:
  - Connect sightings of the same vehicle across cameras into an ordered path
  - Use CityGraph adjacency to decide which cross-camera matches are even
    physically plausible (a vehicle can't jump between non-adjacent cameras
    faster than travel time allows)
  - Estimate possible next locations (delegated to InvestigationAgent /
    CityGraph.rank_next_cameras for the ranking itself)

This agent's real job is vehicle-to-vehicle matching across events (is
MOCK-VEH-001 at CAM-01 the same physical vehicle as an unmatched event at
CAM-03?) — that matching logic is intentionally not built yet since it
depends on real Vision Agent output first.
"""
from __future__ import annotations


class TrajectoryAgent:
    def build_trajectory(self, vehicle_id: str, events: list[dict]) -> dict:
        """
        real implementation: sort events by timestamp, validate camera-to-camera
        adjacency/timing against CityGraph, output an ordered camera_sequence.
        Not implemented yet - depends on real Vision Agent events.
        """
        raise NotImplementedError(
            "TrajectoryAgent.build_trajectory is pending real Vision Agent output."
        )
