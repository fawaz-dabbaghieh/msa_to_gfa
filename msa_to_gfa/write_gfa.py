import logging
import os


def write_gfa(graph, gfa_path):
    """
    output the graph as a gfa file

    :param graph: a graph object
    :param gfa_path: the output gfa file name/path
    """
    # maybe a dictionary of nodes and their classes
    # then a function that reads these colors and make an upset plot or something
    nodes = graph.nodes
    if os.path.exists(gfa_path):
        logging.warning("overwriting {} file".format(gfa_path))

    f = open(gfa_path, "w+")

    for node in nodes.values():
        line = str("\t".join(("S", str(node.id), node.seq, "LN:i:" + str(len(node.seq)))))

        f.write(line + "\n")

        for child in node.out_nodes:
            edge = str("\t".join(("L", str(node.id), "+", str(child.id),
                       "+", "0M")))
            f.write(edge + "\n")

    if len(graph.paths) != 0:
        for p_name, nodes_in_path in graph.paths.items():
            path = ["P", p_name]
            n_nodes = len(nodes_in_path)
            path.append("+,".join([str(x) for x in nodes_in_path]))
            path[-1] += "+"
            path.append(",".join(["0M"]*n_nodes))
            path = "\t".join(path)

            f.write(path + "\n")

    f.close()
