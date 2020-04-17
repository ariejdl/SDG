
import json
from .utils import (camel_to_snake, register_node,
                    create_node, create_edge, NetworkBuildException)
import types

WEB_HELPERS = {
    'js_function': '''({args}) => {
      {body}
    }''',
    'js_body_load': '''document.addEventListener("DOMContentLoaded", function() {
      {body}
    });
    ''',
    'html_page': '''<!html>
              <html>
                <head>
                {head}
                </head>
              <body>
                {body}
              </body>
            </html>'''
}

def get_neighbours(neighbours, tests):
    out = {}
    for n,e in neighbours:
        for key, test in tests.items():
            if test(n,e) == True:
                out.setdefault(key, [])
                out[key].append(n)
    return out

class MIME_TYPES(object):
    HTML = 'text/html'
    JS = 'text/javascript'

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
        return [], []

    def resolve(self, node_id, neighbours):
        # return Code[]
        return [], []
    

class PyNode(Node):
    language = 'python3'

class JSNode(Node):
    language = 'javascript'

class MappingNode(JSNode):
    """
    this is the D3'esque mapping/binding of data to a visual
    """
    size = 1

@register_node
class MappingScalarNode(MappingNode):
    pass

@register_node
class MappingCoordinateSystemNode(MappingNode):
    pass

@register_node
class MappingNetworkNode(MappingNode):
    pass

@register_node
class MappingTableNode(MappingNode):
    pass

@register_node
class MappingLookupNode(MappingNode):
    pass

@register_node
class MappingTreeNode(MappingNode):
    pass

@register_node
class MappingListNode(MappingNode):
    pass

@register_node
class GeneralServerNode(Node):
    size = 4

class WebServerNode(Node):
    size = 3

    # note this may come from config file node
    expected_model = {
        'port': int
    }

@register_node
class NginxServerNode(WebServerNode):
    expected_model = {
        'port': int,
        'config': None
    }
    
@register_node
class GeneralClientNode(Node):
    size = 4

@register_node
class JSClientNode(JSNode, GeneralClientNode):
    size = 3

    default_html_path = 'index.html'
    default_js_path = 'main.js'

    expected_model = {
        'html_uri': str,
        'js_uris': list
    }

    def get_neighbours(self, neighbours):
        return get_neighbours(neighbours,
                       { 'server': lambda n, e: type(n) is WebServerNode,
                         'html': lambda n,e: type(n) is HTML_Node,
                         'js': lambda n,e: type(n) is FileNode and n.model.get('mime_type') == MIME_TYPES.JS })
        

    def get_implicit_nodes_and_edges(self, node_id, neighbours):
        """
        provide default HTML and JS nodes if not provided
        """
        out, errors = [], []

        ns = self.get_neighbours(neighbours)

        html_count = len(ns.get('html', []))
        js_count = len(ns.get('js', []))
        
        if html_count == 0:
            out.append((
                create_node({ 'mime_type': MIME_TYPES.HTML,
                              'path': self.default_html_path },
                            type='file_node'),
                create_edge({ })
            ))
        elif html_count > 1:
            errors.append(NetworkBuildException(
                'found ambiguous HTML node, want 1 not {}'.format(html_count), node_id=node_id))
        
        if js_count == 0:
            out.append((
                create_node({ 'mime_type': MIME_TYPES.JS,
                              'path': self.default_html_path },
                            type='file_node'),
                create_edge({ })
            ))
        elif js_count > 1:
            errors.append(NetworkBuildException(
                'found ambiguous JavaScript node, want 1 not {}'.format(js_count), node_id=node_id))
            
        return out, errors

    def resolve(self, node_id, neighbours):
        """
        derive paths of assets for client
        """
        out, errs = super().resolve(node_id, neighbours)

        ns = self.get_neighbours(neighbours)
        # check neighbours, get any web servers...determine uri of html/js assets...

        server_count = len(ns.get('server', []))
        html_node = ns['html'][0]

        if server_count == 1:
            pass
        elif server_count > 1:
            errors.append(NetworkBuildException(
                'found ambiguous Server count, want 1 not {}'.format(js_count), node_id=node_id))
        
        self.expected_model
        
        if self.model.get('html_uri') is None:
            pass
            #out.append(Code(node_id=node_id, has_symbol=False, language='html', file_name=self.default_html_path, content=""))
        
        return out, errs
        

    
@register_node
class ConfigFileNode(Node):
    size = 1

@register_node
class URI_Node(Node):
    size = 1
    
@register_node
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


@register_node
class HTML_Node(FileNode):
    
    expected_model = {
        'javascript': [],
        'style': []
    }

    def __init__(self, model):
        if model.get('mime_type') is None:
            model['mime_type'] = MIME_TYPES.HTML
        super().__init__(model)

@register_node
class LargeFileNode(Node):
    """
    could be any type of file, but noteworthy that it is large and can be treated differently
    """
    size = 2
    
@register_node
class StaticServerNode(WebServerNode):
    size = 3

    expected_model = {
        'directory': str
    }

    def resolve(self, node_id, neighbours):
        return super().resolve(node_id, neighbours)


@register_node
class PyStaticServerNode(PyNode, StaticServerNode):
    pass

@register_node
class PyFlaskServerNode(PyNode, WebServerNode):
    pass

@register_node
class PyTornadoServerNode(PyNode, WebServerNode):
    pass
    
@register_node
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

@register_node
class JS_D3Node(JSVisualNode):
    size = 2

    expected_model = {
        'object': str,
        'chain': dict
    }
    
@register_node
class JS_CanvasNode(JSVisualNode):
    pass

@register_node
class JS_SVGNode(JSVisualNode):
    pass
