# FastAPI LLM Query Service

FastAPI-based LLM query service with LangGraph, Weaviate RAG, and Tavily search.

## Quickstart

1. Copy `env.template` to `.env` and configure your API keys:
   - `ANTHROPIC_API_KEY` - Required for Claude (LangGraph agent)
   - `OPENAI_API_KEY` - Required for Weaviate embeddings
   - `TAVILY_API_KEY` - Optional, for web search

2. Start all services (API + Weaviate) with Docker Compose:
   ```bash
   make docker-up
   ```
   This will automatically build the images if needed and start both Weaviate and the API service.

3. Visit API docs at http://localhost:8000/docs


## Local Development (without Docker)

If you want to run the API locally without Docker:

1. Install dependencies with Poetry
   ```bash
   poetry install
   ```

2. Make sure Weaviate is running (start it with `make docker-up` or run it separately)

3. Run the API
   ```bash
   make run
   ```

**Note:** When running locally, ensure `WEAVIATE_URL` in `.env` points to `http://localhost:8080`.

## Main Features

- **Query Endpoint** (`/api/v1/query`) - Process queries using LangGraph agent with RAG and web search
- **Ingest Endpoint** (`/api/v1/ingest/pdf`) - Upload and ingest PDF files into Weaviate vector database
- **Weaviate Routes** (`/api/v1/weaviate/status`, `/api/v1/weaviate/objects`) - Debug endpoints for checking Weaviate status and inspecting stored objects

## Environment Variables

See `env.template` for all available configuration options. Key variables:

- `ANTHROPIC_API_KEY` - Claude API key for LLM queries
- `OPENAI_API_KEY` - OpenAI API key for embeddings
- `TAVILY_API_KEY` - Tavily API key for web search 
- `WEAVIATE_URL` - Weaviate instance URL (use `http://weaviate:8080` for Docker, `http://localhost:8080` for local)
- `WEAVIATE_COLLECTION_NAME` - Collection name for documents (default: `Documents`)
