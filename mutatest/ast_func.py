import ast
from astmonkey import visitors, transformers
import json
import random
from datasketch import MinHash, LeanMinHash

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

    return pivot_sets

def calculate_pivot_set_minhash(pivot_set):
    a = 17
    b = 59
    c = 83
    K = 15485863

    with open('./random.json') as fp:
        data = json.load(fp)

    hash_set = []

    for pivot in pivot_set:
        lca, u, v = pivot
        
        lca = lca.__class__.__name__
        u = u.__class__.__name__
        v = v.__class__.__name__

        if lca in data:
            lca_hash = data[lca]
        else:
            lca_hash = random.randint(10, 100000)
            data[lca] = lca_hash
        
        if u in data:
            u_hash = data[u]
        else:
            u_hash = random.randint(10, 100000)
            data[u] = u_hash
        
        if v in data:
            v_hash = data[v]
        else:
            v_hash = random.randint(10, 100000)
            data[v] = v_hash
        
        hash_set.append((a * lca_hash + b * u_hash + c* v_hash) % K)
    
    with open('./random.json', 'w') as fp:
        json.dump(data, fp)

    mh_a = MinHash()
    for item in hash_set:
        mh_a.update(str(item).encode('utf8'))

    return LeanMinHash(mh_a)
        

# history = {(MinHash obj) :{op : {survive_count, total_count}}), ...}
def find_similar_sets(min_hash: MinHash, history: list):

    similar_sets = []

    for item in history:      
        similarity = min_hash.jaccard(item)
        if similarity >= 0.7:
            similar_sets.append((item, history[item]))

    print('similar sets', similar_sets)

    return similar_sets


# similar sets  = [(MinHash obj, {op : {survive_count, total_count}}), ()]
def rank_mutant_operators(similar_sets):

    all_operators = []

    for item in similar_sets:
        for op in item[1]:
            print(item[1][op])
            all_operators.append((op, item[1][op]['survive_count']))
    
    ranked_operators = sorted(all_operators, key=lambda x: x[1], reverse=True)

    print("ranked operators", ranked_operators)

    op_set = set()

    unique_ranked_operators = []

    for item in ranked_operators:
        if item[0] not in op_set:
            unique_ranked_operators.append(item[0])
            op_set.add(item[0])
    
    return unique_ranked_operators
