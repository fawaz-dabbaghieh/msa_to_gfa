def merge_end(nodes, n, k):
    """
    merges the end of a node if possible

    :param nodes: a dictionary of node objects
    :param n: the node to try to merge its end
    :param k: the length of the kmer
    """

    child = list(nodes[n].out_nodes)[0]

    # if child has one parent, it can be merged
    if len(child.in_nodes) == 1:
        # adding the new children to n because
        # n --> child --> child's_child
        # compact
        # n --> child's child
        nodes[n].out_nodes = set()
        for new_out in list(child.out_nodes):
            nodes[n].out_nodes.add(new_out)

        # updating sequence of n
        # I am assuming no overlaps here
        nodes[n].seq += child.seq[k-1:]

        # updating the information in children of child
        # in nodes of child's child need to be updated
        for nn in child.out_nodes:
            nn.in_nodes.remove(child)
            nn.in_nodes.add(nodes[n])

        # remove the merged node
        del nodes[child.id]

        return True

    return False


def compact_graph(graph):
    """
    compacts the graph

    :param graph: a graph object
    """
    k = graph.k
    list_of_nodes = list(graph.nodes.keys())

    for n in list_of_nodes:
        if n in graph.nodes:
            while True:
                # only one child (maybe can be merged)
                if len(graph.nodes[n].out_nodes) == 1:
                    if not merge_end(graph.nodes, n, k):
                        break
                else:
                    break
