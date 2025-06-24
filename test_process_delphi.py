#!/usr/bin/env python3
"""
Test script for Delphi code processing
"""
import os
import json
import requests
import tempfile
import shutil
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

LIGHTRAG_API_URL = os.getenv("LIGHTRAG_API_URL", "http://localhost:8080")


def create_test_delphi_files():
    """Create test Delphi files in a temporary directory"""
    temp_dir = tempfile.mkdtemp()
    
    # Create a simple PAS file
    pas_content = """unit TestUnit;

interface

type
  TTestClass = class
  private
    FValue: Integer;
  public
    constructor Create;
    destructor Destroy; override;
    procedure SetValue(AValue: Integer);
    function GetValue: Integer;
  end;

implementation

constructor TTestClass.Create;
begin
  inherited;
  FValue := 0;
end;

destructor TTestClass.Destroy;
begin
  inherited;
end;

procedure TTestClass.SetValue(AValue: Integer);
begin
  FValue := AValue;
end;

function TTestClass.GetValue: Integer;
begin
  Result := FValue;
end;

end."""
    
    # Create a simple DFM file
    dfm_content = """object Form1: TForm1
  Left = 0
  Top = 0
  Caption = 'Test Form'
  ClientHeight = 299
  ClientWidth = 635
  object Button1: TButton
    Left = 248
    Top = 136
    Width = 75
    Height = 25
    Caption = 'Click Me'
    TabOrder = 0
  end
end"""
    
    # Write files
    pas_path = Path(temp_dir) / "TestUnit.pas"
    dfm_path = Path(temp_dir) / "TestForm.dfm"
    
    with open(pas_path, 'w') as f:
        f.write(pas_content)
    
    with open(dfm_path, 'w') as f:
        f.write(dfm_content)
    
    return temp_dir


def test_processing():
    """Test the Delphi code processing pipeline"""
    print("=== Starting Delphi Code Processing Test ===")
    
    # Create test files
    test_dir = create_test_delphi_files()
    print(f"Created test files in: {test_dir}")
    
    try:
        # Run the processing script
        import subprocess
        import sys
        result = subprocess.run(
            [sys.executable, "process_delphi_code.py", test_dir],
            capture_output=True,
            text=True
        )
        
        print("\n--- Processing Output ---")
        print(result.stdout)
        if result.stderr:
            print("--- Errors ---")
            print(result.stderr)
        
        # Test querying the data
        if result.returncode == 0:
            print("\n=== Testing Query ===")
            test_query()
        
    finally:
        # Clean up
        shutil.rmtree(test_dir)
        print(f"\nCleaned up test directory: {test_dir}")


def test_query():
    """Test querying the processed data"""
    queries = [
        "What classes are defined in the code?",
        "Show me all functions and procedures",
        "What is TTestClass?"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        try:
            response = requests.post(
                f"{LIGHTRAG_API_URL}/query",
                json={"query": query, "mode": "hybrid", "stream": False},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"Response: {result.get('response', 'No response')[:200]}...")
            else:
                print(f"Query failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"Error querying: {e}")


def check_services():
    """Check if required services are running"""
    print("=== Checking Services ===")
    
    # Check LightRAG
    try:
        response = requests.get(f"{LIGHTRAG_API_URL}/docs")
        if response.status_code == 200:
            print("[OK] LightRAG is running")
        else:
            print("[FAIL] LightRAG is not responding properly")
            return False
    except:
        print("[FAIL] LightRAG is not running")
        return False
    
    # Check Qdrant
    try:
        response = requests.get("http://localhost:6333/collections")
        if response.status_code == 200:
            print("[OK] Qdrant is running")
        else:
            print("[FAIL] Qdrant is not responding properly")
            return False
    except:
        print("[FAIL] Qdrant is not running")
        return False
    
    return True


def main():
    print("=== Delphi Code Processing Test ===\n")
    
    # Check if services are running
    if not check_services():
        print("\nPlease ensure docker-compose is running:")
        print("  docker-compose up -d")
        return
    
    # Run the test
    test_processing()


if __name__ == "__main__":
    main()