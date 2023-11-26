import ast
from astmonkey import visitors, transformers

def find_node(node_to_find, tree_node):

    if node_to_find.loc_idx.ast_class == tree_node.__class__.__name__ and node_to_find.loc_idx.lineno == tree_node.lineno and node_to_find.loc_idx.col_offset == tree_node.col_offset:
        return tree_node

    for child_node in tree_node.children:
        found_node = find_node(node_to_find, child_node)
        if found_node:
            return found_node
    
    return None

def find_nodes_at_distance_k(node, k, final_ans, visited = {}):
    
    if node == None or k == 0 or node in visited:
        return
    
    final_ans.append(node)
    visited[node] = True

    find_nodes_at_distance_k(node.parent, k-1, final_ans, visited)

    for child in node.children:
        find_nodes_at_distance_k(child, k-1, final_ans, visited)



def build_ast(mutation_samples: list):

    ast_map = {}

    for mutation_sample in mutation_samples:

        source_path = mutation_sample.source_path
        if source_path not in ast_map:
            with open(source_path, "rb") as src_stream:
                ast_tree = ast.parse(src_stream.read())
                node = transformers.ParentChildNodeTransformer().visit(ast_tree)
                # visitor = visitors.GraphNodeVisitor()
                # visitor.visit(node)
                # visitor.graph.write_png('graph.png')

                ast_map[source_path] = node
    
    return ast_map

def find_LCA(node_a, node_b):

    ancestor_path = []

    while node_a is not None:
        ancestor_path.append(node_a)
        node_a = node_a.parent

    while node_b is not None:
        if node_b in ancestor_path:
            return node_b
        node_b = node_b.parent
    
    return None

def calculate_pivot_set(mutation_sample, ast_map):

    source_path = mutation_sample.source_path

    mutation_node_in_tree = find_node(mutation_sample, ast_map[source_path])

    nodes_at_distance_k = []
    k = 5
    find_nodes_at_distance_k(mutation_node_in_tree, k, nodes_at_distance_k)

    pivot_sets = []
    i = 0

    while i < len(nodes_at_distance_k):
        j = 0
        while j < len(nodes_at_distance_k):
            if j != i:
                node_a, node_b = nodes_at_distance_k[i], nodes_at_distance_k[j]
                lca = find_LCA(node_a, node_b)

                if lca is not None and (lca, node_b, node_a) not in pivot_sets:
                    pivot_sets.append((lca, node_a, node_b))
            
            j += 1
        i += 1

    print(pivot_sets)

