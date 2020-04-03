
class NodeType(object):

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
