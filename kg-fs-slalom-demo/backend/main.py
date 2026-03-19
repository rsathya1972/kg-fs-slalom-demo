"""FastAPI application entry point for the Slalom Field Services Intelligence Platform."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from db.database import create_db_and_tables
from graph.neo4j_client import close_driver, get_driver
from storage.file_manager import ensure_dirs

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Startup and shutdown lifecycle management."""
    logger.info("Starting Slalom Field Services Intelligence Platform...")

    # Ensure storage directories exist
    ensure_dirs()

    # Create SQLite tables
    await create_db_and_tables()

    # Test Neo4j connectivity
    try:
        driver = get_driver()
        async with driver.session(database="neo4j") as session:
            await session.run("RETURN 1")
        logger.info("Neo4j connectivity: OK (bolt://%s)", settings.neo4j_uri)
    except Exception as exc:
        logger.warning("Neo4j connectivity check failed: %s", exc)

    # Test OpenSearch connectivity
    try:
        from opensearchpy import AsyncOpenSearch
        os_client = AsyncOpenSearch(hosts=[settings.opensearch_endpoint])
        info = await os_client.cluster.health()
        logger.info("OpenSearch connectivity: OK — cluster status: %s", info.get("status"))
        await os_client.close()
    except Exception as exc:
        logger.warning("OpenSearch connectivity check failed: %s", exc)

    logger.info("Platform ready.")
    yield

    # Shutdown
    await close_driver()
    logger.info("Platform shut down.")


app = FastAPI(
    title="Slalom Field Services Intelligence Platform",
    description="Knowledge Graph + RAG API for utility FSM consulting intelligence",
    version="1.0.0-phase1a",
    lifespan=lifespan,
)

# Allow all origins for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
from api.routes.health import router as health_router
from api.routes.ingest import router as ingest_router
from api.routes.graph import router as graph_router
from api.routes.query import router as query_router
from api.routes.review import router as review_router
from api.routes.feedback import router as feedback_router

app.include_router(health_router, prefix="/api")
app.include_router(ingest_router, prefix="/api")
app.include_router(graph_router, prefix="/api")
app.include_router(query_router, prefix="/api")
app.include_router(review_router, prefix="/api")
app.include_router(feedback_router, prefix="/api")


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint — redirects users to /docs."""
    return {"message": "Slalom Field Services Intelligence Platform. See /docs for API reference."}
