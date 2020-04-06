
import json

# TODO: easy way to ser and deser different types

def create_edge(**kwargs):
    # TODO: python instance form dictionary
    if kwargs['type'] == 'xyz':
        pass
    return Edge(**kwargs)

class Edge(object):

    _id1 = None
    _id2 = None
    _model = None

    def __init__(self, **kwargs):
        self.deser_instance(**kwargs)

    def ser_instance(self):
        return {
            'id1': self._id1,
            'id2': self._id2,
            'model': self._model
        }

    def deser_instance(self, **kwargs):
        self._id1 = kwargs['id1']
        self._id2 = kwargs['id2']
        self._model = kwargs['model']
    
    def emit_code(self):
        raise NotImplementedError()

    def library_dependencies(self):
        return []
    

class RESTEdge(Edge):
    pass
