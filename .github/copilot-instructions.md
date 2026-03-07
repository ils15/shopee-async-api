# GitHub Copilot Instructions — shopee-async-api

## Project Overview
Async Python client for the Shopee Affiliate Open Platform API.
Target: Python 3.8+, `httpx`-based, zero blocking I/O.

---

## Architecture

```
shopee_async_api/
├── client.py          # ShopeeAffiliateClient — main entry point
├── auth.py            # HMAC-SHA256 request signing
├── exceptions.py      # Typed exception hierarchy
└── models/
    ├── base.py        # BaseResponse shared Pydantic model fields
    ├── feeds.py       # Feed product models
    ├── links.py       # Affiliate link generation models
    ├── offers.py      # Offer/product search models
    └── reports.py     # Performance report models
```

---

## Code Conventions

1. **All I/O is async** — never use blocking calls (`requests`, `time.sleep`, open without aiofiles, etc.)
2. **Type hints everywhere** — all functions must be annotated; use `from __future__ import annotations` at module top if needed
3. **Models = Pydantic** — never return raw `dict`; always return a typed Pydantic model from `models/`
4. **Errors** — raise specific exceptions from `exceptions.py`, never bare `except Exception`
5. **No hardcoded credentials** — use env vars or client constructor params
6. **Conventional Commits** — every commit message must follow: `type(scope): description`
   - Valid types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`
   - Example: `feat(links): add bulk affiliate link generation`

---

## Testing Rules

- Test runner: `pytest tests/ --cov=shopee_async_api --cov-fail-under=80`
- **80% minimum coverage** — any PR that drops below 80% must add missing tests
- Tests must be **fully async** (`pytest-asyncio`, `asyncio_mode = "strict"`)
- **No live API calls** — mock all HTTP using `httpx` mock or `pytest-mock`
- Every new public method needs at least one success test and one error test

---

## Branch Strategy

```
develop  ──── day-to-day development
    │
    └── auto PR ──► master ──► CI bump + PyPI publish
```

- Develop on `develop` or feature branches merged into `develop`
- Only `master`-merges trigger PyPI releases
- The auto-PR bot reads the diff and classifies the change type automatically

---

## Semantic Versioning Rules (from commit messages on PR to master)

| Commit prefix       | Version bump |
|---------------------|--------------|
| `BREAKING CHANGE` or `feat!:` | MAJOR |
| `feat:`             | MINOR        |
| `fix:`, `refactor:` | PATCH        |
| `docs:`, `test:`, `chore:` | no publish |

---

## When Generating Code

- Prefer `async with httpx.AsyncClient() as client` patterns
- Reuse `ShopeeAffiliateClient` authenticated request helpers — do not build raw HTTP calls
- When adding a model, add it to `models/__init__.py` re-exports
- When adding a client method, keep signing logic in `auth.py`
- Tests go in `tests/test_<module>.py`

---

## Agent Ecosystem

Agents are defined in `.github/agents/`. Use them in Copilot Chat with `@agent-name`.

| Agent | Role | When to use |
|---|---|---|
| `@zeus` | Orchestrator | Start here for any new feature or epic |
| `@athena` | Planner | Design a feature — produces a TDD plan, never writes code |
| `@hermes` | Backend | Implement Python/async code (endpoints, models, utils) |
| `@iris` | GitHub ops | Open PRs, create releases, manage branches and issues |
| `@temis` | Reviewer | Code review, security check, coverage validation |
| `@apollo` | Discovery | Codebase exploration, docs research |
| `@mnemosyne` | Memory/Docs | Update CHANGELOG, README, memory bank |
| `@hephaestus` | Hotfix | Emergency fixes directly to master |
| `@ra` | Infra/CI | GitHub Actions, Docker, deployment scripts |
| `@maat` | Data/DB | Data models, schema, serialization |

### Release flow with agents

```
# 1. Develop on develop branch (normal push)
#    → auto-pr.yml creates PR develop → master automatically
#    → @iris can also create the PR manually if needed

# 2. To plan a new feature before starting:
@athena plan: <describe the feature>

# 3. To open / update the release PR manually:
@iris create PR from develop to master for release

# 4. To review the PR before merging:
@temis review PR #<number>
```
