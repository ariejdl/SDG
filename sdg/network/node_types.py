
def create_node(model):
    # TODO: python instance form dictionar
    if model['node_type'] == 'xyz':
        pass
    n = NodeType()
    n.deser_instance(model)

class NodeType(object):

    _id = None

    def __init__(self, **kwargs):
        self._id = kwargs['id']

    @property
    def id(self):
        if _id is None:
            raise ValueError("_id not set")
        return _id

    def ser_instance(self):
        raise NotImplementedError()

    def deser_instance(self, model):
        raise NotImplementedError()
    
    @property
    def language(self):
        raise NotImplementedError()

    def emit_code(self):
        raise NotImplementedError()

    def library_dependencies(self):
        return []
    

class PyNodeType(NodeType):
    
    @property
    def language(self):
        return 'python3'

class JSNodeType(NodeType):
    
    @property
    def language(self):
        return 'javascript'
