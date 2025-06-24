"""
ファイル処理関連のユーティリティ
"""
import os
import chardet
from pathlib import Path
from typing import List, Tuple, Optional
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class FileProcessor:
    """ファイル処理と進捗管理を行うクラス"""
    
    def __init__(self, progress_file: str = ".lightrag_progress.json"):
        self.progress_file = progress_file
        self.progress_data = self.load_progress()
        
    def load_progress(self) -> dict:
        """進捗情報を読み込む"""
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"進捗ファイルの読み込みに失敗: {e}")
        return {
            "processed_files": [],
            "last_processed": None,
            "total_files": 0,
            "completed_files": 0
        }
    
    def save_progress(self):
        """進捗情報を保存"""
        try:
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(self.progress_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"進捗ファイルの保存に失敗: {e}")
    
    def mark_file_processed(self, file_path: str):
        """ファイルを処理済みとしてマーク"""
        self.progress_data["processed_files"].append(file_path)
        self.progress_data["last_processed"] = file_path
        self.progress_data["completed_files"] += 1
        self.progress_data["last_update"] = datetime.now().isoformat()
        self.save_progress()
    
    def is_file_processed(self, file_path: str) -> bool:
        """ファイルが処理済みかチェック"""
        return file_path in self.progress_data["processed_files"]
    
    def reset_progress(self):
        """進捗をリセット"""
        self.progress_data = {
            "processed_files": [],
            "last_processed": None,
            "total_files": 0,
            "completed_files": 0
        }
        self.save_progress()
    
    def detect_encoding(self, file_path: str) -> str:
        """ファイルの文字コードを自動判定"""
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                result = chardet.detect(raw_data)
                encoding = result['encoding']
                confidence = result['confidence']
                
                # 信頼度が低い場合やNoneの場合のフォールバック
                if not encoding or confidence < 0.7:
                    # Shift-JISの可能性をチェック
                    try:
                        raw_data.decode('shift_jis')
                        return 'shift_jis'
                    except:
                        pass
                    
                    # UTF-8を試す
                    try:
                        raw_data.decode('utf-8')
                        return 'utf-8'
                    except:
                        pass
                
                # Windows環境でcp932として検出されることがあるのでshift_jisに統一
                if encoding.lower() in ['cp932', 'shift_jis', 'sjis']:
                    return 'shift_jis'
                
                return encoding or 'utf-8'
                
        except Exception as e:
            logger.warning(f"文字コード検出エラー {file_path}: {e}")
            return 'utf-8'
    
    def read_file_with_encoding(self, file_path: str) -> Tuple[str, str]:
        """文字コードを自動判定してファイルを読み込む"""
        encoding = self.detect_encoding(file_path)
        
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            return content, encoding
        except UnicodeDecodeError:
            # フォールバック: バイナリとして読んでエラーを無視
            logger.warning(f"文字コードエラー {file_path}, バイナリモードで読み込み")
            with open(file_path, 'rb') as f:
                content = f.read().decode(encoding, errors='ignore')
            return content, encoding
    
    def find_delphi_files(self, directory: str, extensions: List[str] = ['.pas', '.dfm']) -> List[str]:
        """ディレクトリ配下のDelphiファイルを検索"""
        delphi_files = []
        
        for root, dirs, files in os.walk(directory):
            # 除外するディレクトリ
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'venv', 'node_modules']]
            
            for file in files:
                if any(file.lower().endswith(ext) for ext in extensions):
                    file_path = os.path.join(root, file)
                    delphi_files.append(file_path)
        
        # 進捗情報を更新
        self.progress_data["total_files"] = len(delphi_files)
        self.save_progress()
        
        return sorted(delphi_files)
    
    def is_auto_generated(self, file_path: str, content: str) -> bool:
        """自動生成ファイルかどうかを判定"""
        # ファイル名パターン
        file_name = os.path.basename(file_path).lower()
        auto_gen_patterns = [
            '.designer.pas', '.designer.dfm',
            'generated', 'autogen', 'auto-gen',
            '.g.pas', '.generated.pas'
        ]
        
        if any(pattern in file_name for pattern in auto_gen_patterns):
            return True
        
        # コンテンツパターン（最初の数行をチェック）
        lines = content.split('\n')[:10]
        content_patterns = [
            'auto-generated', 'autogenerated', 'generated automatically',
            'do not edit', 'do not modify', 'generated code',
            'this file is automatically generated'
        ]
        
        for line in lines:
            line_lower = line.lower()
            if any(pattern in line_lower for pattern in content_patterns):
                return True
        
        return False
    
    def estimate_file_size_category(self, file_path: str) -> str:
        """ファイルサイズに基づいてカテゴリを判定"""
        file_size = os.path.getsize(file_path)
        
        # サイズカテゴリ（バイト単位）
        if file_size < 10 * 1024:  # 10KB未満
            return "small"
        elif file_size < 100 * 1024:  # 100KB未満
            return "medium"
        elif file_size < 1024 * 1024:  # 1MB未満
            return "large"
        else:  # 1MB以上
            return "very_large"