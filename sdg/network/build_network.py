
import os
import tempfile
import logging as log

import networkx as nx

class NetworkBuildException(Exception):
    pass

def resolve_partition(root, language, network):
    pass

def build_network(network):

    # 1) create temp directory
    if network.build_dir is None:
        network.build_dir = tempfile.TemporaryDirectory()
    elif not os.path.exists(network.build_dir):
        dir_ = tempfile.TemporaryDirectory()
        log.warning('build directory for network not found: {}, recreating: {}'
                        .format(network.build_dir, dir_))
        network.build_dir = dir_

    # 2) partition network
    roots = {}

    for node_id, node in network.nodes.items():
        size = node.size
        root_id = node.model.get('meta', {}).get('root_id')
        language = node.language
        
        if root_id is None:
            raise NetworkBuildException("node has no root id")
        if size is None:
            raise NetworkBuildException("node has no size")
        roots.setdefault(root_id, { 'languages': set() })
        
        roots[root_id].setdefault(size, [])
        roots[root_id][size].append(node_id)
        if language is not None:
            roots[root_id]['languages'].add(language)

    # validate that roots are all of same language or None
    for k,v in roots.items():
        if len(v['languages']) != 1:
            raise NetworkBuildException("network partition has ambiguous number of languages: {}, {}".format(
                len(v['languages']), list(v['languages'])))
        v['languages'] = list(v['languages'])

    #print(roots)

    # 3) resolve network into tree:
    # - respect edges
    # - avoid cycles
    # - avoid double resolution
    # - detect communication between languages (edges of a different language)

    """
    for vs in language_roots.values():
        for nid in vs:
            for e in network.G.edges(nid):
                print(e)
    """

    #import pdb; pdb.set_trace()
