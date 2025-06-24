import os
import asyncio
import bisect
from typing import List, Dict, Any
import numpy as np
from tree_sitter import Node, Parser, Language
import tree_sitter_pascal as tspascal
from lightrag import LightRAG, QueryParam
from lightrag.utils import EmbeddingFunc
from lightrag.llm.openai import openai_complete_if_cache
from qdrant_client import QdrantClient
import openai
from .config import config

# Delphi/Pascal言語解析用のTree-sitterを設定
pascal_lang = Language(tspascal.language())

# エンティティとして抽出するDelphiの定義ノードを設定
delphi_definition_dict = {
    "class_type": "identifier",           # クラス定義
    "interface_type": "identifier",       # インターフェース定義
    "function_declaration": "identifier", # 関数宣言
    "procedure_declaration": "identifier", # プロシージャ宣言
    "method_declaration": "identifier",   # メソッド宣言
    "property_declaration": "identifier", # プロパティ宣言
    "constructor_declaration": "identifier", # コンストラクタ
    "destructor_declaration": "identifier"   # デストラクタ
}

class DelphiLightRAG:
    def __init__(self, working_dir=None, qdrant_host=None, qdrant_port=None):
        # 設定から読み込む（引数で上書き可能）
        self.working_dir = working_dir or config.LIGHTRAG_WORKING_DIR
        self.qdrant_host = qdrant_host or config.QDRANT_HOST
        self.qdrant_port = qdrant_port or config.QDRANT_PORT
        self.rag = None
        self.parser = Parser(pascal_lang)
        
    async def initialize(self):
        """LightRAGの初期化（設定に基づいて動的に構成）"""
        # カスタムLLM関数（設定に基づいて選択）
        async def custom_llm_func(prompt: str, system_prompt: str = "", history_messages: list = [], **kwargs):
            """カスタムLLM関数"""
            if config.use_google_ai():
                # Google AI実装（必要に応じて追加）
                raise NotImplementedError("Google AI support coming soon")
            else:
                # OpenAI実装
                return await openai_complete_if_cache(
                    config.LLM_MODEL,
                    prompt,
                    system_prompt=system_prompt,
                    history_messages=history_messages,
                    api_key=config.OPENAI_API_KEY,
                    base_url=config.OPENAI_API_BASE,
                    **kwargs
                )
        
        # カスタム埋め込み関数
        async def custom_embed(texts: List[str]) -> np.ndarray:
            """設定に基づいた埋め込み"""
            if config.use_google_ai():
                # Google AI実装（必要に応じて追加）
                raise NotImplementedError("Google AI embedding support coming soon")
            else:
                # OpenAI実装
                client = openai.AsyncOpenAI(
                    api_key=config.OPENAI_API_KEY,
                    base_url=config.OPENAI_EMBEDDING_API_BASE
                )
                response = await client.embeddings.create(
                    model=config.EMBEDDING_MODEL,
                    input=texts
                )
                embeddings = [item.embedding for item in response.data]
                return np.array(embeddings)
        
        # Qdrantストレージの設定
        # QdrantVectorDBStorageはURLを環境変数から読む
        os.environ["QDRANT_URL"] = f"http://{self.qdrant_host}:{self.qdrant_port}"
        
        qdrant_config = {
            "cosine_better_than_threshold": 0.2,  # Required parameter
            "collection_name": config.QDRANT_COLLECTION,
            "vector_size": config.get_embedding_dim()
        }
        
        self.rag = LightRAG(
            working_dir=self.working_dir,
            llm_model_func=custom_llm_func,
            llm_model_name=config.LLM_MODEL,
            llm_model_max_token_size=8192,
            llm_model_max_async=config.LIGHTRAG_MAX_ASYNC,
            embedding_func=EmbeddingFunc(
                embedding_dim=config.get_embedding_dim(),
                max_token_size=8192,
                func=custom_embed
            ),
            chunk_token_size=config.LIGHTRAG_CHUNK_SIZE,
            chunk_overlap_token_size=config.LIGHTRAG_CHUNK_OVERLAP,
            vector_storage="QdrantVectorDBStorage",
            vector_db_storage_cls_kwargs=qdrant_config,
            addon_params={
                "language": config.LIGHTRAG_LANGUAGE,
                "entity_types": ["class", "interface", "function", "procedure", "property", "method"]
            }
        )
        
    async def analyze_and_insert_delphi_code(self, file_path: str):
        """Delphiコードを解析してLightRAGに挿入"""
        with open(file_path, 'rb') as f:
            content = f.read()
            
        # ASTを生成
        tree = self.parser.parse(content)
        root_node = tree.root_node
        
        # チャンクとエンティティを抽出
        chunks = []
        entities = []
        relationships = []
        
        # ファイル内容をテキストとして取得
        text_content = content.decode('utf-8')
        file_name = os.path.basename(file_path)
        
        # エンティティを抽出
        extracted_entities = await self._extract_entities(
            root_node, 
            content, 
            file_name
        )
        
        # カスタムナレッジグラフとして挿入
        custom_kg = {
            "chunks": chunks,
            "entities": extracted_entities['entities'],
            "relationships": extracted_entities['relationships']
        }
        
        await self.rag.ainsert_custom_kg(custom_kg)
        
    async def _extract_entities(self, node: Node, content: bytes, file_name: str):
        """ASTノードからエンティティを抽出"""
        entities = []
        relationships = []
        
        # ノードを再帰的に探索
        def traverse(node, parent_entity=None):
            # 定義ノードかチェック
            if node.type in delphi_definition_dict:
                # 識別子を探す
                identifier_node = None
                for child in node.children:
                    if child.type == delphi_definition_dict[node.type]:
                        identifier_node = child
                        break
                        
                if identifier_node:
                    entity_name = content[identifier_node.start_byte:identifier_node.end_byte].decode('utf-8')
                    entity_id = f"{file_name}:{entity_name}"
                    
                    # エンティティを作成
                    entities.append({
                        "entity_name": entity_id,
                        "entity_type": node.type,
                        "description": f"{node.type} named {entity_name} in {file_name}",
                        "source_id": f"file:{file_name}_line:{node.start_point[0]}"
                    })
                    
                    # 親エンティティとの関係を作成
                    if parent_entity:
                        relationships.append({
                            "src_id": parent_entity,
                            "tgt_id": entity_id,
                            "description": f"{entity_name} is a member of {parent_entity}",
                            "keywords": f"{parent_entity} {entity_name}",
                            "weight": 1.0,
                            "source_id": f"file:{file_name}_line:{node.start_point[0]}"
                        })
                    
                    # 子ノードを探索（このエンティティを親として）
                    for child in node.children:
                        traverse(child, entity_id)
                else:
                    # 識別子が見つからない場合も子ノードを探索
                    for child in node.children:
                        traverse(child, parent_entity)
            else:
                # 定義ノードでない場合は子ノードを探索
                for child in node.children:
                    traverse(child, parent_entity)
        
        traverse(node)
        
        return {
            "entities": entities,
            "relationships": relationships
        }
    
    async def query(self, question: str, mode="hybrid"):
        """質問に対してRAG検索を実行"""
        return await self.rag.aquery(question, param=QueryParam(mode=mode))


# 使用例
async def main():
    # DelphiLightRAGを初期化
    delphi_rag = DelphiLightRAG()
    await delphi_rag.initialize()
    
    # Delphiコードを解析して挿入
    await delphi_rag.analyze_and_insert_delphi_code("sample_delphi_code.pas")
    
    # 質問する
    result = await delphi_rag.query("TSampleClassのメソッドについて教えてください")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())