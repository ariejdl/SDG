
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

    # 2) TODO: partition network, find "starting points", highest size, and parents, distinct languages
    #    -> cannot have more than one "large" node per partition, want a single starting point
    #    -> rather than create a new graph per partition, find the root and partition language

    # 2) another idea:
    #    -> turn a network into a tree by sorting by size...still need partitions

    # 2) partition network
    # - group by language
    # - consider: nodes may be shared across servers and clients because they are config variables...so do need the idea of a 'child'
    #   in order to be able to separate servers, thus nodes can be found in more than one separate network during resolution
    languages = set()
    largest_node_size = 1
    largest_nodes = set()
    largest_parent_size = 1
    largest_parents = set()
    
    for node_id, node in network.nodes.items():
        if node.language is not None:
            languages.add(node.language)
        if node.size > largest_node_size:
            largest_node_size = node.size
            largest_nodes = set()
        if node.size == largest_node_size:
            largest_nodes.add(node_id)

    # TODO: need the idea of a 'parent' node, either based on size or edge (or something else)
    # -> can then begin resolution from the parent, not necesssarily as a tree, but as a starting point

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
