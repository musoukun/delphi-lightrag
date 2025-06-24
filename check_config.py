#!/usr/bin/env python3
"""
設定確認スクリプト
.envファイルの設定を読み込んで表示
"""

from src.config import config
import sys

def main():
    print("🔧 Configuration Check")
    print("=" * 60)
    
    # OpenAI設定
    print("\n📌 OpenAI Configuration:")
    print(f"  API Key: {'✅ Set' if config.OPENAI_API_KEY else '❌ Not Set'}")
    print(f"  API Base: {config.OPENAI_API_BASE}")
    print(f"  Embedding API Base: {config.OPENAI_EMBEDDING_API_BASE}")
    print(f"  LLM Model: {config.LLM_MODEL}")
    print(f"  Embedding Model: {config.EMBEDDING_MODEL}")
    print(f"  Embedding Dimensions: {config.get_embedding_dim()}")
    
    # Google AI設定
    print("\n📌 Google AI Configuration:")
    print(f"  API Key: {'✅ Set' if config.GOOGLE_API_KEY else '❌ Not Set'}")
    print(f"  Model: {config.GOOGLE_MODEL}")
    print(f"  Embedding Model: {config.GOOGLE_EMBEDDING_MODEL}")
    
    # Qdrant設定
    print("\n📌 Qdrant Configuration:")
    print(f"  Host: {config.QDRANT_HOST}")
    print(f"  Port: {config.QDRANT_PORT}")
    print(f"  URL: {config.QDRANT_URL}")
    print(f"  Collection: {config.QDRANT_COLLECTION}")
    
    # LightRAG設定
    print("\n📌 LightRAG Configuration:")
    print(f"  Working Directory: {config.LIGHTRAG_WORKING_DIR}")
    print(f"  Chunk Size: {config.LIGHTRAG_CHUNK_SIZE}")
    print(f"  Chunk Overlap: {config.LIGHTRAG_CHUNK_OVERLAP}")
    print(f"  Max Async: {config.LIGHTRAG_MAX_ASYNC}")
    print(f"  Mode: {config.LIGHTRAG_MODE}")
    print(f"  Language: {config.LIGHTRAG_LANGUAGE}")
    
    # 検証
    print("\n📌 Validation:")
    try:
        config.validate()
        print("  ✅ Configuration is valid")
    except ValueError as e:
        print(f"  ❌ Configuration error: {e}")
        sys.exit(1)
    
    # 使用するAI
    print("\n📌 Active AI Provider:")
    if config.use_google_ai():
        print("  🤖 Using Google AI")
    else:
        print("  🤖 Using OpenAI")
    
    print("\n" + "=" * 60)
    print("✅ Configuration check completed!")

if __name__ == "__main__":
    main()