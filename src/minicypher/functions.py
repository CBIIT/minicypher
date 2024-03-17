"""
minicypher.functions

Representations of Cypher functions
"""
from __future__ import annotations
import typing
from string import Template
from .entities import (
    _return, _condition, _pattern, _substitution
    )

# cypher functions


class Func(object):
    template = Template("${slot1}")
    joiner = ','

    @staticmethod
    def arg_context(arg : object) -> str:
        return _return(arg)

    def __init__(self, arg : Any, template_str : str = None, As : str = None):
        if (template_str):
            self.template = Template(template_str)
        self.arg = arg
        self._as = As
    
    def __str__(self) -> str:
        return self.Return()

    def condition(self) -> str:
        return self.substitution()
    
    def substitution(self) -> str:
        if self._as:
            return "{}".format(self._as)
        else:
            return self.Return()

    def Return(self) -> str:
        slot = ""
        if type(self.arg) is list:
            slot = self.joiner.join([self.arg_context(a) for a in self.arg])
        else:
            slot = self.arg_context(self.arg)
        
        if self._as:
            return self.template.substitute(slot1=slot)+" as "+self._as
        else:
            return self.template.substitute(slot1=slot)


class count(Func):
    template = Template("count($slot1)")


class exists(Func):
    template = Template("exists($slot1)")


class labels(Func):
    template = Template("labels($slot1)")


class Not(Func):
    template = Template("NOT $slot1")

    @staticmethod
    def arg_context(arg : object) -> str:
        return _condition(arg)


class And(Func):
    template = Template("$slot1")
    joiner = " AND "

    @staticmethod
    def arg_context(arg : object) -> str:
        return _condition(arg)

    def __init__(self, *args):
        self.arg = list(args)
        super().__init__(self.arg)


class Or(Func):
    template = Template("$slot1")
    joiner = " OR "

    @staticmethod
    def arg_context(arg : object) -> str:
        return _condition(arg)

    def __init__(self, *args):
        self.arg = list(args)
        super().__init__(self.arg)


class group(Func):
    template = Template("($slot1)")
    joiner = " "


class is_null(Func):
    template = Template("$slot1 IS NULL")


class is_not_null(Func):
    template = Template("$slot1 IS NOT NULL")

