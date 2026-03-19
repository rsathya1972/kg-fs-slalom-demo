# bugs/

Phase-scoped bug reports written by the `/tester` skill after each phase build.

## Naming convention

`phase-<label>-<YYYY-MM-DD>.md`

Examples:
- `phase-1a-2026-03-19.md`
- `phase-1b-2026-03-25.md`
- `phase-1c-2026-04-02.md`

## Bug statuses

| Status | Meaning |
|--------|---------|
| `open` | Not yet fixed |
| `resolved` | Fixed by the assigned skill; fix description recorded |
| `wontfix` | Explicitly deferred — add a `reason:` line below the status |

## Assignment matrix

| File path prefix | Assigned skill |
|---|---|
| `backend/api/`, `backend/graph/`, `backend/db/`, `backend/storage/`, `backend/config.py`, `backend/main.py` | `backend-engineer` |
| `backend/ai/`, `backend/retrieval/`, `backend/ingestion/` | `ml-engineer` |
| `frontend/` | `frontend-engineer` |
| `data/ontology/`, `data/seed/`, `tests/golden_*` | `domain-sme` |

## Workflow

1. `/tester phase=<label>` runs all test suites (ruff, mypy, pytest, eslint, tsc)
2. Failures are parsed and written to a bug report in this directory
3. Each assigned skill automatically resolves its bugs and marks them `resolved`
4. A final verification re-run confirms the fix
5. The report is updated with before/after error counts

## Reading a report

Reports are Markdown. Open any `.md` file in this directory to see:
- Summary table (skill → open/resolved counts)
- Individual bug entries with file, line, tool, message, and fix
- Verification section with before/after error counts per tool
