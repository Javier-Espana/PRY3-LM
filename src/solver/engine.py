"""
Motor de resolución SLD básico con backtracking.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Generator, Iterable, List as PyList, Optional, Tuple

from core.types import Atom, Clause, Compound, Env, Term, Variable
from solver.indexer import KnowledgeBase
from solver.unify import Trail, apply, deref, unify


@dataclass
class Engine:
	occurs_check: bool = False
	kb: KnowledgeBase = field(default_factory=KnowledgeBase)

	def reset(self) -> None:
		self.kb = KnowledgeBase()

	def load(self, clauses: Iterable[Clause]) -> None:
		for c in clauses:
			self.kb.add_clause(c)

	def query(self, goals: Iterable[Compound]) -> Generator[Env, None, None]:
		goals_list = list(goals)
		env = Env()
		trail = Trail()
		yield from self._solve(goals_list, env, trail)

	def _solve(self, goals: PyList[Compound], env: Env, trail: Trail) -> Generator[Env, None, None]:
		if not goals:
			# solución encontrada
			yield env.copy()
			return

		# Selección izquierda por defecto
		first, rest = goals[0], goals[1:]

		# Verificar si es un builtin primero
		from builtins.registry import GLOBAL_REGISTRY
		if GLOBAL_REGISTRY.is_builtin(first):
			# Ejecutar builtin
			for result_env in GLOBAL_REGISTRY.call(first, self, env, trail):
				# Continuar con el resto de goals
				yield from self._solve(rest, result_env, trail)
			return

		# Buscar cláusulas candidatas en la base de conocimiento
		for clause in self.kb.get_candidates(first):
			# Preparar nuevo entorno y trail para esta rama
			local_env = env.copy()
			local_trail = Trail()
			# Unificar cabeza con goal
			if unify(first, clause.head, local_env, local_trail, self.occurs_check):
				# Nueva lista de metas: cuerpo de la regla + resto
				new_goals = list(clause.body) + rest
				# Resolver recursivamente
				yield from self._solve(new_goals, local_env, local_trail)
			# Si falla, se descartan bindings locales por el Trail de la rama

