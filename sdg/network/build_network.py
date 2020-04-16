
import os
import tempfile
import logging as log

import networkx as nx

from .utils import NetworkBuildException

def resolve_partition(root, size_sorted, language, network):

    #print(roots)

    # 3) resolve network into code (not necessarily a single tree):
    # - respect edges
    # - avoid cycles
    # - avoid double resolution
    # - detect communication between languages (edges of a different language)
    # - [detect which things are static dependencies, and which are dynamic, e.g. sunject to user change]
    #     [- ensure there are no loops in event propagation]

    """
    for vs in language_roots.values():
        for nid in vs:
            for e in network.G.edges(nid):
                print(e)
    """

    print('\n')

    sizes = sorted(size_sorted.keys())
    for s in sizes:
        for nid in size_sorted[s]:
            n = network.nodes[nid]
            n.resolve()
            print(n)
            #import pdb; pdb.set_trace()

    """
    strategies?

    - static server node: serve a given directory
    """

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

    # 3) resolution
    for k,v in roots.items():

        # validate that roots are all of same language or None
        if len(v['languages']) != 1:
            raise NetworkBuildException("network partition has ambiguous number of languages: {}, {}".format(
                len(v['languages']), list(v['languages'])))
        
        language = list(v['languages'])[0]
        del v['languages']
        
        resolve_partition(k, v, language, network)

