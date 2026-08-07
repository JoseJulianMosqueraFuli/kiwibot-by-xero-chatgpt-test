# Kiwibot-by-Xero-OpenAi-ChatGPT

A FastAPI + React (Astro) application for managing Kiwibot problem reports. It integrates with OpenAI GPT to analyze robot issue reports, generate tickets, and track their resolution. Fully containerized with Docker Compose and developed test-first (TDD).

## Stack

- **Backend**: FastAPI (Python 3.12)
- **Frontend**: Astro + React (served by nginx)
- **AI/ML**: OpenAI GPT-3.5 / AWS BEDROCK
- **Database**: Firebase Firestore
- **Authentication**: Firebase Auth
- **Geocoding**: Nominatim (OpenStreetMap) with Google Maps fallback
- **NLP**: spaCy
- **Testing**: pytest (backend), Vitest + Testing Library (frontend)
- **Containerization**: Docker, Docker Compose

## Architecture

```
app/                        # FastAPI backend
├── ai/                     # LangGraph/Bedrock code (NOT wired into the running app)
├── config.py               # App configuration (.env via python-dotenv)
├── firebase.py             # Firestore client (lazy init)
├── gpt.py                  # OpenAI provider (singleton, gpt-3.5-turbo) — active AI provider
├── identify.py             # Firebase email/password login
├── main.py                 # FastAPI app and routes (entrypoint)
├── middleware.py           # Request ID middleware
├── models.py               # Pydantic v2 models
├── problem_utils.py        # Geocoding + problem type detection
└── exceptions.py, logging_config.py
frontend/                   # Astro + React UI
├── src/components/         # React components (Login, ReportForm, TicketLookup, StatusUpdate, TicketCard)
├── src/lib/api.ts          # API client
├── src/pages/index.astro   # Single page hosting the React app
├── tests/                  # Vitest tests
├── Dockerfile              # Multi-stage: node build -> nginx
└── nginx.conf              # Serves static build, proxies /v1/* and /login_user to api
tests/                      # pytest backend tests
```

## Getting Started

### Prerequisites

- Docker & Docker Compose
- Node.js 22+ and pnpm (for local frontend development only)
- Python 3.12 (for local backend development only)

### Running with Docker

```bash
docker compose up --build
```

- Frontend: `http://localhost:80`
- API: `http://localhost:8000`

nginx serves the React build and proxies `/v1/*` and `/login_user` to the API container.

### Running tests (TDD)

All verification runs in Docker or locally:

```bash
# Backend
docker compose run --rm test-api
source .venv/bin/activate && pytest tests/ -v   # local

# Frontend
docker compose run --rm test-frontend
cd frontend && pnpm test                        # local
```

Write a failing test first, then implement, then watch it go green.

### Local development

```bash
# Backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend
cd frontend
pnpm install
pnpm dev        # proxies /v1/* and /login_user to http://localhost:8000
```

## Configuration

Create a `.env` file based on `.env.example`:

```env
OPEN_API_KEY=your_openai_api_key
FIREBASE_API_KEY=your_firebase_api_key
SERVICE_ACCOUNT_KEY_FILE=path/to/service-account.json
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
```

> **Gotcha**: the env var is `OPEN_API_KEY` (NOT `OPENAI_API_KEY`), matching `.env.example` and `app/gpt.py`.

Also required at runtime: a Firebase service-account key file and the spaCy model `en_core_web_sm`. Tests mock all external services — no `.env` or network needed to run them.

## API Endpoints

### POST /login_user

Authenticate a user with email and password (form-encoded). Returns the Firebase `idToken` used as Bearer token.

### POST /v1/problem-reports

Submit a problem report and receive a generated ticket. Requires `Authorization: Bearer <idToken>`.

```json
{
  "content": "My Kiwibot is moving slow and the device is hot. The hardware version is a bit old",
  "heartbeat": {
    "bot_id": "abc12435",
    "timestamp": "2023-05-09T12:00:00",
    "location": { "lat": 40.731, "lon": -73.997 },
    "status": "available",
    "battery_level": 80.08,
    "software_version": "v1.0",
    "hardware_version": "v2.0"
  }
}
```

### GET /v1/ticket/{ticket_id}

Retrieve ticket information by ID. The only unauthenticated ticket endpoint.

### PUT /v1/ticket/{ticket_id}/status

Update ticket status with a reason. Requires Bearer token.

```json
{ "new_status": "closed", "reason": "Ticket is finished and reviewed" }
```

### PUT /v1/ticket/{ticket_id}/assign

Assign a ticket to a support agent. Requires Bearer token.

```json
{ "agent_id": "AGENT_ID" }
```

### GET /health

Health check used by the Docker healthcheck.

## Release

Pushing a `v*` tag triggers `.github/workflows/release.yml` to create a GitHub release.

## Author

Built by Jose Julian Mosquera Fuli.
