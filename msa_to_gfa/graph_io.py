import logging
import os
import sys
from msa_to_gfa.Node import Node
from msa_to_gfa.Graph import Graph


def write_gfa(graph, gfa_path, output_groups=False):
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
    if output_groups:
        if len(graph.groups) != 0:
            for p_name, nodes_in_path in graph.groups.items():
                path = ["P", p_name]
                n_nodes = len(nodes_in_path)
                path.append("+,".join([str(x) for x in nodes_in_path]))
                path[-1] += "+"
                path.append(",".join(["0M"]*n_nodes))
                path = "\t".join(path)

                f.write(path + "\n")

    f.close()


def read_gfa(gfa_path, colored=False):
    """
    read a gfa file and store the information in nodes dictionary

    :param gfa_path: path to the graph file to read
    :param colored: if True, then colors for each node are read and stored
    """
    if not os.path.exists(gfa_path):
        print("Error happened, aborting!!! Please check log file")
        logging.error("The file {} does not exist".format(gfa_path))
        sys.exit(1)

    nodes = dict()
    edges = []
    with open(gfa_path, "r") as in_graph:
        for line in in_graph:

            if line.startswith("S"):  # a node (Segment)
                line = line.strip().split()

                # 1 would be the identifier and 2 is the sequence
                ident = int(line[1])
                nodes[ident] = Node(ident, line[2])
                if colored:
                    nodes[ident].colors = set(line[3].split(":"))

            elif line[0] == "L":  # an edge
                edges.append(line)

        for e in edges:
            # assuming all forward nodes here because directed aa graph (no reverse complement)
            # and the graph represent the protein (from beginning to end of MSA)
            e = e.strip().split()
            parent = int(e[1])
            child = int(e[3])
            if (parent in nodes) and (child in nodes):
                nodes[parent].add_child(nodes[child])
            else:
                logging.warning(f"The edge between {parent} and {child} can't be added, one of these two nodes (or "
                                f"both) do not exist")

    return Graph(nodes, dict())
