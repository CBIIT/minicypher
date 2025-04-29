import re

from minicypher import *
from minicypher.entities import (
    _As,
    _condition,
    _pattern,
    _return,
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

    assert _pattern(m) == f"({m._var}:thing)"
    assert m.pattern() == f"({m._var}:thing)"
    assert n.pattern() == f"({n._var})"
    assert not n.condition()
    assert not m.condition()
    assert not _condition(n)
    assert n.Return() == n._var
    assert m.Return() == m._var

    assert _return(_As(m, "eddie")) == f"{m._var} as eddie"
    assert m.As("eddie").Return() == f"{m._var} as eddie"

    x = N(label="thing", As="dude")
    assert x.label == "thing" and x._as == "dude"
    assert x.Return() == f"{x._var} as dude"

    y = N(var="y")
    assert y._var == "y"

    # relationships
    assert isinstance(R0(), R)
    assert not R0().Type
    assert not R0().props
    assert not R0()._var

    r = R(Type="has_a")
    assert re.match("^r[0-9]+$", r._var)
    s = R(Type="is_a")
    assert r._var != s._var
    assert _pattern(r) == f"-[{r._var}:has_a]-"
    assert r.pattern() == f"-[{r._var}:has_a]-"
    assert not r.condition()
    assert not _condition(r)
    assert _return(r) == f"{r._var}"
    assert r.Return() == f"{r._var}"

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
    pbt = P(handle="is_thing", value=True)
    pbf = P(handle="is_thing", value=False)
    # boolean values for props
    assert type(pbt.value) == bool
    assert type(pbf.value) == bool
    assert pbt.value == True
    assert pbf.value == False
    assert pbf.pattern() == "is_thing:False"
    assert pbt.pattern() == "is_thing:True"
    thing = N(label="thing", props=pbt)
    not_thing = N(label="not_thing", props=pbf)
    assert pbf.condition() == f"{not_thing._var}.is_thing = False"
    assert pbt.condition() == f"{thing._var}.is_thing = True"

    assert not p.condition()
    assert not q.condition()

    w = N(label="item", props=q)
    assert _condition(q) == f"{w._var}.weight = 12"
    assert q.condition() == f"{w._var}.weight = 12"
    x = N(label="item", props=l)
    assert l.condition() == f"{x._var}.color = 'blue'"
    y = N(label="item", props=t)
    assert t.condition() == f"{y._var}.spin = $parm"

    z = y.relate_to(r, x)
    assert isinstance(z, T)
    assert z.pattern() == (
        f"({y._var}:item {{spin:$parm}})-[{r._var}:has_a]->({x._var}:item "
        "{color:'blue'})"
    )
    assert _pattern(z) == _condition(z)
    assert z.pattern() == z.condition()

    u = s.relate(w, x)
    assert isinstance(u, T)
    assert u.plain().pattern() == (f"({w._var}:item)-[{s._var}:is_a]->({x._var}:item)")

    u = s.anon().relate(w, x.anon())
    assert u.plain().pattern() == (f"({w._var}:item)-[:is_a]->(:item)")

    u = R0().relate(w.var(), x.var())
    assert u.plain().pattern() == (f"({w._var})-->({x._var})")

    assert R0().relate(N0(), N0()).pattern() == "()-->()"
