# rag-agent-stack

Multi-agent RAG pipeline with LangGraph, Chroma, and DeepEval — featuring automated eval gates in CI and full LLMOps observability.

## Stack

| Layer               | Tool                            |
| ------------------- | ------------------------------- |
| LLM                 | Groq (Llama 3) + Ollama (local) |
| Embeddings          | sentence-transformers (local)   |
| Vector DB           | Chroma                          |
| Agent framework     | LangGraph                       |
| Evals               | DeepEval                        |
| Tracing             | LangSmith                       |
| Experiment tracking | Weights & Biases                |
| Deployment          | Hugging Face Spaces             |
| CI/CD               | GitHub Actions                  |

## Setup

```bash
# 1. Clone and install
git clone https://github.com/LuVerissimo/rag-agent-stack.git
cd rag-agent-stack
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Fill in your API keys in .env

# 3. Start Chroma
docker compose up chroma -d

# 4. Ingest documents
python -m pipeline.ingest --input ./your-docs/

# 5. Run the API
uvicorn api.main:app --reload
```

## Running Evals

```bash
pytest evals/ -v
```

Evals require a populated `evals/dataset/qa_pairs.json`. See `evals/README.md` for dataset format.

## Quick Architecture (will update w/drawio later)

```
Documents → pipeline/ingest.py → pipeline/embed.py → Chroma
                                                         ↓
User query → agents/orchestrator.py → retrieval_agent → reasoning_agent → Answer
                                             ↑
                                        prompts/
```

## Current Project Structure

```
rag-agent-stack/
├── agents/          # LangGraph agent nodes + orchestrator
├── pipeline/        # Document ingestion and embedding
├── evals/           # DeepEval test suite and golden dataset
├── api/             # FastAPI endpoints
├── prompts/         # Versioned prompt templates
├── observability/   # LangSmith tracing wrappers
└── .github/         # CI eval gate workflow
```

## What Each Piece Does

`pipeline/ingest.py` the entry point. Point it at a folder of PDFs or text files and it chunks them into Chroma.

`agents/` orchestrator.py defines the LangGraph state machine — retrieval agent runs first, passes context to reasoning agent, reasoning agent produces the final answer.

`evals/dataset/qa_pairs.json` test set/curated list of questions and expected answers over your ingested documents. This is what DeepEval scores against. Plan with 20–30 pairs.

`evals/test_faithfulness.py` checks that the answer doesn't hallucinate beyond the retrieved context. This is the eval gate that blocks your CI if scores drop.

`.github/workflows/eval-gate.yml` runs `pytest evals/` on every PR. If faithfulness or relevance drops below your threshold, the PR is blocked.

`prompts/` stores versioned prompt templates. You run `reasoning_v1` and `reasoning_v2` as an A/B experiment logged to W&B so you have a real comparison to show.

## Eventual Structure

```markdown
agentic-rag/
├── .github/
│ └── workflows/
│ └── eval-gate.yml # CI: runs evals on every PR
├── agents/
│ ├── **init**.py
│ ├── retrieval_agent.py # Fetches relevant chunks from vector DB
│ ├── reasoning_agent.py # Synthesizes answer from retrieved context
│ └── orchestrator.py # LangGraph graph wiring all agents together
├── pipeline/
│ ├── **init**.py
│ ├── ingest.py # Loads & chunks documents
│ └── embed.py # Embeds chunks → Chroma via sentence-transformers
├── evals/
│ ├── **init**.py
│ ├── test_faithfulness.py # DeepEval: answer grounded in context?
│ ├── test_relevance.py # DeepEval: answer relevant to question?
│ └── dataset/
│ └── qa_pairs.json # Your golden Q&A test set
├── api/
│ ├── **init**.py
│ └── main.py # FastAPI app exposing /query endpoint
├── prompts/
│ ├── retrieval_v1.txt
│ ├── reasoning_v1.txt
│ └── reasoning_v2.txt # A/B prompt variants to compare in W&B
├── observability/
│ ├── **init**.py
│ └── tracing.py # LangSmith trace wrappers
├── docker-compose.yml # Spins up Chroma + API together
├── requirements.txt
├── .env.example
└── README.md
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).
