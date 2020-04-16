
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

class Node(object):
    """
    note that nodes will have different characteristics when "static" versus when "running", i.e. after
    code has been emitted and has started execution, rather than before code has even been emitted
    """

    # default values where they are not supplied
    model = {}
    language = None

    # indicates scale from variable -> module/program
    size = 0

    # e.g. a DB query
    _async = False

    # for choosing between nodes during resolution, simpler is better
    _complexity_estimate = None

    # other nodes which are created by this one if not in a part of its network
    _node_implicit_dependencies = []

    # other nodes which cannot be part of its compilation/code-emission without some kind of separation
    _node_mutual_exclusions = []

    # language libraries
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
            'model': dict(self.model.items())
        }

    def deserialize(self, model):
        self.model = model
    
    def emit_code(self):
        raise NotImplementedError()
    

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
    model = {
        'port': int
    }

@register_class
class NginxServerNode(WebServerNode):
    model = {
        'port': int,
        'config': None
    }
    
@register_class
class GeneralClientNode(Node):
    size = 4

@register_class
class JSClientNode(JSNode, GeneralClientNode):
    size = 3
    
@register_class
class ConfigFileNode(Node):
    size = 1

@register_class
class FileNode(Node):
    """
    could be any type of file, e.g. csv/json
    """
    size = 2

@register_class
class LargeFileNode(Node):
    """
    could be any type of file, but noteworthy that it is large and can be treated differently
    """
    size = 2
    
@register_class
class StaticServerNode(WebServerNode):
    size = 3

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

    model = {
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
    pass
    
@register_class
class JS_CanvasNode(JSVisualNode):
    pass

@register_class
class JS_SVGNode(JSVisualNode):
    pass
