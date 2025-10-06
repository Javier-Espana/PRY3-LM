"""
Unificación de términos para el motor Prolog.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List as PyList

from core.types import Atom, Compound, Env, Number, Term, Variable


@dataclass
class Trail:
	"""Pila de variables enlazadas para poder deshacer en backtracking."""

	stack: PyList[int]

	def __init__(self) -> None:
		self.stack = []

	def push(self, var: Variable) -> None:
		self.stack.append(var.id)

	def unwind(self, env: Env) -> None:
		while self.stack:
			vid = self.stack.pop()
			if vid in env.bindings:
				del env.bindings[vid]


def deref(term: Term, env: Env) -> Term:
	while isinstance(term, Variable):
		bound = env.get(term)
		if bound is None:
			return term
		term = bound
	return term


def occurs_in(v: Variable, t: Term, env: Env) -> bool:
	t = deref(t, env)
	if isinstance(t, Variable):
		return v.id == t.id
	if isinstance(t, Compound):
		return any(occurs_in(v, a, env) for a in t.args)
	return False


def bind(var: Variable, value: Term, env: Env, trail: Trail) -> None:
	trail.push(var)
	env.set(var, value)


def unify(t1: Term, t2: Term, env: Env, trail: Trail, occurs_check: bool = False) -> bool:
	t1 = deref(t1, env)
	t2 = deref(t2, env)

	if isinstance(t1, Variable):
		if isinstance(t2, Variable) and t1.id == t2.id:
			return True
		if occurs_check and occurs_in(t1, t2, env):
			return False
		bind(t1, t2, env, trail)
		return True

	if isinstance(t2, Variable):
		if occurs_check and occurs_in(t2, t1, env):
			return False
		bind(t2, t1, env, trail)
		return True

	if isinstance(t1, Atom) and isinstance(t2, Atom):
		return t1.name == t2.name

	if isinstance(t1, Number) and isinstance(t2, Number):
		return t1.value == t2.value

	if isinstance(t1, Compound) and isinstance(t2, Compound):
		if t1.functor != t2.functor or len(t1.args) != len(t2.args):
			return False
		for a, b in zip(t1.args, t2.args):
			if not unify(a, b, env, trail, occurs_check):
				return False
		return True

	return False


def apply(env: Env, term: Term) -> Term:
	term = deref(term, env)
	if isinstance(term, Compound):
		return Compound(term.functor, tuple(apply(env, a) for a in term.args))
	return term

