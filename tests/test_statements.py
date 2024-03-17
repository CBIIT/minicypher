import re
import pytest

from minicypher import *
from minicypher.functions import Func

def test_statments():
    n = N(label="node", props={"model": "ICDC", "handle": "diagnosis"})
    m = N(label="property", props={"handle": "disease_type"})
    t = R(Type="has_property").anon().relate(n, m)
    p = P(handle='boog')
    p.entity = n

    assert str(
        Statement(
            Match(t.plain().var()),
            Where(exists(m.props['handle']), n),
            Return(count(n))
            )
        ) == (
            "MATCH ({n})-[:has_property]->({m}) "
            "WHERE exists({m}.handle) AND {n}.model = 'ICDC' AND "
            "{n}.handle = 'diagnosis' "
            "RETURN count({n})"
            ).format(n=n._var, m=m._var)

    assert str(
        Statement(
            Match(t.plain().var()),
            Where(exists(m.props['handle']), n),
            Return(count(n)),
            use_params=True
            )
        ) == (
            "MATCH ({n})-[:has_property]->({m}) "
            "WHERE exists({m}.handle) AND {n}.model = ${p0} AND "
            "{n}.handle = ${p1} "
            "RETURN count({n})"
            ).format(n=n._var, m=m._var, p0=n.props["model"]._var,
                     p1=n.props["handle"]._var)

    assert Statement(
            Match(t.plain().var()),
            Where(exists(m.props['handle']), n),
            Return(count(n)),
            use_params=True
            ).params == {
                n.props['model']._var: "ICDC",
                n.props['handle']._var: "diagnosis"
            }

    assert str(
        Statement(
            Match(t.plain().var()),
            Where(group(And(exists(m.props['handle']), n.props['model'])),
                  Not(n.props['handle'])),
            Return(p),
            'LIMIT 10'
            )
        ) == (
            "MATCH ({n})-[:has_property]->({m}) "
            "WHERE (exists({m}.handle) AND {n}.model = 'ICDC') AND NOT "
            "{n}.handle = 'diagnosis' "
            "RETURN {n}.boog LIMIT 10"
            ).format(n=n._var, m=m._var)

    assert str(
        Statement(
            Create(n.plain()),
            Set(*n.props.values()),
            Return(n)
            )
        ) == (
            "CREATE ({n}:node) "
            "SET {n}.model = 'ICDC', {n}.handle = 'diagnosis' "
            "RETURN {n}"
            ).format(n=n._var)

    assert str(
        Statement(
            Merge(n.plain()),
            OnCreateSet(*n.props.values()),
            Return(n)
            )
        ) == (
            "MERGE ({n}:node) "
            "ON CREATE SET {n}.model = 'ICDC', {n}.handle = 'diagnosis' "
            "RETURN {n}"
            ).format(n=n._var)

    assert str(
        Statement(
            Merge(n.plain()),
            OnMatchSet(*n.props.values()),
            Return(n)
            )
        ) == (
            "MERGE ({n}:node) "
            "ON MATCH SET {n}.model = 'ICDC', {n}.handle = 'diagnosis' "
            "RETURN {n}"
            ).format(n=n._var)

    assert str(
        Statement(
            Match(n),
            Remove(n,label="node")
            )
        ) == (
            "MATCH ({n}:node {{model:'ICDC',handle:'diagnosis'}}) "
            "REMOVE {n}:node"
            ).format(n=n._var)

    assert str(
        Statement(
            Match(n),
            Remove(n,prop="nanoid")
            )
        ) == (
            "MATCH ({n}:node {{model:'ICDC',handle:'diagnosis'}}) "
            "REMOVE {n}.nanoid"
            ).format(n=n._var)
