
import os
import tempfile
import logging as log

import networkx as nx

from .utils import NetworkBuildException, edge_key

def resolve_partition(root, size_sorted, language, network):

    # 3) resolve network into code (not necessarily a single tree):
    # - respect edges
    # - avoid cycles
    # - avoid double resolution
    # - detect communication between languages (edges of a different language)
    # - ** detect which things are static dependencies, and which are dynamic, e.g. subject to user change
    #     - ensure there are no cycles in event propagation (some cycles are ok, think about this situation)

    """
    for vs in language_roots.values():
        for nid in vs:
            for e in network.G.edges(nid):
                print(e)
    """

    print('\n')

    info, warnings, errors = [], [], []

    all_code = []

    sizes = sorted(size_sorted.keys())

    implicit_nodes_and_edges = []
    added_nodes = []
    added_edges = []

    # pass 1)
    for s in sizes:
        for nid in sorted(size_sorted[s]):
            n = network.nodes[nid]
            neighbours = []
            
            for node_id in network.G.neighbors(nid):
                key = edge_key(nid, node_id)
                neighbours.append((network.nodes[node_id], network.edges[key]))

            nes, errs = n.get_implicit_nodes_and_edges(nid, neighbours)

            # check uniqueness, if not unique add another edge
            for n, e in nes:
                unique = True
                for n_, nid_, edges in implicit_nodes_and_edges:
                    if n_.model == n.model and type(n_) == type(n):
                        unique = False
                        edges.append(e)
                        break
                if unique:
                    implicit_nodes_and_edges.append([n, nid, [e]])

            errors += errs

    # now add the implicit nodes
    for n, node_id, edges in implicit_nodes_and_edges:
        if n.size is None:
            errors.append(NetworkBuildException("implicit node has no size", node_id=node_id))
            continue
        
        id = network.add_node(node=n)
        added_nodes.append(id)
        size_sorted[n.size].append(id)

        for e in edges:
            key = network.add_edge(node_id, id, edge=e)
            added_edges.append(key)

    if len(added_nodes):
        info.append(('added nodes', added_nodes))

    if len(added_edges):
        info.append(('added edges', added_edges))

    # pass 2)
    for s in sizes:
        for nid in sorted(size_sorted[s]):
            n = network.nodes[nid]
            neighbours = []
            
            for node_id in network.G.neighbors(nid):
                key = edge_key(nid, node_id)
                neighbours.append((network.nodes[node_id], network.edges[key]))

            code, errs = n.resolve(nid, neighbours)

            all_code += code
            errors += errs

            # ...perhaps don't need a file name for code, can merge by language if blank?
            """
            for code in all_code:
                if code.file_name is None:
                    errors.append(NetworkBuildException('no file specified for node', node_id=nid))
                    continue
                files.setdefault(code.file_name, [])
                files[code.file_name].append(code)
            """

    print(all_code)

    """
    strategies?

    - instrumented code, e.g. event on file download, event on file received
    - static server node: serve a given directory, determine what is being served by looking at edges, may be empty!
    - d3 nodes: object/chain
    - svg nodes: automatically attach to parent/body
    - fetch() - connection
    - js client:
      - html page(s)?
      - appropriate handling of JS files and libraries
    """

    return info, warnings, errors

def build_network(network):

    info, warnings, errors = [], [], []

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
        root_id = node.model.get('meta', {}).get('root_id')
        language = node.language
        size = node.size
        
        if root_id is None:
            errors.append(NetworkBuildException("node has no root id", node_id=node_id))
            continue
        if size is None:
            errors.append(NetworkBuildException("node has no size", node_id=node_id))
            continue
        
        roots.setdefault(root_id, { 'languages': set() })
        
        roots[root_id].setdefault(size, [])
        roots[root_id][size].append(node_id)
        if language is not None:
            roots[root_id]['languages'].add(language)

    # 3) resolution
    for k,v in roots.items():

        # validate that roots are all of same language or None
        if len(v['languages']) != 1:
            errors.append(NetworkBuildException(
                "network partition has ambiguous number of languages, want one: {}, {}"
                .format(len(v['languages']), list(v['languages'])), node_id=k))
            
            continue
        
        language = list(v['languages'])[0]
        del v['languages']
        
        p_info, p_warnings, p_errors = resolve_partition(k, v, language, network)
        
        info += p_info
        warnings += p_warnings
        errors += p_errors


    return info, warnings, errors
