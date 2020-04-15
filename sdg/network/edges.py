
import json
from .utils import camel_to_snake

_classes = {}

def register_class(cls):
    _classes[cls.edge_name()] = cls    
    return cls

def create_edge(model, type=None, edge_meta=None):
    C = _classes.get(type)
    if type is not None and C is None:
        raise Exception('invalid edge type given: {}'.format(type))
    if C is None:
        C = _classes['default_edge']
    return C(model, edge_meta)

class Edge(object):

    _model = None
    _edge_meta = None

    def __init__(self, model, edge_meta=None):
        self.deserialize(model, edge_meta)

    @classmethod
    def edge_name(cls):
        return camel_to_snake(cls.__name__)
    
    def serialize(self, id1_, id2_):
        return {
            'id1': id1_,
            'id2': id2_,
            'type': self.edge_name(),
            'model': dict(self._model.items()),
            'edge_meta': dict(self._edge_meta.items()) if self._edge_meta is not None else None
        }

    def deserialize(self, model, edge_meta):
        self._model = model
        self._edge_meta = edge_meta
    
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

@register_class
class MappingTransformEdge(MappingEdge):
    pass
