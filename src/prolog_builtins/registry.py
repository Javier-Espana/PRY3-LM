"""
Registro y gestión de predicados built-in del motor Prolog.

Este módulo centraliza el registro de predicados predefinidos y su dispatch.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Generator, List as PyList, Optional, Tuple

from core.types import Compound, Env
from solver.unify import Trail


# Tipo para implementaciones de builtins
# Reciben: args (términos), engine, env, trail
# Devuelven: Generator[Env, None, None] (como engine.query)
BuiltinImpl = Callable[[PyList[Any], Any, Env, Trail], Generator[Env, None, None]]


@dataclass
class BuiltinInfo:
    """Información sobre un predicado built-in."""
    
    name: str
    arity: int
    impl: BuiltinImpl
    deterministic: bool = True  # True si siempre produce máximo una solución
    meta: bool = False          # True si es un meta-predicado (ej: call/1)
    description: str = ""


@dataclass
class BuiltinRegistry:
    """Registro central de predicados built-in."""
    
    # Mapa de (functor, arity) -> BuiltinInfo
    builtins: Dict[Tuple[str, int], BuiltinInfo] = field(default_factory=dict)
    
    def register(self, 
                 name: str, 
                 arity: int, 
                 impl: BuiltinImpl,
                 deterministic: bool = True,
                 meta: bool = False,
                 description: str = "") -> None:
        """Registra un nuevo predicado built-in."""
        key = (name, arity)
        info = BuiltinInfo(name, arity, impl, deterministic, meta, description)
        self.builtins[key] = info
    
    def is_builtin(self, goal: Compound) -> bool:
        """Verifica si un goal es un predicado built-in."""
        key = (goal.functor, goal.arity())
        return key in self.builtins
    
    def call(self, 
             goal: Compound, 
             engine: Any,  # Evitar import circular
             env: Env, 
             trail: Trail) -> Generator[Env, None, None]:
        """Invoca un predicado built-in."""
        key = (goal.functor, goal.arity())
        if key not in self.builtins:
            return  # No es builtin, no hacer nada
        
        builtin = self.builtins[key]
        args = list(goal.args)
        
        # Llamar a la implementación
        yield from builtin.impl(args, engine, env, trail)
    
    def list_builtins(self) -> PyList[Tuple[str, int]]:
        """Lista todos los builtins registrados."""
        return list(self.builtins.keys())


# Instancia global del registro
GLOBAL_REGISTRY = BuiltinRegistry()


def load_core_builtins(registry: BuiltinRegistry) -> None:
    """Carga predicados del núcleo ISO."""
    from prolog_builtins.core import (
        true_0, fail_0, equal_2, not_equal_2, 
        var_1, nonvar_1, atom_1, number_1, compound_1
    )
    
    # Predicados de control básicos
    registry.register("true", 0, true_0, deterministic=True, 
                     description="Siempre tiene éxito")
    registry.register("fail", 0, fail_0, deterministic=True,
                     description="Siempre falla")
    
    # Predicados de unificación
    registry.register("=", 2, equal_2, deterministic=True,
                     description="Unificación de términos")
    registry.register("\\=", 2, not_equal_2, deterministic=True,
                     description="No unificación")
    
    # Predicados de testing de tipos
    registry.register("var", 1, var_1, deterministic=True,
                     description="Verifica si es variable no instanciada")
    registry.register("nonvar", 1, nonvar_1, deterministic=True,
                     description="Verifica si no es variable")
    registry.register("atom", 1, atom_1, deterministic=True,
                     description="Verifica si es átomo")
    registry.register("number", 1, number_1, deterministic=True,
                     description="Verifica si es número")
    registry.register("compound", 1, compound_1, deterministic=True,
                     description="Verifica si es término compuesto")


def load_arithmetic_builtins(registry: BuiltinRegistry) -> None:
    """Carga predicados aritméticos básicos."""
    from prolog_builtins.arith import (
        is_2, 
        arithmetic_equal_2, 
        arithmetic_not_equal_2,
        less_than_2, 
        less_equal_2, 
        greater_than_2, 
        greater_equal_2
    )
    
    # Evaluación aritmética
    registry.register("is", 2, is_2, deterministic=True,
                     description="Evaluación aritmética X is Expr")
    
    # Comparaciones aritméticas
    registry.register("=:=", 2, arithmetic_equal_2, deterministic=True,
                     description="Igualdad aritmética")
    registry.register("=\\=", 2, arithmetic_not_equal_2, deterministic=True,
                     description="Desigualdad aritmética")
    registry.register("<", 2, less_than_2, deterministic=True,
                     description="Menor que")
    registry.register("=<", 2, less_equal_2, deterministic=True,
                     description="Menor o igual que")
    registry.register(">", 2, greater_than_2, deterministic=True,
                     description="Mayor que")
    registry.register(">=", 2, greater_equal_2, deterministic=True,
                     description="Mayor o igual que")


def load_list_builtins(registry: BuiltinRegistry) -> None:
    """Carga predicados para listas."""
    # TODO: PARA COMPAÑEROS DE GRUPO
    # Implementar en builtins/lists_atoms.py:
    # - member_2: member(X, List)
    # - append_3: append(L1, L2, L3)
    # - length_2: length(List, N)
    # - reverse_2: reverse(List, Reversed)
    # 
    # Ejemplo member/2:
    # def member_2(args, engine, env, trail):
    #     elem, lista = args
    #     lista = deref(lista, env)
    #     
    #     while isinstance(lista, Compound) and lista.functor == ".":
    #         head, tail = lista.args
    #         if unify(elem, head, env.copy(), Trail()):
    #             yield env
    #         lista = deref(tail, env)
    pass
