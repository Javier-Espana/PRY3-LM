"""
Parser para Prolog con soporte de operadores infijos.

Soporta:
- Términos: Atom, Number, Variable, Compound, listas [a,b|T]
- Operadores infijos: +, -, *, /, ^ con precedencia correcta
- Cláusulas: hechos y reglas con ':-'
- Archivos: secuencia de cláusulas terminadas en '.'
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List as PyList, Tuple

from core.errors import SyntaxErrorProlog
from core.types import Atom, Clause, Compound, Number, Term, Variable
from parse.lexer import Lexer, Token


#precedencia de operadores (menor número = mayor precedencia)
#baasado en Prolog estándar
OPERATOR_PRECEDENCE = {
    "^": 200,   # Potencia (más alta precedencia)
    "*": 400,   # Multiplicación
    "/": 400,   # División
    "+": 500,   # Suma
    "-": 500,   # Resta
}


class Parser:
	def __init__(self, text: str):
		self.lexer = Lexer(text)
		self._tokens = list(self.lexer.tokens())
		self.pos = 0
		self.var_map: Dict[str, Variable] = {}

	def _peek(self) -> Token:
		return self._tokens[self.pos]

	def _advance(self) -> Token:
		tok = self._tokens[self.pos]
		self.pos += 1
		return tok

	def _expect(self, kind: str) -> Token:
		tok = self._peek()
		if tok.kind != kind:
			raise SyntaxErrorProlog(f"se esperaba {kind}, se encontró {tok.kind}", tok.line, tok.col)
		return self._advance()

	# Entrada publica --------------------------------------------------------

	def parse_clause(self) -> Clause:
		self.var_map = {}
		head = self.parse_compound_like()
		tok = self._peek()
		if tok.kind == ":-":
			self._advance()
			goals = self.parse_goals()
			self._expect(".")
			return Clause(head, tuple(goals))
		else:
			self._expect(".")
			return Clause(head, tuple())

	def parse_goals(self) -> PyList[Compound]:
		# Por simplicidad: conjunción por comas en la sintaxis de argumentos.
		# Ej: p :- q(X), r(Y).
		goals: PyList[Compound] = []
		goals.append(self.parse_compound_like())
		while self._peek().kind == ",":
			self._advance()
			goals.append(self.parse_compound_like())
		return goals

	def parse_compound_like(self) -> Compound:
		term = self.parse_term()
		if isinstance(term, Compound):
			return term
		if isinstance(term, Atom):
			return Compound(term.name, tuple())
		raise SyntaxErrorProlog("la cabeza/cuerpo debe ser un predicado (átomo o compuesto)", self._peek().line, self._peek().col)

	def parse_term(self) -> Term:
		"""Parsea un término, incluyendo operadores infijos con precedencia."""
		return self.parse_expression(max(OPERATOR_PRECEDENCE.values()) + 1)
	
	def parse_expression(self, max_precedence: int) -> Term:
		"""Parsea expresiones con operadores infijos respetando precedencia.
		
		Args:
			max_precedence: Precedencia máxima permitida para operadores en este nivel
		"""
		# Parsear el término primario (lado izquierdo)
		left = self.parse_primary()
		
		# Parsear operadores infijos mientras tengan precedencia adecuada
		while True:
			tok = self._peek()
			op = tok.kind
			
			# Verificar si es un operador infijo
			if op not in OPERATOR_PRECEDENCE:
				break
			
			# Verificar precedencia
			precedence = OPERATOR_PRECEDENCE[op]
			if precedence >= max_precedence:
				break
			
			# Consumir el operador
			self._advance()
			
			# Parsear el lado derecho con precedencia apropiada
			# Para asociatividad izquierda, usamos precedence
			# Para asociatividad derecha (como ^), usamos precedence + 1
			if op == "^":
				# Potencia es asociativa a la derecha: 2^3^4 = 2^(3^4)
				right = self.parse_expression(precedence)
			else:
				# Otros operadores son asociativos a la izquierda
				right = self.parse_expression(precedence)
			
			# Crear el término compuesto para el operador
			left = Compound(op, (left, right))
		
		return left
	
	def parse_primary(self) -> Term:
		"""Parsea términos primarios (números, variables, átomos, compuestos, listas, paréntesis)."""
		tok = self._peek()
		
		# Números
		if tok.kind == "NUMBER":
			self._advance()
			val = tok.lexeme
			if "." in val:
				return Number(float(val))
			return Number(int(val))
		
		# Variables
		if tok.kind == "VAR":
			self._advance()
			# Usar la misma instancia de Variable para el mismo nombre en la cláusula
			var_name = tok.lexeme
			if var_name not in self.var_map:
				self.var_map[var_name] = Variable(var_name)
			return self.var_map[var_name]
		
		# Operadores usados como functores: +(A, B), -(X, Y), etc.
		if tok.kind in OPERATOR_PRECEDENCE:
			op = tok.kind
			self._advance()
			# Solo permitir si está seguido por (
			if self._peek().kind == "(":
				self._advance()
				args: PyList[Term] = []
				if self._peek().kind != ")":
					args.append(self.parse_term())
					while self._peek().kind == ",":
						self._advance()
						args.append(self.parse_term())
				self._expect(")")
				return Compound(op, tuple(args))
			else:
				# Si no hay (, es un error (operador usado sin argumentos)
				raise SyntaxErrorProlog(f"operador '{op}' requiere argumentos entre paréntesis", tok.line, tok.col)
		
		# Átomos y functores
		if tok.kind == "ATOM":
			self._advance()
			functor = tok.lexeme
			
			# Verificar si tiene argumentos (término compuesto)
			if self._peek().kind == "(":
				self._advance()
				args: PyList[Term] = []
				if self._peek().kind != ")":
					args.append(self.parse_term())
					while self._peek().kind == ",":
						self._advance()
						args.append(self.parse_term())
				self._expect(")")
				return Compound(functor, tuple(args))
			
			# Átomo simple
			return Atom(functor)
		
		# Listas
		if tok.kind == "[":
			return self._parse_list()
		
		# Expresiones entre paréntesis
		if tok.kind == "(":
			self._advance()
			inner = self.parse_term()
			self._expect(")")
			return inner
		
		# Operador - unario (negación)
		if tok.kind == "-":
			self._advance()
			operand = self.parse_primary()
			return Compound("-", (operand,))
		
		if tok.kind == "EOF":
			raise SyntaxErrorProlog("entrada inesperadamente terminada", tok.line, tok.col)
		
		raise SyntaxErrorProlog(f"token inesperado: {tok.kind}", tok.line, tok.col)

	def _parse_list(self) -> Term:
		# Listas: [a,b]  |  [H|T]
		self._expect("[")
		elements: PyList[Term] = []
		tok = self._peek()
		if tok.kind == "]":
			self._advance()
			return Atom("[]")
		elements.append(self.parse_term())
		while self._peek().kind == ",":
			self._advance()
			elements.append(self.parse_term())
		if self._peek().kind == "|":
			self._advance()
			tail = self.parse_term()
			self._expect("]")
			# construir lista puntada
			term = tail
			for el in reversed(elements):
				term = Compound(".", (el, term))
			return term
		self._expect("]")
		# lista cerrada
		term = Atom("[]")
		for el in reversed(elements):
			term = Compound(".", (el, term))
		return term


# Funciones de conveniencia ---------------------------------------------------


def parse_clause(text: str) -> Clause:
	return Parser(text).parse_clause()


def parse_file(text: str) -> PyList[Clause]:
	p = Parser(text)
	clauses: PyList[Clause] = []
	while p._peek().kind != "EOF":
		clauses.append(p.parse_clause())
	return clauses

