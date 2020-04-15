
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
    pass


def test_basic():
    global _build_dir

    n = Network({
        'nodes': [
            {'id': 2, 'type': 'py_rest_node', 'model': {'x': 2}},
            {'id': 3, 'type': 'py_rest_node', 'model': {'y': 1}},
            {'id': 1, 'type': 'py_rest_node', 'model': {'x': -1}}
        ],
        'edges': [
            {'id1': 1, 'id2': 2, 'type': 'rest_edge', 'model': {'z': 1}, 'edge_meta': { 'child_id': 3 }}]
    })

    n.build_dir = _build_dir
    
    build_network(n)
    
    assert True
