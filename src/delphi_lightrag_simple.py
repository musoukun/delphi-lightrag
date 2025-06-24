"""
Delphi LightRAG Simple Version (Dockerなし、ローカルストレージ使用)
"""
import os
import asyncio
from typing import List, Dict, Any
import numpy as np
from tree_sitter import Node, Parser, Language
import tree_sitter_pascal as tspascal
import openai
from pathlib import Path

# 簡易的なRAG実装（LightRAGを使わない）
class SimpleDelphiRAG:
    def __init__(self, working_dir="./simple_rag_storage"):
        self.working_dir = Path(working_dir)
        self.working_dir.mkdir(exist_ok=True)
        
        # Tree-sitter設定
        self.pascal_lang = Language(tspascal.language())
        self.parser = Parser(self.pascal_lang)
        
        # ストレージ
        self.chunks = []
        self.entities = []
        self.embeddings = []
        
        # OpenAI設定
        self.client = openai.AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
    async def analyze_delphi_code(self, file_path: str):
        """Delphiコードを解析"""
        with open(file_path, 'rb') as f:
            content = f.read()
            
        # AST解析
        tree = self.parser.parse(content)
        root_node = tree.root_node
        
        # エンティティ抽出
        entities = self._extract_entities(root_node, content)
        
        # テキストチャンクとして保存
        text_content = content.decode('utf-8')
        chunk = {
            'file': os.path.basename(file_path),
            'content': text_content,
            'entities': entities
        }
        
        # 埋め込みを生成
        embedding = await self._embed_text(text_content)
        
        self.chunks.append(chunk)
        self.entities.extend(entities)
        self.embeddings.append(embedding)
        
        print(f"✅ Analyzed {file_path}: Found {len(entities)} entities")
        
    def _extract_entities(self, node: Node, content: bytes, entities=None):
        """エンティティを抽出"""
        if entities is None:
            entities = []
            
        # 定義ノードタイプ
        definition_types = {
            "class_type": "class",
            "interface_type": "interface", 
            "function_declaration": "function",
            "procedure_declaration": "procedure",
            "method_declaration": "method"
        }
        
        if node.type in definition_types:
            # 名前を探す
            for child in node.children:
                if child.type == "identifier":
                    name = content[child.start_byte:child.end_byte].decode('utf-8')
                    entities.append({
                        'name': name,
                        'type': definition_types[node.type],
                        'line': node.start_point[0]
                    })
                    break
        
        # 子ノードを再帰的に探索
        for child in node.children:
            self._extract_entities(child, content, entities)
            
        return entities
    
    async def _embed_text(self, text: str) -> List[float]:
        """テキストを埋め込みベクトルに変換"""
        response = await self.client.embeddings.create(
            model="text-embedding-3-large",
            input=text[:8000]  # トークン制限
        )
        return response.data[0].embedding
    
    async def query(self, question: str) -> str:
        """質問に回答"""
        if not self.chunks:
            return "No code has been analyzed yet."
        
        # 質問を埋め込みに変換
        query_embedding = await self._embed_text(question)
        
        # コサイン類似度で最も関連性の高いチャンクを探す
        similarities = []
        for i, chunk_embedding in enumerate(self.embeddings):
            similarity = np.dot(query_embedding, chunk_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(chunk_embedding)
            )
            similarities.append((similarity, i))
        
        # 最も類似度の高いチャンクを取得
        similarities.sort(reverse=True)
        best_chunk = self.chunks[similarities[0][1]]
        
        # エンティティ情報をフォーマット
        entities_info = "\n".join([
            f"- {e['type']} {e['name']} (line {e['line']})"
            for e in best_chunk['entities']
        ])
        
        # GPTで回答を生成
        prompt = f"""
        Based on the following Delphi code analysis, answer the question.
        
        File: {best_chunk['file']}
        
        Entities found:
        {entities_info}
        
        Code excerpt:
        {best_chunk['content'][:2000]}...
        
        Question: {question}
        
        Please answer in Japanese.
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful Delphi code analysis assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message.content


# 使用例
async def main():
    print("🚀 Simple Delphi RAG Demo (No Docker required)")
    print("=" * 50)
    
    # OpenAI APIキーの確認
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not set!")
        print("Please set: export OPENAI_API_KEY='your-api-key'")
        return
    
    # Simple RAGを初期化
    rag = SimpleDelphiRAG()
    
    # サンプルコードを解析
    if os.path.exists("sample_delphi_code.pas"):
        await rag.analyze_delphi_code("sample_delphi_code.pas")
        
        # 質問例
        queries = [
            "TSampleClassにはどのようなメソッドがありますか？",
            "このコードの主な機能は何ですか？",
        ]
        
        for query in queries:
            print(f"\n💬 Q: {query}")
            answer = await rag.query(query)
            print(f"📝 A: {answer}")
            print("-" * 50)
    else:
        print("❌ sample_delphi_code.pas not found!")

if __name__ == "__main__":
    asyncio.run(main())