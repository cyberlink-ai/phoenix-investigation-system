"""
Centralized configuration for Phoenix backend.
All environment-driven settings live here so no module reads os.environ directly.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ENV: str = "development"

    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # Evidence Fusion / Investigation Path Planner thresholds
    # Below this fused confidence, the system must say "Evidence insufficient"
    # rather than returning a ranked recommendation. See docs/phoenix_master_prompt.md
    # Section 3, "Supporting pillar 2: Evidence-Insufficient Guard".
    EVIDENCE_INSUFFICIENT_THRESHOLD: float = 0.55

    # Above this fused confidence, a recommendation is treated as high-confidence
    # for UI highlighting purposes only (does not change reasoning logic).
    EVIDENCE_HIGH_CONFIDENCE_THRESHOLD: float = 0.80

    @property
    def allowed_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    @property
    def supabase_configured(self) -> bool:
        return bool(self.SUPABASE_URL and self.SUPABASE_KEY)


settings = Settings()
