#!/usr/bin/env python3
"""
Delphi code processing script using LightRAG REST API
"""
import os
import sys
import json
import requests
from typing import List, Dict, Any
from pathlib import Path
from dotenv import load_dotenv
from src.delphi_ast_analyzer import DelphiASTAnalyzer

# Load environment variables
load_dotenv()

# Configuration from environment
LIGHTRAG_API_URL = os.getenv("LIGHTRAG_API_URL", "http://localhost:8080")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
OPENAI_EMBEDDING_API_BASE = os.getenv("OPENAI_EMBEDDING_API_BASE", "https://api.openai.com/v1")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")


def read_delphi_files(folder_path: str) -> List[Dict[str, Any]]:
    """Read all .pas and .dfm files from the specified folder"""
    files = []
    path = Path(folder_path)
    
    for file_path in path.rglob("*.pas"):
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            files.append({
                "path": str(file_path),
                "name": file_path.name,
                "type": "pas",
                "content": content
            })
    
    for file_path in path.rglob("*.dfm"):
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            files.append({
                "path": str(file_path),
                "name": file_path.name,
                "type": "dfm",
                "content": content
            })
    
    return files


def analyze_delphi_code(file_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze Delphi code using AST analyzer"""
    if file_data["type"] != "pas":
        return file_data
    
    analyzer = DelphiASTAnalyzer()
    
    # Extract functions and classes
    functions = analyzer.extract_functions(file_data["content"])
    classes = analyzer.extract_classes(file_data["content"])
    
    file_data["analysis"] = {
        "functions": functions,
        "classes": classes
    }
    
    return file_data


def create_chunks(file_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Create chunks from analyzed Delphi code"""
    chunks = []
    
    if file_data["type"] == "dfm":
        # For DFM files, create a single chunk
        chunks.append({
            "content": file_data["content"],
            "metadata": {
                "file_path": file_data["path"],
                "file_name": file_data["name"],
                "file_type": "dfm",
                "chunk_type": "full_file"
            }
        })
    else:
        # For PAS files, create chunks based on AST analysis
        if "analysis" in file_data:
            # Create chunks for each function
            for func in file_data["analysis"]["functions"]:
                chunk_content = f"Function: {func['name']}\nType: {func['type']}\nLine: {func['line']}\n\n{func['full_text']}"
                chunks.append({
                    "content": chunk_content,
                    "metadata": {
                        "file_path": file_data["path"],
                        "file_name": file_data["name"],
                        "file_type": "pas",
                        "chunk_type": "function",
                        "function_name": func["name"],
                        "function_type": func["type"],
                        "line_number": func["line"]
                    }
                })
            
            # Create chunks for each class
            for cls in file_data["analysis"]["classes"]:
                chunk_content = f"Class: {cls['name']}\nLine: {cls['line']}\n\n{cls['full_text']}"
                chunks.append({
                    "content": chunk_content,
                    "metadata": {
                        "file_path": file_data["path"],
                        "file_name": file_data["name"],
                        "file_type": "pas",
                        "chunk_type": "class",
                        "class_name": cls["name"],
                        "line_number": cls["line"]
                    }
                })
    
    return chunks


def insert_to_lightrag(chunks: List[Dict[str, Any]]) -> bool:
    """Insert chunks into LightRAG using REST API"""
    try:
        # Prepare documents for insertion
        documents = []
        for chunk in chunks:
            doc_content = chunk["content"]
            # Add metadata as context
            metadata_str = json.dumps(chunk["metadata"], indent=2)
            full_content = f"{doc_content}\n\n[Metadata]\n{metadata_str}"
            documents.append(full_content)
        
        # Call LightRAG API to insert documents
        response = requests.post(
            f"{LIGHTRAG_API_URL}/documents/texts",
            json={"texts": documents},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print(f"Successfully inserted {len(documents)} chunks")
            return True
        else:
            print(f"Failed to insert chunks: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"Error inserting to LightRAG: {e}")
        return False


def main():
    if len(sys.argv) != 2:
        print("Usage: python process_delphi_code.py <folder_path>")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    
    # Step 1: Read Delphi files
    print(f"Reading Delphi files from: {folder_path}")
    files = read_delphi_files(folder_path)
    print(f"Found {len(files)} files")
    
    # Step 2: Analyze code using AST
    print("Analyzing code with AST...")
    analyzed_files = []
    for file_data in files:
        analyzed = analyze_delphi_code(file_data)
        analyzed_files.append(analyzed)
    
    # Step 3: Create chunks
    print("Creating chunks...")
    all_chunks = []
    for file_data in analyzed_files:
        chunks = create_chunks(file_data)
        all_chunks.extend(chunks)
    print(f"Created {len(all_chunks)} chunks")
    
    # Step 4: Insert to LightRAG
    print("Inserting to LightRAG...")
    success = insert_to_lightrag(all_chunks)
    
    if success:
        print("Processing completed successfully")
    else:
        print("Processing failed")
        sys.exit(1)


if __name__ == "__main__":
    main()