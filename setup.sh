#!/bin/bash
# Delphi LightRAG環境のセットアップスクリプト

echo "🚀 Delphi LightRAG環境セットアップ"
echo "======================================="

# .envファイルの確認
if [ ! -f .env ]; then
    echo "📝 .envファイルを作成します..."
    cp .env.example .env
    echo "⚠️  .envファイルにOPENAI_API_KEYを設定してください"
    exit 1
fi

# OpenAI APIキーの確認
if ! grep -q "OPENAI_API_KEY=sk-" .env; then
    echo "❌ エラー: .envファイルにOPENAI_API_KEYが設定されていません"
    exit 1
fi

# 既存のコンテナを停止
echo "🛑 既存のコンテナを停止..."
docker-compose down

# イメージをビルド
echo "🔨 Dockerイメージをビルド..."
docker-compose build

# コンテナを起動
echo "🚀 コンテナを起動..."
docker-compose up -d

# 起動確認
echo "⏳ 起動を待機中..."
sleep 5

# ステータス確認
echo "📊 コンテナの状態:"
docker-compose ps

echo ""
echo "✅ セットアップ完了!"
echo ""
echo "🎯 使い方:"
echo "  1. コード実行: ./run-in-docker.sh python demo_delphi_ast_lightrag.py"
echo "  2. 対話シェル: ./run-in-docker.sh bash"
echo "  3. APIサーバー: docker-compose up api-server"
echo "  4. Qdrant UI: http://localhost:6333/dashboard"
echo ""
echo "💡 ヒント: ソースコードの変更は即座に反映されます（再起動不要）"