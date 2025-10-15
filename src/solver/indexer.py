"""
Indexación y almacenamiento de cláusulas.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import DefaultDict, Dict, Iterable, List as PyList, Tuple

from core.types import Atom, Clause, Compound, Term


PredKey = Tuple[str, int]


def _first_arg_key(head: Compound) -> Tuple[str, str]:
	"""Devuelve una clave simple para indexar por primer argumento.

	- Si primer arg es átomo o número: clave concreta.
	- Si no: comodín '_'.
	"""
	if head.args:
		a0 = head.args[0]
		if isinstance(a0, Compound):
			return (".", "_")
		if isinstance(a0, Atom):
			return ("a", a0.name)
		# número, variable u otro -> comodín
	return ("*", "_")


@dataclass
class Index:
	by_key: DefaultDict[Tuple[str, str], PyList[Clause]] = field(default_factory=lambda: defaultdict(list))

	def add(self, clause: Clause) -> None:
		k = _first_arg_key(clause.head)
		self.by_key[k].append(clause)

	def candidates(self, head: Compound) -> Iterable[Clause]:
		# devolver por clave concreta + comodín para cobertura
		k = _first_arg_key(head)
		
		# Si el goal tiene una variable en el primer argumento, puede matchear
		# con cualquier cláusula, entonces devolver todas
		if k == ("*", "_"):
			for clauses in self.by_key.values():
				for c in clauses:
					yield c
		else:
			# Devolver cláusulas con clave específica + cláusulas comodín
			for c in self.by_key.get(k, []):
				yield c
			for c in self.by_key.get(("*", "_"), []):
				yield c


@dataclass
class KnowledgeBase:
	clauses: DefaultDict[PredKey, PyList[Clause]] = field(default_factory=lambda: defaultdict(list))
	indices: Dict[PredKey, Index] = field(default_factory=dict)

	def add_clause(self, clause: Clause) -> None:
		key = (clause.head.functor, clause.head.arity())
		self.clauses[key].append(clause)
		if key not in self.indices:
			self.indices[key] = Index()
		self.indices[key].add(clause)

	def predicates(self) -> Iterable[PredKey]:
		return self.clauses.keys()
	
	def list_predicates(self) -> PyList[str]:
		"""Devuelve una lista formateada de predicados cargados."""
		result = []
		for functor, arity in self.clauses.keys():
			result.append(f"{functor}/{arity}")
		return result

	def get_candidates(self, goal: Compound) -> Iterable[Clause]:
		key = (goal.functor, goal.arity())
		idx = self.indices.get(key)
		if not idx:
			return []
		return idx.candidates(goal)

