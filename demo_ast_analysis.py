#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.delphi_ast_analyzer import DelphiASTAnalyzer


def demo_analysis():
    analyzer = DelphiASTAnalyzer()
    
    # サンプルコードを読み込む
    with open("sample_delphi_code.pas", "r") as f:
        code = f.read()
    
    print("=== Delphi AST Analysis Demo ===\n")
    
    # クラスの抽出
    print("📦 Classes found:")
    print("-" * 40)
    classes = analyzer.extract_classes(code)
    for cls in classes:
        print(f"  • {cls['name']} (line {cls['line']})")
    
    # 関数/プロシージャの抽出（インターフェース部のみ）
    print("\n📋 Interface Methods:")
    print("-" * 40)
    functions = analyzer.extract_functions(code)
    interface_funcs = [f for f in functions if f['line'] < 35]  # implementation前
    for func in interface_funcs:
        print(f"  • {func['type']:12} {func['name']:20} (line {func['line']})")
    
    # 実装部のメソッド
    print("\n🔧 Implementation Methods:")
    print("-" * 40)
    impl_funcs = [f for f in functions if f['line'] >= 35]
    for func in impl_funcs:
        print(f"  • {func['type']:12} {func['name']:20} (line {func['line']})")
    
    # 統計情報
    print("\n📊 Statistics:")
    print("-" * 40)
    print(f"  Total classes:     {len(classes)}")
    print(f"  Total methods:     {len(functions)}")
    print(f"  Interface methods: {len(interface_funcs)}")
    print(f"  Implementation:    {len(impl_funcs)}")
    
    # 特定のノードタイプの検索例
    tree = analyzer.parse_code(code)
    print("\n🔍 AST Node Types Found:")
    print("-" * 40)
    
    # 変数宣言
    var_nodes = analyzer.find_nodes_by_type(tree.root_node, "declVar")
    print(f"  Variable declarations: {len(var_nodes)}")
    
    # フィールド宣言
    field_nodes = analyzer.find_nodes_by_type(tree.root_node, "declField")
    print(f"  Field declarations:    {len(field_nodes)}")
    
    # プロパティ宣言
    prop_nodes = analyzer.find_nodes_by_type(tree.root_node, "declProp")
    print(f"  Property declarations: {len(prop_nodes)}")
    
    # Uses句
    uses_nodes = analyzer.find_nodes_by_type(tree.root_node, "declUses")
    print(f"  Uses clauses:          {len(uses_nodes)}")
    
    print("\n✅ Analysis completed successfully!")


if __name__ == "__main__":
    demo_analysis()