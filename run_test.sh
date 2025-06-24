#!/bin/bash

echo "=== Delphi Code Processing Test ==="

# Check if services are running
echo "Checking services..."
if ! docker ps | grep -q delphi-lightrag; then
    echo "Error: LightRAG service is not running. Please run: docker-compose up -d"
    exit 1
fi

if ! docker ps | grep -q delphi-qdrant; then
    echo "Error: Qdrant service is not running. Please run: docker-compose up -d"
    exit 1
fi

echo "✓ Services are running"

# Check if venv exists, if not create it
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
echo "Checking Python dependencies..."
pip install -q -r requirements.txt
cd tree-sitter-pascal && pip install -q . && cd ..

# Run the test
echo "Running test..."
python test_process_delphi.py

echo "Test completed."