#!/bin/bash
# LightRAGの再インストールスクリプト

echo "🔄 Reinstalling LightRAG..."

# 既存のlightrag関連パッケージをアンインストール
pip uninstall -y lightrag lightrag-hku

# キャッシュをクリア
pip cache purge

# 正しいパッケージをインストール
pip install lightrag-hku==1.3.7

# tree-sitter-pascalをインストール
pip install git+https://github.com/Isopod/tree-sitter-pascal.git

# その他の依存関係
pip install qdrant-client openai python-dotenv fastapi uvicorn

echo "✅ Installation completed!"
echo "📦 Installed packages:"
pip list | grep -E "(lightrag|qdrant|tree-sitter)"