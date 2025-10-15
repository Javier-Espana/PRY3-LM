"""
Evaluación aritmética y funciones numéricas para el motor Prolog.

Implementa:
- Evaluador para is/2 y comparaciones aritméticas
- Operadores: +, -, *, /, //, mod, **
- Funciones: abs, floor, ceil, sqrt, sin, cos, tan, exp, log
- Manejo de errores aritméticos
"""

from __future__ import annotations

import math
from typing import Any, Generator, List as PyList, Union

from core.types import Atom, Compound, Env, Number, Term, Variable
from solver.unify import Trail, deref, unify


def evaluate(expr: Term, env: Env) -> Union[int, float]:
    """Evalúa una expresión aritmética a un número.
    
    Args:
        expr: Término que representa la expresión aritmética
        env: Entorno de variables
        
    Returns:
        Número resultante de la evaluación
        
    Raises:
        ValueError: Si la expresión no es evaluable
        ZeroDivisionError: En caso de división por cero
    """
    expr = deref(expr, env)
    
    # Casos base: números directos
    if isinstance(expr, Number):
        return expr.value
    
    # Variables deben estar instanciadas
    if isinstance(expr, Variable):
        raise ValueError(f"Variable no instanciada: {expr.name}")
    
    # Átomos especiales
    if isinstance(expr, Atom):
        # Constantes matemáticas
        if expr.name == "pi":
            return math.pi
        if expr.name == "e":
            return math.e
        raise ValueError(f"Átomo no evaluable: {expr.name}")
    
    # Términos compuestos (operadores y funciones)
    if isinstance(expr, Compound):
        functor = expr.functor
        args = expr.args
        
        # Operadores binarios
        if functor == "+" and len(args) == 2:
            return evaluate(args[0], env) + evaluate(args[1], env)
        
        if functor == "-" and len(args) == 2:
            return evaluate(args[0], env) - evaluate(args[1], env)
        
        if functor == "*" and len(args) == 2:
            return evaluate(args[0], env) * evaluate(args[1], env)
        
        if functor == "/" and len(args) == 2:
            divisor = evaluate(args[1], env)
            if divisor == 0:
                raise ZeroDivisionError("División por cero")
            return evaluate(args[0], env) / divisor
        
        if functor == "//" and len(args) == 2:
            divisor = evaluate(args[1], env)
            if divisor == 0:
                raise ZeroDivisionError("División por cero")
            return int(evaluate(args[0], env) // divisor)
        
        if functor == "mod" and len(args) == 2:
            divisor = evaluate(args[1], env)
            if divisor == 0:
                raise ZeroDivisionError("Módulo por cero")
            return evaluate(args[0], env) % divisor
        
        if functor == "**" and len(args) == 2:
            return evaluate(args[0], env) ** evaluate(args[1], env)
        
        if functor == "^" and len(args) == 2:
            return evaluate(args[0], env) ** evaluate(args[1], env)
        
        # Operador unario negación
        if functor == "-" and len(args) == 1:
            return -evaluate(args[0], env)
        
        # Funciones matemáticas
        if functor == "abs" and len(args) == 1:
            return abs(evaluate(args[0], env))
        
        if functor == "floor" and len(args) == 1:
            return math.floor(evaluate(args[0], env))
        
        if functor == "ceil" and len(args) == 1:
            return math.ceil(evaluate(args[0], env))
        
        if functor == "sqrt" and len(args) == 1:
            val = evaluate(args[0], env)
            if val < 0:
                raise ValueError("Raíz cuadrada de número negativo")
            return math.sqrt(val)
        
        # Funciones trigonométricas
        if functor == "sin" and len(args) == 1:
            return math.sin(evaluate(args[0], env))
        
        if functor == "cos" and len(args) == 1:
            return math.cos(evaluate(args[0], env))
        
        if functor == "tan" and len(args) == 1:
            return math.tan(evaluate(args[0], env))
        
        if functor == "asin" and len(args) == 1:
            return math.asin(evaluate(args[0], env))
        
        if functor == "acos" and len(args) == 1:
            return math.acos(evaluate(args[0], env))
        
        if functor == "atan" and len(args) == 1:
            return math.atan(evaluate(args[0], env))
        
        # Funciones exponenciales y logarítmicas
        if functor == "exp" and len(args) == 1:
            return math.exp(evaluate(args[0], env))
        
        if functor == "log" and len(args) == 1:
            val = evaluate(args[0], env)
            if val <= 0:
                raise ValueError("Logaritmo de número no positivo")
            return math.log(val)
        
        if functor == "ln" and len(args) == 1:
            val = evaluate(args[0], env)
            if val <= 0:
                raise ValueError("Logaritmo natural de número no positivo")
            return math.log(val)
        
        if functor == "log10" and len(args) == 1:
            val = evaluate(args[0], env)
            if val <= 0:
                raise ValueError("Logaritmo de número no positivo")
            return math.log10(val)
        
        raise ValueError(f"Función/operador no soportado: {functor}/{len(args)}")
    
    raise ValueError(f"Expresión no evaluable: {expr}")


def is_2(args: PyList[Term], engine: Any, env: Env, trail: Trail) -> Generator[Env, None, None]:
    """Predicado is/2: X is Expr.
    
    Evalúa la expresión aritmética Expr y unifica el resultado con X.
    """
    if len(args) != 2:
        return
    
    lhs, rhs = args
    
    try:
        # Evaluar la expresión del lado derecho
        value = evaluate(rhs, env)
        
        # Unificar con el lado izquierdo
        if unify(lhs, Number(value), env, trail, engine.occurs_check if engine else False):
            yield env
    except (ValueError, ZeroDivisionError, OverflowError):
        # Si hay error aritmético, el predicado falla
        return


def arithmetic_equal_2(args: PyList[Term], engine: Any, env: Env, trail: Trail) -> Generator[Env, None, None]:
    """Predicado =:=/2: X =:= Y.
    
    Evalúa ambos lados y verifica si son iguales.
    """
    if len(args) != 2:
        return
    
    lhs, rhs = args
    
    try:
        val_lhs = evaluate(lhs, env)
        val_rhs = evaluate(rhs, env)
        
        if val_lhs == val_rhs:
            yield env
    except (ValueError, ZeroDivisionError, OverflowError):
        return


def arithmetic_not_equal_2(args: PyList[Term], engine: Any, env: Env, trail: Trail) -> Generator[Env, None, None]:
    """Predicado =\\=/2: X =\\= Y.
    
    Evalúa ambos lados y verifica si son diferentes.
    """
    if len(args) != 2:
        return
    
    lhs, rhs = args
    
    try:
        val_lhs = evaluate(lhs, env)
        val_rhs = evaluate(rhs, env)
        
        if val_lhs != val_rhs:
            yield env
    except (ValueError, ZeroDivisionError, OverflowError):
        return


def less_than_2(args: PyList[Term], engine: Any, env: Env, trail: Trail) -> Generator[Env, None, None]:
    """Predicado </2: X < Y."""
    if len(args) != 2:
        return
    
    lhs, rhs = args
    
    try:
        val_lhs = evaluate(lhs, env)
        val_rhs = evaluate(rhs, env)
        
        if val_lhs < val_rhs:
            yield env
    except (ValueError, ZeroDivisionError, OverflowError):
        return


def less_equal_2(args: PyList[Term], engine: Any, env: Env, trail: Trail) -> Generator[Env, None, None]:
    """Predicado =</2: X =< Y."""
    if len(args) != 2:
        return
    
    lhs, rhs = args
    
    try:
        val_lhs = evaluate(lhs, env)
        val_rhs = evaluate(rhs, env)
        
        if val_lhs <= val_rhs:
            yield env
    except (ValueError, ZeroDivisionError, OverflowError):
        return


def greater_than_2(args: PyList[Term], engine: Any, env: Env, trail: Trail) -> Generator[Env, None, None]:
    """Predicado >/2: X > Y."""
    if len(args) != 2:
        return
    
    lhs, rhs = args
    
    try:
        val_lhs = evaluate(lhs, env)
        val_rhs = evaluate(rhs, env)
        
        if val_lhs > val_rhs:
            yield env
    except (ValueError, ZeroDivisionError, OverflowError):
        return


def greater_equal_2(args: PyList[Term], engine: Any, env: Env, trail: Trail) -> Generator[Env, None, None]:
    """Predicado >=/2: X >= Y."""
    if len(args) != 2:
        return
    
    lhs, rhs = args
    
    try:
        val_lhs = evaluate(lhs, env)
        val_rhs = evaluate(rhs, env)
        
        if val_lhs >= val_rhs:
            yield env
    except (ValueError, ZeroDivisionError, OverflowError):
        return
