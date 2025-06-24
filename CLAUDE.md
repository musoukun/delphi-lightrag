# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Delphi LightRAG is a project for analyzing Delphi/Pascal code and building a RAG (Retrieval-Augmented Generation) system. It uses tree-sitter-pascal to parse Delphi code into AST (Abstract Syntax Tree) structures, making the code searchable and understandable.

## Common Development Commands

### Environment Setup

```bash
# Create and activate virtual environment (Linux/Mac)
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# For Windows PowerShell
python -m venv venv_windows
.\venv_windows\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Running Tests and Demos

```bash
# Run AST analysis demo
python demo_ast_analysis.py

# Run tests
python test_delphi_ast.py
```

## Architecture and Key Components

### Core Module

**src/delphi_ast_analyzer.py** - The main AST analyzer that:
- Uses tree-sitter-pascal to parse Delphi/Pascal code
- Extracts code structures (classes, functions, procedures, types)
- Provides methods for analyzing and traversing the AST
- Supports pattern matching and code intelligence features

### Key Files

- **demo_ast_analysis.py** - Demonstrates AST analysis capabilities
- **test_delphi_ast.py** - Test script for the AST analyzer
- **sample_delphi_code.pas** - Sample Delphi code for testing
- **requirements.txt** - Python dependencies including:
  - lightrag>=0.1.0b6
  - qdrant-client>=1.7.0
  - tree-sitter>=0.20.0
  - click>=8.0.0
  - python-dotenv>=1.0.0

### Tree-sitter-pascal Integration

The project includes tree-sitter-pascal as a git submodule for parsing Delphi/Pascal code. This provides:
- Grammar-based parsing
- Fast and accurate AST generation
- Support for modern Delphi syntax features

## Environment Configuration

The project uses environment variables configured in `.env` (create from `.env.example`):

```bash
# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_EMBEDDING_API_BASE=https://api.openai.com/v1

# Model Settings
LLM_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-large

# Qdrant Vector Database
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=delphi_code

# LightRAG Configuration
LIGHTRAG_WORKING_DIR=./lightrag_storage
LIGHTRAG_CHUNK_SIZE=1200
LIGHTRAG_CHUNK_OVERLAP=100
LIGHTRAG_MAX_ASYNC=4
LIGHTRAG_MODE=hybrid
LIGHTRAG_LANGUAGE=English
```

## Project Structure

```
delphi-lightrag/
├── src/
│   ├── __init__.py
│   └── delphi_ast_analyzer.py    # Core AST analyzer
├── tree-sitter-pascal/            # Submodule for Pascal grammar
├── demo_ast_analysis.py           # Demo script
├── test_delphi_ast.py            # Test script
├── sample_delphi_code.pas        # Sample code
├── requirements.txt              # Dependencies
└── .env.example                  # Environment template
```

## Key Features Implemented

1. **AST Analysis**: Parse and analyze Delphi/Pascal code structure
2. **Code Intelligence**: Extract classes, methods, functions, and their relationships
3. **Tree-sitter Integration**: Fast and accurate parsing using tree-sitter-pascal

## Development Notes

1. **Tree-sitter Compilation**: The tree-sitter-pascal grammar requires C/C++ compilation. Ensure you have a C compiler installed.

2. **Python Version**: Requires Python 3.8 or higher

3. **Virtual Environment**: Different virtual environments may be needed for Windows vs Linux/Mac due to binary dependencies

4. **Future Integration**: The project is designed to integrate with LightRAG and Qdrant for advanced code search and RAG capabilities