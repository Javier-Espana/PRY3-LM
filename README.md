# PRY3-LM - Motor Prolog en Python con Sistema de Derivadas

Intérprete de Prolog implementado en Python con soporte completo para cálculo simbólico de derivadas usando la regla de la cadena.

## Características

### Motor Prolog
- Parser completo para sintaxis Prolog
- Motor de resolución SLD con backtracking
- Unificación con occurs-check opcional
- Sistema de indexación de cláusulas
- REPL interactivo con visualización mejorada

### Predicados Built-in
- Control: `true/0`, `fail/0`
- Unificación: `=/2`, `\=/2`
- Testing de tipos: `var/1`, `nonvar/1`, `atom/1`, `number/1`, `compound/1`
- Aritmética: `is/2`, `=:=/2`, `=\=/2`, `</2`, `=</2`, `>/2`, `>=/2`
- Operadores infijos: `+`, `-`, `*`, `/`, `^` con precedencia correcta

### Sistema de Derivadas
- Derivadas de polinomios
- Derivadas de funciones trigonométricas: `sen/1`, `cos/1`, `tan/1`
- Derivadas de funciones trigonométricas inversas: `arctan/1`
- Derivadas de funciones exponenciales: `exp/1`
- Derivadas de funciones logarítmicas: `ln/1`
- Regla de la cadena para composiciones
- Reglas del producto y cociente

## Instalación

```bash
git clone https://github.com/Javier-Espana/PRY3-LM.git
cd PRY3-LM
```

## Uso

### Inicio Rápido

```bash

python main.py derivadas.pl

```

### Ejemplos de Derivadas (Notación Infija Natural)

```prolog
% Derivada de ln(x/(x+1))
?- derivada(ln(x/(x+1)), x, Y).
Y = (1 * (x + 1) - x * (1 + 0)) / (x + 1)^2 / (x / (x + 1))

% Derivada de sen(exp(3*x))
?- derivada(sen(exp(3*x)), x, Y).
Y = cos(exp(3 * x)) * (exp(3 * x) * (3 * 1))

% Derivada de (x^5+x^3)/(x^2+1)
?- derivada((x^5+x^3)/(x^2+1), x, Y).
Y = ((5 * x^4 * 1 + 3 * x^2 * 1) * (x^2 + 1) - (x^5 + x^3) * (2 * x^1 * 1 + 0)) / (x^2 + 1)^2

% Derivada de arctan((x^2+1)^10)
?- derivada(arctan((x^2+1)^10), x, Y).
Y = 10 * (x^2 + 1)^9 * (2 * x^1 * 1 + 0) / (1 + ((x^2 + 1)^10)^2)
```

## Autores

Proyecto desarrollado para el curso de Lógica Matemática.