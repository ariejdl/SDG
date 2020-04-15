
import json
from .utils import camel_to_snake

_classes = {}

def register_class(cls):
    nn = cls.node_name()
    if nn in _classes:
        raise Exception('class name already seen: {}'.format(nn))
    _classes[nn] = cls
    return cls

def create_node(model, type=None):
    C = _classes.get(type)
    if C is None:
        raise Exception('invalid "type" specified: {}'.format(type))
    return C(model)

class Node(object):

    _model = {}
    _language = None

    # nullable, 1-3, useful for resolution code emission
    _size = None

    # e.g. a DB query
    _async = False

    # for choosing between nodes during resolution, simpler is better
    _complexity_estimate = None

    _library_dependencies = []

    def __init__(self, model):
        self.deserialize(model)

    @classmethod
    def node_name(cls):
        return camel_to_snake(cls.__name__)

    def serialize(self, id_):
        return {
            'id': id_,
            'type': self.node_name(),
            'model': dict(self._model.items())
        }

    def deserialize(self, model):
        self._model = model
    
    @property
    def language(self):
        if self._language is None:
            raise Exception('subclass needs a "_language"')
        return self._language

    def emit_code(self):
        # TODO: would be sensible to cache the last value and clear if change
        raise NotImplementedError()
    

class PyNode(Node):
    _language = 'python3'

class JSNode(Node):
    _language = 'javascript'

@register_class
class GeneralServerNode(Node):
    _size = 4

@register_class
class GeneralClientNode(Node):
    _size = 4
    
@register_class
class ConfigFileNode(Node):
    _size = 1

@register_class
class FileNode(Node):
    _size = 2

@register_class
class StaticServerNode(Node):
    _size = 3
    
@register_class
class PyFlaskServerNode(PyNode):
    _size = 3

@register_class
class PyTornadoServerNode(PyNode):
    _size = 3
    
@register_class
class PyRESTNode(PyNode):
    _size = 3
