"""Async Neo4j driver wrapper — singleton driver with session context manager."""

import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from neo4j import AsyncGraphDatabase, AsyncDriver

from config import settings

logger = logging.getLogger(__name__)

_driver: AsyncDriver | None = None


def get_driver() -> AsyncDriver:
    """
    Return the singleton AsyncNeo4j driver, creating it on first call.

    The driver is thread-safe and should be reused across all requests.
    """
    global _driver
    if _driver is None:
        _driver = AsyncGraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_username, settings.neo4j_password),
            max_connection_lifetime=3600,
            max_connection_pool_size=50,
            connection_acquisition_timeout=30,
        )
        logger.info("Neo4j driver initialized: %s", settings.neo4j_uri)
    return _driver


async def close_driver() -> None:
    """
    Close the singleton driver and release all connections.

    Must be called during application shutdown.
    """
    global _driver
    if _driver is not None:
        await _driver.close()
        _driver = None
        logger.info("Neo4j driver closed.")


@asynccontextmanager
async def get_session(database: str = "neo4j") -> AsyncGenerator:
    """
    Async context manager that yields a Neo4j session.

    Usage:
        async with get_session() as session:
            await session.run(...)
    """
    driver = get_driver()
    async with driver.session(database=database) as session:
        yield session


async def run_query(
    query: str,
    params: dict[str, Any] | None = None,
    database: str = "neo4j",
) -> list[dict[str, Any]]:
    """
    Execute a Cypher query and return all rows as a list of dicts.

    Args:
        query:    Cypher query string.
        params:   Query parameters dict.
        database: Target database name (default: "neo4j").

    Returns:
        List of row dicts, where each dict maps column name → value.
    """
    if params is None:
        params = {}

    async with get_session(database=database) as session:
        result = await session.run(query, params)
        records = await result.data()
        return records
