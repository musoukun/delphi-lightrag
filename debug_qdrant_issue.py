#!/usr/bin/env python3
"""
Debug Qdrant connection issue
"""
import os
import time
import asyncio
from qdrant_client import QdrantClient
from lightrag.kg.qdrant_impl import QdrantVectorDBStorage

async def debug_connection():
    """Debug the Qdrant connection issue"""
    print("🔍 Debugging Qdrant connection issue...")
    
    # Get config from environment
    host = os.getenv("QDRANT_HOST", "localhost")
    port = int(os.getenv("QDRANT_PORT", "6333"))
    
    print(f"\n1️⃣ Environment variables:")
    print(f"   QDRANT_HOST: {host}")
    print(f"   QDRANT_PORT: {port}")
    
    # Test 1: Direct connection
    print(f"\n2️⃣ Testing direct QdrantClient connection...")
    try:
        client = QdrantClient(host=host, port=port)
        collections = client.get_collections()
        print(f"✅ Direct connection successful! Found {len(collections.collections)} collections")
    except Exception as e:
        print(f"❌ Direct connection failed: {type(e).__name__}: {e}")
    
    # Test 2: Check what QdrantVectorDBStorage is doing
    print(f"\n3️⃣ Testing QdrantVectorDBStorage initialization...")
    try:
        # This is what LightRAG does internally
        qdrant_config = {
            "host": host,
            "port": port,
            "collection_name": "test_collection",
            "vector_size": 3072
        }
        
        print(f"   Config: {qdrant_config}")
        
        # Try to create the storage directly
        storage = QdrantVectorDBStorage(
            namespace="test",
            global_config={},
            embedding_func=None,
            meta_fields={},
            **qdrant_config
        )
        print("✅ QdrantVectorDBStorage created successfully!")
        
    except Exception as e:
        print(f"❌ QdrantVectorDBStorage failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Try different connection methods
    print(f"\n4️⃣ Testing alternative connection methods...")
    
    # Try with URL
    try:
        url = f"http://{host}:{port}"
        print(f"   Trying URL: {url}")
        client2 = QdrantClient(url=url)
        collections2 = client2.get_collections()
        print(f"✅ URL connection successful! Found {len(collections2.collections)} collections")
    except Exception as e:
        print(f"❌ URL connection failed: {type(e).__name__}: {e}")
    
    # Test 4: Check network resolution
    print(f"\n5️⃣ Checking network resolution...")
    import socket
    try:
        ip = socket.gethostbyname(host)
        print(f"✅ Host '{host}' resolves to: {ip}")
    except Exception as e:
        print(f"❌ Failed to resolve host: {e}")

if __name__ == "__main__":
    # Add a small delay to ensure services are ready
    print("⏳ Waiting 3 seconds for services to be ready...")
    time.sleep(3)
    asyncio.run(debug_connection())