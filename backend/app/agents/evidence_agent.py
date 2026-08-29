"""
Evidence Agent — the Evidence-Fusion Confidence Engine.

See docs/phoenix_master_prompt.md, Section 3, "Supporting pillar 1".

Takes multiple weak, independently-computed signals (plate match, appearance
match, color match, direction match, travel-time plausibility) and fuses
them into a single calibrated confidence score, together with a deterministic,
template-generated explanation built from the actual numbers — never an LLM
inventing a plausible-sounding justification.
"""
from __future__ import annotations

from dataclasses import dataclass, field


# Explicit, tunable weights. Sum to 1.0. Kept as named constants (not buried
# magic numbers) so the "why 88%?" question always has a traceable answer.
WEIGHTS = {
    "plate_match": 0.30,
    "appearance_match": 0.25,
    "color_match": 0.15,
    "direction_match": 0.15,
    "travel_time_match": 0.15,
}


@dataclass
class FusionResult:
    fused_confidence: float
    sub_scores: dict[str, float]
    reasoning: list[str] = field(default_factory=list)
    sufficient: bool = True


class EvidenceFusionEngine:
    def __init__(self, insufficient_threshold: float = 0.55) -> None:
        self.insufficient_threshold = insufficient_threshold

    def fuse(
        self,
        plate_match: float | None = None,
        appearance_match: float | None = None,
        color_match: float | None = None,
        direction_match: float | None = None,
        travel_time_match: float | None = None,
    ) -> FusionResult:
        """
        Any sub-score can be None if that signal is unavailable (e.g. plate
        unreadable). Missing signals are excluded from the weighted sum and
        their weight is redistributed proportionally across the signals that
        ARE present — this is what lets the system keep reasoning when, e.g.,
        the plate is unclear but appearance + direction + timing still agree.
        """
        raw = {
            "plate_match": plate_match,
            "appearance_match": appearance_match,
            "color_match": color_match,
            "direction_match": direction_match,
            "travel_time_match": travel_time_match,
        }
        present = {k: v for k, v in raw.items() if v is not None}

        if not present:
            return FusionResult(
                fused_confidence=0.0,
                sub_scores={},
                reasoning=["No evidence signals available at all."],
                sufficient=False,
            )

        weight_sum = sum(WEIGHTS[k] for k in present)
        fused = sum(WEIGHTS[k] * v for k, v in present.items()) / weight_sum
        fused = round(fused, 3)

        reasoning = self._build_reasoning(present, raw, fused)
        sufficient = fused >= self.insufficient_threshold

        if not sufficient:
            missing = [k for k, v in raw.items() if v is None]
            gap_note = self._gap_to_threshold_note(present, missing, fused)
            reasoning.append(gap_note)

        return FusionResult(
            fused_confidence=fused,
            sub_scores=present,
            reasoning=reasoning,
            sufficient=sufficient,
        )

    # ------------------------------------------------------------------
    @staticmethod
    def _build_reasoning(present: dict, raw: dict, fused: float) -> list[str]:
        lines = []
        label_map = {
            "plate_match": "Plate match",
            "appearance_match": "Vehicle appearance match",
            "color_match": "Color match",
            "direction_match": "Direction match",
            "travel_time_match": "Travel-time plausibility",
        }
        for key, value in present.items():
            lines.append(f"{label_map[key]}: {value:.0%} (weight {WEIGHTS[key]:.0%})")

        missing = [label_map[k] for k, v in raw.items() if v is None]
        if missing:
            lines.append(f"Unavailable signals (excluded, weight redistributed): {', '.join(missing)}")

        lines.append(f"Final fused confidence: {fused:.0%}")
        return lines

    @staticmethod
    def _gap_to_threshold_note(present: dict, missing: list[str], fused: float) -> str:
        if missing:
            return (
                "Evidence insufficient. Confidence would likely increase if any of the "
                f"following became available: {', '.join(missing)}."
            )
        return (
            "Evidence insufficient even with all available signals considered. "
            "Recommend waiting for a new camera sighting before proceeding."
        )
