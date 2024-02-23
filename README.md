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
			 Return( movie.props['title']._as('Title') ))

When `stmt` is rendered as a string, e.g., when printed, it yields the query:

    > print(stmt)
    MATCH (n1:Actor)-[:played_in]->(n0:Movie) \
	WHERE n1.name = 'Sean Connery' \
	RETURN n0.title as Title

with dummy variables n0 and n1 correctly placed.

## Examples







