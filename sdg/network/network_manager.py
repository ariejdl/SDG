
from node_types import create_node
from edge_types import create_edge
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

    def add_node(self, model):
        if model['id'] in self.nodes or model['id'] in self.G.nodes:
            raise Exception('node already in network')
        self.G.add_node(model['id'])
        self.nodes[model['id']] = create_node(model)

    def add_edge(self, model1, model2):
        key = sorted([model1['id'], model['id']])
        if key in self.edges or key in self.G.edges:
            raise Exception('edge already in network')
        self.G.add_edge(*key)
        self.edges[key] = create_edge(model1, model2)

    def remove_node(self, _id):
        if _id not in self.nodes or _id not in self.G.nodes:
            raise Exception('node not found')
        for e in list(self.G.edges(_id)):
            self.remove_edge(*e)
        del self.nodes[_id]
        self.G.remove_node(_id)

    def remove_edge(self, id1, id2):
        key = sorted([id1, id2])
        if key not in self.edges or key not in self.G.edges:
            raise Exception('edge not found')
        self.G.remove_edge(*key)
        del self.edges[key]

    def update_node(self, model):
        current = self.nodes[model['id'])
        mod = current.ser_instance()
        mod.update(model)
        current.deser_instance(mod)

    def update_edge(self, model):
        current = self.edges[model['id'])
        mod = current.ser_instance()
        mod.update(model)
        current.deser_instance(mod)
        
    def deserialize(self, model):
        self.G = nx.from_dict_of_lists(model['network'])
        self.nodes = dict([(node.id, node.deser_instance()) for node in model['nodes']])
        self.edges = dict([(edge.id, edge.deser_instance()) for edge in model['edges']])

    def serialize(self):
        return {
            'model': nx.to_dict_of_lists(self.G),
            'nodes': [node.ser_instance() for node in self.nodes.values()],
            'edge': [edge.ser_instance() for edge in self.edgesvalues()]
        }

    def validate(self):
        """
        validate the entire network,
        including if all edges can be implemented given node types, they may be incompatible
        """
        raise NotImplementedError()

class NetworkManager(object):

    def __init__(self):
        self.networks = {}
