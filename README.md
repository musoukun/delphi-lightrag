# Delphi LightRAG

Delphi/Pascalコードの解析とRAG（Retrieval-Augmented Generation）システムの構築を目的としたプロジェクトです。

## 概要

このプロジェクトは、Tree-sitter-pascalを使用してDelphiコードを解析し、AST（抽象構文木）を生成して、LightRAGとQdrantを組み合わせた高度な検索システムを構築します。

### 主な特徴

- 🔍 **AST解析**: Tree-sitter-pascalによる高精度なコード構造解析
- 🧠 **LightRAG統合**: ハイブリッド検索（ローカル・グローバル・ナイーブ）対応
- 🗄️ **Qdrantベクトルデータベース**: 高速なベクトル検索
- 🤖 **OpenAI統合**: GPT-4とtext-embedding-3-largeによる高品質な理解と検索
- 🐳 **Docker対応**: 簡単なセットアップと実行
- ⚙️ **柔軟な設定**: 環境変数による細かい設定が可能

## 必要要件

- Python 3.8以上
- Git
- C/C++コンパイラ（tree-sitterのビルド用）

## セットアップ

### 1. リポジトリのクローン

```bash
git clone <your-repository-url>
cd delphi-lightrag
```

### 2. Tree-sitter-pascalのセットアップ

```bash
git submodule init
git submodule update
```

または新規に追加する場合：

```bash
git submodule add https://github.com/Isopod/tree-sitter-pascal.git
```

### 3. Python環境のセットアップ

#### Linux/Mac環境

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Windows環境（PowerShell）

Linux/Mac環境で作成されたvenvは直接使用できません。以下のいずれかの方法を選択してください：

**方法1: WSL経由で実行（推奨）**
```powershell
wsl python demo_ast_analysis.py
```

**方法2: Windows用venvを新規作成**
```powershell
python -m venv venv_windows
.\venv_windows\Scripts\Activate.ps1
pip install -r requirements.txt
```

**方法3: 既存venvの再構築**
```powershell
Remove-Item -Recurse -Force venv
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 使用方法

### 1. Dockerを使用した実行（推奨）

```bash
# 初回セットアップ
./setup.sh

# Pythonスクリプトの実行
./run-in-docker.sh python demo_delphi_ast_lightrag.py

# 対話的シェル
./run-in-docker.sh bash

# コンテナ内で直接実行
docker-compose exec python-runner python demo_delphi_ast_lightrag.py

# APIサーバーの起動（別ターミナル）
docker-compose up api-server
```

**メリット:**
- ✅ ソースコードの変更が即座に反映
- ✅ venv不要、依存関係の問題なし
- ✅ デバッグが簡単
- ✅ ホストPCが汚れない
- ✅ チーム開発で環境統一

### 2. ローカル実行

#### Qdrantの起動
```bash
docker run -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage \
    qdrant/qdrant
```

#### Pythonでの実行
```bash
# 仮想環境の作成と有効化
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存関係のインストール
pip install -r requirements.txt

# デモの実行
python demo_delphi_ast_lightrag.py
```

### 3. API経由での使用

サーバーが起動したら、以下のエンドポイントが利用可能です：

#### ヘルスチェック
```bash
curl http://localhost:8000/health
```

#### Delphiコードの解析
```bash
curl -X POST http://localhost:8000/analyze \
  -F "file=@sample_delphi_code.pas"
```

#### 質問の実行
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "TSampleClassのメソッドについて教えてください",
    "mode": "hybrid"
  }'
```

### デモの実行

サンプルのDelphiコードを解析するデモ：

```bash
# AST解析のみ
python demo_ast_analysis.py

# LightRAG統合版
python demo_delphi_ast_lightrag.py
```

### テストの実行

```bash
python test_delphi_ast.py
```

## カスタム設定

`.env`ファイルで以下の設定をカスタマイズできます：

### OpenAI設定
```bash
OPENAI_API_KEY=sk-xxxxxxxx              # APIキー（必須）
OPENAI_API_BASE=https://api.openai.com/v1  # APIエンドポイント
LLM_MODEL=gpt-4o-mini                   # 使用するLLMモデル
EMBEDDING_MODEL=text-embedding-3-large   # 埋め込みモデル
```

### Qdrant設定
```bash
QDRANT_HOST=localhost                    # Qdrantホスト
QDRANT_PORT=6333                        # Qdrantポート
QDRANT_COLLECTION=delphi_code           # コレクション名
```

### LightRAG設定
```bash
LIGHTRAG_WORKING_DIR=./lightrag_storage  # データ保存先
LIGHTRAG_CHUNK_SIZE=1200                # チャンクサイズ
LIGHTRAG_CHUNK_OVERLAP=100              # チャンクオーバーラップ
LIGHTRAG_MAX_ASYNC=4                    # 最大並列数
LIGHTRAG_MODE=hybrid                    # 検索モード
LIGHTRAG_LANGUAGE=English               # 言語設定（Japanese可）
```

### 設定の確認
```bash
python check_config.py
```

## プロジェクト構成

```
delphi-lightrag/
├── .env.example          # 環境変数の設定例
├── .gitignore           # Gitで無視するファイルの設定
├── README.md            # このファイル
├── requirements.txt     # Pythonの依存関係
├── demo_ast_analysis.py # AST解析のデモスクリプト
├── test_delphi_ast.py   # テストスクリプト
├── sample_delphi_code.pas # サンプルのDelphiコード
├── src/                 # ソースコードディレクトリ
└── tree-sitter-pascal/  # Tree-sitter-pascalサブモジュール
```

## 主な機能

- Delphi/PascalコードのAST解析
- 関数、プロシージャ、クラスの抽出
- コード構造の可視化
- RAGシステムへの統合準備

## 今後の開発予定

- ベクトルデータベースへの統合
- より高度なコード解析機能
- LLMとの連携機能
- コード検索機能の実装

## トラブルシューティング

### tree-sitterのビルドエラー

C/C++コンパイラがインストールされていることを確認してください：
- Windows: Visual Studio Build Toolsまたはmingw
- Linux: gcc/g++
- Mac: Xcode Command Line Tools

### ModuleNotFoundError

必要な依存関係がインストールされているか確認：
```bash
pip install -r requirements.txt
```

## ライセンス

[ライセンス情報を追加してください]

## 貢献

プルリクエストや課題報告を歓迎します。