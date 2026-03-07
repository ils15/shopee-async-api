# Contributing to Shopee Async API

First off, thank you for considering contributing to `shopee-async-api`. This library was heavily inspired by standard asynchronous python patterns and aims to be the most performant and easy-to-use Shopee toolkit available.

## Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ils15/shopee-async-api.git
   cd shopee-async-api
   ```

2. **Set up a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. **Install development dependencies:**
   ```bash
   pip install -e ".[dev]"
   ```

## Testing

We use `pytest` for all tests. Since `shopee-async-api` communicates with external servers, we rely heavily on `unittest.mock.AsyncMock` to validate our client state.

To run the test suite:
```bash
pytest tests/
```

### Adding New Tests
If you add a new endpoint, please ensure:
1. You mock the `httpx.AsyncClient.post` GraphQL response gracefully.
2. Your test uses the `@pytest.mark.asyncio` decorator.

## Submitting Pull Requests

1. Fork the repository and create your branch from `develop`.
2. Format your code using `black` and `isort`.
3. Ensure all tests pass (`pytest`).
4. Type hint any new functions.
5. Create a comprehensive PR explaining the change, with links to the corresponding GraphQL specification if relevant.
