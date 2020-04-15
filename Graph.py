import logging
import sys
from topological_sorting import top_sorting
from compact import compact_graph

class Graph:
    __slots__ = ['nodes', 'paths', 'sorted', 'colors']

    def __init__(self, nodes):
        self.nodes = nodes
        self.paths = dict()
        self.sorted = []
        self.colors = dict()

    def __len__(self):
        return len(self.nodes)

    def __getitem__(self, item):
        if item in self.nodes:
            return self.nodes[item]
        else:
            print("Node {} is not in the graph")
            return None

    def sort(self):
        if not self.sorted:
            self.sorted = top_sorting(self)
            if not self.sorted:
                logging.error("The graph cannot be topologically sorted")
                sys.exit()
            elif len(self.sorted) != len(self.nodes):
                logging.error("The sorted list of nodes does not equal the number of nodes \n"
                              "Something went wrong, investigate please!")
                sys.exit()
        else:
            pass

    def compact(self):
        compact_graph(self)

    def add_paths(self):
        pass