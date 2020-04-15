import logging
import os


def write_gfa(graph, gfa_path, colored=False):
    """
    output the graph as a gfa file

    :param graph: a graph object
    :param gfa_path: the output gfa file name/path
    :param colored: If I want to output the classes too
    """
    # maybe a dictionary of nodes and their classes
    # then a function that reads these colors and make an upset plot or something
    k = graph.k
    nodes = graph.nodes
    if os.path.exists(gfa_path):
        logging.warning("overwriting {} file".format(gfa_path))

    overlap = str(k-1) + "M"
    f = open(gfa_path, "w+")

    for node in nodes.values():
        if not colored:
            line = str("\t".join(("S", str(node.id), node.seq)))
        else:
            colors = "|".join(list(node.colors))
            line = str("\t".join(("S", str(node.id), node.seq, colors)))
        f.write(line + "\n")

        for child in node.out_nodes:
            edge = str("\t".join(("L", str(node.id), "+", str(child.id),
                       "+", overlap)))
            f.write(edge + "\n")

    if len(graph.paths) != 0:
        for p_name in graph.paths.keys():
            segment = []
            for n in graph.paths[p_name]:
                if n.id in graph.nodes:
                    segment.append(n.id)
            segment = ",".join([str(x) + "+" for x in segment])
            # pdb.set_trace()
            # segment = ",".join([str(x.id) + "+" for x in graph.paths[p_name]])
            overlaps = "0M," * (len(graph.paths[p_name]) - 1)
            overlaps = overlaps[0:len(overlaps) - 1]
            out_path = "\t".join(["P", p_name, segment, overlaps])
            # pdb.set_trace()
            f.write(out_path + "\n")

    f.close()
