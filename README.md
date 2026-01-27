# Chains API

A modern Python API built with FastAPI and LangChain.

## Project Structure

```
chains/
├── app/
│   ├── api/              # API routes
│   ├── chains/           # LangChain chains
│   ├── utils/            # Utility functions
│   ├── config.py         # Settings management
│   ├── main.py           # Application entry point
│   └── __init__.py
├── tests/                # Test suite
├── .env.example          # Environment template
├── pyproject.toml        # Poetry configuration
├── .gitignore
└── README.md
```

## Setup

### Prerequisites

- Python 3.11+
- Poetry

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   poetry install
   ```

3. Create `.env` from `.env.example`:
   ```bash
   cp .env.example .env
   ```

4. Add your OpenAI API key to `.env`

## Development

### Running the API

```bash
poetry run uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

**Interactive API docs**: http://localhost:8000/docs

### Running Tests

```bash
poetry run pytest
```

With coverage:
```bash
poetry run pytest --cov=app
```

### Code Quality

**Format code:**
```bash
poetry run black .
```

**Lint code:**
```bash
poetry run ruff check .
```

**Type checking:**
```bash
poetry run mypy app
```

## Adding Dependencies

```bash
poetry add package-name
```

For development dependencies:
```bash
poetry add --group dev package-name
```

## Environment Variables

See `.env.example` for available configuration options.

## API Endpoints

### Health Check
- `GET /health` - Check API status

### API v1
- `GET /api/v1/` - Root endpoint

## Next Steps

1. Add your chains in `app/chains/`
2. Create route handlers in `app/api/router.py`
3. Define request/response models in `app/api/schemas.py`
4. Add integration tests in `tests/`

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LangChain Documentation](https://langchain.readthedocs.io/)
- [Poetry Documentation](https://python-poetry.org/)
