# PHOENIX — Master Project Prompt (Locked Direction)
### SIH26127 | Bharat Electronics Limited | Smart Automation
### "City-Wide AI Engine for Multi-Camera ANPR, Trajectory Tracking, and Urban Traffic Analytics"

---

## 1. PROJECT IDENTITY

**Team:** Phoenix
**Prototype type:** 100% software. No physical cameras, no edge hardware, no real IoT/GPS hardware.
**Input simulation method:** A small set (3–4) of pre-recorded traffic video files, each file treated as one "camera feed" in the simulated city camera network. Feeds are ingested via `OpenCV VideoCapture` (or similar), not live RTSP streams.
**GPS:** Fully simulated/mocked as authorized demo data — no real device tracking. System must function correctly even with GPS entirely absent.
**Edge computing claims:** Any "edge" or "distributed processing" language must be described honestly as *edge-simulated logic* (a software module that mimics what an edge device would do) — never presented as real deployed edge hardware.

---

## 2. BASELINE (REQUIRED, NOT INNOVATIVE)

These three are explicitly demanded by the SIH problem statement and must exist, but are NOT to be pitched as innovation, since equivalent open-source/commercial solutions already exist:

1. **Multi-camera ANPR** — plate detection + OCR across more than one video feed (commodity: YOLO + OCR pipelines, vendor SDKs like Dahua already do this).
2. **Trajectory tracking** — following a vehicle across feeds over time (commodity: ByteTrack/DeepSORT-style tracking-by-detection).
3. **Urban traffic analytics** — aggregate flow/congestion stats (commodity: mature commercial dashboard category).

These form the *floor* of the prototype, built quickly and cleanly, but never the centerpiece of the pitch.

---

## 3. CHOSEN INNOVATION DIRECTION (THE SPINE OF THE PROJECT)

**Core reframe:** Phoenix is not a monitoring dashboard. It is an **Autonomous Investigation Decision-Support System** that reasons under incomplete evidence and tells an investigator what to check next, why, and how confident to be — updating itself the moment new evidence arrives.

### Primary innovation (spine): Autonomous Investigation Path Planner
- **Problem solved:** When a vehicle disappears from a camera, existing systems only show "last seen here." They don't rank *where to look next* or explain *why*, and they don't revise that ranking as new evidence comes in.
- **Technical approach:** Model the camera/road network as a weighted graph (nodes = cameras, edges = distance / expected travel time / historical flow probability). On each new evidence event, re-run a scored ranking (graph-search style, e.g. modified Dijkstra or belief-propagation over nodes) to output ranked "check here next" recommendations with confidence and stated reasons. Re-planning is triggered automatically whenever new or contradicting evidence arrives.
- **Why it's genuinely different:** No open-source project found implements this specific combination (evidence-triggered, explainable, continuously re-planning investigation search) for vehicle investigation. Academic vehicle re-ID and commercial traffic dashboards exist, but not this decision-support layer.

### Supporting pillar 1: Evidence-Fusion Confidence Engine
- **Problem solved:** Existing systems output a single, unreconciled confidence per detection (e.g. raw OCR confidence). They don't fuse multiple weak signals (plate match, appearance, color, direction, travel-time plausibility) into one calibrated score, and they don't explain *why* confidence rose or fell.
- **Technical approach:** Weighted/rule-based (or lightweight Bayesian) fusion of sub-scores into one final confidence value, paired with a template-driven "reasoning trace" generated directly from the computed sub-scores (not an LLM inventing explanations — a deterministic explanation built from real numbers).
- **Role in system:** Feeds every node/edge score used by the Path Planner above.

### Supporting pillar 2: Evidence-Insufficient Guard (anti-hallucination safety layer)
- **Problem solved:** AI surveillance tools tend to always output *something* confidently, even from weak data — a real risk of false accusation in a policing context.
- **Technical approach:** Hard confidence thresholds tied to the Fusion Engine. Below threshold, the system explicitly returns "Evidence insufficient" plus what additional evidence would resolve it (e.g., "If Camera C09 sights this vehicle within 6 minutes, confidence would reach 80%").
- **Why it matters for judges:** Directly addresses responsible-AI-in-policing concerns; costs little to build; strong credibility signal for a BEL/government evaluation panel.

### Explicitly deprioritized (mention only as "future roadmap," not core build)
- **Vehicle Re-Identification via appearance embeddings** — real research value, but high implementation risk in hackathon time; academic prior art already exists, weakening novelty claims.
- **Adaptive historical-pattern camera prioritization** — closer to existing predictive-traffic-analytics research; hard to fake convincingly live; weaker novelty story.

---

## 4. NOVELTY / PATENT POSTURE (HONEST)

- **What already exists (do not claim as novel):** plate detection+OCR pipelines, vendor camera SDKs extracting plate events, tracking-by-detection algorithms, traffic analytics dashboards, "privacy-aware ANPR" as a labeled OSS category, single-camera edge AI devices.
- **Where a genuine gap may exist:** the specific combination of (a) multi-signal evidence fusion with explainable contradiction detection, (b) graph-based investigation re-planning triggered by new evidence, and (c) an explicit, threshold-based "insufficient evidence" guarantee — combined into one investigator-facing decision-support workflow — was not found as an existing open-source or clearly documented commercial product during research.
- **Framing rule for the team:** present this as "a credible technical novelty gap identified through research," never as "this is patented" or "this is guaranteed patentable." No claim of patentability without a real technical argument.

---

## 5. HARD CONSTRAINTS CARRIED FORWARD INTO ALL FUTURE PHASES

1. Software-only prototype — every phase (architecture, roadmap, team, repo structure, DB, Figma, PPT, demo script) must assume pre-recorded video files as camera input, not live hardware.
2. No fabricated AI output — all agents/modules must reason only over verified, computed evidence (from CV pipeline / database), never invent sightings or confidence numbers.
3. No overclaiming — "edge," "security," "privacy," and "patentability" language must stay technically honest per Sections 1 and 4 above.
4. One dominant differentiator (the Investigation Path Planner + Fusion Engine + Insufficient-Evidence Guard) — do not dilute the pitch by re-introducing the deprioritized ideas as core features.
5. The prototype must actually run end-to-end on the demo video files — real detection, real fusion scoring, real graph re-planning, real database updates — no scripted/fake results.

---

## 6. NEXT STEPS (PENDING — AWAITING "CONTINUE")

- **Phase 5:** Complete technical architecture (Camera/Video Input → Vision Engine → Structured Metadata → Evidence Fusion Engine → Investigation Path Planner/Insufficient-Evidence Guard → Database → Dashboard), scoped to software-only video-file input.
- **Phase 6:** Exact day-by-day build roadmap from zero.
- **Phase 7:** 6-person team structure.
- **Phase 8:** GitHub repository structure.
- **Phase 9:** Supabase/PostgreSQL database design.
- **Phase 10:** Figma screen design.
- **Phase 11:** SIH PPT structure.
- **Phase 12:** Final live demo script (video-file-driven scenes).

---

*This document is the locked reference brief. All future phases should be built strictly consistent with Sections 1–5 above.*
