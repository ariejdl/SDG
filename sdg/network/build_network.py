
import os
import tempfile
import logging as log

import networkx as nx

class NetworkBuildException(Exception):
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

    # 2) partition network by size 3+, resolve partitions individually
    # TODO: needs to be a bit cleverer than this...if children within parent, ignore children
    roots = []
    for node_id, node in network.nodes.items():
        if node.size >= 3:
            roots.append(node_id)

    # 3) resolve network into tree:
    # - respect edges
    # - avoid cycles
    # - avoid double resolution

    for nid in roots:
        for e in network.G.edges(nid):
            print(e)

    #import pdb; pdb.set_trace()
