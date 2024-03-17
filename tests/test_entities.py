import re
import pytest

from minicypher import *
from minicypher.entities import (
    _pattern, _As, _condition, _return,
    _plain, _anon, _var, _plain_var
    )


def test_entities():
    # nodes
    assert isinstance(N0(), N)
    assert not N0().label
    assert not N0().props
    assert not N0()._as
    assert not N0()._var

    n = N()
    assert n._var
    assert re.match("^n[0-9]+$", n._var)
    m = N(label="thing")
    assert m.label == "thing"
    assert n._var != m._var
    assert m.As("THING")._as == "THING"

    assert _pattern(m) == "({}:thing)".format(m._var)
    assert m.pattern() == "({}:thing)".format(m._var)
    assert n.pattern() == "({})".format(n._var)
    assert not n.condition()
    assert not m.condition()
    assert not _condition(n)
    assert n.Return() == n._var
    assert m.Return() == m._var

    assert _return(_As(m, "eddie")) == "{} as eddie".format(m._var)
    
    x = N(label="thing", As="dude")
    assert x.label == "thing" and x._as == "dude"
    assert x.Return() == "{} as dude".format(x._var)
    
    # relationships
    assert isinstance(R0(), R)
    assert not R0().Type
    assert not R0().props
    assert not R0()._var
    
    r = R(Type="has_a")
    assert re.match("^r[0-9]+$", r._var)
    s = R(Type="is_a")
    assert r._var != s._var
    assert _pattern(r) == "-[{}:has_a]-".format(r._var)
    assert r.pattern() == "-[{}:has_a]-".format(r._var)
    assert not r.condition()
    assert not _condition(r)
    assert _return(r) == "{}".format(r._var)
    assert r.Return() == "{}".format(r._var)

    
    # props
    p = P(handle="height")
    assert p.handle == "height"
    q = P(handle="weight", value=12)
    assert type(q.value) == int
    assert q.value == 12
    l = P(handle="color", value="blue")
    assert type(l.value) == str
    assert l.value == "blue"
    t = P(handle="spin", value="$parm")

    assert not p.condition()
    assert not q.condition()

    w = N(label="item", props=q)
    assert _condition(q) == "{}.weight = 12".format(w._var)
    assert q.condition() == "{}.weight = 12".format(w._var)
    x = N(label="item", props=l)
    assert l.condition() == "{}.color = 'blue'".format(x._var)
    y = N(label="item", props=t)
    assert t.condition() == "{}.spin = $parm".format(y._var)

    z = y.relate_to(r, x)
    assert isinstance(z, T)
    assert z.pattern() == (
        "({}:item {{spin:$parm}})-[{}:has_a]->({}:item "
        "{{color:'blue'}})"
        ).format(y._var, r._var, x._var)
    assert _pattern(z) == _condition(z)
    assert z.pattern() == z.condition()


    u = s.relate(w, x)
    assert isinstance(u, T)
    assert u.plain().pattern() == (
        "({}:item)-[{}:is_a]->({}:item)"
        ).format(w._var, s._var, x._var)

    u = s.anon().relate(w, x.anon())
    assert u.plain().pattern() == (
        "({}:item)-[:is_a]->(:item)"
        ).format(w._var)

    u = R0().relate(w.var(), x.var())
    assert u.plain().pattern() == (
        "({})-->({})"
        ).format(w._var, x._var)

    assert R0().relate(N0(), N0()).pattern() == "()-->()"

