"""
Errores y excepciones propias del motor Prolog.

Implementamos un subconjunto mínimo para habilitar parser, solver e IO.
La jerarquía se puede ampliar posteriormente para cubrir ISO por completo.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


class PrologError(Exception):
	"""Base de todas las excepciones del motor Prolog."""


@dataclass
class SyntaxErrorProlog(PrologError):
	"""Error de sintaxis en el código fuente Prolog."""

	message: str
	line: Optional[int] = None
	column: Optional[int] = None

	def __str__(self) -> str:  # pragma: no cover - simple formato
		loc = f" (línea {self.line}, col {self.column})" if self.line is not None else ""
		return f"SyntaxErrorProlog{loc}: {self.message}"


@dataclass
class InstantiationError(PrologError):
	message: str


@dataclass
class TypeErrorProlog(PrologError):
	expected: str
	found: str
	message: str = ""

	def __str__(self) -> str:  # pragma: no cover
		base = f"TypeErrorProlog: se esperaba {self.expected}, se encontró {self.found}"
		return f"{base}. {self.message}" if self.message else base


@dataclass
class DomainError(PrologError):
	domain: str
	found: str


@dataclass
class ExistenceError(PrologError):
	object_type: str
	object: str


@dataclass
class LoadError(PrologError):
	path: str
	message: str


@dataclass
class OperatorError(PrologError):
	message: str
