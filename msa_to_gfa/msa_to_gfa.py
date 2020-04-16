from .Node import Node
from .Graph import Graph


def sync_lists(nodes, current, previous):
    """
    syncing the previous column and current column lists

    The idea is that we have 4 possibilities for each row
    And 0 represent when we have a gap "-"
    1- previous has no node (has 0) and current is some amino acid
    nothing to do here

    2- previous position is a node and current is 0
    push the previous node to current replacing 0

    3- previous 0 and current 0
    nothing to do

    4- previous position is a node and current is a node
    connect them with an edge

    :param nodes: a dictionary of node ids and objects
    :param current: a list with nodes in the current column
    :param previous: a list with nodes in the previous column
    """

    # todo the same node shouldn't have a self loop
    for i in range(len(current)):  # they both have the same size
        if (current[i] == 0) and (previous[i] != 0):
            # in case there was an amino acid in some sequence
            # then there's a gap, I push this amino acid (which is a node now)
            # to the next list, and I keep pushing it until the gap ends
            # so I can connect it with the next amino acid (node)
            current[i] = previous[i]

        # adding edges
        elif (current[i] != 0) and (previous[i] != 0):
            nodes[previous[i]].add_child(nodes[current[i]])

        else:
            pass
        # previous is current now and we have a new current
        # previous = current
        # current = [0] * len(previous)


def msa_graph(sequences, seq_names):
    """
    build graph from MSA

    :param sequences: sequences dictionary
    :param seq_names: a dictionary of name of sequence in fasta file and potential shorter name
    """
    nodes = dict()
    previous_nodes = [0] * len(sequences)
    current_nodes = [0] * len(sequences)
    node_id = 1
    len_seq = len(sequences[list(sequences.keys())[0]])
    seq_names_keys = list(sequences.keys())

    for j in range(len_seq):

        # sync previous and current
        sync_lists(nodes, current_nodes, previous_nodes)
        previous_nodes = current_nodes
        current_nodes = [0] * len(previous_nodes)

        column = [x[j] for x in sequences.values()]
        already_seen = dict()

        for i, aa in enumerate(column):

            if aa != "-":
                if aa in already_seen.keys():

                    # adding the same amino acid at the same position
                    # this returns the last node created in this column with
                    # the same amino acid
                    node = nodes[already_seen[aa]]
                    color = seq_names[seq_names_keys[i]]
                    node.colors.add(color)
                    current_nodes[i] = node.id
                    # node = lists_of_nodes[already_seen[aa]][-1]
                    # color = seq_names[seq_names_keys[i]]
                    # node.colors.add(color)
                    # lists_of_nodes[i].append(color)

                else:
                    # make a new node
                    node = Node(node_id, aa)
                    color = seq_names[seq_names_keys[i]]
                    node.colors.add(color)
                    nodes[node_id] = node
                    current_nodes[i] = node_id
                    # this tell me where I already saw this aa
                    # in which sequence (basically in which row)
                    already_seen[aa] = node_id
                    # creating a new node
                    # node = Node(node_id, aa)
                    # color = seq_names[seq_names_keys[i]]
                    # node.colors.add(color)
                    # nodes[node_id] = node
                    # already_seen[aa] = i
                    node_id += 1
                    # previous_nodes[i] = node

    # syncing last column
    sync_lists(nodes, current_nodes, previous_nodes)
    # for l in lists_of_nodes:
    #     for idx in range(len(l) - 1):
    #         if l[idx+1] not in l[idx].out_nodes:
    #             l[idx].add_child(l[idx+1])
    #
    graph = Graph(nodes)
    # samples = list(sequences.keys())
    # for i in range(len(lists_of_nodes)):
    #     graph.paths[samples[i]] = lists_of_nodes[i]

    return graph
