"""
設定管理モジュール
環境変数から設定を読み込む
"""
import os
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

# .envファイルを探す
def find_env_file():
    """プロジェクトルートから.envファイルを探す"""
    # 可能な.envファイルの場所
    possible_paths = [
        Path.cwd() / '.env',  # 現在のディレクトリ
        Path(__file__).parent.parent / '.env',  # プロジェクトルート
        Path('/mnt/d/develop/delphi-lightrag/.env'),  # 絶対パス
    ]
    
    for path in possible_paths:
        if path.exists():
            return path
    return None

# .envファイルを読み込む
env_path = find_env_file()
if env_path:
    load_dotenv(dotenv_path=env_path)
    # デバッグメッセージは環境変数で制御
    if os.getenv('DEBUG_CONFIG', '').lower() == 'true':
        print(f"✅ Loaded .env from: {env_path}")
else:
    # .envファイルが見つからない場合の警告
    if os.getenv('DEBUG_CONFIG', '').lower() == 'true':
        print("⚠️  No .env file found, using system environment variables")

class Config:
    """アプリケーション設定"""
    
    # OpenAI設定
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_API_BASE: str = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
    OPENAI_EMBEDDING_API_BASE: str = os.getenv("OPENAI_EMBEDDING_API_BASE", "https://api.openai.com/v1")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")
    
    # Google AI設定（オプション）
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
    GOOGLE_MODEL: str = os.getenv("GOOGLE_MODEL", "gemini-2.5-flash")
    GOOGLE_EMBEDDING_MODEL: str = os.getenv("GOOGLE_EMBEDDING_MODEL", "text-embedding-004")
    
    # Qdrant設定
    QDRANT_HOST: str = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT: int = int(os.getenv("QDRANT_PORT", "6333"))
    QDRANT_URL: str = os.getenv("QDRANT_URL", f"http://{QDRANT_HOST}:{QDRANT_PORT}")
    QDRANT_COLLECTION: str = os.getenv("QDRANT_COLLECTION", "delphi_code")
    
    # LightRAG設定
    LIGHTRAG_WORKING_DIR: str = os.getenv("LIGHTRAG_WORKING_DIR", "./lightrag_storage")
    LIGHTRAG_CHUNK_SIZE: int = int(os.getenv("LIGHTRAG_CHUNK_SIZE", "1200"))
    LIGHTRAG_CHUNK_OVERLAP: int = int(os.getenv("LIGHTRAG_CHUNK_OVERLAP", "100"))
    LIGHTRAG_MAX_ASYNC: int = int(os.getenv("LIGHTRAG_MAX_ASYNC", "4"))
    LIGHTRAG_MODE: str = os.getenv("LIGHTRAG_MODE", "hybrid")
    LIGHTRAG_LANGUAGE: str = os.getenv("LIGHTRAG_LANGUAGE", "English")
    
    @classmethod
    def validate(cls) -> bool:
        """設定の検証"""
        if not cls.OPENAI_API_KEY and not cls.GOOGLE_API_KEY:
            raise ValueError("Either OPENAI_API_KEY or GOOGLE_API_KEY must be set")
        return True
    
    @classmethod
    def get_embedding_dim(cls) -> int:
        """埋め込みモデルの次元数を取得"""
        embedding_dims = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536,
            "text-embedding-004": 768,
        }
        return embedding_dims.get(cls.EMBEDDING_MODEL, 1536)
    
    @classmethod
    def use_google_ai(cls) -> bool:
        """Google AIを使用するかどうか"""
        return bool(cls.GOOGLE_API_KEY)

# シングルトンインスタンス
config = Config()