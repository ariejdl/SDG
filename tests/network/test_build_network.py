
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
            {'id': 1, 'type': 'static_server_node', 'model': None },
            {'id': 2, 'type': 'file_node', 'model': None },
            {'id': 3, 'type': 'js_client_node', 'model': {'y': 1}},
            {'id': 4, 'type': 'mapping_table_node', 'model': {'y': 1}},
             # convert one table to a grouped table
            {'id': 5, 'type': 'mapping_table_node', 'model': {'y': 1}}, 
            {'id': 6, 'type': 'js_svg_node', 'model': {'y': 1}},
        ],
        'edges': [
            {'id1': 1, 'id2': 3, 'type': None, 'model': {'z': 1}, 'edge_meta': { 'child_id': 3 }},
            {'id1': 1, 'id2': 2, 'type': None, 'model': None, 'edge_meta': None },
            {'id1': 2, 'id2': 4, 'type': None, 'model': None, 'edge_meta': None },
            {'id1': 4, 'id2': 5, 'type': 'mapping_transform_edge', 'model': None, 'edge_meta': None },
            {'id1': 5, 'id2': 6, 'type': None, 'model': None, 'edge_meta': None }
        ]
    })

    n.build_dir = _build_dir
    
    build_network(n)
    
    assert True
