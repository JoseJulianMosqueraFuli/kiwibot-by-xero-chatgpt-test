# Kiwibot-by-Xero-OpenAi-ChatGPT

A Python FastAPI application for managing Kiwibot problem reports. It integrates with AI providers (OpenAI GPT and AWS Bedrock) to analyze robot issue reports, generate tickets, and track their resolution.

## Features

- **Problem Report Processing**: Receive and analyze robot problem reports using AI
- **Ticket Management**: Create, retrieve, update status, and assign tickets
- **Geolocation**: Reverse geocoding to identify problem locations
- **Authentication**: Firebase-based user authentication
- **AI Providers**: Support for OpenAI GPT and AWS Bedrock (Claude)
- **Structured Logging**: JSON-formatted logs for production monitoring
- **Request Tracing**: X-Request-ID middleware for request correlation

## Tech Stack

- **Framework**: FastAPI
- **AI/ML**: OpenAI GPT-3.5, AWS Bedrock (Claude), LangChain, LangGraph
- **Database**: Firebase Firestore
- **Authentication**: Firebase Auth
- **Geocoding**: Google Maps API, Nominatim (OpenStreetMap)
- **NLP**: spaCy
- **Testing**: pytest, pytest-mock, httpx
- **Containerization**: Docker, Docker Compose

## Getting Started

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- OpenAI API key
- Firebase service account credentials
- Google Maps API key (optional, fallback geocoding)
- AWS credentials (optional, for Bedrock)

### Setup

1. Clone the repository:

```bash
git clone git@github.com:JoseJulianMosqueraFuli/kiwibot-by-xero-chatgpt-test.git
cd kiwibot-by-xero-chatgpt-test
```

2. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Create a `.env` file based on `.env.example`:

```env
OPEN_API_KEY=your_openai_api_key
FIREBASE_API_KEY=your_firebase_api_key
SERVICE_ACCOUNT_KEY_FILE=path/to/service-account.json
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
```

4. Create a Firebase service account key file (`service-account.json`):

```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "your-private-key-id",
  "private_key": "-----BEGIN RSA PRIVATE KEY-----\n...",
  "client_email": "firebase-adminsdk-xxxxx@your-project.iam.gserviceaccount.com",
  "client_id": "your-client-id",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/..."
}
```

5. Download the spaCy English model:

```bash
python -m spacy download en_core_web_sm
```

### Running with Docker

```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000`.

### Running Locally

```bash
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Running Tests

```bash
# With virtual environment
source .venv/bin/activate
pytest tests/ -v

# With Docker
docker-compose run --rm fastAPI pytest tests/ -v
```

## API Endpoints

### Authentication

#### POST /login_user

Authenticate a user with email and password.

**Request** (`x-www-form-urlencoded`):
```
email=user@example.com
password=yourpassword
```

**Response**:
```json
{
  "kind": "toolik",
  "localId": "USER_ID",
  "email": "user@example.com",
  "displayName": "kiwi-bot",
  "idToken": "ID_TOKEN",
  "registered": true,
  "refreshToken": "REFRESH_TOKEN",
  "expiresIn": "1200"
}
```

### Problem Reports

#### POST /v1/problem-reports

Submit a problem report and receive a generated ticket.

**Headers**:
```
Authorization: Bearer <idToken>
```

**Request Body**:
```json
{
  "content": "My Kiwibot is moving slow and the device is hot. The hardware version is a bit old",
  "heartbeat": {
    "bot_id": "abc12435",
    "timestamp": "2023-05-09T12:00:00",
    "location": {
      "lat": 40.731,
      "lon": -73.997
    },
    "status": "available",
    "battery_level": 80.08,
    "software_version": "v1.0",
    "hardware_version": "v2.0"
  }
}
```

**Response**:
```json
{
  "ticket_id": "77af15af-4536-435d-bd2d-323c3707e2cf",
  "problem_location": "New York University, Bond Street, Manhattan, New York, 10012, United States",
  "problem_type": "hardware",
  "summary": "The Kiwibot is facing a hardware problem causing reduced speed and overheating. The old hardware version may require component replacement.",
  "bot_id": "abc12435",
  "status": "open",
  "status_changes": [],
  "assigned_agent": null
}
```

### Tickets

#### GET /v1/ticket/{ticket_id}

Retrieve ticket information by ID.

**Response**:
```json
{
  "ticket_id": "95b13970-2819-4684-8ef5-2b8aef8c825c",
  "problem_location": "New York University, Bond Street, Manhattan, New York, 10012, United States",
  "problem_type": "hardware",
  "summary": "The hardware issue with the Kiwibot is related to wheels getting stuck on uneven surfaces.",
  "bot_id": "abc12435",
  "status": "open",
  "status_changes": [],
  "assigned_agent": null
}
```

#### PUT /v1/ticket/{ticket_id}/status

Update ticket status with a reason.

**Headers**:
```
Authorization: Bearer <idToken>
```

**Request Body**:
```json
{
  "new_status": "closed",
  "reason": "Ticket is finished and reviewed"
}
```

**Response**:
```json
{
  "ticket_id": "2575574d-26dd-485c-8a70-80ca42b52f56",
  "problem_location": "New York University, Bond Street, Manhattan, New York, 10012, United States",
  "problem_type": "hardware",
  "summary": "The wheels of the Kiwibot are not moving properly on uneven surfaces.",
  "bot_id": "abc123",
  "status": "closed",
  "status_changes": [
    {
      "timestamp": "2023-05-09T14:34:45.133064+00:00",
      "status": "in progress",
      "reason": "Ticket is being worked on"
    },
    {
      "timestamp": "2023-05-09T20:18:02.314041",
      "status": "closed",
      "reason": "Ticket is finished and reviewed"
    }
  ],
  "assigned_agent": null
}
```

#### PUT /v1/ticket/{ticket_id}/assign

Assign a ticket to a support agent.

**Headers**:
```
Authorization: Bearer <idToken>
```

**Request Body**:
```json
{
  "agent_id": "AGENT_ID"
}
```

**Response**:
```json
{
  "ticket_id": "ab7dd907-14f9-4c4c-a979-f5381c9f52cf",
  "problem_location": "Pecos County, Texas, United States",
  "problem_type": "software",
  "summary": "The Kiwibot has a software problem - no notification received through the app.",
  "bot_id": "Pruebaid1",
  "status": "open",
  "status_changes": [],
  "assigned_agent": "AGENT_ID"
}
```

## Architecture

```
app/
├── ai/                    # AI provider implementations
│   ├── bedrock.py         # AWS Bedrock (Claude) provider
│   ├── prompts.py         # LangChain prompt templates
│   ├── provider.py        # Abstract AI provider interface
│   └── workflow.py        # LangGraph workflow for report processing
├── templates/             # Jinja2 HTML templates
├── config.py              # Application configuration
├── exceptions.py          # Custom exception classes
├── firebase.py            # Firebase Firestore client (lazy init)
├── gpt.py                 # OpenAI GPT provider
├── identify.py            # Firebase authentication helper
├── logging_config.py      # Structured JSON logging
├── main.py                # FastAPI application and routes
├── middleware.py          # Request ID middleware
├── models.py              # Pydantic data models
└── problem_utils.py       # Geocoding and problem type detection
```

## Improvements Made

- **Pydantic v2 Compatibility**: Updated deprecated `constr`, `confloat`, and `.dict()` to modern equivalents
- **OpenAI API v1**: Migrated from legacy `openai.ChatCompletion` to `openai.ChatCompletions` client
- **Authentication Middleware**: Extracted duplicated auth logic into reusable `get_current_user` dependency
- **Structured Logging**: Replaced `print()` statements with proper JSON-formatted logging
- **Lazy Initialization**: Firebase and geocoder clients now initialize on-demand
- **Request ID Middleware**: Added `X-Request-ID` header for request tracing
- **Test Coverage**: Fixed test endpoints and added proper mocking for external services

## Author

Built by Jose Julian Mosquera Fuli.
