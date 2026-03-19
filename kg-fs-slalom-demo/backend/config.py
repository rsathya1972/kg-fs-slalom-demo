"""Application configuration via Pydantic Settings."""

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central settings class that reads from .env file."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Anthropic — required; no default so startup fails fast if missing
    anthropic_api_key: str

    # Neo4j
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_username: str = "neo4j"
    neo4j_password: str = "devpassword"  # local dev only — override via .env in all other envs

    @field_validator("anthropic_api_key")
    @classmethod
    def api_key_must_be_real(cls, v: str) -> str:
        if v.startswith("sk-ant-placeholder"):
            raise ValueError("ANTHROPIC_API_KEY is a placeholder — set a real key in .env")
        return v

    # OpenSearch
    opensearch_endpoint: str = "http://localhost:9200"
    opensearch_index: str = "slalom-kg-phase1"

    # SQLite
    database_url: str = "sqlite+aiosqlite:///./kg_slalom.db"

    # Storage
    upload_dir: str = "./storage/uploads"
    output_dir: str = "./storage/outputs"

    # Tenant
    tenant_id: str = "utilities"


# Module-level singleton
settings = Settings()
