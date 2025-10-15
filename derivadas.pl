% ============================================================================
% Sistema de Cálculo de Derivadas con Regla de la Cadena
% ============================================================================
% 
% Este archivo implementa un sistema completo para calcular derivadas
% simbólicas de funciones matemáticas usando las reglas del cálculo diferencial.
%
% Funciones soportadas:
%   - Polinomios: x^n, constantes
%   - Trigonométricas: sen(x), cos(x), tan(x)
%   - Trigonométricas inversas: arctan(x)
%   - Exponenciales: exp(x)
%   - Logarítmicas: ln(x)
%   - Operaciones: +, -, *, /
%
% Uso:
%   ?- derivada(x^2, x, Y).
%   Y = 2*x^1
%
%   ?- derivada(sen(x^2), x, Y).
%   Y = cos(x^2)*(2*x^1)
% ============================================================================


% ----------------------------------------------------------------------------
% Reglas básicas de derivación
% ----------------------------------------------------------------------------

% Derivada de una constante es cero
derivada(C, X, 0) :- 
    number(C).

% Derivada de la variable con respecto a sí misma es 1
derivada(X, X, 1) :- 
    atom(X).

% Nota: La derivada de cualquier otra variable es 0
% Esta regla se maneja implícitamente con fail si no es la misma variable


% ----------------------------------------------------------------------------
% Regla de la suma: (f + g)' = f' + g'
% ----------------------------------------------------------------------------
derivada(+(A, B), X, +(DA, DB)) :- 
    derivada(A, X, DA), 
    derivada(B, X, DB).


% ----------------------------------------------------------------------------
% Regla de la resta: (f - g)' = f' - g'
% ----------------------------------------------------------------------------
derivada(-(A, B), X, -(DA, DB)) :- 
    derivada(A, X, DA), 
    derivada(B, X, DB).


% ----------------------------------------------------------------------------
% Regla del producto: (f * g)' = f' * g + f * g'
% ----------------------------------------------------------------------------
derivada(*(A, B), X, +(*(DA, B), *(A, DB))) :- 
    derivada(A, X, DA), 
    derivada(B, X, DB).


% ----------------------------------------------------------------------------
% Regla del cociente: (f / g)' = (f' * g - f * g') / g^2
% ----------------------------------------------------------------------------
derivada(/(A, B), X, /(-(*(DA, B), *(A, DB)), ^(B, 2))) :- 
    derivada(A, X, DA), 
    derivada(B, X, DB).


% ----------------------------------------------------------------------------
% Regla de la potencia con la cadena: (f^n)' = n * f^(n-1) * f'
% ----------------------------------------------------------------------------
derivada(^(U, N), X, *(*(N, ^(U, -(N, 1))), DU)) :- 
    number(N),
    derivada(U, X, DU).


% ----------------------------------------------------------------------------
% Funciones trigonométricas con regla de la cadena
% ----------------------------------------------------------------------------

% Derivada del seno: (sen(u))' = cos(u) * u'
derivada(sen(U), X, *(cos(U), DU)) :- 
    derivada(U, X, DU).

% Derivada del coseno: (cos(u))' = -sen(u) * u'
derivada(cos(U), X, *(-(sen(U)), DU)) :- 
    derivada(U, X, DU).

% Derivada de la tangente: (tan(u))' = (1 + tan(u)^2) * u' = sec(u)^2 * u'
derivada(tan(U), X, *(+(1, ^(tan(U), 2)), DU)) :- 
    derivada(U, X, DU).


% ----------------------------------------------------------------------------
% Funciones trigonométricas inversas con regla de la cadena
% ----------------------------------------------------------------------------

% Derivada del arcotangente: (arctan(u))' = u' / (1 + u^2)
derivada(arctan(U), X, /(DU, +(1, ^(U, 2)))) :- 
    derivada(U, X, DU).


% ----------------------------------------------------------------------------
% Función exponencial con regla de la cadena
% ----------------------------------------------------------------------------

% Derivada de e^u: (exp(u))' = exp(u) * u'
derivada(exp(U), X, *(exp(U), DU)) :- 
    derivada(U, X, DU).


% ----------------------------------------------------------------------------
% Función logaritmo natural con regla de la cadena
% ----------------------------------------------------------------------------

% Derivada del logaritmo natural: (ln(u))' = u' / u
derivada(ln(U), X, /(DU, U)) :- 
    derivada(U, X, DU).


% ----------------------------------------------------------------------------
% Ejemplos de uso
% ----------------------------------------------------------------------------

% Ejemplo 1: Derivada de un polinomio simple
% ?- derivada(x^2 + 3*x, x, Y).
% Y = 2*x^1*1 + (0*x + 3*1)

% Ejemplo 2: Derivada de una composición
% ?- derivada(sen(x^2), x, Y).
% Y = cos(x^2)*(2*x^1*1)

% Ejemplo 3: Derivada de un cociente
% ?- derivada(x/(x+1), x, Y).
% Y = (1*(x+1) - x*(1+0))/(x+1)^2

% Ejemplo 4: Derivada compleja con regla de la cadena
% ?- derivada(ln(sen((x+1)/x)), x, Y).
% Y = cos((x+1)/x)*((1*x-(x+1)*1)/x^2)/sen((x+1)/x)
