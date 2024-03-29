import re
import pytest

from minicypher import *
from minicypher.functions import Func
from minicypher.clauses import Clause

def test_clauses():

    n = N(label="node", props={"model": "ICDC", "handle": "diagnosis"})
    m = N(label="property", props={"handle": "disease_type"})
    t = R(Type="has_property").anon().relate(n, m)

    c = count(n)
    assert isinstance(c, count)
    assert isinstance(c, Func)
    assert str(c) == "count({})".format(n._var)
    assert str(count("this")) == "count(this)"
    x = exists(m.props['handle'])
    assert isinstance(x, exists)
    assert isinstance(x, Func)
    assert str(x) == "exists({}.handle)".format(m._var)
    assert str(exists("this.that")) == "exists(this.that)"

    match = Match(t)
    assert isinstance(match, Match)
    assert isinstance(match, Clause)
    assert str(match) == (
        "MATCH ({}:node {{model:'ICDC',handle:'diagnosis'}})"
        "-[:has_property]->({}:property {{handle:'disease_type'}})"
        ).format(n._var, m._var)

    where = Where(*t.nodes())
    assert isinstance(where, Where)
    assert isinstance(where, Clause)
    assert str(where) == (
        "WHERE {n}.model = 'ICDC' AND {n}.handle = 'diagnosis' "
        "AND {m}.handle = 'disease_type'"
        ).format(n=n._var, m=m._var)

    ret = Return(t)
    assert isinstance(ret, Return)
    assert isinstance(ret, Clause)
    assert str(ret) == (
        "RETURN {n}, {m}"
        ).format(n=n._var, m=m._var)

    st = Set(*n.props.values())
    assert isinstance(st, Set)
    assert isinstance(st, Clause)
    assert str(st) == "SET {n}.model = 'ICDC', {n}.handle = 'diagnosis'".format(n=n._var)

    st = OnMatchSet(*n.props.values())
    assert isinstance(st, Set)
    assert isinstance(st, Clause)
    assert str(st) == "ON MATCH SET {n}.model = 'ICDC', {n}.handle = 'diagnosis'".format(n=n._var)

    st = OnCreateSet(*n.props.values())
    assert isinstance(st, Set)
    assert isinstance(st, Clause)
    assert str(st) == "ON CREATE SET {n}.model = 'ICDC', {n}.handle = 'diagnosis'".format(n=n._var)

    N._reset_counter()
    n = N(props=[P("this",1)])
    m = N(props=[P("that",2)])
    st = Where(And(n, m))
    assert str(st) == "WHERE n0.this = 1 AND n1.that = 2"
    st = Where(Or(n, m))
    assert str(st) == "WHERE n0.this = 1 OR n1.that = 2"
    st = Where(Cat(n.props['this'],"> 1"))
    assert str(st) == "WHERE n0.this > 1"
    
def test_as_substitutions():
    # AS substitutions

    #     MATCH (user)-[:FRIEND]-(friend)
    #     WHERE user.name = $name
    #     WITH user, count(friend) AS friends
    #     WHERE friends > 10
    #     RETURN user

    u = N(var="user")
    f = N(var="friend")
    c = count(f)
    st = With(u, c.As("friends"))
    assert str(st) == "WITH user, count(friend) AS friends"
    st = Where(Cat(c, "> 10"))
    assert str(st) == "WHERE count(friend) > 10"
    st = Where(Cat(c.As("friends"), "> 10"))
    assert str(st) == "WHERE friends > 10"
    st = Where("friends > 10")
    assert str(st) == "WHERE friends > 10"
    st = With(u, Func(f, name="count").As("friends"))
    assert str(st) == "WITH user, count(friend) AS friends"

