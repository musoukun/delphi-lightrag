# Delphi LightRAG

Delphi/PascalコードをLightRAG（軽量RAGシステム）で解析・検索可能にするプロジェクトです。

## 概要

このプロジェクトは、Tree-sitter-pascalを使用してDelphiコードをAST（抽象構文木）に変換し、LightRAGとQdrantベクトルデータベースを使用して、コードの意味的検索と質問応答を可能にします。

### 主な特徴

- 🔍 **高度なコード解析**: Tree-sitterによる正確なAST解析
- 🌐 **文字コード自動判定**: UTF-8、Shift-JISなど様々なエンコーディングに対応
- 📁 **ディレクトリ一括処理**: プロジェクト全体を簡単に解析
- 🔄 **進捗管理**: 中断・再開機能で大規模プロジェクトにも対応
- 🧩 **スマートチャンク分割**: トークン制限を考慮した適切な分割
- 🤖 **AI検索**: 自然言語でDelphiコードを検索・質問

## 必要要件

- Python 3.8以上
- Docker & Docker Compose
- Git
- C/C++コンパイラ（tree-sitterのビルド用）
- OpenAI APIキー（埋め込みとLLM用）

## セットアップ

### 1. リポジトリのクローン

```bash
git clone <your-repository-url>
cd delphi-lightrag

# サブモジュールも含めてクローン
git submodule init
git submodule update
```

### 2. 環境設定

```bash
# 環境変数ファイルをコピー
cp .env.example .env

# .envファイルを編集してOpenAI APIキーを設定
# OPENAI_API_KEY=your-api-key-here
```

### 3. Dockerサービスの起動

```bash
# Qdrant（ベクトルDB）とLightRAGを起動
docker-compose up -d

# サービスの確認
docker ps
```

### 4. Python環境のセットアップ

```bash
# 仮想環境の作成と有効化
python -m venv venv
source venv/bin/activate  # Linux/Mac/WSL

# Windows PowerShellの場合
# python -m venv venv
# .\venv\Scripts\Activate.ps1

# 依存関係のインストール
pip install -r requirements.txt
cd tree-sitter-pascal && pip install . && cd ..
```

## 使用方法

### 基本的な使用方法

#### 1. Delphiプロジェクトの解析と登録

```bash
# 基本的な使用（ディレクトリ指定）
python process_delphi_code_enhanced.py /path/to/delphi/project

# 進捗をリセットして最初から処理
python process_delphi_code_enhanced.py /path/to/delphi/project --reset

# 再開機能を無効化
python process_delphi_code_enhanced.py /path/to/delphi/project --no-resume

# カスタム進捗ファイル
python process_delphi_code_enhanced.py /path/to/delphi/project --progress-file .my_progress.json
```

#### 2. コードの検索と質問

```python
import requests

# LightRAG APIエンドポイント
LIGHTRAG_API_URL = "http://localhost:8080"

# クエリの実行
response = requests.post(
    f"{LIGHTRAG_API_URL}/query",
    json={
        "query": "TCalculatorクラスのメソッドを教えて",
        "mode": "hybrid",  # "naive", "local", "global", "hybrid"から選択
        "stream": False
    }
)

print(response.json()["response"])
```

### 高度な使用例

#### サンプルプロジェクトでのテスト

```bash
# サンプルプロジェクトの処理
python process_delphi_code_enhanced.py sample_delphi_project --reset

# テストクエリの実行
python -c "
import requests
queries = [
    'TCalculatorクラスについて教えてください',
    'エラー処理の実装方法は？',
    'メモリ機能の使い方を説明して'
]
for q in queries:
    resp = requests.post('http://localhost:8080/query', 
                        json={'query': q, 'mode': 'hybrid'})
    print(f'Q: {q}')
    print(f'A: {resp.json().get(\"response\", \"No response\")[:200]}...\n')
"
```

#### プログラムからの利用

```python
from src.file_utils import FileProcessor
from src.text_chunker import TextChunker
from process_delphi_code_enhanced import EnhancedDelphiProcessor

# プロセッサの初期化
processor = EnhancedDelphiProcessor()

# ディレクトリの処理
processor.process_directory(
    "/path/to/delphi/project",
    resume=True,  # 前回の続きから処理
    reset=False   # 進捗をリセットしない
)
```

## 拡張機能

### 文字コード自動判定

- UTF-8、Shift-JIS、その他のエンコーディングを自動検出
- 日本語コメントを含むDelphiコードも正しく処理

### スマートチャンク分割

- OpenAI text-embedding-3-largeの8,191トークン制限を考慮
- 関数・クラス単位での論理的な分割
- 大きなファイルも適切に処理

### 進捗管理

- `.lightrag_progress.json`で処理状況を記録
- 中断後も続きから再開可能
- 大規模プロジェクトの段階的処理に対応

### 自動生成ファイルの検出

以下のパターンを自動的に検出してスキップ：
- `.designer.pas`、`.generated.pas`
- `auto-generated`、`do not edit`コメントを含むファイル

## プロジェクト構成

```
delphi-lightrag/
├── .env.example              # 環境変数の設定例
├── docker-compose.yml        # Docker設定
├── requirements.txt          # Python依存関係
├── CLAUDE.md                # Claude Code用の指示書
├── README.md                # このファイル
├── process_delphi_code_enhanced.py  # メイン処理スクリプト
├── test_enhanced_processor.py       # テストスクリプト
├── sample_delphi_project/    # サンプルプロジェクト
│   ├── Calculator.pas        # 計算機クラス
│   ├── MainForm.pas         # メインフォーム
│   └── MainForm.dfm         # フォーム定義
├── src/                     # ソースコード
│   ├── delphi_ast_analyzer.py  # AST解析器
│   ├── file_utils.py          # ファイル処理ユーティリティ
│   └── text_chunker.py        # テキスト分割器
├── docs/                    # ドキュメント
│   └── enhanced_features.md # 拡張機能の詳細
└── tree-sitter-pascal/      # Tree-sitter Pascalパーサー
```

## API エンドポイント

### LightRAG API (ポート 8080)

- `POST /documents/texts` - テキストドキュメントの追加
- `POST /query` - クエリの実行
- `GET /docs` - APIドキュメント

### Qdrant API (ポート 6333)

- `GET /collections` - コレクション一覧
- `GET /dashboard` - ダッシュボード

## トラブルシューティング

### Docker関連

```bash
# サービスが起動しない場合
docker-compose down
docker-compose up -d

# ログの確認
docker logs delphi-lightrag
docker logs delphi-qdrant
```

### Python関連

```bash
# tree-sitterのビルドエラー
# C/C++コンパイラを確認
gcc --version  # Linux/Mac
cl             # Windows

# 依存関係の再インストール
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### 文字コードエラー

```python
# デバッグモードで文字コードを確認
from src.file_utils import FileProcessor
fp = FileProcessor()
encoding = fp.detect_encoding("問題のファイル.pas")
print(f"検出されたエンコーディング: {encoding}")
```

## パフォーマンスのヒント

1. **大規模プロジェクト**: 進捗管理機能を活用して段階的に処理
2. **メモリ使用量**: Dockerのメモリ割り当てを調整
3. **処理速度**: 並列処理のためにLightRAGワーカー数を増やす

## ライセンス

[ライセンス情報を追加してください]

## 貢献

プルリクエストや課題報告を歓迎します。

## 参考リンク

- [LightRAG Documentation](https://github.com/HKUDS/LightRAG)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Tree-sitter Pascal](https://github.com/Isopod/tree-sitter-pascal)
- [OpenAI API Reference](https://platform.openai.com/docs/)