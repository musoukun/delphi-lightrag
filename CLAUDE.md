# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Delphi LightRAG is a project for analyzing Delphi/Pascal code and building a RAG (Retrieval-Augmented Generation) system. It uses tree-sitter-pascal to parse Delphi code into AST (Abstract Syntax Tree) structures, making the code searchable and understandable.

## Common Development Commands

### Initial Setup

```bash
# Clone with submodules
git clone <repository-url>
cd delphi-lightrag
git submodule init
git submodule update

# Or add tree-sitter-pascal if missing
git submodule add https://github.com/Isopod/tree-sitter-pascal.git
```

### Environment Setup

```bash
# Create and activate virtual environment (Linux/Mac/WSL)
python -m venv venv
source venv/bin/activate

# For Windows PowerShell
python -m venv venv_windows
.\venv_windows\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### Running the Application

```bash
# Run AST analysis demo
python demo_ast_analysis.py

# Run tests
python tests/test_delphi_ast.py

# Start Docker services (Qdrant + LightRAG)
docker-compose up -d
```

## Architecture and Key Components

### Core AST Analyzer

The `DelphiASTAnalyzer` class in `src/delphi_ast_analyzer.py` provides:

- **parse_code()**: Converts Delphi code to AST using tree-sitter-pascal
- **extract_functions()**: Finds all functions, procedures, constructors, and destructors
- **extract_classes()**: Identifies class declarations from type sections
- **find_nodes_by_type()**: Generic AST traversal for specific node types
- **analyze_ast()**: Returns complete AST structure as JSON-compatible dict

### Key Methods and Node Types

When analyzing Delphi code, the analyzer looks for:

- **Function/Procedure nodes**: `declProc`, `defProc`
- **Class declarations**: `declType` containing `declClass`
- **Variable declarations**: `declVar`
- **Field declarations**: `declField`
- **Property declarations**: `declProp`
- **Uses clauses**: `declUses`

### Docker Architecture

The project includes a `docker-compose.yml` that sets up:

1. **Qdrant** (port 6333): Vector database for storing code embeddings
2. **LightRAG** (ports 8080, 3000): RAG API server and web UI

## Key Implementation Details

### AST Analysis Flow

1. Tree-sitter-pascal parses Delphi source into C-based AST
2. Python bindings traverse the AST tree structure
3. Specific patterns identify code elements:
   - Functions/procedures check for `kFunction`/`kProcedure` child nodes
   - Class names extracted from `identifier` nodes within `declType`
   - Implementation methods use `genericDot` pattern for `ClassName.MethodName`

### Testing Approach

Tests use the sample file `sample_delphi_code.pas` and verify:
- AST structure generation
- Function/procedure extraction accuracy
- Class detection
- Node type counting

## Important Configuration

### Required Environment Variables

- `OPENAI_API_KEY`: Required for LightRAG embeddings and LLM features
- `QDRANT_HOST`/`QDRANT_PORT`: Vector database connection (defaults: localhost:6333)
- `LLM_MODEL`: OpenAI model selection (default: gpt-4o-mini)
- `EMBEDDING_MODEL`: Embedding model (default: text-embedding-3-large)

### Project Dependencies

The project requires:
- Python 3.8+
- C/C++ compiler for tree-sitter compilation
- Docker & Docker Compose (optional, for full RAG stack)
- OpenAI API access for RAG features