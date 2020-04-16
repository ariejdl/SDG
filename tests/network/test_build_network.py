
import os
import shutil
import pytest

from sdg.network.network import Network
from sdg.network.build_network import build_network

_build_dir = None

def setup_module():
    global _build_dir
    pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '_build'))
    _build_dir = pth
    if not os.path.exists(_build_dir):
        os.mkdir(_build_dir)

def teardown_module():
    shutil.rmtree(_build_dir)


def test_basic():
    global _build_dir

    n = Network({
        'nodes': [
            {'id': 1, 'type': 'py_static_server_node', 'model': { 'meta': { 'root_id': 1 }  } },
            {'id': 2, 'type': 'file_node', 'model': { 'meta': { 'root_id': 1 }  } },
            {'id': 3, 'type': 'js_client_node', 'model': { 'meta': { 'root_id': 3 }  } },
            {'id': 4, 'type': 'mapping_table_node', 'model': { 'meta': { 'root_id': 3 }  } },
             # convert one table to a grouped table
            {'id': 5, 'type': 'mapping_table_node', 'model': { 'meta': { 'root_id': 3 }  } },

            {'id': 10, 'type': 'mapping_lookup_node', 'model': { 'meta': { 'root_id': 3 }, 'width': 200, 'height': 200 } },
            
            {'id': 6, 'type': 'js_svg_node', 'model': {
                'meta': { 'root_id': 3 },
                'tag': 'svg', 'attrs': { 'width': 'conf.width', 'height': 'conf.height' } } },
            {'id': 7, 'type': 'js_svg_node', 'model': {
                'meta': { 'root_id': 3 },
                'tag': 'circle', 'attrs': { 'cx': 'x_scale($row[0])', 'cy': 'y_scale($row[1])', 'r': 4 } } },
            {'id': 8, 'type': 'js_d3_node', 'model': {
                'meta': { 'root_id': 3 },
                'object': 'scaleLinear', 'range': [0, 'conf.width'] } },
            {'id': 9, 'type': 'js_d3_node', 'model': {
                'meta': { 'root_id': 3 },
                'object': 'scaleLinear', 'range': [0, 'conf.height'] } },
        ],
        'edges': [
            {'id1': 1, 'id2': 3, 'type': None, 'model': None },
            {'id1': 1, 'id2': 2, 'type': None, 'model': None },
            {'id1': 2, 'id2': 4, 'type': None, 'model': None },
            {'id1': 4, 'id2': 5, 'type': None, 'model': None },

            # only needed for mapping data to something dynamic, everything else is just an object
            {'id1': 5, 'id2': 6, 'type': 'mapping_edge', 'model': { } },

            {'id1': 8, 'id2': 7, 'type': None, 'model': { 'names': { 8: 'x_scale' } } },
            {'id1': 9, 'id2': 7, 'type': None, 'model': { 'names': { 9: 'y_scale' } } },

            {'id1': 10, 'id2': 6, 'type': None, 'model': { 'names': { 10: 'conf' } } },
            {'id1': 10, 'id2': 8, 'type': None, 'model': { 'names': { 10: 'conf' } } }, 
            {'id1': 10, 'id2': 9, 'type': None, 'model': { 'names': { 10: 'conf' } } }
        ]
    })

    n.build_dir = _build_dir
    
    build_network(n)
    
    assert True
