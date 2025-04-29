from __future__ import annotations

from .entities import N, P, R


class Statement:
    """Create a Neo4j statement comprised of clauses (and strings) in order."""

    def __init__(self, *args, terminate: bool = False, use_params: bool = False):
        self.clauses = args
        self.terminate = terminate
        self.use_params = use_params
        self._params = None

    def __str__(self):
        stash = P.parameterize
        P.parameterize = bool(self.use_params)
        ret = " ".join([str(x) for x in self.clauses])
        if self.terminate:
            ret = ret + ";"
        P.parameterize = stash
        return ret

    @property
    def params(self) -> dict[str, str]:
        if self._params is None:
            self._params = {}
            for c in self.clauses:
                for ent in c.args:
                    if isinstance(ent, (N, R)):
                        for p in ent.props.values():
                            self._params[p._var] = p.value
                    elif isinstance(ent, P):
                        if ent.entity:
                            self._params[ent._var] = ent.value
                    else:
                        if "nodes" in vars(type(ent)):
                            for n in ent.nodes():
                                for p in n.props.values():
                                    self._params[p._var] = p.value
                        if "edges" in vars(type(ent)):
                            for e in ent.edges():
                                for p in e.props.values():
                                    self._params[p._var] = p.value
        return self._params
