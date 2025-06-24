#!/usr/bin/env python3
"""
Enhanced Delphi code processing script with advanced features
"""
import os
import sys
import json
import requests
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv
from src.delphi_ast_analyzer import DelphiASTAnalyzer
from src.file_utils import FileProcessor
from src.text_chunker import TextChunker

# Load environment variables
load_dotenv()

# Configuration from environment
LIGHTRAG_API_URL = os.getenv("LIGHTRAG_API_URL", "http://localhost:8080")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
OPENAI_EMBEDDING_API_BASE = os.getenv("OPENAI_EMBEDDING_API_BASE", "https://api.openai.com/v1")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('process_delphi.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class EnhancedDelphiProcessor:
    """Enhanced Delphi code processor with advanced features"""
    
    def __init__(self, progress_file: str = ".lightrag_progress.json"):
        self.file_processor = FileProcessor(progress_file)
        self.text_chunker = TextChunker(model_name=EMBEDDING_MODEL, max_tokens=8000)
        self.ast_analyzer = DelphiASTAnalyzer()
        self.stats = {
            "total_files": 0,
            "processed_files": 0,
            "skipped_files": 0,
            "failed_files": 0,
            "total_chunks": 0,
            "auto_generated_files": 0
        }
    
    def process_directory(self, directory: str, resume: bool = True, reset: bool = False):
        """Process all Delphi files in a directory"""
        logger.info(f"Processing directory: {directory}")
        
        if reset:
            logger.info("Resetting progress...")
            self.file_processor.reset_progress()
        
        # Find all Delphi files
        delphi_files = self.file_processor.find_delphi_files(directory)
        self.stats["total_files"] = len(delphi_files)
        logger.info(f"Found {len(delphi_files)} Delphi files")
        
        # Process each file
        for file_path in delphi_files:
            if resume and self.file_processor.is_file_processed(file_path):
                logger.info(f"Skipping already processed: {file_path}")
                self.stats["skipped_files"] += 1
                continue
            
            try:
                self.process_file(file_path)
                self.stats["processed_files"] += 1
            except Exception as e:
                logger.error(f"Failed to process {file_path}: {e}")
                self.stats["failed_files"] += 1
        
        # Print final statistics
        self.print_statistics()
    
    def process_file(self, file_path: str):
        """Process a single Delphi file"""
        logger.info(f"Processing: {file_path}")
        
        # Read file with encoding detection
        try:
            content, encoding = self.file_processor.read_file_with_encoding(file_path)
            logger.info(f"  Detected encoding: {encoding}")
        except Exception as e:
            logger.error(f"  Failed to read file: {e}")
            raise
        
        # Check if it's auto-generated
        if self.file_processor.is_auto_generated(file_path, content):
            logger.warning(f"  Skipping auto-generated file: {file_path}")
            self.stats["auto_generated_files"] += 1
            self.file_processor.mark_file_processed(file_path)
            return
        
        # Check file size category
        size_category = self.file_processor.estimate_file_size_category(file_path)
        logger.info(f"  File size category: {size_category}")
        
        # Analyze and chunk the file
        file_extension = Path(file_path).suffix.lower()
        chunks = []
        
        if file_extension == '.pas':
            chunks = self.process_pas_file(file_path, content, size_category)
        elif file_extension == '.dfm':
            chunks = self.process_dfm_file(file_path, content)
        
        # Insert chunks to LightRAG
        if chunks:
            self.insert_chunks_to_lightrag(chunks)
            self.stats["total_chunks"] += len(chunks)
        
        # Mark as processed
        self.file_processor.mark_file_processed(file_path)
        logger.info(f"  Completed: {len(chunks)} chunks created")
    
    def process_pas_file(self, file_path: str, content: str, size_category: str) -> List[Dict[str, Any]]:
        """Process a Pascal source file"""
        chunks = []
        
        try:
            # Perform AST analysis
            logger.info("  Performing AST analysis...")
            functions = self.ast_analyzer.extract_functions(content)
            classes = self.ast_analyzer.extract_classes(content)
            ast_info = {
                "functions": functions,
                "classes": classes
            }
            logger.info(f"  Found {len(functions)} functions and {len(classes)} classes")
            
            # Use intelligent chunking for large files
            if size_category in ["large", "very_large"]:
                logger.info("  Using intelligent chunking for large file...")
                raw_chunks = self.text_chunker.chunk_code_intelligently(content, ast_info)
            else:
                # For smaller files, use simple function/class-based chunking
                raw_chunks = self.create_simple_chunks(file_path, content, ast_info)
            
            # Format chunks for LightRAG
            for chunk_data in raw_chunks:
                formatted_chunk = {
                    "content": chunk_data["content"],
                    "metadata": {
                        "file_path": file_path,
                        "file_name": os.path.basename(file_path),
                        "file_type": "pas",
                        **chunk_data.get("metadata", {}),
                        "token_count": chunk_data.get("token_count", 0)
                    }
                }
                chunks.append(formatted_chunk)
                
        except Exception as e:
            logger.error(f"  AST analysis failed: {e}")
            # Fallback: create a single chunk or use basic text chunking
            if size_category in ["large", "very_large"]:
                text_chunks = self.text_chunker.chunk_text(content)
                for i, text_chunk in enumerate(text_chunks):
                    chunks.append({
                        "content": text_chunk,
                        "metadata": {
                            "file_path": file_path,
                            "file_name": os.path.basename(file_path),
                            "file_type": "pas",
                            "chunk_type": "text_chunk",
                            "chunk_index": i,
                            "total_chunks": len(text_chunks)
                        }
                    })
            else:
                chunks.append({
                    "content": content,
                    "metadata": {
                        "file_path": file_path,
                        "file_name": os.path.basename(file_path),
                        "file_type": "pas",
                        "chunk_type": "full_file"
                    }
                })
        
        return chunks
    
    def process_dfm_file(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        """Process a Delphi Form file"""
        # DFM files are usually small, create a single chunk
        token_count = self.text_chunker.count_tokens(content)
        
        if token_count > self.text_chunker.max_tokens:
            # Very large DFM file, need to chunk
            logger.warning(f"  Large DFM file ({token_count} tokens), chunking...")
            text_chunks = self.text_chunker.chunk_text(content)
            chunks = []
            for i, text_chunk in enumerate(text_chunks):
                chunks.append({
                    "content": text_chunk,
                    "metadata": {
                        "file_path": file_path,
                        "file_name": os.path.basename(file_path),
                        "file_type": "dfm",
                        "chunk_type": "partial_form",
                        "chunk_index": i,
                        "total_chunks": len(text_chunks)
                    }
                })
            return chunks
        else:
            return [{
                "content": content,
                "metadata": {
                    "file_path": file_path,
                    "file_name": os.path.basename(file_path),
                    "file_type": "dfm",
                    "chunk_type": "full_form",
                    "token_count": token_count
                }
            }]
    
    def create_simple_chunks(self, file_path: str, content: str, ast_info: Dict) -> List[Dict[str, Any]]:
        """Create simple chunks based on functions and classes"""
        chunks = []
        
        # Create chunks for functions
        for func in ast_info.get("functions", []):
            chunk_content = f"Function: {func['name']}\nType: {func['type']}\nLine: {func['line']}\n\n{func['full_text']}"
            chunks.append({
                "content": chunk_content,
                "metadata": {
                    "chunk_type": "function",
                    "function_name": func['name'],
                    "function_type": func['type'],
                    "line_number": func['line']
                }
            })
        
        # Create chunks for classes
        for cls in ast_info.get("classes", []):
            chunk_content = f"Class: {cls['name']}\nLine: {cls['line']}\n\n{cls['full_text']}"
            chunks.append({
                "content": chunk_content,
                "metadata": {
                    "chunk_type": "class",
                    "class_name": cls['name'],
                    "line_number": cls['line']
                }
            })
        
        # If no functions or classes found, create a single chunk
        if not chunks:
            chunks.append({
                "content": content,
                "metadata": {
                    "chunk_type": "full_file"
                }
            })
        
        return chunks
    
    def insert_chunks_to_lightrag(self, chunks: List[Dict[str, Any]]) -> bool:
        """Insert chunks into LightRAG using REST API"""
        try:
            # Prepare documents for insertion
            documents = []
            for chunk in chunks:
                doc_content = chunk["content"]
                # Add metadata as context
                metadata_str = json.dumps(chunk["metadata"], ensure_ascii=False, indent=2)
                full_content = f"{doc_content}\n\n[Metadata]\n{metadata_str}"
                documents.append(full_content)
            
            # Call LightRAG API to insert documents
            response = requests.post(
                f"{LIGHTRAG_API_URL}/documents/texts",
                json={"texts": documents},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                logger.info(f"  Inserted {len(documents)} chunks to LightRAG")
                return True
            else:
                logger.error(f"  Failed to insert chunks: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"  Error inserting to LightRAG: {e}")
            return False
    
    def print_statistics(self):
        """Print processing statistics"""
        logger.info("\n=== Processing Statistics ===")
        logger.info(f"Total files found: {self.stats['total_files']}")
        logger.info(f"Files processed: {self.stats['processed_files']}")
        logger.info(f"Files skipped (already processed): {self.stats['skipped_files']}")
        logger.info(f"Files failed: {self.stats['failed_files']}")
        logger.info(f"Auto-generated files skipped: {self.stats['auto_generated_files']}")
        logger.info(f"Total chunks created: {self.stats['total_chunks']}")
        
        if self.stats['processed_files'] > 0:
            avg_chunks = self.stats['total_chunks'] / self.stats['processed_files']
            logger.info(f"Average chunks per file: {avg_chunks:.2f}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced Delphi code processor for LightRAG")
    parser.add_argument("directory", help="Directory containing Delphi files")
    parser.add_argument("--reset", action="store_true", help="Reset progress and start fresh")
    parser.add_argument("--no-resume", action="store_true", help="Don't resume from previous progress")
    parser.add_argument("--progress-file", default=".lightrag_progress.json", help="Progress file path")
    
    args = parser.parse_args()
    
    # Check if services are running
    try:
        response = requests.get(f"{LIGHTRAG_API_URL}/docs")
        if response.status_code != 200:
            logger.error("LightRAG service is not running properly")
            sys.exit(1)
    except:
        logger.error("LightRAG service is not running. Please run: docker-compose up -d")
        sys.exit(1)
    
    # Process directory
    processor = EnhancedDelphiProcessor(args.progress_file)
    processor.process_directory(
        args.directory,
        resume=not args.no_resume,
        reset=args.reset
    )


if __name__ == "__main__":
    main()