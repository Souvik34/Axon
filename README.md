# Axon

**An AI-powered document assistant built with Retrieval-Augmented Generation (RAG).**

Axon is an open-source AI project focused on building a document-aware assistant that can understand uploaded documents, retrieve relevant information, and generate context-aware responses using LLMs.

The project currently focuses on document ingestion, semantic search, hybrid retrieval, and RAG.

> 🚧 **Status: Under Active Development**

## ✨ Current Features

- **LLM Integration:** Groq as the primary language model provider with Gemini as a fallback.
- **Document Upload:** Supports PDF, TXT, and DOCX files.
- **Text Extraction:** Extracts text from uploaded documents.
- **Text Chunking:** Splits documents into manageable chunks with overlapping content.
- **Embeddings:** Generates 768-dimensional text embeddings using Gemini Embedding 2.
- **Vector Search:** Performs semantic similarity search using PostgreSQL and pgvector.
- **Keyword Search:** Uses PostgreSQL full-text search to retrieve keyword-relevant chunks.
- **Hybrid Retrieval:** Combines semantic and keyword search results.
- **Reciprocal Rank Fusion:** Uses RRF to merge rankings from multiple retrieval methods.
- **RAG Pipeline:** Uses retrieved document context to generate answers.
- **Source Attribution:** Returns document IDs, chunk indices, and retrieval scores.
- **Duplicate Detection:** Uses SHA-256 content hashing to identify duplicate document uploads.
- **Conversation Persistence:** Stores conversations and messages in PostgreSQL.
- **Automated Tests:** Includes pytest tests for vector, keyword, and hybrid retrieval.

## 🛠️ Tech Stack

| Category | Technology |
|---|---|
| AI Runtime | Python, FastAPI |
| LLM Providers | Groq, Google Gemini |
| Embeddings | Gemini Embedding 2 |
| Database | PostgreSQL (Neon) |
| Vector Database | pgvector |
| Full-Text Search | PostgreSQL |
| ORM | SQLAlchemy |
| Migrations | Alembic |
| Testing | pytest |
| API Testing | Postman |

## 🏗️ Current Architecture

```text
                 Client
                   |
                   v
              FastAPI API
                   |
          +--------+--------+
          |        |        |
          v        v        v
        Chat   Documents   RAG
          |        |        |
          |        v        |
          |   Text Extraction
          |        |
          |        v
          |      Chunking
          |        |
          |        v
          |    Embeddings
          |        |
          |        v
          |   PostgreSQL
          |    + pgvector
          |        |
          |        v
          |   Hybrid Search
          |        |
          |        v
          |       RRF
          |        |
          +--------+
                   |
                   v
             LLM Provider
              /       \
            Groq     Gemini
           Primary   Fallback
                   |
                   v
              AI Response
```

## 🔎 Hybrid Retrieval

Axon combines two retrieval techniques:

**1. Semantic Search**
- Generates query embeddings.
- Finds semantically similar document chunks using vector similarity.

**2. Keyword Search**
- Uses PostgreSQL full-text search.
- Retrieves chunks matching important query terms.

**3. Reciprocal Rank Fusion (RRF)**
- Combines rankings from both retrieval methods.
- Produces a unified ranked list of relevant chunks.

The retrieved context is passed to the LLM to generate an answer.

## 📁 Project Structure

```text
Axon/
│
├── services/
│   └── ai-runtime/
│       ├── app/
│       │   ├── api/
│       │   ├── core/
│       │   ├── models/
│       │   └── services/
│       │       ├── document/
│       │       └── llm/
│       │
│       ├── migrations/
│       ├── tests/
│       ├── alembic.ini
│       └── requirements.txt
│
└── README.md
```

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL database with pgvector support
- Groq API key
- Google Gemini API key

### 1. Clone the repository

```bash
git clone https://github.com/souvik34/Axon.git
cd Axon/services/ai-runtime
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

**Windows:**
```powershell
.venv\Scripts\activate
```

**Linux/macOS:**
```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the AI runtime directory.

Configure your database connection and API credentials according to the application's environment configuration.

Never commit API keys or other secrets to Git.

### 5. Run database migrations

```bash
alembic upgrade head
```

### 6. Start the FastAPI server

```bash
uvicorn app.main:app --reload
```

### 7. Access the API

- Health Check: `http://127.0.0.1:8000/health`
- Swagger Documentation: `http://127.0.0.1:8000/docs`

## 🧪 Running Tests

Run the retrieval tests using:

```bash
python -m pytest tests/test_retrieval.py -v
```

## 🔐 Environment Configuration

The application requires environment variables for:

- PostgreSQL database connection.
- Groq API credentials.
- Gemini API credentials.
- Application configuration.

Refer to the application's configuration module for the exact variable names.

## 🤝 Contributing

Contributions, ideas, and feedback are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Open a pull request.

## 📄 License

This project is open source. A license will be added to the repository.

---

**Built with curiosity and a focus on understanding how modern AI systems work under the hood.**
