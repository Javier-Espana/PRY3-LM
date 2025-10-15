"""
Utilidades varias para el motor Prolog.

Incluye pretty-printing, generación de nombres de variables, y herramientas de debug.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, List as PyList, Set

from core.types import Atom, Compound, Env, Number, Term, Variable, is_list, list_to_python


# Contador global para nombres de variables frescas
_var_counter = 0


def fresh_var_name(prefix: str = "_G") -> str:
    """Genera un nombre fresco para una variable."""
    global _var_counter
    _var_counter += 1
    return f"{prefix}{_var_counter}"


def fresh_var(prefix: str = "_G") -> Variable:
    """Genera una nueva variable con nombre fresco."""
    return Variable(fresh_var_name(prefix))


# Precedencia de operadores (menor número = mayor precedencia)
OPERATOR_PRECEDENCE = {
    "^": 200,
    "*": 400,
    "/": 400,
    "+": 500,
    "-": 500,
}


def _get_precedence(term: Term) -> int:
    """Obtiene la precedencia de un término operador."""
    if isinstance(term, Compound) and term.functor in OPERATOR_PRECEDENCE:
        return OPERATOR_PRECEDENCE[term.functor]
    return 0  # Términos no-operadores tienen precedencia más alta (no necesitan paréntesis)


def _pretty_term_with_precedence(term: Term, env: Env, max_depth: int, parent_prec: int, is_right_child: bool = False) -> str:
    """Pretty-printer interno que considera precedencia del padre.
    
    Args:
        term: Término a formatear
        env: Entorno para desreferenciar
        max_depth: Profundidad máxima
        parent_prec: Precedencia del operador padre (menor = más alta)
        is_right_child: True si este término es el hijo derecho de un operador binario
    """
    if max_depth <= 0:
        return "..."
    
    if env:
        from solver.unify import deref
        term = deref(term, env)
    
    if isinstance(term, Variable):
        return term.name
    
    if isinstance(term, Atom):
        if term.name == "[]":
            return "[]"
        if _needs_quotes(term.name):
            return f"'{term.name}'"
        return term.name
    
    if isinstance(term, Number):
        return str(term.value)
    
    if isinstance(term, Compound):
        # Casos especiales para listas
        if is_list(term):
            try:
                elements = list_to_python(term)
                if len(elements) > 20:
                    shown = elements[:20]
                    elem_strs = [_pretty_term_with_precedence(e, env, max_depth-1, 9999, False) for e in shown]
                    return f"[{', '.join(elem_strs)}, ...]"
                else:
                    elem_strs = [_pretty_term_with_precedence(e, env, max_depth-1, 9999, False) for e in elements]
                    return f"[{', '.join(elem_strs)}]"
            except ValueError:
                pass
        
        if term.functor == "." and term.arity() == 2:
            head = _pretty_term_with_precedence(term.args[0], env, max_depth-1, 9999, False)
            tail = _pretty_term_with_precedence(term.args[1], env, max_depth-1, 9999, False)
            if tail == "[]":
                return f"[{head}]"
            return f"[{head}|{tail}]"
        
        # Operadores infijos binarios
        if term.arity() == 2 and term.functor in OPERATOR_PRECEDENCE:
            my_prec = OPERATOR_PRECEDENCE[term.functor]
            
            # Formatear hijo izquierdo
            left_str = _pretty_term_with_precedence(term.args[0], env, max_depth-1, my_prec, False)
            
            # Formatear hijo derecho
            right_str = _pretty_term_with_precedence(term.args[1], env, max_depth-1, my_prec, True)
            
            result = f"{left_str} {term.functor} {right_str}"
            
            # Decidir si ESTE término necesita paréntesis
            needs_parens = False
            
            if parent_prec < my_prec:
                # Padre tiene mayor precedencia (número menor), necesitamos paréntesis
                # Ejemplo: (a + b) * c -- la suma necesita paréntesis
                needs_parens = True
            elif parent_prec == my_prec and is_right_child:
                # Mismo nivel y somos hijo derecho
                # Para asociatividad izquierda (+,-,*,/), necesitamos paréntesis
                # Ejemplo: a - (b - c) necesita paréntesis, pero a - b - c no
                if term.functor != "^":
                    needs_parens = True
            
            if needs_parens:
                result = f"({result})"
            
            return result
        
        # Operador unario menos
        if term.arity() == 1 and term.functor == "-":
            operand = _pretty_term_with_precedence(term.args[0], env, max_depth-1, 0, False)
            return f"-{operand}"
        
        # Término compuesto estándar (funciones como ln, sen, exp, etc.)
        if term.arity() == 0:
            return term.functor
        
        args_str = ", ".join(_pretty_term_with_precedence(arg, env, max_depth-1, 9999, False) for arg in term.args)
        return f"{term.functor}({args_str})"
    
    return str(term)


def pretty_term(term: Term, env: Env = None, max_depth: int = 10) -> str:
    """Pretty-printer para términos Prolog.
    
    Args:
        term: El término a formatear
        env: Entorno para desreferenciar variables (opcional)
        max_depth: Profundidad máxima para evitar recursión infinita
    """
    return _pretty_term_with_precedence(term, env, max_depth, parent_prec=9999, is_right_child=False)


def _needs_quotes(atom_name: str) -> bool:
    """Determina si un átomo necesita comillas."""
    if not atom_name:
        return True
    
    # Si empieza con minúscula y solo contiene alfanuméricos y _, no necesita comillas
    if atom_name[0].islower() and all(c.isalnum() or c == '_' for c in atom_name):
        return False
    
    # Operadores especiales conocidos
    special_ops = {":-", ";", ",", "=", "\\=", "==", "\\==", "<", "=<", ">", ">=",
                   "is", "=:=", "=\\=", "+", "-", "*", "/", "//", "mod", "**"}
    if atom_name in special_ops:
        return False
    
    return True


def format_error(error: Exception, context: str = "") -> str:
    """Formatea un error para mostrar en el REPL."""
    error_type = type(error).__name__
    message = str(error)
    
    if context:
        return f"[{error_type}] {message} (en {context})"
    return f"[{error_type}] {message}"


def format_solution(env: Env, query_vars: Set[Variable]) -> str:
    """Formatea una solución mostrando solo las variables relevantes de la consulta.
    
    Args:
        env: Entorno con los bindings
        query_vars: Variables que aparecían en la consulta original
    """
    if not query_vars:
        return "yes"
    
    bindings = []
    for var in query_vars:
        if var.id in env.bindings:
            value = env.bindings[var.id]
            value_str = pretty_term(value, env)
            bindings.append(f"{var.name} = {value_str}")
    
    if not bindings:
        return "yes"
    
    return ", ".join(bindings)


@dataclass
class Stopwatch:
    """Cronómetro simple para medir tiempos de ejecución."""
    
    _start_time: float = field(default_factory=time.time)
    _elapsed: float = 0.0
    _running: bool = True
    
    def start(self) -> None:
        """Inicia o reinicia el cronómetro."""
        self._start_time = time.time()
        self._running = True
    
    def stop(self) -> float:
        """Detiene el cronómetro y devuelve el tiempo transcurrido."""
        if self._running:
            self._elapsed = time.time() - self._start_time
            self._running = False
        return self._elapsed
    
    def elapsed(self) -> float:
        """Devuelve el tiempo transcurrido (sin detener el cronómetro)."""
        if self._running:
            return time.time() - self._start_time
        return self._elapsed


@dataclass
class Statistics:
    """Contador de estadísticas de ejecución del motor."""
    
    queries: int = 0
    unifications: int = 0
    choice_points: int = 0
    backtracks: int = 0
    
    def reset(self) -> None:
        """Reinicia todas las estadísticas."""
        self.queries = 0
        self.unifications = 0
        self.choice_points = 0
        self.backtracks = 0
    
    def summary(self) -> str:
        """Devuelve un resumen de las estadísticas."""
        return (f"Consultas: {self.queries}, "
                f"Unificaciones: {self.unifications}, "
                f"Choice points: {self.choice_points}, "
                f"Backtracks: {self.backtracks}")


# TODO: PARA COMPAÑEROS DE GRUPO
# Implementar las siguientes utilidades adicionales:

def rename_variables(term: Term, var_map: Dict[int, Variable] = None) -> Term:
    """Renombra todas las variables en un término para evitar conflictos.
    
    Args:
        term: Término a renombrar
        var_map: Mapa de renombramiento (se crea si no se proporciona)
    
    Returns:
        Término con variables renombradas
    """
    if var_map is None:
        var_map = {}
    
    if isinstance(term, Variable):
        if term.id not in var_map:
            var_map[term.id] = fresh_var(term.name)
        return var_map[term.id]
    
    if isinstance(term, Compound):
        new_args = tuple(rename_variables(arg, var_map) for arg in term.args)
        return Compound(term.functor, new_args)
    
    # Átomos y números no cambian
    return term


def extract_variables(term: Term) -> Set[Variable]:
    """Extrae todas las variables de un término.
    
    Args:
        term: Término del cual extraer variables
    
    Returns:
        Conjunto de todas las variables encontradas
    """
    variables: Set[Variable] = set()
    
    if isinstance(term, Variable):
        variables.add(term)
    elif isinstance(term, Compound):
        for arg in term.args:
            variables.update(extract_variables(arg))
    
    return variables
