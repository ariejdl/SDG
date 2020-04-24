
import os
import shutil
import pytest

from sdg.network.network import Network
from sdg.network.build_network import build_network

_build_dir = None
_launch_dir = None
_test_data = None

def setup_module():
    global _build_dir
    global _launch_dir
    global _test_data
    
    _build_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', '_build'))
    _launch_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', '_launch'))

    # TODO: remove
    _teardown()
    
    if not os.path.exists(_build_dir):
        os.mkdir(_build_dir)
        
    if not os.path.exists(_launch_dir):
        os.mkdir(_launch_dir)

    _test_data = os.path.join(_build_dir, "test_data.csv")

    with open(_test_data, 'w') as f:
        f.write("a,b,c\n")
        f.write("1,2,3\n")
        f.write("4,5,6\n")
        f.write("7,8,9")

def _teardown():
    global _build_dir
    global _launch_dir
    if os.path.exists(_build_dir):
        shutil.rmtree(_build_dir)
        
    if os.path.exists(_launch_dir):
        shutil.rmtree(_launch_dir)
    
        
def teardown_module():
    # TODO: uncomment
    #_teardown()
    pass


def test_basic():
    global _build_dir
    global _launch_dir
    global _test_data

    n = Network({
        'nodes': [
            {'id': 1, 'type': 'py_static_server_node',
             'model': { 'meta': { 'root_id': 1 }, 'launch_directory': _launch_dir  } },
            
            {'id': 2, 'type': 'file_node', 'model': {
                'meta': { 'root_id': 1 },
                'path': os.path.abspath(_test_data)
            }, },
            
            {'id': 3, 'type': 'js_client_node', 'model': { 'meta': { 'root_id': 3 }  } },
             # convert one table to a grouped table
            {'id': 5, 'type': 'mapping_table_node', 'model': { 'meta': { 'root_id': 3 }  } },

            {'id': 10, 'type': 'mapping_lookup_node', 'model': {
                'meta': { 'root_id': 3 },
                'lookup': {
                    'width': 200,
                    'height': 200,
                    'x_accessor': '(v) => v[1]', # could use static analysis on this
                    'y_accessor': '(v) => v[2]',
                    'id_accessor': '(v) => v[0]'
                } } },
            
            {'id': 6, 'type': 'dom_svg_node', 'model': {
                'meta': { 'root_id': 3 },
                'tag': 'svg',
                'attrs': { 'width': '$conf.width', 'height': '$conf.height' } } },
            
            {'id': 7, 'type': 'dom_svg_node', 'model': {
                'meta': { 'root_id': 3 },
                'tag': 'circle', 'attrs': {
                    'cx': '$x_scale($conf.x_accessor($row))',
                    'cy': '$y_scale($conf.y_accessor($row))', 'r': 4 } } },
            
            {'id': 8, 'type': 'js_d3_node', 'model': {
                'meta': { 'root_id': 3 },
                'object': 'scaleLinear',
                'methods': {
                    'domain': ['d3.min($data, $conf.x_accessor)', 'd3.max($data, $conf.x_accessor)'],
                    'range': [0, '$conf.width']                    
                }
            } },
            
            {'id': 9, 'type': 'js_d3_node', 'model': {
                'meta': { 'root_id': 3 },
                'object': 'scaleLinear',
                'methods': {
                    'domain': ['d3.min($data, $conf.y_accessor)', 'd3.max($data, $conf.y_accessor)'],
                    'range': [0, '$conf.height']
                }} },
        ],
        'edges': [
            {'id1': 1, 'id2': 3, 'type': None, 'model': None },
            {'id1': 1, 'id2': 2, 'type': None, 'model': None },
            {'id1': 2, 'id2': 5, 'type': None, 'model': None },

            # only needed for mapping data to something variable
            {'id1': 5, 'id2': 6, 'type': 'mapping_edge', 'model': { } },

            # TODO: probably implement this with TNG-Hooks

            # NB: this implies directionality...
            # TODO: figure this out!
            {'id1': 8, 'id2': 7, 'type': None, 'model': {
                'meta': { 'target_id': 7 }, 'names': { 8: '$x_scale' } } },
            {'id1': 9, 'id2': 7, 'type': None, 'model': {
                'meta': { 'target_id': 7 }, 'names': { 9: '$y_scale' } } },

            # places where $conf is used
            {'id1': 10, 'id2': 7, 'type': None, 'model': {
                'meta': { 'target_id': 7, 'name': '$conf' } } },
            {'id1': 10, 'id2': 6, 'type': None, 'model': { 
                'meta': { 'target_id': 6, 'name': '$conf' } } },
            {'id1': 10, 'id2': 8, 'type': None, 'model': { 
                'meta': { 'target_id': 8, 'name': '$conf' } } },
            {'id1': 10, 'id2': 9, 'type': None, 'model': { 
                'meta': { 'target_id': 9, 'name': '$conf' } } },

            # places where data is used
            {'id1': 5, 'id2': 8, 'type': None, 'model': { 
                'meta': { 'target_id': 8, 'name': '$data' } } },
            {'id1': 5, 'id2': 9, 'type': None, 'model': { 
                'meta': { 'target_id': 9, 'name': '$data' } } }
        ]
    })

    n.build_dir = _build_dir
    
    build_network(n)
    
    assert True
