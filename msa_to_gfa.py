from Node import Node
from Graph import Graph
import pdb


def msa_graph(sequences):
    """
    build graph from MSA

    :param sequences: sequences dictionary
    """
    nodes = dict()
    lists_of_nodes = [[] for i in sequences]

    node_id = 1

    len_seq = len(sequences[list(sequences.keys())[0]])
    for i in range(len_seq):
        column = [x[i] for x in sequences.values()]
        already_seen = dict()
        for idx, j in enumerate(column):
            if j != "-":
                if j in already_seen:
                    # pdb.set_trace()
                    # adding the same amino acid at the same position
                    lists_of_nodes[idx].append(lists_of_nodes[already_seen[j]][-1])

                else:
                    # creating a new node
                    node = Node(node_id, j)
                    node.colors = "class " + str(idx)
                    nodes[node_id] = node
                    already_seen[j] = idx
                    node_id += 1
                    lists_of_nodes[idx].append(node)

    for l in lists_of_nodes:
        for idx in range(len(l) - 1):
            if l[idx+1] not in l[idx].out_nodes:
                l[idx].add_child(l[idx+1])

    graph = Graph(nodes)
    samples = list(sequences.keys())
    for i in range(len(lists_of_nodes)):
        graph.paths[samples[i]] = lists_of_nodes[i]

    return graph
