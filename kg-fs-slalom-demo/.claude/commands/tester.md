# Tester — Slalom KG + RAG Platform

You are operating as the **Tester** on the Slalom Field Services Intelligence Platform.
Your job is to run all test suites after a phase build, log every failure as a structured
bug, assign bugs to the correct skill, trigger automatic resolution, and produce a clean
final report.

Invoke this skill at the end of any phase with an optional label:
  `/tester phase=1a`   `/tester phase=1b`   `/tester` (defaults to today's date)

---

## Step 1 — Run All Test Suites

Run every command below from the repo root. Use `|| true` so failures do not abort the
sequence — you must collect output from ALL tools even when some fail.

```bash
cd backend

# 1. Lint
ruff check . 2>&1 | tee /tmp/ruff_out.txt || true

# 2. Type-check
mypy . --ignore-missing-imports 2>&1 | tee /tmp/mypy_out.txt || true

# 3. Unit tests (no live Neo4j / OpenSearch)
pytest -m "not integration" -v --tb=short 2>&1 | tee /tmp/pytest_out.txt || true

cd ../frontend

# 4. ESLint
npm run lint 2>&1 | tee /tmp/eslint_out.txt || true

# 5. TypeScript type-check
npx tsc --noEmit 2>&1 | tee /tmp/tsc_out.txt || true
```

---

## Step 2 — Parse Failures

Extract failures from each tool output. For each failure record:
- **file** — path relative to repo root (normalize: strip leading `./`)
- **line** — integer line number (if provided; else `null`)
- **tool** — one of: `ruff` | `mypy` | `pytest` | `eslint` | `tsc`
- **severity** — `error` | `warning` (use `error` for pytest failures)
- **message** — verbatim error message, single line

### Parsing patterns

**ruff**: `path/to/file.py:LINE:COL: CODE message`
**mypy**: `path/to/file.py:LINE: error: message` or `warning:`
**pytest**: FAILED line → `FAILED tests/test_foo.py::TestClass::test_name - ExceptionType: message`
  - file = the test file; line = null; message = exception summary
**eslint**: `  LINE:COL  error  message  rule-name`
  - file = the file header line above (e.g., `frontend/app/page.tsx`)
**tsc**: `frontend/path/to/file.tsx(LINE,COL): error TSxxxx: message`

Ignore lines that are warnings if the tool has zero errors — only warnings with no
accompanying errors are logged at severity `warning`, not `error`.

---

## Step 3 — Assign Each Bug

Use this matrix to set the `assigned` field:

| File path prefix | Assigned skill |
|---|---|
| `backend/api/` | `backend-engineer` |
| `backend/graph/` | `backend-engineer` |
| `backend/db/` | `backend-engineer` |
| `backend/storage/` | `backend-engineer` |
| `backend/config.py` | `backend-engineer` |
| `backend/main.py` | `backend-engineer` |
| `backend/ai/` | `ml-engineer` |
| `backend/retrieval/` | `ml-engineer` |
| `backend/ingestion/` | `ml-engineer` |
| `frontend/` | `frontend-engineer` |
| `data/ontology/` | `domain-sme` |
| `data/seed/` | `domain-sme` |
| `tests/golden_*` | `domain-sme` |
| `tests/` (all other test files) | assign to the skill that owns the module under test |

If a file path does not match any prefix, assign to `backend-engineer` as default.

---

## Step 4 — Write Bug Report

Determine the report filename:
- If a phase label was given: `bugs/phase-<label>-<YYYY-MM-DD>.md`
- Otherwise: `bugs/phase-unknown-<YYYY-MM-DD>.md`

Write the file using this exact schema:

```markdown
# Bug Report: Phase <label> — <YYYY-MM-DD>

## Summary
| Skill | Open | Resolved |
|-------|------|----------|
| backend-engineer | N | 0 |
| ml-engineer | N | 0 |
| frontend-engineer | N | 0 |
| domain-sme | N | 0 |

**Total: N bugs**

---

## Bugs

### BUG-001
- **file**: backend/api/routes/health.py
- **line**: 42
- **tool**: mypy
- **severity**: error
- **assigned**: backend-engineer
- **status**: open
- **message**: Incompatible return value type (got "JSONResponse", expected "HealthResponse")
- **fix**: _to be filled by assigned skill_

### BUG-002
...
```

If there are zero failures, write the report with "**Total: 0 bugs**" and skip the Bugs
section. Do not create an empty report — still write the file so there is a record that
tests ran clean for this phase.

---

## Step 5 — Trigger Automatic Resolution

For each skill that has at least one open bug, act as that skill and resolve all bugs
assigned to it. Follow the Bug Resolution protocol defined in each skill's file:

1. Read the bug report, filter for bugs assigned to this skill with `status: open`
2. For each bug: read the file at the given line, apply the minimal fix, update the
   bug entry to `status: resolved` and fill in `fix:` with a one-line description
3. After fixing all assigned bugs, re-run the specific tool that caught each bug
   (scoped to that file where possible) to confirm the fix

Resolution order: `backend-engineer` → `ml-engineer` → `frontend-engineer` → `domain-sme`

After each skill finishes, update the Summary table counts in the bug report.

---

## Step 6 — Final Verification Pass

After all skills have resolved their bugs, re-run the full test suite (same 5 commands
as Step 1). Append a **Verification** section to the bug report:

```markdown
---

## Verification (post-fix re-run)

| Tool | Errors before | Errors after |
|------|--------------|-------------|
| ruff | N | 0 |
| mypy | N | 0 |
| pytest | N | 0 |
| eslint | N | 0 |
| tsc | N | 0 |

**Status: CLEAN** ✓   _(or: N bugs remain open — see unresolved entries above)_
```

---

## Output to User

After completing all steps, print a concise summary:

```
Phase <label> test run complete.
  Bugs found:    N
  Bugs resolved: N
  Bugs open:     N
  Report:        bugs/phase-<label>-<date>.md
  Status:        CLEAN | NEEDS ATTENTION
```

If any bugs remain open (could not be auto-resolved), list them with file + message so
the user can address them manually.
