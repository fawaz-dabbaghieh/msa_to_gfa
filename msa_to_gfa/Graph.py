import logging
import sys
import collections
import json
import pdb
from msa_to_gfa.topological_sorting import top_sorting
from msa_to_gfa.compact import compact_graph


class Graph:
    __slots__ = ['nodes', 'sorted', 'colors', 'groups']

    def __init__(self, nodes, groups):
        self.nodes = nodes
        self.sorted = []
        self.colors = dict()
        self.groups = groups

    def __len__(self):
        return len(self.nodes)

    def __getitem__(self, item):
        if item in self.nodes:
            return self.nodes[item]
        else:
            raise KeyError

    def __str__(self):
        for n in self.nodes.values():
            for nn in n.out_nodes:
                print("{} {} --> {} {}".format(n.id, n.seq, nn.seq, nn.id))
        return ""

    def __repr__(self):
        print(f"The graph has {len(self.nodes)} nodes and "
              f"grouped into {len(self.groups)} groups (paths)")

    def sort(self):
        """
        calls the toplogical sorting function on the graph
        """
        if not self.sorted:
            self.sorted = top_sorting(self)
            if not self.sorted:
                print("Error! Please check the log file...")
                logging.error("The graph cannot be topologically sorted")
                sys.exit()
            elif len(self.sorted) != len(self.nodes):
                print("Error! Please check the log file...")
                logging.error("The sorted list of nodes does not equal the number of nodes \n"
                              "Something went wrong, investigate please!")
                sys.exit()
        else:
            pass

    def compact(self):
        """
        compacts the linear stretches of nodes in the graph
        """
        compact_graph(self)

    def output_groups(self, out_file="groups_paths.json"):
        """
        Generates all the paths in the graph according to the nodes colors and add these paths
        to the path dictionary in the graph object
        Then merges the paths that are similar
        """
        if not self.sorted:
            self.sort()

        paths = dict()
        for n in self.sorted:
            for color in self.nodes[n].colors:
                if color not in paths:
                    paths[color] = [n]
                else:
                    paths[color].append(n)

        output = {"all_paths": paths, "groups": self.groups}

        out_file = open(out_file, "w")
        out_file.write(json.dumps(output))
        out_file.close()

    def nodes_info(self, output_file):
        """
        Dumps all the node information in a JSON file

        :param output_file: path to output file to dump the JSON object
        """
        out_file = open(output_file, "w")
        node_info = dict()
        for n in self.nodes.values():
            node_info[n.id] = dict()
            node_info[n.id]["id"] = n.id
            node_info[n.id]["colors"] = list(n.colors)
            node_info[n.id]["seq"] = n.seq

        out_file.write(json.dumps(node_info) + "\n")
        out_file.close()

    def check_path(self, path_id, path):
        """
        Checks if the path exists in the graph

        :param path: a list of node ides of the path, doesn't need to be ordered
        :param path_id: a string for the path id
        :return answer: True if path exists, otherwise, False.
        """
        ordered_path = []
        NP = collections.namedtuple('NP', 'name position')
        for n in path:
            pos = self.sorted.index(n)
            ordered_path.append(NP(name=n, position=pos))
        # this way I sort the nodes in the path according to their position in the topological sort
        ordered_path.sort(key=lambda x: x.position)

        # now I check that each node is a child of the previous one, if so, then the path exists
        for i in range(1, len(ordered_path)):
            current_node = self.nodes[ordered_path[i].name]
            previous_node = self.nodes[ordered_path[i - 1].name]
            if previous_node.is_parent_of(current_node):
                continue
            else:
                logging.error("in path {}, node {} is not a child of {}, "
                              "no continuous walk through the path".format(path_id, current_node.id, previous_node.id))
                # print("The path is not a valid path")
                return False

        return True
