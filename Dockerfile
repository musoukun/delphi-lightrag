FROM python:3.10-slim

# システム依存関係のインストール
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    vim \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 依存関係のみコピー（キャッシュ効率化）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 開発用ツール追加
RUN pip install ipython ipdb

# 必要なディレクトリを作成
RUN mkdir -p /app/rag_storage /app/data /app/src

# Pythonパスを設定
ENV PYTHONPATH=/app

# ポート公開
EXPOSE 8000

# デフォルトコマンド（bashシェル）
CMD ["/bin/bash"]