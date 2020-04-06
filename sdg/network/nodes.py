
import json

# TODO: easy way to ser and deser different types

def create_node(**kwargs):
    # TODO: python instance form dictionar
    if model['type'] == 'xyz':
        pass
    return Node(**kwargs)

class Node(object):

    _model = {}
    _id = None

    # nullable, 1-3, useful for resolution code emission
    _size = None

    def __init__(self, **kwargs):
        self.deser_instance(**kwargs)

    @property
    def id(self):
        if _id is None:
            raise ValueError("_id not set")
        return _id

    def ser_instance(self):
        return {
            'id': self._id,
            'model': self._model
        }

    def deser_instance(self, **kwargs):
        self._id = kwargs['id']
        self._model = kwargs['model']
    
    @property
    def language(self):
        raise NotImplementedError()

    def emit_code(self):
        raise NotImplementedError()

    def library_dependencies(self):
        return []
    

class PyNode(Node):
    
    @property
    def language(self):
        return 'python3'

class JSNode(Node):
    
    @property
    def language(self):
        return 'javascript'


class RESTNode(PyNode):
    _size = 3
