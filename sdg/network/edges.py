
import json
from .utils import camel_to_snake, register_edge, create_edge

class Edge(object):

    model = None

    def __init__(self, model):
        self.deserialize(model)

    @classmethod
    def edge_name(cls):
        return camel_to_snake(cls.__name__)
    
    def serialize(self, id1_, id2_):
        return {
            'id1': id1_,
            'id2': id2_,
            'type': self.edge_name(),
            'model': dict(self.model.items())
        }

    def deserialize(self, model):
        self.model = model
    
    def emit_code(self):
        raise NotImplementedError()

    def library_dependencies(self):
        return []
    

@register_edge
class DefaultEdge(Edge):
    pass

@register_edge
class RESTEdge(Edge):
    pass

@register_edge
class MappingEdge(Edge):
    """
    this is the D3'esque mapping/binding of data to a visual
    """
