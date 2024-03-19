# minicypher - Object representations of Neo4j Cypher query elements

minicypher is a set of classes that can be used together to create
Python representations of Neo4j
[Cypher](https://neo4j.com/docs/cypher-manual/current/introduction/)
query statements. It allows the user to create syntactically correct
Cypher statements in a less error-prone and more conceptual way by using
Python, without having to manipulate strings, or keep track of Cypher
variable names. It can automatically parameterize a statement,
providing a dict of parameters and values.

[Pypher](https://github.com/emehrkay/pypher) is a more complete
facility that does similar things in a nice way. There is less magic
in minicypher, and its internal concepts may be slightly different.
Unlike Pypher, minicypher is not at pains to mimic the declarative form 
of a Cypher statement. minicypher is more function-oriented.

## Motivation

Suppose you want to create the following Cypher statement for execution

    MATCH (a:Actor)-[:played_in]->(m:Movie)
    WHERE a.name = "Sean Connery"
    RETURN m.title as Title;

There are three clauses, MATCH, WHERE, and RETURN, in this statement.
The use of variable `m` indicates that value of the `title` property
in the RETURN should come from the Movie node matched in the MATCH pattern.
Variable `a` in the statement indicates that the Actor node matched in
the MATCH pattern should be constrained by the equality in the WHERE clause.

In minicypher, you construct two node objects, one for the Movie and one for
the Actor. These objects will be used in the contexts of the two clauses in
which they appear. minicypher will render them in a statement appropriately.

    from minicypher import *
    actor = N('Actor',{'name':'Sean Connery'})
    movie = N('Movie',{'title':''})
    
    stmt = Statement(
             Match( R('played_in').anon().relate(actor.plain(), movie.plain()) ),
			 Where( actor.props['name'] ),
			 Return( movie.props['title'].As('Title') ))

When `stmt` is rendered as a string, e.g., when printed, it yields the query:

    > print(stmt)
    MATCH (n1:Actor)-[:played_in]->(n0:Movie) \
	WHERE n1.name = 'Sean Connery' \
	RETURN n0.title as Title

with dummy variables n0 and n1 correctly placed.

## Entities, Clauses, Functions, Statements

### Entities: Nodes, Relationships, and Properties

The basic idea is that a node, relationship, or property instance
knows how to behave depending on where it shows up in a
statement. Using the same instance in different parts of a statement
will ensure that the variable name stays the same, for
example. Variable names are provided automatically.

Constructors for entities:

| Entity | Constructor |
| --- | --- |
| Node | `N(label=,props=,As=,var=)` |
| Relationship | `R(Type=,props=,As=,var=)` |
| Property | `P(handle=,value=,As=,var=)` |

Properties are associated with a node or relationship as members of
the `.props` attribute, a dict. Property instances can be provided
with a value; this value is rendered in a statement depending on
whether the property appears in a Cypher pattern, a Where clause, or a
Return clause.

Example:

    actor = N('Actor', P('name', 'Sean Connery'))

Then the property instance 'name' is accessed as
`actor.props["name"]`, and its value is at
`actor.props["name"].value`.

In a Cypher MATCH pattern, a node or relationship may be represented
in different ways - from anonymous entities, as in  `()-[]->()`, to
entities with variable names and property maps specified, as in
`(m:Movie {title:"Goldeneye"})<-[r:acted_in]-(a:Actor {name:"Sean
Connery"})`. The modifier methods `.anon()`, `.var()`, `.plain()`, and
`.plain_var()` provide control over what information is rendered in
the final Statement.

| This item | is rendered as | Notes |
| --- | --- | --- |
| `actor` | `(n:Actor {name:"Sean Connery"})` | Both label and property map are produced by default |
| `actor.anon()` | `(:Actor {name: "Sean Connery"})` | Do not produce the variable |
| `actor.var()` | `(n {name: "Sean Connery"})` | Do not produce the label (or relationship type) |
| `actor.plain()` | `(n:Actor)` | Do not produce the property map |
| `actor.plain_var()` | `(n)` | Only produce the variable name |

### Clauses and Statements

Clauses correspond to parts of a Cypher statement prefaced by a keyword,
such as `MATCH`, `WHERE`, or `RETURN`. Clause instances provide a
context for rendering their arguments (nodes, relationships,
properties) so that they try to  "do what you mean."

The `Match()` clause treats its arguments as elements of a Cypher
graph pattern. If nodes or relationships have properties with values
set, the property map is rendered by default. See the table above to 
tweak the pattern production with modifier methods.

The `Where()` clause considers its arguments as participating in a
boolean condition. If a property instance on a node or relationship 
has a set value, then in a `Where()` clause, an equals condition
for the property is produced:

    >>> n = N('', [ P('this', 1), P('that', 2)])
    >>> print(Where(n))
    WHERE n0.this = 1 AND n0.that = 2

Override this behavior by referencing the properties directly.

    >>> print(Where(n.props['this']))
	WHERE n0.this = 1
    >>> print(Where(n.props['that'].with_value(3)))
    WHERE n0.that = 3

The `Return()` and other clauses render their arguments as variables,
or as aliases if the `.As` attribute is set to a desired alias.

### Functions

Cypher functions, such as `count()`, `labels()`, `ltrim()`, and others
that appear in conditions or return clauses can be produced with the
`Func` class. Instances will know how to render themselves
and their arguments depending on context and the presence of `AS`
aliases.

To render a function like `labels()`, with a simple name and
argument(s) in parens, use the `name` parameter in a `Func()`
constructor:

    >>> n = N('this:that',var='node')
	>>> f = Func(n, name='labels')
    >>> print(f)
    labels(node)
	>>> print(f.As('lbls'))
	labels(node) AS lbls
	>>> print(Func(n, name='labels').As('lbls').substitution())
	lbls

Additional arguments will be added as expected:

	>>> print(Func(n, "x", "y", name="location"))
	location(n0,x,y)

A few functions with special rendering are provided: `And`, `Or`,
`Not`, `is_null`, `is_not_null`:

    >>> n = N(props=[P("this",1)])
	>>> m = N(props=[P("that",2)])
    >>> print(Where(AND(n, m)))
	WHERE n0.this = 1 AND n1.that = 2

    >>> print(Where(is_not_null(n)))
    WHERE n0 IS NOT NULL

The `Cat` (concatentate) class can be used to construct other infix
functions (like `>`, `<`) appropriately:

    >>> val = 1
    >>> print(Where(Cat(n.props['this'],f"> {val}")))
    WHERE n0.this > 1

### Statements

Clauses are strung together in order as arguments to a `Statement()`
constructor. When printed or otherwise used as a string, a Statement
instance yields a Cypher query. The Statement instance can also
parameterize the statement and provide a dict of params and values.

Plain strings as arguments to clause constructors and `Statement()`
will be rendered verbatim.

