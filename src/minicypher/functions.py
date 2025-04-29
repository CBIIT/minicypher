"""
minicypher.functions

Representations of Cypher functions
"""

from __future__ import annotations

from string import Template
from typing import Any

from .entities import _As, _condition, _substitution

# cypher functions


class Func:
    template = Template("${slot1}")
    joiner = ","

    @staticmethod
    def arg_context(arg: object) -> str:
        return _substitution(arg)

    def __init__(
        self,
        *args: Any,
        name: str | None = None,
        template_str: str | None = None,
        As: str | None = None,
    ):
        if name:
            self.template = Template(f"{name}(${{slot1}})")
        elif template_str:
            self.template = Template(template_str)
        else:
            pass

        self.arg = list(args)
        self._as = As

    def __str__(self) -> str:
        return self.Return()

    def As(self, alias) -> Func:
        return _As(self, alias)

    def condition(self) -> str:
        return self.substitution()

    def substitution(self) -> str:
        if self._as:
            return f"{self._as}"
        return self.Return()

    def Return(self) -> str:
        val = ""
        if type(self.arg) is list:
            items = []
            for a in self.arg:
                it = type(self).arg_context(a)
                if type(it) == list:
                    items.extend(it)
                else:
                    items.append(it)
            val = self.joiner.join(items)
        else:
            val = self.arg_context(self.arg)

        if self._as:
            return self.template.substitute(slot1=val) + " AS " + self._as
        return self.template.substitute(slot1=val)


class count(Func):
    template = Template("count($slot1)")


class exists(Func):
    template = Template("exists($slot1)")


class labels(Func):
    template = Template("labels($slot1)")


class Not(Func):
    template = Template("NOT $slot1")

    @staticmethod
    def arg_context(arg: object) -> str:
        return _condition(arg)


class And(Func):
    template = Template("$slot1")
    joiner = " AND "

    @staticmethod
    def arg_context(arg: object) -> str:
        return _condition(arg)


class Or(Func):
    template = Template("$slot1")
    joiner = " OR "

    @staticmethod
    def arg_context(arg: object) -> str:
        return _condition(arg)


class group(Func):
    template = Template("($slot1)")
    joiner = " "


class is_null(Func):
    template = Template("$slot1 IS NULL")


class is_not_null(Func):
    template = Template("$slot1 IS NOT NULL")


class Cat(Func):
    """
    Concatentate string representations of the arguments with spaces.

    Example: to produce "count(a) > 1", use concat(count("a"),"> 1").
    """

    @staticmethod
    def arg_context(arg: object) -> str:
        return _substitution(arg)

    template = Template("${slot1}")
    joiner = " "
