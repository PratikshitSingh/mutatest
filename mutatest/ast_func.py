import ast
from astmonkey import visitors, transformers

def find_node(node_to_find, tree_node):

    print(node_to_find.loc_idx.ast_class == tree_node.__class__.__name__)

    if node_to_find.loc_idx.ast_class == tree_node.__class__.__name__ and node_to_find.loc_idx.lineno == tree_node.lineno and node_to_find.loc_idx.col_offset == tree_node.col_offset:
        return tree_node

    for child_node in tree_node.children:
        found_node = find_node(node_to_find, child_node)
        if found_node:
            return found_node
    
    return None


def build_ast(mutation_samples: list):

    ast_map = {}

    for mutation_sample in mutation_samples:

        source_path = mutation_sample.source_path
        if source_path not in ast_map:
            with open(source_path, "rb") as src_stream:
                ast_tree = ast.parse(src_stream.read())
                node = transformers.ParentChildNodeTransformer().visit(ast_tree)

                ast_map[source_path] = node
    
    return ast_map

def calculate_pivot_set(mutation_sample, ast_map):

    source_path = mutation_sample.source_path
    print(mutation_sample)
    found_node = find_node(mutation_sample, ast_map[source_path])
    print(found_node)