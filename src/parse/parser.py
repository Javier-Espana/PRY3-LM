"""
Parser básico para un subconjunto de Prolog sin operadores definidos.

Soporta:
- Términos: Atom, Number, Variable, Compound, listas [a,b|T]
- Cláusulas: hechos y reglas con ':-'
- Archivos: secuencia de cláusulas terminadas en '.'
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List as PyList, Tuple

from core.errors import SyntaxErrorProlog
from core.types import Atom, Clause, Compound, Number, Term, Variable
from parse.lexer import Lexer, Token


class Parser:
	def __init__(self, text: str):
		self.lexer = Lexer(text)
		self._tokens = list(self.lexer.tokens())
		self.pos = 0

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

	# Entrada pública --------------------------------------------------------

	def parse_clause(self) -> Clause:
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
		# Permitir hecho tipo atom/0 como Compound(functor, ())
		if isinstance(term, Atom):
			return Compound(term.name, tuple())
		raise SyntaxErrorProlog("la cabeza/cuerpo debe ser un predicado (átomo o compuesto)", self._peek().line, self._peek().col)

	def parse_term(self) -> Term:
		tok = self._peek()
		if tok.kind == "NUMBER":
			self._advance()
			val = tok.lexeme
			if "." in val:
				return Number(float(val))
			return Number(int(val))
		if tok.kind == "VAR":
			self._advance()
			return Variable(tok.lexeme)
		if tok.kind == "ATOM":
			self._advance()
			functor = tok.lexeme
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
			return Atom(functor)
		if tok.kind == "[":
			return self._parse_list()
		if tok.kind == "(":
			self._advance()
			inner = self.parse_term()
			self._expect(")")
			return inner
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

