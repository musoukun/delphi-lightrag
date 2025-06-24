#!/usr/bin/env python3
"""
Test Qdrant connection
"""
import os
import time
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

def test_qdrant_connection():
    """Test basic Qdrant connection"""
    print("🔍 Testing Qdrant connection...")
    
    # Get config from environment
    host = os.getenv("QDRANT_HOST", "localhost")
    port = int(os.getenv("QDRANT_PORT", "6333"))
    
    print(f"📍 Connecting to Qdrant at {host}:{port}")
    
    try:
        # Create client
        client = QdrantClient(host=host, port=port)
        
        # Test 1: Check if service is alive
        print("\n1️⃣ Checking if Qdrant is alive...")
        collections = client.get_collections()
        print(f"✅ Connected! Found {len(collections.collections)} collections")
        
        # Test 2: Create a test collection
        test_collection = "test_connection"
        print(f"\n2️⃣ Creating test collection '{test_collection}'...")
        
        if client.collection_exists(test_collection):
            client.delete_collection(test_collection)
            print("   Deleted existing test collection")
        
        client.create_collection(
            collection_name=test_collection,
            vectors_config=VectorParams(size=3072, distance=Distance.COSINE)
        )
        print("✅ Test collection created successfully")
        
        # Test 3: Verify collection exists
        print("\n3️⃣ Verifying collection exists...")
        exists = client.collection_exists(test_collection)
        print(f"✅ Collection exists: {exists}")
        
        # Clean up
        print("\n4️⃣ Cleaning up...")
        client.delete_collection(test_collection)
        print("✅ Test collection deleted")
        
        print("\n🎉 All tests passed! Qdrant is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure Qdrant container is running: docker-compose ps")
        print("2. Check logs: docker-compose logs qdrant")
        print("3. If running in Docker, use QDRANT_HOST=qdrant")
        print("4. If running locally, use QDRANT_HOST=localhost")

if __name__ == "__main__":
    # Add a small delay to ensure Qdrant is fully started
    print("⏳ Waiting 2 seconds for Qdrant to be ready...")
    time.sleep(2)
    test_qdrant_connection()