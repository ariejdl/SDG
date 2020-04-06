
from .nodes import create_node
from .edges import create_edge
import networkx as nx

class Network(object):
    """
    a graph/network of node types, does not need to be a connected network
    """

    def __init__(self, model=None):
        if model is not None:
            self.deserialize(model)
        else:
            # not a directed graph
            self.G = nx.Graph()
            self.nodes = {}
            self.edges = {}

    def genid(self):
        if len(self.G.nodes):
            return max(self.G.nodes) + 1
        else:
            return 1

    def add_node(self, id=None, model=None, type=None):
        if id is None:
            id = self.genid()

        if id in self.nodes or id in self.G.nodes:
            raise Exception('node already in network')
        self.G.add_node(id)
        self.nodes[id] = create_node(model=model, type=type)

    def add_edge(self, id1=None, id2=None, model=None, type=None):
        if id1 is None:
            id1 = self.genid()
        if id2 is None:
            id2 = self.genid()

        if id1 not in self.G.nodes or id2 not in self.G.nodes:
            raise Exception('edge\'s nodes not found in network')
        
        key = tuple(sorted([id1, id2]))
        if key in self.edges or key in self.G.edges:
            raise Exception('edge already in network')
        self.G.add_edge(*key)
        self.edges[key] = create_edge(model=model, type=type)

    def remove_node(self, id):
        if id not in self.nodes or id not in self.G.nodes:
            raise Exception('node not found')
        for e in list(self.G.edges(id)):
            self.remove_edge(*e)
        del self.nodes[id]
        self.G.remove_node(id)

    def remove_edge(self, id1, id2):
        key = tuple(sorted([id1, id2]))
        if key not in self.edges or key not in self.G.edges:
            raise Exception('edge not found')
        self.G.remove_edge(*key)
        del self.edges[key]

    def update_node(self, id, model):
        current = self.nodes[id]
        current.deserialize(mod['model'])

    def update_edge(self, id1, id2, model):
        if id1 not in self.G.nodes or id2 not in self.G.nodes:
            raise Exception('edge\'s nodes not found in network')
        
        key = tuple(sorted([id1, id2]))
        current = self.edges[key]
        current.deserialize(mod['model'])
        
    def deserialize(self, model):
        self.G = nx.Graph()
        self.nodes = {}
        self.edges = {}

        for node in model['nodes']:
            self.add_node(**node)

        for edge in model['edges']:
            self.add_edge(**edge)
            
        self.nodes = dict([(node['id'], create_node(
            node['model'], type=node['type'])) for node in model['nodes']])
        self.edges = dict([((edge['id1'], edge['id2']),
                            create_edge(edge['model'], type=edge['type']))
                           for edge in model['edges']])

    def serialize(self):
        return {
            'nodes': [node.serialize(id) for (id, node) in self.nodes.items()],
            'edges': [edge.serialize(*key) for (key, edge) in self.edges.items()]
        }

    def validate(self):
        """
        validate the entire network,
        including if all edges can be implemented given node types, they may be incompatible
        """
        raise NotImplementedError()

class NetworkManager(object):
    """
    currently open "network" files
    """

    def __init__(self, model):
        self.networks = dict([
            (n['path'], Network(n['network'])) for n in model['networks']])

    def get(self, path):
        return self.networks[path]

    def create(self, path):
        if path in self.networks:
            raise Exception('path already in use')
        n = Network()
        self.networks[path] = n
        return n

    def delete(self, path):
        del self.networks[path]
