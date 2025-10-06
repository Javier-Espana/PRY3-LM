"""
Carga de archivos .pl y gestión de módulos (mínimo viable).
"""

from __future__ import annotations

import os
from typing import Iterable

from core.errors import LoadError
from core.types import Clause
from parse.parser import parse_file
from solver.engine import Engine


def resolve_path(base: str, relative: str) -> str:
	if os.path.isabs(relative):
		return relative
	return os.path.normpath(os.path.join(os.path.dirname(base), relative))


def consult(path: str, engine: Engine) -> None:
	if not os.path.exists(path):
		raise LoadError(path, "archivo no encontrado")
	try:
		with open(path, "r", encoding="utf-8") as f:
			text = f.read()
	except OSError as e:
		raise LoadError(path, str(e))
	clauses = parse_file(text)
	engine.load(clauses)

