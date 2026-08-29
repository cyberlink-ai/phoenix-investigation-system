-- ============================================================================
-- PHOENIX DATABASE SCHEMA (Postgres / Supabase)
-- Improved from the original draft in docs/phoenix_master_prompt.md
-- Changes made and why:
--   1. Proper UUID/serial primary keys + explicit foreign keys (original draft
--      had bare id columns with no declared relationships).
--   2. Added CAMERA_EDGES table - the original schema had no way to represent
--      the city/camera graph (nodes+edges) that the Investigation Path Planner
--      depends on. "connected_cameras" as a text/array field on CAMERAS is not
--      queryable or weighted, so it's replaced with a real edge table.
--   3. Added EVIDENCE_SCORES table - the original schema stored only a final
--      plate_confidence per event, with nowhere to persist the individual
--      sub-scores (appearance, color, direction, travel-time) that the
--      Evidence Fusion Engine combines. Without this table the "explain why"
--      requirement (Section 3, Supporting Pillar 1) has no data to draw from.
--   4. INVESTIGATION_CASES.status constrained to an explicit enum-like check.
--   5. Added indexes on the columns the Path Planner and dashboard will query
--      most often (camera_id, vehicle_id, timestamp, case_id).
-- ============================================================================

-- Enable UUID generation (Supabase has this available by default)
create extension if not exists "pgcrypto";

-- ----------------------------------------------------------------------------
-- CAMERAS: one row per simulated camera (in the prototype, one row per video file)
-- ----------------------------------------------------------------------------
create table if not exists cameras (
    camera_id       text primary key,             -- e.g. 'CAM-01'
    label           text not null,                 -- human-readable name, e.g. 'MG Road Junction'
    latitude        double precision,
    longitude       double precision,
    video_source    text,                          -- path/filename of the demo video file this camera simulates
    created_at      timestamptz not null default now()
);

-- ----------------------------------------------------------------------------
-- CAMERA_EDGES: the city/camera graph used by the Investigation Path Planner.
-- Directed edges so travel-time/flow can differ by direction.
-- ----------------------------------------------------------------------------
create table if not exists camera_edges (
    edge_id                 uuid primary key default gen_random_uuid(),
    from_camera_id          text not null references cameras(camera_id) on delete cascade,
    to_camera_id            text not null references cameras(camera_id) on delete cascade,
    distance_meters         double precision,
    expected_travel_seconds double precision,
    historical_flow_prob    double precision check (historical_flow_prob between 0 and 1),
    unique (from_camera_id, to_camera_id)
);

create index if not exists idx_camera_edges_from on camera_edges(from_camera_id);

-- ----------------------------------------------------------------------------
-- VEHICLE_EVENTS: one row per detection event produced by the Vision Agent
-- ----------------------------------------------------------------------------
create table if not exists vehicle_events (
    event_id            uuid primary key default gen_random_uuid(),
    vehicle_id          text,                       -- nullable: may be unknown until matched
    camera_id           text not null references cameras(camera_id) on delete cascade,
    event_timestamp     timestamptz not null default now(),
    plate_text          text,
    plate_confidence    double precision check (plate_confidence between 0 and 1),
    vehicle_type        text,                       -- car, motorcycle, truck, bus...
    color               text,
    direction           text,                       -- compass or relative direction of travel
    created_at          timestamptz not null default now()
);

create index if not exists idx_vehicle_events_camera on vehicle_events(camera_id);
create index if not exists idx_vehicle_events_vehicle on vehicle_events(vehicle_id);
create index if not exists idx_vehicle_events_timestamp on vehicle_events(event_timestamp);

-- ----------------------------------------------------------------------------
-- EVIDENCE_SCORES: sub-scores computed by the Evidence Fusion Engine for a
-- given event, tied to an investigation case. This is what makes the
-- "explain why confidence is X%" requirement possible.
-- ----------------------------------------------------------------------------
create table if not exists evidence_scores (
    score_id                uuid primary key default gen_random_uuid(),
    case_id                 uuid not null,          -- references investigation_cases(case_id)
    event_id                uuid not null references vehicle_events(event_id) on delete cascade,
    plate_match_score       double precision check (plate_match_score between 0 and 1),
    appearance_match_score  double precision check (appearance_match_score between 0 and 1),
    color_match_score       double precision check (color_match_score between 0 and 1),
    direction_match_score   double precision check (direction_match_score between 0 and 1),
    travel_time_match_score double precision check (travel_time_match_score between 0 and 1),
    fused_confidence        double precision check (fused_confidence between 0 and 1),
    reasoning               jsonb,                  -- structured, template-generated explanation
    created_at              timestamptz not null default now()
);

create index if not exists idx_evidence_scores_case on evidence_scores(case_id);

-- ----------------------------------------------------------------------------
-- TRAJECTORIES: assembled multi-camera path for a vehicle
-- ----------------------------------------------------------------------------
create table if not exists trajectories (
    trajectory_id   uuid primary key default gen_random_uuid(),
    vehicle_id      text not null,
    camera_sequence text[] not null default '{}',  -- ordered array of camera_ids
    timestamps      timestamptz[] not null default '{}',
    confidence      double precision check (confidence between 0 and 1),
    updated_at      timestamptz not null default now()
);

create index if not exists idx_trajectories_vehicle on trajectories(vehicle_id);

-- ----------------------------------------------------------------------------
-- INVESTIGATION_CASES: one row per active/closed investigation
-- ----------------------------------------------------------------------------
create table if not exists investigation_cases (
    case_id             uuid primary key default gen_random_uuid(),
    vehicle_description text,
    plate_query         text,                        -- partial/unclear plate as entered by investigator
    last_known_camera   text references cameras(camera_id),
    last_known_time     timestamptz,
    status              text not null default 'open'
                        check (status in ('open', 'insufficient_evidence', 'resolved', 'closed')),
    created_at          timestamptz not null default now(),
    updated_at          timestamptz not null default now()
);

alter table evidence_scores
    add constraint fk_evidence_scores_case
    foreign key (case_id) references investigation_cases(case_id) on delete cascade;

-- ----------------------------------------------------------------------------
-- AGENT_DECISIONS: every recommendation the Investigation Path Planner makes,
-- kept as an immutable log so re-planning history is auditable and explainable.
-- ----------------------------------------------------------------------------
create table if not exists agent_decisions (
    decision_id         uuid primary key default gen_random_uuid(),
    case_id             uuid not null references investigation_cases(case_id) on delete cascade,
    recommended_camera  text references cameras(camera_id),
    rank                int,                          -- 1 = top priority recommendation
    confidence          double precision check (confidence between 0 and 1),
    reasoning           jsonb,
    triggered_by_event  uuid references vehicle_events(event_id),
    created_at          timestamptz not null default now()
);

create index if not exists idx_agent_decisions_case on agent_decisions(case_id);

-- ----------------------------------------------------------------------------
-- AUDIT_LOGS: access/action log for the Security & Privacy Agent
-- ----------------------------------------------------------------------------
create table if not exists audit_logs (
    log_id            uuid primary key default gen_random_uuid(),
    user_identifier   text not null,
    action            text not null,
    resource_accessed text,
    "timestamp"       timestamptz not null default now()
);

create index if not exists idx_audit_logs_timestamp on audit_logs("timestamp");
