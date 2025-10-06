"""
Constantes y configuración base del motor Prolog.

Definimos valores por defecto, operadores predefinidos y configuración global.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple


# Configuración por defecto del motor
@dataclass
class DefaultConfig:
    """Configuración por defecto del motor Prolog."""
    
    # Control de unificación
    occurs_check: bool = False
    
    # Límites de recursos
    max_depth: int = 1000
    max_choice_points: int = 10000
    
    # Opciones de tracing y debug
    trace: bool = False
    debug: bool = False
    
    # Versión del motor
    version: str = "0.1.0-dev"


# Instancia global de configuración por defecto
DEFAULT_CONFIG = DefaultConfig()


# Predicados especiales reservados del sistema
SPECIAL_PREDICATES = {
    "true": 0,
    "fail": 0,
    "!": 0,  # cut
    "=": 2,
    "\\=": 2,
    "==": 2,
    "\\==": 2,
    "is": 2,
    "=:=": 2,
    "=\\=": 2,
    "<": 2,
    "=<": 2,
    ">": 2,
    ">=": 2,
}


# Operadores predefinidos con precedencia y asociatividad
# Formato: (precedencia, tipo, asociatividad)
# tipo: 'fx' (prefix), 'fy' (prefix right-assoc), 'xf' (postfix), etc.
PREDEFINED_OPERATORS = {
    ":-": (1200, "xfx", "none"),  # implicación (reglas)
    ";": (1100, "xfy", "right"),  # disyunción
    ",": (1000, "xfy", "right"),  # conjunción
    "\\+": (900, "fy", "none"),   # negación
    "=": (700, "xfx", "none"),     # unificación
    "\\=": (700, "xfx", "none"),   # no unificación
    "==": (700, "xfx", "none"),    # igualdad estricta
    "\\==": (700, "xfx", "none"),  # desigualdad estricta
    "is": (700, "xfx", "none"),    # evaluación aritmética
    "=:=": (700, "xfx", "none"),   # igualdad aritmética
    "=\\=": (700, "xfx", "none"),  # desigualdad aritmética
    "<": (700, "xfx", "none"),     # menor que
    "=<": (700, "xfx", "none"),    # menor o igual
    ">": (700, "xfx", "none"),     # mayor que
    ">=": (700, "xfx", "none"),    # mayor o igual
    "+": (500, "yfx", "left"),     # suma
    "-": (500, "yfx", "left"),     # resta
    "*": (400, "yfx", "left"),     # multiplicación
    "/": (400, "yfx", "left"),     # división
    "//": (400, "yfx", "left"),    # división entera
    "mod": (400, "yfx", "left"),   # módulo
    "**": (200, "xfx", "none"),    # potencia
    "-": (200, "fy", "none"),      # negación unaria
    "+": (200, "fy", "none"),      # signo positivo unario
}


# Nombres de archivos estándar
STANDARD_EXTENSIONS = [".pl", ".pro", ".prolog"]


# Configuración de pretty-printing
MAX_TERM_DEPTH = 10
MAX_LIST_ELEMENTS = 20
