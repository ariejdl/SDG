
import json
from .utils import camel_to_snake

_classes = {}

def register_class(cls):
    _classes[cls.edge_name()] = cls    
    return cls

def create_edge(model, type=None):
    C = _classes.get(type)
    if type is not None and C is None:
        raise Exception('invalid edge type given: {}'.format(type))
    if C is None:
        C = _classes['default_edge']
    return C(model)

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
    

@register_class
class DefaultEdge(Edge):
    pass

@register_class
class RESTEdge(Edge):
    pass

@register_class
class MappingEdge(Edge):
    """
    this is the D3'esque mapping/binding of data to a visual
    """
