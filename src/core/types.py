"""
Tipos y contratos centrales del motor (subconjunto mínimo funcional).

Definimos Term, Atom, Number, Variable, Compound, List, Clause y un entorno de
bindings simple que usará el unificador y el motor.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List as PyList, Optional, Sequence, Tuple, Union


# Representación de términos -------------------------------------------------


class Term:
	"""Supertipo de todos los términos Prolog."""

	def __repr__(self) -> str:  # pragma: no cover - debug helper
		return self.__str__()


@dataclass(frozen=True)
class Atom(Term):
	name: str

	def __str__(self) -> str:  # pragma: no cover
		return self.name


@dataclass(frozen=True)
class Number(Term):
	value: Union[int, float]

	def __str__(self) -> str:  # pragma: no cover
		return str(self.value)


# Contador para IDs únicos de variables
_var_id_counter = 0

def _next_var_id() -> int:
	global _var_id_counter
	_var_id_counter += 1
	return _var_id_counter


@dataclass(unsafe_hash=True)
class Variable(Term):
	name: str
	id: int = field(default_factory=_next_var_id, compare=False)

	def __str__(self) -> str:  # pragma: no cover
		return self.name


@dataclass(frozen=True)
class Compound(Term):
	functor: str
	args: Tuple[Term, ...]

	def arity(self) -> int:
		return len(self.args)

	def __str__(self) -> str:  # pragma: no cover
		if self.arity() == 0:
			return self.functor
		inner = ", ".join(map(str, self.args))
		return f"{self.functor}({inner})"


def List(items: Sequence[Term]) -> Term:
	"""Construye una lista Prolog a partir de una secuencia Python.

	Representación como términos '.'/2 y '[]'.
	"""

	nil = Atom("[]")
	result: Term = nil
	for item in reversed(items):
		result = Compound(".", (item, result))
	return result


def is_list(term: Term) -> bool:
	if isinstance(term, Atom) and term.name == "[]":
		return True
	if isinstance(term, Compound) and term.functor == "." and len(term.args) == 2:
		return is_list(term.args[1])
	return False


def list_to_python(term: Term) -> PyList[Term]:
	"""Convierte una lista Prolog bien formada en lista Python."""
	out: PyList[Term] = []
	while isinstance(term, Compound) and term.functor == "." and len(term.args) == 2:
		out.append(term.args[0])
		term = term.args[1]
	if not (isinstance(term, Atom) and term.name == "[]"):
		raise ValueError("lista Prolog mal formada")
	return out


# Cláusulas ------------------------------------------------------------------


@dataclass(frozen=True)
class Clause:
	head: Compound
	body: Tuple[Compound, ...]  # conjunción de goals

	def is_fact(self) -> bool:
		return len(self.body) == 0


# Entorno de unificación -----------------------------------------------------


Bindings = Dict[int, Term]


@dataclass
class Env:
	"""Entorno de bindings de variables (por id)."""

	bindings: Bindings = field(default_factory=dict)

	def get(self, v: Variable) -> Optional[Term]:
		return self.bindings.get(v.id)

	def set(self, v: Variable, t: Term) -> None:
		self.bindings[v.id] = t

	def copy(self) -> "Env":
		return Env(dict(self.bindings))

