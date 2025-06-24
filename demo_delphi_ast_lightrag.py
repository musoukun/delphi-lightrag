#!/usr/bin/env python3
"""
Delphi AST分析とLightRAG統合デモ（ローカル実行版）
"""

import asyncio
import os
from src.delphi_lightrag import DelphiLightRAG

async def main():
    print("🚀 Delphi AST + LightRAG Demo")
    print("=" * 50)
    
    # DelphiLightRAGを初期化（.envの設定を自動的に使用）
    delphi_rag = DelphiLightRAG()
    # 必要に応じて個別に上書き可能
    # delphi_rag = DelphiLightRAG(qdrant_host="localhost")
    
    print("📝 Initializing LightRAG...")
    await delphi_rag.initialize()
    
    # サンプルDelphiコードを解析して挿入
    delphi_file = "sample_delphi_code.pas"
    
    if os.path.exists(delphi_file):
        print(f"\n📂 Analyzing Delphi code: {delphi_file}")
        await delphi_rag.analyze_and_insert_delphi_code(delphi_file)
        print("✅ Code analysis and indexing completed!")
        
        # 質問例
        queries = [
            "TSampleClassにはどのようなメソッドがありますか？",
            "THelperClassの機能について教えてください",
            "AddItemメソッドとGetItemCountメソッドの関係は？",
            "コンストラクタとデストラクタの実装について教えてください"
        ]
        
        print("\n🔍 Running queries...")
        print("=" * 50)
        
        for query in queries:
            print(f"\n💬 Query: {query}")
            print("-" * 40)
            
            # ハイブリッドモードで検索
            result = await delphi_rag.query(query, mode="hybrid")
            print(f"📄 Answer: {result}")
            print("=" * 50)
            
        # 詳細な統計情報を表示
        print("\n📊 Knowledge Graph Statistics:")
        print("-" * 40)
        
        # グローバル検索で全体像を把握
        global_result = await delphi_rag.query(
            "このコードベースの全体的な構造について教えてください", 
            mode="global"
        )
        print(f"Global view: {global_result}")
        
    else:
        print(f"❌ Error: {delphi_file} not found!")
        print("Please ensure sample_delphi_code.pas exists in the current directory.")

if __name__ == "__main__":
    # OpenAI APIキーが設定されているか確認
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not set!")
        print("Please set: export OPENAI_API_KEY='your-api-key'")
    else:
        asyncio.run(main())