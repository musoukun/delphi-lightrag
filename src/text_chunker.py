"""
テキストのチャンク分割とトークン管理
"""
import tiktoken
from typing import List, Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class TextChunker:
    """トークン制限を考慮したテキストチャンク分割クラス"""
    
    def __init__(self, model_name: str = "text-embedding-3-large", max_tokens: int = 8000):
        """
        Args:
            model_name: 使用するOpenAIモデル名
            max_tokens: 最大トークン数（8191の制限に対して余裕を持たせる）
        """
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.encoder = tiktoken.encoding_for_model(model_name)
        
    def count_tokens(self, text: str) -> int:
        """テキストのトークン数をカウント"""
        try:
            tokens = self.encoder.encode(text)
            return len(tokens)
        except Exception as e:
            logger.error(f"トークンカウントエラー: {e}")
            # フォールバック: 文字数ベースの推定（日本語は1文字約2トークンと仮定）
            return len(text) * 2
    
    def chunk_text(self, text: str, overlap: int = 100) -> List[str]:
        """テキストを最大トークン数以下のチャンクに分割"""
        tokens = self.encoder.encode(text)
        
        if len(tokens) <= self.max_tokens:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(tokens):
            end = min(start + self.max_tokens, len(tokens))
            
            # オーバーラップを考慮（最後のチャンク以外）
            if end < len(tokens):
                end = end - overlap
            
            chunk_tokens = tokens[start:end]
            chunk_text = self.encoder.decode(chunk_tokens)
            chunks.append(chunk_text)
            
            start = end
        
        return chunks
    
    def chunk_by_section(self, text: str, section_delimiters: List[str] = None) -> List[Dict[str, Any]]:
        """セクション（関数、クラスなど）単位でチャンク分割"""
        if section_delimiters is None:
            section_delimiters = [
                '\nprocedure ', '\nfunction ', '\nclass ', 
                '\ntype ', '\nconst ', '\nvar ',
                '\nimplementation', '\ninterface'
            ]
        
        chunks = []
        current_chunk = ""
        current_tokens = 0
        chunk_metadata = {"type": "mixed", "sections": []}
        
        # 行単位で処理
        lines = text.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i]
            line_tokens = self.count_tokens(line + '\n')
            
            # セクション開始を検出
            is_section_start = any(line.strip().lower().startswith(delimiter.strip().lower()) 
                                 for delimiter in section_delimiters)
            
            # 新しいセクションかつ現在のチャンクが大きい場合
            if is_section_start and current_tokens > 0:
                # 現在のチャンクが最大トークンの50%を超えていたら新しいチャンクを開始
                if current_tokens + line_tokens > self.max_tokens * 0.5:
                    if current_chunk:
                        chunks.append({
                            "content": current_chunk,
                            "metadata": chunk_metadata,
                            "token_count": current_tokens
                        })
                    current_chunk = line + '\n'
                    current_tokens = line_tokens
                    chunk_metadata = {"type": self._detect_section_type(line), "sections": [line.strip()]}
                else:
                    current_chunk += line + '\n'
                    current_tokens += line_tokens
                    chunk_metadata["sections"].append(line.strip())
            else:
                # トークン制限チェック
                if current_tokens + line_tokens > self.max_tokens:
                    if current_chunk:
                        chunks.append({
                            "content": current_chunk,
                            "metadata": chunk_metadata,
                            "token_count": current_tokens
                        })
                    current_chunk = line + '\n'
                    current_tokens = line_tokens
                    chunk_metadata = {"type": "continuation", "sections": []}
                else:
                    current_chunk += line + '\n'
                    current_tokens += line_tokens
            
            i += 1
        
        # 最後のチャンクを追加
        if current_chunk:
            chunks.append({
                "content": current_chunk,
                "metadata": chunk_metadata,
                "token_count": current_tokens
            })
        
        return chunks
    
    def _detect_section_type(self, line: str) -> str:
        """セクションタイプを検出"""
        line_lower = line.strip().lower()
        if line_lower.startswith('procedure') or line_lower.startswith('function'):
            return "function"
        elif line_lower.startswith('class'):
            return "class"
        elif line_lower.startswith('type'):
            return "type"
        elif line_lower.startswith('const'):
            return "const"
        elif line_lower.startswith('var'):
            return "var"
        else:
            return "other"
    
    def chunk_code_intelligently(self, code: str, ast_info: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """AST情報を活用したインテリジェントなチャンク分割"""
        chunks = []
        
        if ast_info and "functions" in ast_info:
            # 関数単位でチャンク化
            for func in ast_info["functions"]:
                func_content = self._extract_function_content(code, func)
                func_tokens = self.count_tokens(func_content)
                
                if func_tokens <= self.max_tokens:
                    chunks.append({
                        "content": func_content,
                        "metadata": {
                            "type": "function",
                            "name": func["name"],
                            "line_start": func["line_start"],
                            "line_end": func["line_end"]
                        },
                        "token_count": func_tokens
                    })
                else:
                    # 大きな関数はさらに分割
                    sub_chunks = self.chunk_text(func_content)
                    for i, sub_chunk in enumerate(sub_chunks):
                        chunks.append({
                            "content": sub_chunk,
                            "metadata": {
                                "type": "function_part",
                                "name": func["name"],
                                "part": i + 1,
                                "total_parts": len(sub_chunks)
                            },
                            "token_count": self.count_tokens(sub_chunk)
                        })
        
        # クラス単位でもチャンク化
        if ast_info and "classes" in ast_info:
            for cls in ast_info["classes"]:
                cls_content = self._extract_class_content(code, cls)
                cls_tokens = self.count_tokens(cls_content)
                
                if cls_tokens <= self.max_tokens:
                    chunks.append({
                        "content": cls_content,
                        "metadata": {
                            "type": "class",
                            "name": cls["name"],
                            "line_start": cls.get("line_start", 0),
                            "line_end": cls.get("line_end", 0)
                        },
                        "token_count": cls_tokens
                    })
        
        # チャンク化されていない部分があれば追加
        if not chunks:
            chunks = self.chunk_by_section(code)
        
        return chunks
    
    def _extract_function_content(self, code: str, func_info: Dict) -> str:
        """関数のコンテンツを抽出"""
        lines = code.split('\n')
        # line_startとline_endが存在しない場合はlineを使用
        if "line_start" in func_info and "line_end" in func_info:
            start = max(0, func_info["line_start"] - 1)
            end = min(len(lines), func_info["line_end"])
        elif "line" in func_info:
            # line情報のみの場合は、関数全体を推定
            start = max(0, func_info["line"] - 1)
            # 関数の終わりを探す（簡易的な実装）
            end = start + 1
            for i in range(start + 1, len(lines)):
                if lines[i].strip().lower() in ['end;', 'end.'] or (i < len(lines) - 1 and lines[i+1].strip() and not lines[i+1].startswith(' ')):
                    end = i + 1
                    break
            else:
                end = min(start + 50, len(lines))  # 最大50行
        else:
            # 情報がない場合は全体を返す
            return func_info.get("full_text", "// Function content not found")
        
        return '\n'.join(lines[start:end])
    
    def _extract_class_content(self, code: str, class_info: Dict) -> str:
        """クラスのコンテンツを抽出（簡易実装）"""
        # クラス名を含む行から次のクラスまたはendまでを抽出
        lines = code.split('\n')
        class_name = class_info["name"]
        
        start_idx = None
        end_idx = None
        
        for i, line in enumerate(lines):
            if start_idx is None and class_name in line and 'class' in line.lower():
                start_idx = i
            elif start_idx is not None and line.strip().lower() == 'end;':
                end_idx = i + 1
                break
        
        if start_idx is not None:
            if end_idx is None:
                end_idx = len(lines)
            return '\n'.join(lines[start_idx:end_idx])
        
        return f"// Class {class_name} definition not found"