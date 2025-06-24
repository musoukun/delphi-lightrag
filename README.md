# Delphi LightRAG

Delphi/Pascalコードの解析とRAG（Retrieval-Augmented Generation）システムの構築を目的としたプロジェクトです。

## 概要

このプロジェクトは、Tree-sitter-pascalを使用してDelphiコードを解析し、AST（抽象構文木）を生成して、コードの構造を理解・検索可能にします。

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

### デモの実行

サンプルのDelphiコードを解析するデモ：

```bash
python demo_ast_analysis.py
```

### テストの実行

```bash
python test_delphi_ast.py
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