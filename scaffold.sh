#!/usr/bin/env bash
# scaffold.sh
# Creates missing folders and files for rag-agent-stack.
# Safe to run on an existing repo — never overwrites existing files.
# Usage: bash scaffold.sh

set -e

echo "Scaffolding rag-agent-stack..."
echo ""

create_file() {
  local path="$1"
  local content="$2"
  if [ -f "$path" ]; then
    echo "  skip  $path"
  else
    mkdir -p "$(dirname "$path")"
    echo "$content" > "$path"
    echo "  create $path"
  fi
}

create_dir() {
  local path="$1"
  if [ -d "$path" ]; then
    echo "  skip  $path/"
  else
    mkdir -p "$path"
    echo "  create $path/"
  fi
}

# ── Directories ───────────────────────────────────────────────────────────────

create_dir "agents"
create_dir "pipeline"
create_dir "evals/dataset"
create_dir "api"
create_dir "observability"
create_dir "prompts"
create_dir ".github/workflows"
create_dir "docs"

echo ""

# ── __init__.py files ─────────────────────────────────────────────────────────

for pkg in agents pipeline evals api observability; do
  create_file "$pkg/__init__.py" ""
done

echo ""

# ── Agent modules ─────────────────────────────────────────────────────────────

create_file "agents/retrieval_agent.py" '"""agents/retrieval_agent.py — Query Chroma by similarity, return top-k chunks."""'
create_file "agents/reasoning_agent.py" '"""agents/reasoning_agent.py — Accept context + question, call LLM, return answer."""'
create_file "agents/orchestrator.py" '"""agents/orchestrator.py — LangGraph state machine: retrieval → reasoning."""'

echo ""

# ── Pipeline modules ──────────────────────────────────────────────────────────

create_file "pipeline/ingest.py" '"""pipeline/ingest.py — Load documents, chunk, store in Chroma."""'
create_file "pipeline/embed.py" '"""pipeline/embed.py — Embed chunks via sentence-transformers, persist to Chroma."""'

echo ""

# ── API ───────────────────────────────────────────────────────────────────────

create_file "api/main.py" '"""api/main.py — FastAPI app: POST /query and POST /ingest."""'

echo ""

# ── Evals ─────────────────────────────────────────────────────────────────────

create_file "evals/test_faithfulness.py" '"""evals/test_faithfulness.py — DeepEval FaithfulnessMetric gate."""'
create_file "evals/test_relevance.py" '"""evals/test_relevance.py — DeepEval AnswerRelevancyMetric gate."""'
create_file "evals/dataset/qa_pairs.json" '[]'

echo ""

# ── Observability ─────────────────────────────────────────────────────────────

create_file "observability/tracing.py" '"""observability/tracing.py — LangSmith @traceable wrappers."""'

echo ""

# ── Prompts ───────────────────────────────────────────────────────────────────

create_file "prompts/retrieval_v1.txt" "You are a retrieval assistant. Given the user query below, identify the most relevant information needed to answer it.

Query: {query}"

create_file "prompts/reasoning_v1.txt" 'You are a precise question-answering assistant. Use only the context provided below to answer the question. If the answer cannot be found in the context, say "I do not have enough information to answer this."

Context:
{context}

Question: {question}

Answer:'

create_file "prompts/reasoning_v2.txt" 'You are a precise question-answering assistant. Think step by step before answering.

First, review the context carefully:
{context}

Now answer the following question. Show your reasoning, then give a final answer. If the answer is not in the context, say "I do not have enough information to answer this."

Question: {question}

Reasoning:
Final Answer:'

echo ""

# ── GitHub ────────────────────────────────────────────────────────────────────

create_file ".github/PULL_REQUEST_TEMPLATE.md" "## What does this PR do?

<!-- One or two sentences describing the change -->

## Related issue

Closes #

## Checklist

- [ ] Evals pass locally (\`pytest evals/ -v\`)
- [ ] New or changed logic has a docstring
- [ ] \`.env.example\` updated if new env vars were added
- [ ] \`requirements.txt\` updated if new packages were added"

create_file ".github/workflows/eval-gate.yml" 'name: Eval gate

on:
  pull_request:
    branches: [main]

env:
  FAITHFULNESS_THRESHOLD: "0.75"
  RELEVANCE_THRESHOLD: "0.70"

jobs:
  eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Start Chroma
        run: docker compose up chroma -d
      - name: Wait for Chroma
        run: |
          for i in {1..10}; do
            curl -s http://localhost:8001/api/v1/heartbeat && break
            sleep 3
          done
      - name: Run evals
        env:
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
          LANGCHAIN_API_KEY: ${{ secrets.LANGCHAIN_API_KEY }}
          LANGCHAIN_TRACING_V2: "false"
        run: pytest evals/ -v'

echo ""

# ── Docs ──────────────────────────────────────────────────────────────────────

create_file "docs/.gitkeep" ""

echo ""

# ── Summary ───────────────────────────────────────────────────────────────────

echo "Done. Current structure:"
echo ""
find . -not -path './.venv/*' \
       -not -path './.git/*' \
       -not -path './rag_agent_stack.egg-info/*' \
       -not -name '__pycache__' \
       | sort | sed 's|[^/]*/|  |g'