#!/bin/bash
# Docker内でPythonスクリプトを実行するヘルパー

# 使い方を表示
show_usage() {
    echo "使い方:"
    echo "  ./run-in-docker.sh [command]"
    echo ""
    echo "例:"
    echo "  ./run-in-docker.sh python demo_delphi_ast_lightrag.py"
    echo "  ./run-in-docker.sh python test_delphi_ast.py"
    echo "  ./run-in-docker.sh python check_config.py"
    echo "  ./run-in-docker.sh bash  # 対話的シェル"
    echo ""
    echo "事前準備:"
    echo "  1. docker-compose up -d"
    echo "  2. .envファイルにOPENAI_API_KEYを設定"
}

# 引数チェック
if [ $# -eq 0 ]; then
    show_usage
    exit 1
fi

# Docker Composeでコンテナ内でコマンドを実行
docker-compose exec python-runner "$@"