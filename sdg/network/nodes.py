
import os
import json
from .utils import (camel_to_snake, register_node,
                    create_node, create_edge, NetworkBuildException,
                    get_neighbours)
import types

class JS_TEMPLATES(object):
    ui_header = open(os.path.join(os.path.dirname(__file__), 'js/ui_header.js')).read(),
    ui_node = open(os.path.join(os.path.dirname(__file__), 'js/ui_node.js')).read()


class WEB_HELPERS(object):
    js_function = '''({args}) => {{
      {body}
    }}'''

    js_body_load = '''document.addEventListener("DOMContentLoaded", function() {{
      {body}
    }});
    '''
    
    html_page = '''<!html>
              <html>
                <head>
                {head}
                </head>
              <body>
                {body}
              </body>
            </html>'''


def test_neighbours(neighbours, tests):
    out = {}
    for nid, n, e in neighbours:
        for key, test in tests.items():
            if test(n,e) == True:
                out.setdefault(key, [])
                out[key].append(n)
    return out

def get_args(upstream):
    errors, args = [], []
    
    for nid, n, e in upstream:
        arg_name = e.model['meta'].get('name')
        if arg_name is not None:
            if not arg_name.startswith('$'):
                errors.append(NetworkBuildException("edge name should begin with $", node_id))
                continue
            args.append(arg_name)
        
    return errors, args

def get_upstream_downstream(node_id, neighbours):
    upstream, downstream = [], []

    for nid, n, e in neighbours:
        if e.model is not None:
            t_id = e.model.get('meta', {}).get('target_id')
            if t_id is not None:
                if t_id == node_id:
                    upstream.append((nid, n, e))
                elif t_id == nid:
                    downstream.append((nid, n, e))
                else:
                    raise Exception('passed node/edge is not a neighbour')

    return upstream, downstream



class MIME_TYPES(object):
    HTML = 'text/html'
    JS = 'text/javascript'

class Code():
    language = None # required
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

    def __repr__(self):
        rep = self.serialize(None)
        del rep['id']
        return json.dumps(rep)

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
    
    def get_implicit_nodes_and_edges(self, node_id, neighbours):
        return [], []

    def emit_code(self, node_id, network):
        # return Code[]
        return [], []
    

class PyNode(Node):
    language = 'python3'

class JSNode(Node):
    language = 'javascript'

    expected_model = {
        'allow_null_activation': bool
    }

    def make_body(self):
        return 'null'

    def emit_code(self, node_id, network):

        neighbours = get_neighbours(node_id, network)
        upstream, downstream = get_upstream_downstream(node_id, neighbours)

        non_js = []
        for nid, n, e in neighbours:
            language = n.language
            if language != self.language:
                # TODO: cater for cross language calls...
                non_js.append((nid, n, e))

        out, errors = super().emit_code(node_id, network)

        template_args = {
            'sym': node_id, # the unique node id
            'initBody': 'null', # optional initialisation of content, defaults to null
            'namedArgs': [], # named arguments passed through edge model's 'names'
            'body': self.make_body(), # the body of this node
            
            'dependents': [], # downstream symbols of node
            'dependencies': [], # upstream symbols of node
            'dependentAllowNulls': [], # downstream symbols that can be activated with null values
            'dependentArgs': [] # the arguments supplied to a dependent
        }
        
        errs, args = get_args(upstream)
        errors += errs

        for nid, n, e in upstream:
            template_args['dependencies'].append('node_{sym}_data'.format(sym=nid))

        for nid, n, e in downstream:
            template_args['dependents'].append('node_{sym}_data'.format(sym=nid))
            template_args['dependentAllowNulls'].append(
                'True' if n.model.get('allow_null_activation') == True else 'False')

            upstream_, _ = get_upstream_downstream(nid, get_neighbours(nid, network))
            errs, dep_args = get_args(upstream_)
            if len(errs) == 0:
                dep_args_str = '[{}]'.format(', '.join(sorted(dep_args)))
                template_args['dependentArgs'].append(dep_args_str)
        
        template_args['namedArgs'] = sorted(args)

        # convert list to string
        for k,v in template_args.items():
            if type(v) is list:
                template_args[k] = ', '.join(template_args[k])

        out.append(Code(
            node_id=node_id,
            has_symbol=False,
            language=self.language,
            file_name=None,
            content=JS_TEMPLATES.ui_node.format(**template_args)
        ))
        
        return out, errors
    

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

    def emit_code(self, node_id, network):
        out, errors = super().emit_code(node_id, network)
        #raise NotImplementedError()
        return out, errors

@register_node
class MappingLookupNode(MappingNode):

    expected_model = {
        'lookup': dict
    }
    
    def emit_code(self, node_id, network):
        out, errors = super().emit_code(node_id, network)

        parts = []

        for k, v in self.model.get('lookup', {}).items():
            if type(v) not in (str, int, float):
                error.append(NetworkBuildException(
                    'invalid type for lookup item: {}'.format(type(v)), node_id))
                continue
            parts.append('{}: {}'.format(k, v))

        out.append(Code(
            node_id=node_id,
            has_symbol=True,
            language=self.language,
            file_name=None,
            content="""{{
              {}
            }}""".format(',\n'.join(parts))
        ))

        return out, errors


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

    def get_static_path(self, asset):
        raise NotImplementedError()

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
class JSClientNode(GeneralClientNode):
    size = 3

    default_html_path = 'index.html'
    default_js_path = 'main.js'

    expected_model = {
        'html_uri': str,
        'js_uris': list
    }

    def test_neighbours(self, neighbours):
        return test_neighbours(neighbours,
                       { 'server': lambda n, e: isinstance(n, WebServerNode),
                         'html': lambda n,e: isinstance(n, HTML_Node),
                         'js': lambda n,e: (isinstance(n, FileNode) and
                                            n.model.get('mime_type') == MIME_TYPES.JS) })
        

    def get_implicit_nodes_and_edges(self, node_id, neighbours):
        """
        provide default HTML and JS nodes if not provided
        """
        out, errors = super().get_implicit_nodes_and_edges(node_id, neighbours)
        
        ns = self.test_neighbours(neighbours)

        html_count = len(ns.get('html', []))
        js_count = len(ns.get('js', []))
        
        if html_count == 0:

            n = create_node({ 'mime_type': MIME_TYPES.HTML,
                              'path': self.default_html_path },
                            type='html_node')
            e = create_edge({ })

            out.append((n, e))
            ns2,es2 = n.get_implicit_nodes_and_edges(node_id, [(self, e)])

            out += ns2
            errors += es2
            
        elif html_count > 1:
            errors.append(NetworkBuildException(
                'found ambiguous HTML node, want 1 not {}'.format(html_count), node_id=node_id))
        
        if js_count == 0:

            n = create_node({ 'mime_type': MIME_TYPES.JS,
                              'path': self.default_js_path },
                            type='file_node')
            e = create_edge({ })

            out.append((n, e))
            ns2,es2 = n.get_implicit_nodes_and_edges(node_id, [(self, e)])

            out += ns2
            errors += es2
            
        elif js_count > 1:
            errors.append(NetworkBuildException(
                'found ambiguous JavaScript node, want 1 not {}'.format(js_count), node_id=node_id))

        
            
        return out, errors

    def emit_code(self, node_id, network):
        """
        derive paths of assets for client

        ...check neighbours, get any web servers...determine uri of html/js assets...
        """
        out, errors = super().emit_code(node_id, network)
        
        neighbours = get_neighbours(node_id, network)
        ns = self.test_neighbours(neighbours)

        server_count = len(ns.get('server', []))
        html_node = ns['html'][0]
        js_nodes = ns['js']
        server = None

        if server_count == 1:
            server = ns['server'][0]
        elif server_count > 1:
            errors.append(NetworkBuildException(
                'found ambiguous Server count, want 1 not {}'.format(js_count), node_id=node_id))

        # HTML URI
        if self.model.get('html_uri') is None:
            if server is None:
                errors.append(NetworkBuildException(
                    'JS Client has no server specified, cannot get HTML path', node_id=node_id))
            else:
                try:
                    self.model['html_uri'] = server.get_static_path(node_id, html_node.model['path'])
                except NetworkBuildException as e:
                    errors.append(e)

        # JS URIS
        if len(self.model.get('js_uris', [])) == 0:
            if server is None:
                errors.append(NetworkBuildException(
                    'JS Client has no server specified, cannot get JavaScript path', node_id=node_id))
            else:
                self.model.setdefault('js_uris', [])
                for n in js_nodes:
                    try:
                        self.model['js_uris'].append(server.get_static_path(node_id, n.model['path']))
                    except NetworkBuildException as e:
                        errors.append(e)

        html_node.model.setdefault('javascripts', [])
        html_node.model['javascripts'] += self.model.get('js_uris', [])
        
        return out, errors


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

    def emit_code(self, node_id, network):
        out, errors = super().emit_code(node_id, network)

        mime_type = self.model.get('mime_type')
        if mime_type == MIME_TYPES.JS:
            out.append(Code(
                node_id=node_id,
                has_symbol=False,
                language='javascript',
                file_name=self.model.get('path'),
                content=None)
            )
        elif mime_type is not None:
            errors.append(NetworkBuildException('file could not be emit_coded', node_id))
        
        return out, errors

@register_node
class PythonScript(FileNode):
    language = 'python'

@register_node
class HTML_Node(FileNode):
    
    expected_model = {
        'javascripts': [],
        'stylesheets': []
    }

    def __init__(self, model):
        if model.get('mime_type') is None:
            model['mime_type'] = MIME_TYPES.HTML
        super().__init__(model)


    def emit_code(self, node_id, network):
        out, errors = super().emit_code(node_id, network)

        js = ['<script src="{}"></script>'.format(js) for js in self.model.get('javascripts', [])]
        css = ['<link rel="stylesheet" href="{}">'.format(css) for css in self.model.get('stylesheets', [])]

        out.append(Code(
            node_id=node_id,
            has_symbol=False,
            language='html',
            file_name=self.model['path'],
            content=WEB_HELPERS.html_page.format(
                head='\n'.join(js + css),
                body=""
            ))
        )
        
        return out, errors



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

    def emit_code(self, node_id, network):
        return super().emit_code(node_id, network)

@register_node
class PyStaticServerNode(PyNode, StaticServerNode):

    def get_static_path(self, node_id, asset):
        if asset is None:
            raise NetworkBuildException('no asset specified', node_id=node_id)
        if asset.startswith('/') or asset.startswith(os.sep):
            raise NetworkBuildException('please use a relative file path', node_id=node_id)
        return '/{}'.format(asset.replace(os.sep, '/'))


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
        'methods': dict
    }

    def make_body(self):
        s = 'd3.{}'.format(self.model['object'])

        ms = self.model.get('methods')
        if ms is not None:
            for k,v in ms.items():
                if type(v) is not list:
                    raise ValueError("expected list for argument")
                s += '.{}({})\n'.format(k, ', '.join(map(str,v)))
        
        return s

    def emit_code(self, node_id, network):
        out, errors = super().emit_code(node_id, network)
        #raise NotImplementedError()
        return out, errors
    
    
@register_node
class JS_CanvasNode(JSVisualNode):
    pass

@register_node
class DOM_SVGNode(Node):
    
    def emit_code(self, node_id, network):
        out, errors = super().emit_code(node_id, network)
        #raise NotImplementedError()
        return out, errors
