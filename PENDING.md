# Pending Improvements - Kiwibot AI Report System

## Priority Matrix

| Priority | Feature | Effort | Impact for Portfolio |
|----------|---------|--------|---------------------|
| P0 | RAG System Integration | High | ⭐⭐⭐⭐⭐ |
| P0 | Vector Database (OpenSearch/Pinecone) | High | ⭐⭐⭐⭐⭐ |
| P1 | Fine-tuning Pipeline | Medium | ⭐⭐⭐⭐ |
| P1 | Multi-model Routing & Evaluation | Medium | ⭐⭐⭐⭐ |
| P2 | Real-time Streaming Responses | Low | ⭐⭐⭐ |
| P2 | Conversation Memory (Redis) | Medium | ⭐⭐⭐ |
| P3 | Admin Dashboard (React) | High | ⭐⭐⭐ |
| P3 | WebSocket Notifications | Medium | ⭐⭐ |

---

## P0: Critical for IA Generativa Electiva

### 1. RAG (Retrieval Augmented Generation) System
**Why**: Demonstrates production-grade GenAI beyond basic API calls.

**Target Architecture**:
```
┌──────────────────────────────────────────────────────────────┐
│                    RAG PIPELINE                                │
│                                                               │
│  [Kiwibot Manuals]    [Past Tickets]    [Knowledge Base]      │
│        │                    │                  │               │
│        └────────────────────┼──────────────────┘               │
│                             ▼                                  │
│                    ┌─────────────────┐                         │
│                    │  Document Loader │                         │
│                    │  + Chunking      │                         │
│                    └────────┬────────┘                         │
│                             ▼                                  │
│                    ┌─────────────────┐                         │
│                    │  Embeddings      │                         │
│                    │  (Bedrock/OpenAI)│                         │
│                    └────────┬────────┘                         │
│                             ▼                                  │
│                    ┌─────────────────┐                         │
│                    │  Vector Store    │                         │
│                    │  (OpenSearch)    │                         │
│                    └────────┬────────┘                         │
│                             ▼                                  │
│  [User Report] ──► Retriever ──► Context + Report ──► LLM     │
│                                                       │        │
│                                              ┌────────┘        │
│                                              ▼                 │
│                                    [Enhanced Summary +          │
│                                     Suggested Solution +        │
│                                     Similar Past Issues]        │
└──────────────────────────────────────────────────────────────┘
```

**Files to create**:
```
app/rag/
├── __init__.py
├── document_loader.py      # Load PDFs, Markdown, past tickets
├── chunking.py             # Semantic chunking strategies
├── embeddings.py           # Bedrock Titan / OpenAI embeddings
├── vector_store.py         # OpenSearch Serverless client
├── retriever.py            # Similarity search + reranking
└── rag_chain.py            # Full RAG chain with LangChain
```

**Implementation Steps**:
1. Create document loader for Kiwibot hardware/software manuals
2. Implement chunking strategy (RecursiveCharacterTextSplitter, 512 tokens)
3. Generate embeddings via Amazon Titan Embeddings or OpenAI text-embedding-3-small
4. Store in OpenSearch Serverless (or Pinecone for simplicity)
5. Build retriever with MMR (Maximum Marginal Relevance) for diversity
6. Integrate into existing LangGraph workflow as new node
7. Add evaluation metrics (relevance, faithfulness, answer correctness)

---

### 2. Vector Database Integration
**Why**: Core component for RAG, semantic search, and recommendation features.

**Options** (pick one):
| Option | Pros | Cons |
|--------|------|------|
| OpenSearch Serverless | AWS-native, scales to zero, IAM auth | Complex setup |
| Pinecone | Simple API, free tier, fast | External dependency |
| ChromaDB | Local dev, open source | Not production-scale |
| pgvector (RDS) | SQL familiar, single DB | Less performant at scale |

**Recommended**: OpenSearch Serverless (best for AWS portfolio) + ChromaDB for local dev.

**Files to create**:
```
app/vectordb/
├── __init__.py
├── opensearch_client.py    # Production: AWS OpenSearch Serverless
├── chroma_client.py        # Development: Local ChromaDB
├── base.py                 # Abstract VectorStore interface
└── index_manager.py        # Create/update/delete indices
```

---

## P1: Important for Differentiation

### 3. Fine-tuning Pipeline
**Why**: Shows advanced ML/AI skills beyond API consumption.

**Implementation Plan**:
```
app/finetuning/
├── data_preparation.py     # Convert tickets to training format (JSONL)
├── upload_training.py      # Upload to OpenAI / SageMaker
├── run_finetune.py         # Launch fine-tuning job
├── evaluate_model.py       # Compare base vs fine-tuned
└── deploy_model.py         # Switch to fine-tuned model
```

**Data Format** (from existing tickets):
```jsonl
{"messages": [{"role": "system", "content": "..."}, {"role": "user", "content": "Robot wheels stuck in NY"}, {"role": "assistant", "content": "{\"summary\": \"...\", \"problem_type\": \"hardware\"}"}]}
```

**Steps**:
1. Export 100+ tickets from Firestore as training data
2. Format as OpenAI fine-tuning JSONL or SageMaker format
3. Run fine-tuning job (GPT-3.5-turbo or Claude via Bedrock)
4. A/B test fine-tuned vs base model
5. Document accuracy improvements

---

### 4. Multi-model Routing & Evaluation
**Why**: Production systems need model selection based on cost/quality/latency.

**Architecture**:
```
app/routing/
├── router.py               # Route requests to optimal model
├── evaluator.py            # Score responses (BLEU, semantic similarity)
├── cost_tracker.py         # Track API costs per model
└── ab_test.py              # A/B testing framework
```

**Routing Logic**:
- Simple reports → GPT-3.5 (fast, cheap)
- Complex/ambiguous reports → Claude Sonnet (better reasoning)
- Critical reports → Both models + consensus

---

## P2: Nice to Have

### 5. Streaming Responses (SSE)
```python
# app/streaming.py
from fastapi.responses import StreamingResponse

@app.post("/v1/problem-reports/stream")
async def stream_report(report: ProblemReport):
    async def generate():
        async for chunk in llm.astream(report.content):
            yield f"data: {chunk}\n\n"
    return StreamingResponse(generate(), media_type="text/event-stream")
```

### 6. Conversation Memory (Redis)
```
app/memory/
├── redis_store.py          # Redis-backed chat history
├── session_manager.py      # Session lifecycle
└── context_window.py       # Token-aware context management
```

### 7. Hallucination Detection
```
app/evaluation/
├── hallucination_detector.py   # Cross-reference with knowledge base
├── confidence_scorer.py        # Model confidence metrics
└── human_feedback.py           # RLHF-style feedback collection
```

---

## P3: Future Enhancements

### 8. Admin Dashboard
- React/Next.js frontend
- Real-time ticket updates via WebSocket
- Analytics: tickets by type, response times, model performance
- Cost monitoring per AI provider

### 9. Multi-language Support
- Detect language of report (spaCy or LangDetect)
- Translate before processing
- Respond in user's language

### 10. Automated Ticket Resolution
- Match similar resolved tickets
- Suggest solutions from knowledge base
- Auto-close if confidence > threshold

---

## Infrastructure Improvements

### CI/CD Pipeline Enhancement
```yaml
# .github/workflows/ci.yml (TO ADD)
- Lint (ruff + mypy)
- Unit tests + coverage
- Integration tests (TestContainers)
- Security scan (bandit + safety)
- Build & push Docker image
- Deploy to staging
- Smoke tests
- Deploy to production
```

### Monitoring & Observability
```
monitoring/
├── prometheus_metrics.py   # Custom metrics (latency, tokens, errors)
├── opentelemetry_setup.py  # Distributed tracing
└── alerts/
    ├── high_latency.yml
    ├── error_rate.yml
    └── cost_threshold.yml
```

### AWS Infrastructure (Terraform/CDK)
```
infrastructure/
├── main.tf
├── ecs_fargate.tf          # ECS Fargate for API
├── opensearch.tf           # OpenSearch Serverless
├── secrets_manager.tf      # API keys storage
├── cloudwatch.tf           # Logs + alarms
└── api_gateway.tf          # Optional: API Gateway frontend
```

---

## Suggested Repo Rename

**Current**: `kiwibot-by-xero-chatgpt-test`  
**Suggested**: `kiwibot-ai-support-system` or `rag-ticket-system-aws`

**Reasoning**: Current name sounds like a test/experiment. New name communicates production-ready system with clear purpose.

---

## Quick Wins (Can Do Today)

- [ ] Add GitHub Topics: `generative-ai`, `rag`, `langchain`, `langgraph`, `fastapi`, `aws-bedrock`, `openai`, `python`, `docker`
- [ ] Add badges to README (Python version, Docker, License)
- [ ] Pin this repo on GitHub profile
- [ ] Add `ARCHITECTURE.md` with visual diagram
- [ ] Add OpenAPI spec export (`/docs` endpoint screenshot in README)
- [ ] Add `.env.example` with all required vars documented

---

## Estimated Timeline

| Week | Deliverable |
|------|-------------|
| 1 | RAG document loader + chunking + embeddings |
| 2 | Vector store integration + retriever |
| 3 | RAG chain integrated into LangGraph workflow |
| 4 | Fine-tuning data prep + initial fine-tune |
| 5 | Multi-model router + A/B testing |
| 6 | Streaming + evaluation metrics |
| 7 | Infrastructure (Terraform) + CI/CD |
| 8 | Documentation + portfolio presentation |
