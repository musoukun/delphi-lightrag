#!/usr/bin/env python3
"""
.envファイルの読み込みテスト
"""
import os
from pathlib import Path

# 現在の作業ディレクトリを表示
print(f"Current working directory: {os.getcwd()}")

# .envファイルの存在確認
env_files = [
    ".env",
    "./.env",
    "/mnt/d/develop/delphi-lightrag/.env"
]

print("\n📁 Checking .env file locations:")
for env_file in env_files:
    path = Path(env_file)
    exists = path.exists()
    print(f"  {env_file}: {'✅ Found' if exists else '❌ Not found'}")
    if exists:
        print(f"    Absolute path: {path.absolute()}")

# 環境変数の確認（.env読み込み前）
print("\n🔍 Environment variables (before loading .env):")
print(f"  OPENAI_API_KEY: {'Set' if os.getenv('OPENAI_API_KEY') else 'Not set'}")
print(f"  QDRANT_HOST: {os.getenv('QDRANT_HOST', 'Not set')}")

# config.pyをインポートして.envを読み込む
print("\n📥 Importing config.py...")
from src.config import config

# 環境変数の確認（.env読み込み後）
print("\n🔍 Environment variables (after loading .env):")
print(f"  OPENAI_API_KEY: {'Set' if config.OPENAI_API_KEY else 'Not set'}")
print(f"  QDRANT_HOST: {config.QDRANT_HOST}")
print(f"  LLM_MODEL: {config.LLM_MODEL}")
print(f"  EMBEDDING_MODEL: {config.EMBEDDING_MODEL}")
print(f"  LIGHTRAG_LANGUAGE: {config.LIGHTRAG_LANGUAGE}")

print("\n✅ Test completed!")