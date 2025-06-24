import tree_sitter
import tree_sitter_pascal
from typing import Dict, List, Any, Optional
import json


class DelphiASTAnalyzer:
    def __init__(self):
        self.parser = tree_sitter.Parser(tree_sitter.Language(tree_sitter_pascal.language()))
        
    def parse_code(self, code: str) -> tree_sitter.Tree:
        return self.parser.parse(bytes(code, "utf8"))
    
    def extract_node_info(self, node: tree_sitter.Node) -> Dict[str, Any]:
        return {
            "type": node.type,
            "text": node.text.decode("utf8") if node.text else "",
            "start_point": {"row": node.start_point[0], "column": node.start_point[1]},
            "end_point": {"row": node.end_point[0], "column": node.end_point[1]},
            "children": [self.extract_node_info(child) for child in node.children]
        }
    
    def analyze_ast(self, code: str) -> Dict[str, Any]:
        tree = self.parse_code(code)
        return self.extract_node_info(tree.root_node)
    
    def find_nodes_by_type(self, node: tree_sitter.Node, node_type: str) -> List[tree_sitter.Node]:
        results = []
        if node.type == node_type:
            results.append(node)
        for child in node.children:
            results.extend(self.find_nodes_by_type(child, node_type))
        return results
    
    def extract_functions(self, code: str) -> List[Dict[str, Any]]:
        tree = self.parse_code(code)
        function_nodes = self.find_nodes_by_type(tree.root_node, "declProc")
        function_defs = self.find_nodes_by_type(tree.root_node, "defProc")
        
        functions = []
        for node in function_nodes + function_defs:
            func_type = "unknown"
            name = "unknown"
            
            for child in node.children:
                if child.type in ["kFunction", "kProcedure", "kConstructor", "kDestructor"]:
                    func_type = child.type[1:].lower()  # Remove 'k' prefix
                elif child.type == "identifier":
                    name = child.text.decode("utf8")
                elif child.type == "genericDot":
                    # For implementation section: ClassName.MethodName
                    for subchild in child.children:
                        if subchild.type == "identifier" and subchild.next_sibling and subchild.next_sibling.type != ".":
                            name = subchild.text.decode("utf8")
            
            if name != "unknown":
                functions.append({
                    "type": func_type,
                    "name": name,
                    "line": node.start_point[0] + 1,
                    "full_text": node.text.decode("utf8")[:100] + "..."
                })
        
        return functions
    
    def extract_classes(self, code: str) -> List[Dict[str, Any]]:
        tree = self.parse_code(code)
        type_nodes = self.find_nodes_by_type(tree.root_node, "declType")
        
        classes = []
        for node in type_nodes:
            name = "unknown"
            is_class = False
            
            for child in node.children:
                if child.type == "identifier":
                    name = child.text.decode("utf8")
                elif child.type == "declClass":
                    is_class = True
            
            if is_class and name != "unknown":
                classes.append({
                    "name": name,
                    "line": node.start_point[0] + 1,
                    "full_text": node.text.decode("utf8")[:200] + "..."
                })
        
        return classes
    
    def print_ast_tree(self, node: tree_sitter.Node, indent: int = 0) -> None:
        print("  " * indent + f"{node.type}: {node.text.decode('utf8')[:50] if node.text else ''}")
        for child in node.children:
            self.print_ast_tree(child, indent + 1)