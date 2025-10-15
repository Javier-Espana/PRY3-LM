"""
REPL interactivo para el motor Prolog con visualización mejorada de soluciones.

Formato de consulta admitido:
  ?- pred(arg1, arg2).
o bien varias metas separadas por coma:
  ?- p(X), q(X).
"""

from __future__ import annotations

import sys
from typing import List as PyList, Set

from core.types import Atom, Clause, Compound, Variable
from parse.parser import Parser
from solver.engine import Engine
from utils.helpers import extract_variables, format_solution, pretty_term


def _parse_query(text: str) -> PyList[Compound]:
	"""Parsea una consulta del usuario."""
	if not text.strip().endswith("."):
		text = text.strip() + "."
	p = Parser(text)
	# Parsear como si fuera 'dummy :- goals.' y recuperar goals
	p2 = Parser(f"dummy :- {text}")
	clause = p2.parse_clause()
	return list(clause.body)


def start(engine: Engine, prompt: str = "?- ") -> None:
	"""Inicia el REPL interactivo."""
	print("Prolog (subset) REPL. Ctrl+C para salir.")
	print("Comandos: \\help, \\quit, \\listing")
	print()
	
	while True:
		try:
			line = input(prompt)
		except (EOFError, KeyboardInterrupt):
			print()
			break
		
		s = line.strip()
		if not s:
			continue
		
		# Procesar comandos especiales
		if s.startswith("\\"):
			if s == "\\help":
				print("Comandos disponibles:")
				print("  \\help     - Mostrar esta ayuda")
				print("  \\quit     - Salir del REPL")
				print("  \\listing  - Listar predicados cargados")
				print("\nEjemplos de consultas:")
				print("  ?- derivada(x^2, x, Y).")
				print("  ?- derivada(sen(x), x, Y).")
			elif s == "\\quit":
				break
			elif s == "\\listing":
				predicates = engine.kb.list_predicates()
				if predicates:
					print("Predicados cargados:")
					for pred in sorted(predicates):
						print(f"  {pred}")
				else:
					print("No hay predicados cargados.")
			else:
				print("Comando desconocido. Use \\help para ver los comandos disponibles.")
			continue
		
		# Parsear y ejecutar consulta
		try:
			goals = _parse_query(s)
		except Exception as e:
			print(f"Error de sintaxis: {e}")
			continue
		
		# Extraer variables de la consulta original
		query_vars: Set[Variable] = set()
		for goal in goals:
			query_vars.update(extract_variables(goal))
		
		# Ejecutar consulta
		solution_count = 0
		try:
			for env in engine.query(goals):
				solution_count += 1
				
				# Mostrar la solución
				if query_vars:
					# Mostrar bindings de variables
					bindings = []
					for var in sorted(query_vars, key=lambda v: v.name):
						# Obtener el valor de la variable del entorno
						value_term = env.get(var)
						if value_term is not None:
							value = pretty_term(value_term, env)
						else:
							value = var.name  # Variable no instanciada
						bindings.append(f"{var.name} = {value}")
					
					print(f"\n{', '.join(bindings)}")
				else:
					# Consulta sin variables
					print("\nyes")
				
				# Preguntar si continuar
				if solution_count == 1:
					ans = input("\n; (más soluciones), . (terminar) > ")
					if ans.strip() not in [";", ";"]:
						break
				else:
					ans = input("; (más soluciones), . (terminar) > ")
					if ans.strip() not in [";", ";"]:
						break
			
			if solution_count == 0:
				print("no.")
		except Exception as e:
			print(f"Error durante ejecución: {e}")
			import traceback
			traceback.print_exc()

