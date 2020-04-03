
import networkx

class Network(object):
    """
    a graph/network of node types, does not need to be a connected network
    """

    def add_node(self):
        raise NotImplementedError()

    def add_edge(self):
        raise NotImplementedError()

    def remove_node(self):
        raise NotImplementedError()

    def remove_edge(self):
        raise NotImplementedError()

    def update_node(self):
        raise NotImplementedError()

    def update_edge(self):
        raise NotImplementedError()
        
    def deserialize(self):
        raise NotImplementedError()

    def serialize(self):
        raise NotImplementedError()

class NetworkManager(object):

    def __init__(self):
        self.networks = {}
