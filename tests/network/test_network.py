
from sdg.network.network import Network
from sdg.network.nodes import Node
from sdg.network.edges import Edge

def test_basic():
    nw = Network()
    
    n1 = Node(id=1, model={'a': 1})
    n2 = Node(id=2, model={'b': 1})

    e1 = Edge(id1=1, id2=1, model={'c': 1})
    e2 = Edge(id1=2, id2=1, model={'d': 1})

    n1_s = n1.ser_instance()
    n2_s = n2.ser_instance()
    
    assert n1_s['id'] == 1
    assert n1_s['model']['a'] == 1
    assert n1_s['model'].get('b') == None

    assert n2_s['id'] == 2
    assert n2_s['model']['b'] == 1
    assert n2_s['model'].get('c') == None

    nws = nw.serialize()
    assert nws['nodes'] == []
    assert nws['edges'] == []
    assert nws['network'] == {}
