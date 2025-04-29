"""
minicypher.clauses

Representations of Cypher statement clauses, statements,
and statement parameters.
"""

from __future__ import annotations

from string import Template

from .entities import P, _condition, _pattern, _return, _substitution
from .functions import Func


class Clause:
    """Represents a generic Cypher clause."""

    template = Template("$slot1")
    joiner = ", "

    @staticmethod
    def context(arg) -> str:
        return _return(arg)

    def __init__(self, *args, **kwargs):
        self.args = list(args)
        self.kwargs = kwargs

    def __str__(self):
        values = []
        for c in [type(self).context(x) for x in self.args]:
            if isinstance(c, str):
                values.append(c)
            elif isinstance(c, list):
                values.extend([str(x) for x in c])
            else:
                values.append(str(c))
        return self.template.substitute(
            slot1=self.joiner.join(values),
        )


class Match(Clause):
    """Create a MATCH clause with the arguments."""

    template = Template("MATCH $slot1")

    @staticmethod
    def context(arg) -> str:
        return _pattern(arg)

    def __init__(self, *args):
        super().__init__(*args)


class Where(Clause):
    """
    Create a WHERE clause with the arguments
    (joining conditions with 'op').
    """

    template = Template("WHERE $slot1")
    joiner = " {} "

    @staticmethod
    def context(arg) -> str:
        return _condition(arg)

    def __init__(self, *args, op="AND"):
        super().__init__(*args, op=op)
        self.op = op

    def __str__(self):
        values = []
        for c in [self.context(x) for x in self.args]:
            if isinstance(c, str):
                values.append(c)
            elif isinstance(c, Func):
                values.append(str(c))
            elif isinstance(c, list):
                values.extend([str(x) for x in c])
            else:
                values.append(str(c))
        return self.template.substitute(
            slot1=self.joiner.format(self.op).join(values),
        )


class With(Clause):
    """Create a WITH clause with the arguments."""

    template = Template("WITH $slot1")

    def __init__(self, *args):
        super().__init__(*args)

    def context(arg: object) -> str:
        return _return(arg)


class Create(Clause):
    """Create a CREATE clause with the arguments."""

    template = Template("CREATE $slot1")

    @staticmethod
    def context(arg) -> str:
        return _pattern(arg)

    def __init__(self, *args):
        super().__init__(*args)


class Merge(Clause):
    """Create a MERGE clause with the arguments."""

    template = Template("MERGE $slot1")

    @staticmethod
    def context(arg) -> str:
        return _pattern(arg)

    def __init__(self, *args):
        super().__init__(*args)


class Remove(Clause):
    """Create a REMOVE clause with the arguments."""

    template = Template("REMOVE $slot1")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def context(arg: object) -> str:
        return _substitution(arg)

    def __str__(self):
        ent = self.args[0]
        item = ""
        sep = ""
        if "prop" in self.kwargs:
            item = self.kwargs["prop"]
            sep = "."
        elif "label" in self.kwargs:
            item = self.kwargs["label"]
            sep = ":"
        return self.template.substitute(
            slot1=f"{self.context(ent)}{sep}{item}",
        )


class Set(Clause):
    """Create a SET clause with the arguments. (Only property arguments matter)."""

    template = Template("SET $slot1")

    @staticmethod
    def context(arg) -> str:
        return _condition(arg)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        values = []
        for c in [self.context(x) for x in self.args if isinstance(x, P)]:
            if isinstance(c, str):
                values.append(c)
            elif isinstance(c, list):
                values.extend([str(x) for x in c])
            else:
                values.append(str(c))
        if "update" in self.kwargs:
            values = [x.replace("=", "+=") for x in values]
        return self.template.substitute(
            slot1=self.joiner.join(values),
        )


class OnCreateSet(Set):
    """Create an ON CREATE SET clause for a MERGE with the arguments."""

    template = Template("ON CREATE SET $slot1")

    def __init__(self, *args):
        super().__init__(*args)


class OnMatchSet(Set):
    """Create an ON CREATE SET clause for a MERGE with the arguments."""

    template = Template("ON MATCH SET $slot1")

    def __init__(self, *args):
        super().__init__(*args)


class Return(Clause):
    """Create a RETURN clause with the arguments."""

    template = Template("RETURN $slot1")

    @staticmethod
    def context(arg) -> str:
        return _substitution(arg)

    def __init__(self, *args):
        super().__init__(*args)


class OptionalMatch(Clause):
    """Create an OPTIONAL MATCH clause with the arguments."""

    template = Template("OPTIONAL MATCH $slot1")

    @staticmethod
    def context(arg) -> str:
        return _pattern(arg)

    def __init__(self, *args):
        super().__init__(*args)


class Collect(Clause):
    """Create a COLLECT clause with the arguments."""

    template = Template("COLLECT $slot1")

    def __init__(self, *args):
        super().__init__(*args)

    def context(self, arg: object) -> str:
        return _substitution(arg)


# should be a Func?
class Unwind(Clause):
    """Create an UNWIND clause with the arguments."""

    template = Template("UNWIND $slot1")

    def __init__(self, *args):
        super().__init__(*args)


class As(Clause):
    """Create an AS clause with the arguments."""

    template = Template("AS $slot1")

    def __init__(self, *args):
        super().__init__(*args)

    def context(self, arg: object) -> str:
        return _return(arg)
