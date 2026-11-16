# Axon

**An Open-Source Agentic AI Platform for RAG, Live Data, and Persistent Memory.**

Axon is an AI platform that connects documents, external data sources, and persistent memory to answer complex queries and execute multi-step tasks autonomously.

It combines Agentic AI, Retrieval-Augmented Generation (RAG), MCP integrations, and intelligent orchestration to deliver context-aware, evidence-backed responses with minimal user intervention.

> 🚧 **Status: Under Active Development**

## ✨ Features

- **Agentic Orchestration:** Intelligent planning, task decomposition, dynamic tool selection, and multi-step execution.
- **Agentic RAG:** Semantic search, keyword search, hybrid retrieval, and Reciprocal Rank Fusion (RRF).
- **Live Data Integration:** Connects with Gmail, GitHub, and other external services through MCP.
- **Cross-Source Retrieval:** Automatically gathers and connects information across multiple data sources.
- **Persistent Memory:** Retains relevant context across conversations.
- **Shared Evidence:** Collects, organizes, and shares structured findings across agents.
- **Autonomous Execution:** Supports follow-up research, retries, and execution recovery.
- **Source Attribution:** Generates evidence-grounded responses with source references.
- **LLM Failover:** Groq as the primary provider with Google Gemini as fallback.

## 🏗️ Architecture

```text
                  User Query
                      |
                      v
               Agent Orchestrator
                      |
                Task Planning
                      |
                Tool Selection
                      |
          +-----------+-----------+
          |           |           |
          v           v           v
       Documents    Gmail       GitHub
          |           |           |
          +-----------+-----------+
                      |
                      v
              Shared Evidence
                      |
             Persistent Memory
                      |
                      v
              Response Synthesis
                      |
                LLM Providers
                 /         \
               Groq       Gemini
             Primary     Fallback
                      |
                      v
                Final Response
                 + Citations
```

## 🛠️ Tech Stack

| Category | Technology |
|---|---|
| AI Runtime | Python, FastAPI |
| Orchestration | LangGraph |
| LLM Providers | Groq, Google Gemini |
| Agent Integrations | MCP |
| RAG | Hybrid Search, RRF |
| Embeddings | Gemini Embedding 2 |
| Database | PostgreSQL, Neon |
| Vector Search | pgvector |
| Full-Text Search | PostgreSQL |
| ORM & Migrations | SQLAlchemy, Alembic |
| Testing | pytest |

## 🔄 How Axon Works

1. **Understand:** Interprets the user's request and identifies the objective.
2. **Plan:** Decomposes the request into executable tasks.
3. **Discover:** Selects relevant tools and data sources dynamically.
4. **Execute:** Retrieves information from documents, integrations, and memory.
5. **Collaborate:** Shares findings and identifiers across execution steps.
6. **Research:** Performs additional retrieval when information is insufficient.
7. **Synthesize:** Produces a consolidated, evidence-backed response with citations.

## 📁 Project Structure

```text
Axon/
├── services/
│   └── ai-runtime/
│       ├── app/
│       │   ├── api/
│       │   ├── core/
│       │   ├── models/
│       │   └── services/
│       │       ├── agent/
│       │       ├── document/
│       │       ├── memory/
│       │       └── llm/
│       ├── migrations/
│       ├── evaluation/
│       ├── tests/
│       └── requirements.txt
└── README.md
```

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL with pgvector
- Groq API key
- Google Gemini API key

### Installation

```bash
git clone https://github.com/souvik34/Axon.git
cd Axon/services/ai-runtime

python -m venv .venv
```

Activate the environment:

```powershell
# Windows
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure the required environment variables in `.env`, then run:

```bash
alembic upgrade head
uvicorn app.main:app --reload
```

API documentation: `http://127.0.0.1:8000/docs`


## 🤝 Contributing

Contributions, ideas, and feedback are welcome. Feel free to fork the repository and submit a pull request.

## 📄 License

Open source. License details will be added.

---

**Built to explore the future of autonomous, context-aware AI systems.**
