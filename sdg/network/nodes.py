
import json
from .utils import camel_to_snake
import types

_classes = {}

def register_class(cls):
    nn = cls.node_name()
    if nn in _classes:
        raise Exception('class name already seen: {}'.format(nn))
    _classes[nn] = cls
    return cls

def create_node(model, type=None):
    """
    factory for nodes, this is how deserialization is done
    """
    C = _classes.get(type)
    if C is None:
        raise Exception('invalid "type" specified: {}'.format(type))
    return C(model)

JS_HELPERS = {
    'function': '''({}) => {
      {}
    }''',
    'body_load': '''document.addEventListener("DOMContentLoaded", function() {
      {}
    });
    '''
}

class Code():
    language = None # invalid
    file_name = None # anon
    content = None
    has_symbol = False
    node_id = None
    
    def __init__(self, **kwargs):
        self.language = kwargs.get('language')
        self.file_name = kwargs.get('file_name')
        self.content = kwargs.get('content')
        self.has_symbol = kwargs.get('has_symbol', False)
        self.node_id = kwargs['node_id']

class Node(object):
    """
    note that nodes will have different characteristics when "static" versus when "running", i.e. after
    code has been emitted and has started execution, rather than before code has even been emitted
    """

    # default values where they are not supplied
    expected_model = {}
    model = {}
    language = None

    # indicates scale from variable -> module/program
    size = 0

    # other nodes which are created by this one if not in a part of its network
    required_nodes = []

    # other nodes which cannot be part of its compilation/code-emission without some kind of separation
    node_mutual_exclusions = []

    # language libraries
    library_dependencies = []

    def __init__(self, model):
        self.deserialize(model)

    @classmethod
    def node_name(cls):
        return camel_to_snake(cls.__name__)

    def serialize(self, id_):
        return {
            'id': id_,
            'type': self.node_name(),
            'model': dict(self.model.items())
        }

    def deserialize(self, model):
        self.model = model
    
    def emit_code(self):
        raise NotImplementedError()

    def get_implicit_nodes_and_edges(self, node_id, neighbours):
        return []

    def resolve(self, node_id):
        # return Code[]
        return []
    

class PyNode(Node):
    language = 'python3'

class JSNode(Node):
    language = 'javascript'

class MappingNode(JSNode):
    """
    this is the D3'esque mapping/binding of data to a visual
    """
    size = 1

@register_class
class MappingScalarNode(MappingNode):
    pass

@register_class
class MappingCoordinateSystemNode(MappingNode):
    pass

@register_class
class MappingNetworkNode(MappingNode):
    pass

@register_class
class MappingTableNode(MappingNode):
    pass

@register_class
class MappingLookupNode(MappingNode):
    pass

@register_class
class MappingTreeNode(MappingNode):
    pass

@register_class
class MappingListNode(MappingNode):
    pass

@register_class
class GeneralServerNode(Node):
    size = 4

class WebServerNode(Node):
    size = 3

    # note this may come from config file node
    expected_model = {
        'port': int
    }

@register_class
class NginxServerNode(WebServerNode):
    expected_model = {
        'port': int,
        'config': None
    }
    
@register_class
class GeneralClientNode(Node):
    size = 4

@register_class
class JSClientNode(JSNode, GeneralClientNode):
    size = 3

    expected_model = {
        'html_uri': str,
        'js_uris': list
    }

    def get_implicit_nodes_and_edges(self, node_id, neighbours):
        have_html = False
        have_js = False
        out = []

        # might this cause problems if no other validation is done on neighbour to detect it?
        # e.g. if only one appropriate neighbour, then this could be the correct approach...
        # ...may need a specific edge... e.g. 'host' page
        
        for n, e in neighbours:
            if type(n) is FileNode:
                if n.model.get('mime_type') == 'text/html':
                    have_html = True
                if n.model.get('mime_type') == 'text/javascript':
                    have_js = True

        if not have_html:
            # create_edge...
            out.append(create_node({ 'mime_type': 'text/html' }, type='file_node'))
            pass

        
        if not have_js:
            pass
            
        return out

    def resolve(self, node_id):
        out = super().resolve(node_id)
        
        self.expected_model
        if self.model.get('html_uri') is None:
            out.append(Code(node_id=node_id, has_symbol=False, language='html', file_name='index.html', content="""
            <!html>
              <html>
                <head>
                </head>
              <body>
              </body>
            </html>
            """))
        
        

        return out
        

    
@register_class
class ConfigFileNode(Node):
    size = 1

@register_class
class URI_Node(Node):
    size = 1
    
@register_class
class FileNode(Node):
    """
    could be any type of file, e.g. csv/json
    """
    size = 2

    expected_model = {
        'path': None, # optional
        'content': None, # optional
        'mime_type': None # optional
    }

@register_class
class LargeFileNode(Node):
    """
    could be any type of file, but noteworthy that it is large and can be treated differently
    """
    size = 2
    
@register_class
class StaticServerNode(WebServerNode):
    size = 3

    expected_model = {
        'directory': str
    }

    def resolve(self, node_id):
        return super().resolve(node_id)


@register_class
class PyStaticServerNode(PyNode, StaticServerNode):
    pass

@register_class
class PyFlaskServerNode(PyNode, WebServerNode):
    pass

@register_class
class PyTornadoServerNode(PyNode, WebServerNode):
    pass
    
@register_class
class PyRESTNode(PyNode):
    size = 2

    expected_model = {
        'route': str,
        'get': types.FunctionType,
        'post': types.FunctionType,
        'put': types.FunctionType,
        'patch': types.FunctionType,
        'delete': types.FunctionType,
    }

class JSVisualNode(JSNode):
    size = 1

@register_class
class JS_D3Node(JSVisualNode):
    size = 2

    expected_model = {
        'object': str,
        'chain': dict
    }
    
@register_class
class JS_CanvasNode(JSVisualNode):
    pass

@register_class
class JS_SVGNode(JSVisualNode):
    pass
