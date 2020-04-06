
import json
from .utils import camel_to_snake

_classes = {}

def register_class(cls):
    _classes[cls.node_name()] = cls
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

    # for choosing between nodes during resolution, simpler is better
    _complexity_estimate = None

    _library_dependencies = []

    def __init__(self, model):
        self.deserialize(model)

    @classmethod
    def node_name(cls):
        return camel_to_snake(cls.__name__)

    def serialize(self, _id):
        return {
            'id': _id,
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
        raise NotImplementedError()
    

class PyNode(Node):
    _language = 'python3'

class JSNode(Node):
    _language = 'javascript'


@register_class
class PyRESTNode(PyNode):
    _size = 3
