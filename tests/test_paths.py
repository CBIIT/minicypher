import re
import pytest

from minicypher import *

def test_paths():
    # happy paths:
    # G(N, R, N), G(T, T), G(N, R, T), G(T, R, N)
    # G(N, R, P), G(G, R, N)
    # G(N, R, N, R, N, R, N), G(T, G), G(G, T)
    # G(G, G)
    # G(G, R, N, R, T) ...
    # unhappy paths: with pytest.raises(Exception)
    # G(N), G(R), G(N, R), G(R, N), G(N, N)
    # G(N, T), G(R, T), G(N, G), G(R, G)
    # G(N, R, N, R, N, R)
    nodes = [N(label="case"), N(label="sample"), N(label="aliquot"),
             N(label="file")]
    edges = [R(Type="of_case"), R(Type="of_sample"), R(Type="of_aliquot")]

    t1 = edges[0].relate(nodes[1], nodes[0])  # (sample)-[:of_case]->(case)
    t2 = edges[1].relate(nodes[2], nodes[1])  # (aliquot)-[:of_sample]->(sample)
    t3 = edges[2].relate(nodes[3], nodes[2])  # (file)-[:of_aliquot]->(aliquot)

    pth0 = G(nodes[1], edges[0], nodes[0])  # G(N, R, N)
    assert re.match(
        "\\(n[0-9]+:sample\\)-\\[r[0-9]+:of_case\\]->\\(n[0-9]+:case\\)",
        pth0.pattern())
    pth1 = G(t1)  # G(T)
    assert re.match(
        "\\(n[0-9]+:sample\\)-\\[r[0-9]+:of_case\\]->\\(n[0-9]+:case\\)",
        pth1.pattern())
    pth2 = G(t1, t2)  # G(T, T)
    assert re.match(
        "\\(n[0-9]+:aliquot\\)-\\[r[0-9]+:of_sample\\]->\\(n[0-9]+:sample\\)-\\[r[0-9]+:of_case\\]->\\(n[0-9]+:case\\)",
        pth2.pattern()
        )
    pth3 = G(t2)
    pth4 = G(pth1, pth3)  # G(G, G)
    assert re.match(
        "\\(n[0-9]+:aliquot\\)-\\[r[0-9]+:of_sample\\]->\\(n[0-9]+:sample\\)-\\[r[0-9]+:of_case\\]->\\(n[0-9]+:case\\)",
        pth4.pattern()
        )
    pth5 = G(t2, nodes[1], edges[2], nodes[3])
    assert re.match(
        "\\(n[0-9]+:aliquot\\)-\\[r[0-9]+:of_sample\\]->\\(n[0-9]+:sample\\)-\\[r[0-9]+:of_aliquot\\]->\\(n[0-9]+:file\\)",
        pth5.pattern())
    pth6 = G(t2, edges[2], nodes[3])  # G(T, R, N)
    assert re.match(
        "\\(n[0-9]+:aliquot\\)-\\[r[0-9]+:of_sample\\]->\\(n[0-9]+:sample\\)-\\[r[0-9]+:of_aliquot\\]->\\(n[0-9]+:file\\)",
        pth6.pattern())
    pth7 = G(nodes[0], edges[0], t2)  # G(N, R, T)
    pth8 = G(pth1, edges[1], nodes[2], edges[2], t3)
    assert re.match(
        "\\(n[0-9]+:sample\\)-\\[r[0-9]+:of_case\\]->\\(n[0-9]+:case\\)-\\[r[0-9]+:of_sample\\]->\\(n[0-9]+:aliquot\\)<-\\[r[0-9]+:of_aliquot\\]-\\(n[0-9]+:file\\)",
        pth8.pattern())
    pth9 = G(t1,  nodes[2], edges[1], nodes[1], t3)
    assert re.match(
        "\\(n[0-9]+:file\\)-\\[r[0-9]+:of_aliquot\\]->\\(n[0-9]+:aliquot\\)-\\[r[0-9]+:of_sample\\]->\\(n[0-9]+:sample\\)-\\[r[0-9]+:of_case\\]->\\(n[0-9]+:case\\)",
        pth9.pattern())

    with pytest.raises(RuntimeError, match="needs _join hints"):
        pth10 = G(t1, edges[1], t3)
    edges[1]._join = ['sample', 'aliquot']
    assert re.match(
        "\\(n[0-9]+:file\\)-\\[r[0-9]+:of_aliquot\\]->\\(n[0-9]+:aliquot\\)-\\[r[0-9]+:of_sample\\]->\\(n[0-9]+:sample\\)-\\[r[0-9]+:of_case\\]->\\(n[0-9]+:case\\)",
        pth9.pattern())

    with pytest.raises(RuntimeError, match="do not define a complete Path"):
        G(nodes[0])  # G(N)
    with pytest.raises(RuntimeError, match="is not valid at arg position 1"):
        G(edges[0])  # G(R)
    with pytest.raises(RuntimeError, match="do not define a complete Path"):
        G(nodes[0], edges[0])  # G(N, R)
    with pytest.raises(RuntimeError, match="is not valid at arg position 2"):
        G(nodes[0], nodes[1])  # G(N, N)
    with pytest.raises(RuntimeError, match="is not valid at arg position 2"):
        G(nodes[0], t1)  # G(N, T)
    with pytest.raises(RuntimeError, match="is not valid at arg position 1"):
        G(edges[1], t1)  # G(R, T)
    with pytest.raises(RuntimeError, match="do not define a complete Path"):
        G(nodes[0], edges[0], nodes[1], nodes[2], edges[1])  # G(N, R, N, N, R)
    with pytest.raises(RuntimeError, match="from-node is ambiguous"):
        G(pth4, edges[2], nodes[3])  # G(G, R, N) when num G triples > 1
    with pytest.raises(RuntimeError, match="to-node is ambiguous"):
        G(nodes[3], edges[2], pth4)  # G(G, R, N) when num G triples > 1
    # two overlapping triples work: call it a feature
    G(nodes[1], edges[0], nodes[0], nodes[2], edges[1], nodes[1])
    
    # equivalent
    G(nodes[2], edges[1], nodes[1], edges[0], nodes[0])

    mm = G(R(Type="funk").relate(nodes[0].plain_var(),
                                 nodes[1].plain_var()),
           R(Type="master").relate(nodes[0].plain_var(), nodes[2].plain_var()))
    assert len(mm.triples) == 2
    
    with pytest.raises(RuntimeError, match="do not overlap"):
        G(t1, t3)
    # same semantics as G(t1, t2), but not the same objects:
    with pytest.raises(RuntimeError, match="do not overlap"):
        G(t1, R(Type=edges[1].Type).relate(N(label=nodes[2].label),
                                           N(label=nodes[1].label)))
