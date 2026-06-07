# Implementation Guide - Kiwibot AI Report System

## Current Architecture (What's Already Built)

### Core System
| Component | Status | Description |
|-----------|--------|-------------|
| FastAPI Application | ✅ Complete | REST API with CORS, middleware, auth |
| OpenAI GPT Provider | ✅ Complete | GPT-3.5-turbo for report summarization |
| AWS Bedrock Provider | ✅ Complete | Claude via LangChain for report analysis |
| LangGraph Workflow | ✅ Complete | State machine: summarize -> validate -> END |
| Firebase Firestore | ✅ Complete | Ticket storage and user-ticket mapping |
| Firebase Auth | ✅ Complete | JWT token verification via `get_current_user` |
| Geolocation | ✅ Complete | Google Maps + Nominatim reverse geocoding |
| Structured Logging | ✅ Complete | JSON-formatted logs with request tracing |
| Docker + Compose | ✅ Complete | Containerized deployment |
| CI/CD Release | ✅ Complete | GitHub Actions tag-based releases |
| Pydantic v2 Models | ✅ Complete | Type-safe request/response models |
| Request ID Middleware | ✅ Complete | X-Request-ID for distributed tracing |
| Test Suite | ✅ Complete | pytest + mocking for external services |

### API Endpoints
| Method | Route | Function |
|--------|-------|----------|
| GET | `/` | Landing page (HTML template) |
| POST | `/login_user` | Firebase email/password auth |
| POST | `/v1/problem-reports` | AI-powered report processing + ticket creation |
| GET | `/v1/ticket/{id}` | Get ticket by ID |
| PUT | `/v1/ticket/{id}/status` | Update ticket status with reason |
| PUT | `/v1/ticket/{id}/assign` | Assign ticket to agent |

### AI Pipeline Flow
```
User Report (text) 
    │
    ├─► OpenAI GPT-3.5 (gpt.py) ─── Singleton pattern, context-aware
    │       │
    │       └─► Summarize + Classify (hardware/software/field/undefined)
    │
    └─► AWS Bedrock Claude (ai/bedrock.py) ─── LangChain + retry logic
            │
            └─► LangGraph Workflow (ai/workflow.py)
                    │
                    ├─► summarize_node: Bedrock analysis
                    └─► validate_node: Output validation
```

### Tech Stack Details
- **Runtime**: Python 3.11+
- **Framework**: FastAPI with uvicorn/gunicorn
- **AI/LLM**: OpenAI SDK v1+ / LangChain-AWS / LangGraph
- **Database**: Firebase Firestore (NoSQL)
- **Auth**: Firebase Admin SDK
- **Geocoding**: googlemaps + geopy (Nominatim fallback)
- **NLP**: spaCy (en_core_web_sm) for problem type extraction
- **Resilience**: tenacity (exponential backoff retries)
- **Testing**: pytest + pytest-mock + httpx (async)
- **Container**: Docker multi-stage ready

---

## Implementation Phases Completed

### Phase 1: Core API (Done)
- FastAPI setup with proper middleware stack
- Pydantic v2 models for all request/response schemas
- Error handling with custom exceptions
- CORS configuration for frontend integration

### Phase 2: AI Integration (Done)
- OpenAI GPT-3.5 with system prompt engineering (few-shot examples)
- AWS Bedrock Claude via LangChain with structured JSON output
- LangGraph state machine for workflow orchestration
- Retry logic with exponential backoff for API resilience

### Phase 3: Data Layer (Done)
- Firebase Firestore for ticket persistence
- Lazy initialization pattern for Firebase client
- User-ticket relationship mapping
- Ticket lifecycle management (open -> in_progress -> closed)

### Phase 4: DevOps (Done)
- Dockerized application with docker-compose
- GitHub Actions release workflow (tag-triggered)
- Environment variable configuration (.env)
- Structured logging for production observability

---

## Key Design Decisions

1. **Dual AI Provider**: OpenAI + Bedrock provides redundancy and showcases multi-cloud
2. **LangGraph over simple chains**: Demonstrates production-grade AI orchestration
3. **Firebase over SQL**: Real-time capabilities, serverless scaling, auth integration
4. **Singleton GPT instance**: Avoids repeated client initialization, maintains context
5. **spaCy NLP**: Local inference for problem type classification (no API call needed)
6. **Geopy fallback**: Google Maps primary, Nominatim (free) as fallback

---

## How to Extend

### Adding a New AI Provider
1. Create `app/ai/new_provider.py` implementing the provider interface
2. Add configuration in `app/config.py`
3. Register in the workflow or create alternate endpoint

### Adding New Ticket Fields
1. Update `app/models.py` with new Pydantic fields
2. Update Firestore document structure
3. Add migration logic if needed (Firestore is schema-less)

### Adding New Endpoints
1. Add route in `app/main.py` or create a new router
2. Add Pydantic models for request/response
3. Add tests in `tests/`
