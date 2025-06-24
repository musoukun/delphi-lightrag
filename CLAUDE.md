# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Delphi LightRAG is a sophisticated code analysis and retrieval system specifically designed for Delphi/Pascal codebases. It combines AST (Abstract Syntax Tree) analysis using tree-sitter-pascal with LightRAG for hybrid retrieval-augmented generation, enabling intelligent code search and understanding capabilities.

## Common Development Commands

### Docker-based Development (Recommended)

```bash
# Initial setup - creates .env, builds images, starts containers
./setup.sh

# Run Python scripts in Docker
./run-in-docker.sh python demo_delphi_ast_lightrag.py
./run-in-docker.sh python test_delphi_ast.py

# Interactive shell in Docker
./run-in-docker.sh bash

# Start API server
docker-compose up api-server

# View container status
docker-compose ps

# Stop all containers
docker-compose down
```

### Local Development

```bash
# Install dependencies (in venv)
pip install -r requirements.txt

# Run tests
python test_delphi_ast.py

# Run demos
python demo_ast_analysis.py              # AST analysis only
python demo_delphi_ast_lightrag.py      # Full LightRAG integration

# Check configuration
python check_config.py

# Start Qdrant locally (if not using Docker)
docker run -p 6333:6333 -p 6334:6334 -v $(pwd)/qdrant_storage:/qdrant/storage qdrant/qdrant
```

### API Testing

```bash
# Health check
curl http://localhost:8000/health

# Analyze Delphi code
curl -X POST http://localhost:8000/analyze -F "file=@sample_delphi_code.pas"

# Query the system
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "TSampleClassのメソッドについて教えてください", "mode": "hybrid"}'
```

## Architecture and Key Components

### Core Modules

1. **src/delphi_ast_analyzer.py** - The foundation module that uses tree-sitter-pascal to parse Delphi/Pascal code and extract AST structures (classes, functions, procedures). This is the core parsing engine.

2. **src/delphi_lightrag.py** - Main integration module that bridges AST analysis with LightRAG. Handles code parsing, entity extraction, knowledge graph building, and RAG queries. Uses async/await throughout.

3. **src/delphi_lightrag_server.py** - FastAPI server providing REST API endpoints for code analysis and queries. Includes file upload, analysis, and query endpoints.

4. **src/config.py** - Centralized configuration management that reads from environment variables and provides defaults. All configuration flows through this module.

### Key Design Patterns

- **Async First**: All LightRAG operations use Python's asyncio for better performance
- **Configuration Driven**: Extensive use of environment variables via `src/config.py`
- **Modular Architecture**: Clear separation between AST analysis, RAG integration, and API layers
- **Docker-based Development**: Source code is mounted as volumes for real-time updates without rebuilds

### Data Flow

1. Delphi/Pascal code → tree-sitter-pascal → AST
2. AST → Entity/Relationship extraction → LightRAG knowledge graph
3. LightRAG + Qdrant vector DB → Hybrid search (local/global/naive)
4. Search results + OpenAI GPT-4 → Intelligent responses

### Storage Directories

- `lightrag_storage/` - LightRAG knowledge graphs and indexes
- `qdrant_storage/` - Qdrant vector database persistent storage
- `rag_storage/` - RAG system artifacts
- `data/` - Input/output data for processing
- `delphi_exports/` - Exported analysis results

## Environment Configuration

The project uses `.env` file for configuration. Key variables:

- `OPENAI_API_KEY` - Required for LLM and embeddings
- `LLM_MODEL` - Default: gpt-4o-mini
- `EMBEDDING_MODEL` - Default: text-embedding-3-large
- `QDRANT_HOST/PORT` - Vector database connection
- `LIGHTRAG_MODE` - Search mode: hybrid/local/global/naive
- `LIGHTRAG_CHUNK_SIZE/OVERLAP` - Text chunking parameters

## Testing Approach

- Unit tests: `test_delphi_ast.py` - Tests AST analyzer functionality
- Integration demos: `demo_*.py` files demonstrate various features
- No specific test framework - tests are simple Python scripts
- Docker environment ensures consistent testing

## Key Dependencies

- `lightrag-hku>=1.3.7` - Core RAG framework
- `tree-sitter>=0.20.0` + `tree-sitter-pascal` - AST parsing
- `qdrant-client>=1.7.0` - Vector database
- `openai>=1.0.0` - LLM integration
- `fastapi>=0.100.0` + `uvicorn>=0.23.0` - Web API

## Development Notes

1. **Tree-sitter Compilation**: The tree-sitter-pascal grammar needs C/C++ compilation. This is handled automatically in the Docker build.

2. **Real-time Code Updates**: When using Docker, source code changes are immediately reflected without container rebuilds due to volume mounts.

3. **API Server**: The FastAPI server (`src/delphi_lightrag_server.py`) runs on port 8000 and provides endpoints for file analysis and queries.

4. **Hybrid Search**: LightRAG supports three search modes:
   - Local: Entity-based search
   - Global: Community/cluster-based search
   - Hybrid: Combines both for best results

5. **Language Support**: While UI strings are in Japanese, the system works with English or Japanese for queries (configurable via `LIGHTRAG_LANGUAGE`).