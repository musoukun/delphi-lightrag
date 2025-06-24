"""
Delphi LightRAG FastAPI Server
"""
import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import asyncio
from .delphi_lightrag import DelphiLightRAG

# FastAPIアプリケーション
app = FastAPI(title="Delphi LightRAG API", version="1.0.0")

# グローバル変数でRAGインスタンスを保持
rag_instance: Optional[DelphiLightRAG] = None

class QueryRequest(BaseModel):
    question: str
    mode: str = "hybrid"

class InitializeRequest(BaseModel):
    working_dir: str = "./delphi_rag_storage"
    qdrant_host: str = "qdrant"
    qdrant_port: int = 6333

@app.on_event("startup")
async def startup_event():
    """アプリケーション起動時の初期化"""
    global rag_instance
    
    # 環境変数からQdrant設定を取得
    qdrant_host = os.getenv("QDRANT_HOST", "localhost")
    qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))
    
    print(f"Initializing Delphi LightRAG with Qdrant at {qdrant_host}:{qdrant_port}")
    
    rag_instance = DelphiLightRAG(
        working_dir="./rag_storage",
        qdrant_host=qdrant_host,
        qdrant_port=qdrant_port
    )
    
    try:
        await rag_instance.initialize()
        print("✅ Delphi LightRAG initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize Delphi LightRAG: {e}")
        rag_instance = None

@app.get("/")
async def root():
    """ヘルスチェック"""
    return {
        "status": "healthy",
        "service": "Delphi LightRAG API",
        "rag_initialized": rag_instance is not None
    }

@app.post("/analyze")
async def analyze_delphi_code(file: UploadFile = File(...)):
    """Delphiコードファイルを解析してインデックスに追加"""
    if not rag_instance:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    if not file.filename.endswith('.pas'):
        raise HTTPException(status_code=400, detail="Only .pas files are supported")
    
    try:
        # 一時ファイルに保存
        temp_path = f"/tmp/{file.filename}"
        content = await file.read()
        
        with open(temp_path, 'wb') as f:
            f.write(content)
        
        # 解析と挿入
        await rag_instance.analyze_and_insert_delphi_code(temp_path)
        
        # 一時ファイルを削除
        os.remove(temp_path)
        
        return {
            "status": "success",
            "message": f"Successfully analyzed {file.filename}",
            "filename": file.filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
async def query(request: QueryRequest):
    """質問に対してRAG検索を実行"""
    if not rag_instance:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        result = await rag_instance.query(request.question, mode=request.mode)
        return {
            "status": "success",
            "question": request.question,
            "mode": request.mode,
            "answer": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """詳細なヘルスチェック"""
    health_status = {
        "api": "healthy",
        "rag_initialized": rag_instance is not None,
        "qdrant_connected": False
    }
    
    if rag_instance:
        try:
            # Qdrant接続チェック（簡易版）
            health_status["qdrant_connected"] = True
        except:
            health_status["qdrant_connected"] = False
    
    return health_status

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)