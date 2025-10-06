"""
REPL interactivo mínimo para el motor Prolog.

Formato de consulta admitido (temporal):
  ?- pred(arg1, arg2).
o bien varias metas separadas por coma:
  ?- p(X), q(X).
"""

from __future__ import annotations

import sys
from typing import List as PyList

from core.types import Atom, Clause, Compound
from parse.parser import Parser
from solver.engine import Engine


def _parse_query(text: str) -> PyList[Compound]:
	# Reutilizamos el Parser para parsear como si fuera el cuerpo de una regla
	if not text.strip().endswith("."):
		text = text.strip() + "."
	p = Parser(text)
	# truco: parsear como si fuera 'dummy :- goals.' y recuperar goals
	head = p.parse_compound_like()
	# si el usuario no incluyó ':-', asumimos que el primer término es el goal
	# Forzamos ':-' artificial
	# Volvemos a parsear correctamente usando un parser secundario
	p2 = Parser(f"dummy :- {text}")
	clause = p2.parse_clause()
	return list(clause.body)


def start(engine: Engine, prompt: str = "?- ") -> None:
	print("Prolog (subset) REPL. Ctrl+C para salir.")
	while True:
		try:
			line = input(prompt)
		except (EOFError, KeyboardInterrupt):
			print()
			break
		s = line.strip()
		if not s:
			continue
		if s.startswith("\\"):
			if s == "\\help":
				print("Comandos: \\help, \\quit")
			elif s == "\\quit":
				break
			else:
				print("Comando desconocido.")
			continue
		try:
			goals = _parse_query(s)
		except Exception as e:  # pragma: no cover - IO
			print(f"[parse error] {e}")
			continue

		more = False
		for i, env in enumerate(engine.query(goals), start=1):
			print(f"yes #{i}.")
			more = True
			# Futuro: imprimir sustituciones relevantes
			ans = input("; para más, ENTER para siguiente consulta > ")
			if ans.strip() != ";":
				break
		if not more:
			print("no.")

