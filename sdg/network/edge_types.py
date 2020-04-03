
def create_edge(model1, model2):
    # TODO: python instance form dictionary
    if model['edge_type'] == 'xyz':
        pass
    n = EdgeType()
    n.deser_instance(model)
    return n

class EdgeType(object):

    _id1 = None
    _id2 = None

    def __init__(self, **kwargs):
        self._id1 = kwargs['id1']
        self._id2 = kwargs.get('id2')

    @property
    def id(self):
        if _id1 is None:
            raise ValueError("id 1 not set")
        return _id

    def ser_instance(self):
        raise NotImplementedError()

    def deser_instance(self, model):
        raise NotImplementedError()
    
    def emit_code(self):
        raise NotImplementedError()

    def library_dependencies(self):
        return []
    

class RESTEdgeType(EdgeType):
    pass
