# Technical Context

## Runtime Environment
- **Python**: ≥ 3.8 (tested on 3.12.3)
- **OS**: Linux (also expected to work on macOS/Windows)
- **Async framework**: asyncio standard library

## Dependencies

### Production
| Package | Version | Purpose |
|---------|---------|---------|
| `httpx` | ≥ 0.23.0 | Async HTTP client |
| `pydantic` | ≥ 2.0.0 | Response model validation |
| `python-dotenv` | ≥ 1.0.0 | Load `.env` credentials |

### Development
| Package | Version | Purpose |
|---------|---------|---------|
| `pytest` | ≥ 7.0.0 | Test runner |
| `pytest-asyncio` | ≥ 0.21.0 | Async test support |
| `pytest-cov` | (available) | Coverage reporting |
| `black` | ≥ 23.0.0 | Code formatter |
| `isort` | ≥ 5.12.0 | Import sorting |
| `mypy` | ≥ 1.0.0 | Static type checking |

## Test Configuration
- **pytest mode**: `asyncio_mode = strict` (set in `pyproject.toml`)
- **Coverage**: 98% as of v0.2.0 (25 tests)
- **Run tests**: `python -m pytest tests/ -v`
- **Run with coverage**: `python -m pytest tests/ --cov=shopee_async_api --cov-report=term-missing`

## Known API Limitations
1. `shopeeOfferV2` keyword parameter — the keyword filter returns empty results for this endpoint in most configurations. Use without keyword for browsing platform-wide promotions.  
2. `generateBatchShortLink` and `partnerOrderReport` — require MCN partner level access; return error 10031 for standard accounts.  
3. `getItemFeedData` — responses can be very large (10,000+ rows). Use pagination (`offset`, `limit`) and higher `timeout` values.

## Build & Publish
```bash
# Dev install
pip install -e ".[dev]"

# Run tests
python -m pytest tests/

# Build distribution
python -m build

# Upload to PyPI (future)
twine upload dist/*
```

## Environment Variables (`.env`)
```
SHOPEE_APP_ID=<your_app_id>
SHOPEE_SECRET=<your_secret>
```
See `.env.example` for the template. **Never commit `.env`** — it is in `.gitignore`.
