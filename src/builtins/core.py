"""
Predicados built-in del núcleo ISO para el motor Prolog.

Implementa predicados fundamentales como true/0, fail/0, unificación y testing de tipos.
"""

from __future__ import annotations

from typing import Any, Generator, List as PyList

from core.types import Atom, Compound, Env, Number, Term, Variable
from solver.unify import Trail, deref, unify


def true_0(args: PyList[Term], engine: Any, env: Env, trail: Trail) -> Generator[Env, None, None]:
    """true/0 - Siempre tiene éxito."""
    yield env


def fail_0(args: PyList[Term], engine: Any, env: Env, trail: Trail) -> Generator[Env, None, None]:
    """fail/0 - Siempre falla."""
    return
    yield  # Nunca se ejecuta, pero hace que sea un generador


def equal_2(args: PyList[Term], engine: Any, env: Env, trail: Trail) -> Generator[Env, None, None]:
    """=/2 - Unificación de términos."""
    if len(args) != 2:
        return
    
    lhs, rhs = args
    if unify(lhs, rhs, env, trail, engine.occurs_check if engine else False):
        yield env


def not_equal_2(args: PyList[Term], engine: Any, env: Env, trail: Trail) -> Generator[Env, None, None]:
    """\=/2 - No unificación (falla si los términos se unifican)."""
    if len(args) != 2:
        return
    
    lhs, rhs = args
    # Intentar unificar en un entorno temporal
    temp_env = env.copy()
    temp_trail = Trail()
    
    if not unify(lhs, rhs, temp_env, temp_trail, engine.occurs_check if engine else False):
        yield env  # Éxito si NO se unifica


def var_1(args: PyList[Term], engine: Any, env: Env, trail: Trail) -> Generator[Env, None, None]:
    """var/1 - Verifica si el argumento es una variable no instanciada."""
    if len(args) != 1:
        return
    
    term = deref(args[0], env)
    if isinstance(term, Variable):
        yield env


def nonvar_1(args: PyList[Term], engine: Any, env: Env, trail: Trail) -> Generator[Env, None, None]:
    """nonvar/1 - Verifica si el argumento NO es una variable no instanciada."""
    if len(args) != 1:
        return
    
    term = deref(args[0], env)
    if not isinstance(term, Variable):
        yield env


def atom_1(args: PyList[Term], engine: Any, env: Env, trail: Trail) -> Generator[Env, None, None]:
    """atom/1 - Verifica si el argumento es un átomo."""
    if len(args) != 1:
        return
    
    term = deref(args[0], env)
    if isinstance(term, Atom):
        yield env


def number_1(args: PyList[Term], engine: Any, env: Env, trail: Trail) -> Generator[Env, None, None]:
    """number/1 - Verifica si el argumento es un número."""
    if len(args) != 1:
        return
    
    term = deref(args[0], env)
    if isinstance(term, Number):
        yield env


def compound_1(args: PyList[Term], engine: Any, env: Env, trail: Trail) -> Generator[Env, None, None]:
    """compound/1 - Verifica si el argumento es un término compuesto."""
    if len(args) != 1:
        return
    
    term = deref(args[0], env)
    if isinstance(term, Compound):
        yield env


# TODO: PARA COMPAÑEROS DE GRUPO
# Implementar los siguientes predicados adicionales:

def cut_0(args: PyList[Term], engine: Any, env: Env, trail: Trail) -> Generator[Env, None, None]:
    """!/0 - Corte (cut). 
    
    TODO: Implementar el mecanismo de corte que elimine choice points.
    Por ahora, simplemente tiene éxito sin hacer nada.
    
    Instrucciones para implementar:
    1. El engine necesita un stack de choice points
    2. El cut debe marcar todos los choice points creados desde la cláusula actual
    3. Cuando se hace backtrack, no se deben considerar esos choice points
    """
    # Implementación temporal - solo tiene éxito
    yield env


def call_1(args: PyList[Term], engine: Any, env: Env, trail: Trail) -> Generator[Env, None, None]:
    """call/1 - Meta-predicado que ejecuta su argumento como goal.
    
    TODO: PARA COMPAÑEROS - Implementar meta-predicado call/1
    
    Instrucciones:
    1. Tomar el primer argumento
    2. Desreferenciarlo en el entorno actual
    3. Si es un Compound, ejecutarlo como goal usando engine.query([goal])
    4. Si es un Atom, convertirlo a Compound con arity 0
    5. Propagar todas las soluciones
    
    Ejemplo de uso en Prolog:
    ?- call(append([1,2], [3], X)).
    """
    # Stub - los compañeros deben implementar
    return
    yield


def once_1(args: PyList[Term], engine: Any, env: Env, trail: Trail) -> Generator[Env, None, None]:
    """once/1 - Ejecuta el goal pero solo devuelve la primera solución.
    
    TODO: PARA COMPAÑEROS - Implementar once/1
    
    Instrucciones:
    1. Similar a call/1 pero detener después de la primera solución
    2. Usar 'break' o 'return' después del primer 'yield'
    """
    # Stub - los compañeros deben implementar
    return
    yield


# TODO: PARA COMPAÑEROS DE GRUPO
# Los siguientes predicados necesitan el evaluador aritmético (builtins/arith.py):
# - is_2(args, engine, env, trail): X is Expr
# - arithmetic_equal_2: X =:= Y  
# - arithmetic_not_equal_2: X =\= Y
# - less_than_2: X < Y
# - less_equal_2: X =< Y  
# - greater_than_2: X > Y
# - greater_equal_2: X >= Y
#
# También implementar:
# - not_1: \+ Goal (negación por falla)
# - throw_1, catch_3: manejo de excepciones
