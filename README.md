# Trade Confirmation Agent System

An intelligent agentic system for processing, reconciling, and validating trade confirmations from PDF documents.

## 🎯 Overview

This system uses AI agents to automatically:
- Extract trade data from PDF confirmations
- Reconcile extracted data with your trade suite
- Intelligently resolve discrepancies using aliases and semantic understanding
- Validate data against business rules
- Calculate confidence scores
- Auto-process high-confidence confirmations or escalate to human review

## 🏗️ Architecture

The system follows an **agentic architecture** where specialized AI agents work together:

### Agents
1. **Extractor Agent** - Extracts structured data from PDF confirmations using LLM
2. **Reconciler Agent** - Compares extracted data with trade suite and decides resolution strategies
3. **Resolution Agent** - Executes resolution actions (apply aliases, recheck PDFs, flag for review)

### Orchestrator
The **AgenticOrchestrator** coordinates all agents in an intelligent retry loop, allowing agents to learn from previous attempts and progressively resolve issues.

### Validation Layers
1. **Pydantic Model Validation** - Type and format validation
2. **Business Rules Validator** - Organization-specific rules (approved counterparties, thresholds, etc.)
3. **Cross-Field Validator** - Validates relationships between fields

## 📁 Project Structure

```
trade-confirmation-agent/
├── main.py                     # FastAPI application entry point
├── orchestrator.py             # Main orchestration logic
├── agents/                     # AI agents
│   ├── extractor.py           # PDF extraction agent
│   ├── reconciler.py          # Reconciliation agent
│   └── resolver.py            # Resolution agent
├── validators/                 # Validation layers
│   ├── validation_models.py   # Pydantic models and base validation
│   ├── business_rules.py      # Business-specific rules
│   └── cross_field_validator.py  # Cross-field validation
├── models/                     # Data models
│   ├── workflow_state.py      # Workflow state tracking
│   ├── alias_db.py            # Alias database
│   └── schemas.py             # Pydantic schemas
├── api/                        # API layer
│   ├── routes.py              # FastAPI routes
│   └── dependencies.py        # Dependency injection
├── database/                   # Database layer
│   └── db.py                  # SQLAlchemy models
├── utils/                      # Utilities
│   ├── helpers.py             # Helper functions (COMPLETE)
│   └── logging_config.py      # Logging setup (COMPLETE)
└── tests/                      # Test suite
    └── test_validators.py     # Validation tests
```

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- OpenAI API key
- Virtual environment tool (venv, conda, etc.)

### Installation

1. **Clone the repository**
   ```bash
   cd trade-confirmation-agent
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and set:
   ```
   OPENAI_API_KEY=your_actual_api_key_here
   DATABASE_URL=sqlite:///./confirmations.db
   API_HOST=0.0.0.0
   API_PORT=8000
   LARGE_TRADE_THRESHOLD=10000000
   AUTO_PROCESS_CONFIDENCE_THRESHOLD=0.7
   ```

5. **Initialize the database**
   ```bash
   python -c "from database.db import init_db; init_db()"
   ```

### Running the Application

**Development mode** (with auto-reload):
```bash
python main.py
```

**Production mode**:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

The API will be available at:
- Main API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

## 📝 Implementation Guide

The project is scaffolded with clear **TODO markers** for you to implement the core logic. Here's the recommended implementation order:

### Phase 1: Core Utilities (Already Complete ✅)
- `utils/helpers.py` - All helper functions
- `utils/logging_config.py` - Logging setup
- `database/db.py` - Database models
- `main.py` - FastAPI app setup

### Phase 2: Models and State Management
1. **`models/workflow_state.py`** - Implement state tracking methods
2. **`models/alias_db.py`** - Implement alias resolution logic
3. **`models/schemas.py`** - Already complete

### Phase 3: Validation Layers
1. **`validators/validation_models.py`** - Implement Pydantic validators
2. **`validators/business_rules.py`** - Implement business rule checks
3. **`validators/cross_field_validator.py`** - Implement cross-field validations

### Phase 4: AI Agents
1. **`agents/extractor.py`** - Implement PDF extraction with LangChain
   - This is where your existing PDF extraction code goes
   - Focus on getting high-quality, structured extraction
2. **`agents/reconciler.py`** - Implement reconciliation logic
   - Comparison logic
   - Semantic equivalence checking with LLM
   - Decision tree for discrepancy handling
3. **`agents/resolver.py`** - Implement resolution actions
   - Alias application
   - PDF re-extraction
   - Human review task creation

### Phase 5: Orchestration
1. **`orchestrator.py`** - Implement the main agentic loop
   - Coordinate all agents
   - Retry logic
   - Confidence calculation

### Phase 6: API Layer
1. **`api/dependencies.py`** - Implement singleton getters and TradeSuiteDB
2. **`api/routes.py`** - Implement all API endpoints

### Phase 7: Testing
1. **`tests/test_validators.py`** - Implement validation tests
2. Add integration tests

## 🔌 API Endpoints

### Confirmations

#### Upload and Process Confirmation
```http
POST /api/confirmations/process
Content-Type: multipart/form-data

file: [PDF file]
```

Response:
```json
{
  "confirmation_id": "CONF_ABC12345",
  "status": "processing",
  "message": "Processing started"
}
```

#### Get Confirmation Status
```http
GET /api/confirmations/{confirmation_id}
```

Response:
```json
{
  "confirmation_id": "CONF_ABC12345",
  "status": "completed",
  "confidence": 0.92,
  "final_data": {...},
  "validation_issues": [...],
  "agent_history": [...]
}
```

#### List Confirmations
```http
GET /api/confirmations?skip=0&limit=100
```

### Human Review

#### Get Review Queue
```http
GET /api/human-review?status=pending
```

### Aliases

#### Add Alias
```http
POST /api/aliases
{
  "field": "counterparty",
  "from_value": "JPM",
  "to_value": "JP Morgan Chase",
  "counterparty_id": null
}
```

#### Get Aliases for Field
```http
GET /api/aliases/{field}
```

#### Get All Aliases
```http
GET /api/aliases
```

## 🧪 Testing

Run tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=. --cov-report=html
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for LLM calls | Required |
| `DATABASE_URL` | Database connection string | `sqlite:///./confirmations.db` |
| `API_HOST` | API host address | `0.0.0.0` |
| `API_PORT` | API port number | `8000` |
| `LARGE_TRADE_THRESHOLD` | Threshold for large trade warnings | `10000000` |
| `AUTO_PROCESS_CONFIDENCE_THRESHOLD` | Min confidence for auto-processing | `0.7` |

### Customization Points

1. **Business Rules** - Edit `validators/business_rules.py`:
   - Approved counterparties list
   - Valid products list
   - Rate reasonableness ranges

2. **Aliases** - Pre-populated in `models/alias_db.py`:
   - Add more global aliases
   - Customize by your organization's naming conventions

3. **Confidence Calculation** - Adjust in `orchestrator.py`:
   - Penalty weights for retries
   - Penalty weights for validation issues

## 📊 Workflow Example

1. **User uploads PDF** → API returns confirmation ID immediately
2. **Background processing starts**:
   - Extractor extracts trade data
   - Reconciler compares with trade suite
   - Finds discrepancy: "JPM" vs "JP Morgan Chase"
   - Reconciler uses LLM to check semantic equivalence (high confidence)
   - Resolver auto-applies alias and creates pending approval
   - Validation layers run
   - Confidence calculated: 0.92
3. **Result**: Auto-processed (confidence > 0.7 threshold)

Alternative flow with low confidence:
1. Extraction uncertain
2. Reconciler can't resolve discrepancy
3. Resolver flags for human review
4. **Result**: Requires human review (confidence < 0.7)

## 🎯 Key Features

### 1. Intelligent Alias Resolution
- Global aliases (apply to all)
- Counterparty-specific aliases
- Fuzzy matching with similarity scoring
- Semantic equivalence checking with LLM

### 2. Agentic Retry Loop
- Agents can retry up to 3 times
- Each retry has full context of previous attempts
- Progressive problem solving

### 3. Multi-Layer Validation
- Type/format validation (Pydantic)
- Business rules validation
- Cross-field relationship validation

### 4. Confidence Scoring
- Automatic calculation based on:
  - Number of retries
  - Validation issues
  - Agent decision confidence
- Threshold-based auto-processing

### 5. Human-in-the-Loop
- Low-confidence cases escalate to review
- Clear reasoning provided to reviewers
- Manual alias approval workflow

## 🐛 Debugging

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
python main.py
```

Check logs:
```bash
tail -f logs/app.log
```

Database inspection:
```bash
sqlite3 confirmations.db
.tables
SELECT * FROM confirmations;
```

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LangChain Documentation](https://python.langchain.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

## 🤝 Contributing

1. Implement TODOs in order (see Implementation Guide)
2. Write tests for new functionality
3. Update documentation
4. Follow existing code style and patterns

## 📄 License

MIT License

---

**Happy Building! 🚀**

If you have questions about implementing any TODO, check the comments in the code - they provide detailed guidance and hints for each implementation.
