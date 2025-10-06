# Paquete raíz del motor Prolog en Python.
#
# Este paquete agrupa los módulos principales:
# - core/: tipos y utilidades base del motor
# - parse/: lexer y parser para Prolog (términos, cláusulas, operadores)
# - solver/: unificación, elección (choice points), backtracking y resolución SLD
# - builtins/: predicados y operadores predefinidos
# - io/: carga de archivos .pl y REPL (interfaz)
# - utils/: herramientas auxiliares
#
# Nota de diseño:
# - Evitar dependencias cíclicas; los módulos de capas superiores dependen de core.
# - Mantener APIs explícitas y documentadas en cada módulo.
