"""
Neo4j migration runner — executes all .cypher files in order against the configured database.

Usage:
    python run_migrations.py

Each .cypher file is treated as an ordered migration script. Statements are split on ';'
and executed individually so multi-statement files work correctly.
"""

import asyncio
import logging
import re
import sys
from pathlib import Path

# Allow running from any directory
sys.path.insert(0, str(Path(__file__).parents[2]))

from graph.neo4j_client import close_driver, get_driver

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

MIGRATIONS_DIR = Path(__file__).parent


def load_cypher_file(path: Path) -> list[str]:
    """
    Read a .cypher file and split it into individual Cypher statements.

    Splits on ';', strips comments and whitespace, drops empty statements.
    """
    text = path.read_text(encoding="utf-8")

    # Remove single-line comments
    text = re.sub(r"//[^\n]*", "", text)

    statements = [stmt.strip() for stmt in text.split(";")]
    return [s for s in statements if s]


async def run_migration(path: Path) -> bool:
    """
    Execute a single .cypher migration file.

    Returns True on success, False on failure.
    """
    logger.info("Running migration: %s", path.name)
    statements = load_cypher_file(path)

    driver = get_driver()
    success_count = 0
    fail_count = 0

    for i, stmt in enumerate(statements, start=1):
        try:
            async with driver.session(database="neo4j") as session:
                await session.run(stmt)
            success_count += 1
        except Exception as exc:
            logger.error("  Statement %d FAILED: %s\n  Query: %s", i, exc, stmt[:120])
            fail_count += 1

    if fail_count == 0:
        logger.info("  OK — %d statements executed successfully.", success_count)
        return True
    else:
        logger.warning(
            "  PARTIAL — %d succeeded, %d failed.", success_count, fail_count
        )
        return False


async def main() -> None:
    """Discover and execute all migration files in lexicographic order."""
    cypher_files = sorted(MIGRATIONS_DIR.glob("*.cypher"))

    if not cypher_files:
        logger.info("No .cypher migration files found in %s", MIGRATIONS_DIR)
        return

    logger.info("Found %d migration file(s):", len(cypher_files))
    for f in cypher_files:
        logger.info("  %s", f.name)

    all_ok = True
    for migration_path in cypher_files:
        ok = await run_migration(migration_path)
        if not ok:
            all_ok = False

    await close_driver()

    if all_ok:
        logger.info("All migrations completed successfully.")
        sys.exit(0)
    else:
        logger.error("One or more migrations had failures. Check logs above.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
