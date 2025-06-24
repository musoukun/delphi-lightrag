#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.delphi_ast_analyzer import DelphiASTAnalyzer
import json


def main():
    analyzer = DelphiASTAnalyzer()
    
    # サンプルコードを読み込む
    with open("sample_delphi_code.pas", "r") as f:
        code = f.read()
    
    print("=== Delphi AST Analysis Test ===\n")
    
    # 1. AST全体の構造を表示
    print("1. AST Structure:")
    print("-" * 50)
    ast = analyzer.analyze_ast(code)
    print(json.dumps(ast, indent=2)[:1000] + "...\n")
    
    # 2. 関数/プロシージャの抽出
    print("2. Functions and Procedures:")
    print("-" * 50)
    functions = analyzer.extract_functions(code)
    for func in functions:
        print(f"{func['type']}: {func['name']} (line {func['line']})")
    print()
    
    # 3. クラスの抽出
    print("3. Classes:")
    print("-" * 50)
    classes = analyzer.extract_classes(code)
    for cls in classes:
        print(f"Class: {cls['name']} (line {cls['line']})")
    print()
    
    # 4. AST Tree表示（簡易版）
    print("4. AST Tree (simplified):")
    print("-" * 50)
    tree = analyzer.parse_code(code)
    analyzer.print_ast_tree(tree.root_node)
    
    # 5. 特定のノードタイプを検索
    print("\n5. Specific Node Types:")
    print("-" * 50)
    
    # 変数宣言を探す
    var_declarations = analyzer.find_nodes_by_type(tree.root_node, "var_declaration")
    print(f"Variable declarations found: {len(var_declarations)}")
    
    # 型宣言を探す
    type_declarations = analyzer.find_nodes_by_type(tree.root_node, "type_declaration")
    print(f"Type declarations found: {len(type_declarations)}")
    
    # Uses句を探す
    uses_clauses = analyzer.find_nodes_by_type(tree.root_node, "uses_clause")
    print(f"Uses clauses found: {len(uses_clauses)}")
    
    print("\n=== Test completed successfully! ===")


if __name__ == "__main__":
    main()