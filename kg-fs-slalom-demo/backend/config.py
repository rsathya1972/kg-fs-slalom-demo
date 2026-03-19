"""Application configuration via Pydantic Settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central settings class that reads from .env file."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Anthropic
    anthropic_api_key: str = "sk-ant-placeholder"

    # Neo4j
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_username: str = "neo4j"
    neo4j_password: str = "devpassword"

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
