#!/usr/bin/env python3
"""
Punto de entrada principal del intérprete Prolog en Python.

Uso:
    python main.py                    # Iniciar REPL interactivo
    python main.py archivo.pl         # Cargar archivo y abrir REPL
    python main.py --help             # Mostrar ayuda

Opciones de configuración:
    --occurs-check    Habilitar occurs-check en unificación
    --trace          Habilitar modo de tracing
    --max-depth N    Límite máximo de profundidad de resolución
"""

import argparse
import sys
from pathlib import Path

# Agregar src/ al path para imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from builtins.registry import GLOBAL_REGISTRY, load_core_builtins
from core.constants import DEFAULT_CONFIG
from core.errors import LoadError, PrologError
from io.loader import consult
from io.repl import start
from solver.engine import Engine


def setup_argument_parser() -> argparse.ArgumentParser:
    """Configura el parser de argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(
        description="Intérprete Prolog en Python",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python main.py                    # REPL interactivo
  python main.py test.pl            # Cargar test.pl y abrir REPL
  python main.py --occurs-check     # REPL con occurs-check habilitado
  python main.py --trace test.pl    # Cargar archivo con tracing

Comandos del REPL:
  \\help                             # Mostrar ayuda
  \\quit                             # Salir del REPL
  \\load archivo.pl                 # Cargar archivo
  \\trace on/off                    # Activar/desactivar tracing
  \\listing                         # Listar predicados cargados
  \\stats                           # Mostrar estadísticas
        """
    )
    
    # Archivo opcional a cargar
    parser.add_argument(
        "file", 
        nargs="?", 
        help="Archivo .pl a cargar al inicio (opcional)"
    )
    
    # Opciones de configuración
    parser.add_argument(
        "--occurs-check", 
        action="store_true", 
        help="Habilitar occurs-check en unificación (más lento pero más seguro)"
    )
    
    parser.add_argument(
        "--trace", 
        action="store_true", 
        help="Habilitar modo de tracing para debug"
    )
    
    parser.add_argument(
        "--max-depth", 
        type=int, 
        default=DEFAULT_CONFIG.max_depth, 
        help=f"Límite máximo de profundidad (default: {DEFAULT_CONFIG.max_depth})"
    )
    
    parser.add_argument(
        "--version", 
        action="version", 
        version=f"Prolog-Python {DEFAULT_CONFIG.version}"
    )
    
    return parser


def initialize_engine(args: argparse.Namespace) -> Engine:
    """Inicializa el motor Prolog con la configuración especificada."""
    
    # Crear engine con configuración
    engine = Engine(occurs_check=args.occurs_check)
    
    # TODO: Añadir más opciones de configuración cuando estén implementadas
    # engine.set_option("trace", args.trace)
    # engine.set_option("max_depth", args.max_depth)
    
    # Cargar predicados built-in
    load_core_builtins(GLOBAL_REGISTRY)
    
    # TODO: PARA COMPAÑEROS DE GRUPO
    # Descomentar cuando implementen los módulos correspondientes:
    # load_arithmetic_builtins(GLOBAL_REGISTRY)
    # load_list_builtins(GLOBAL_REGISTRY)
    
    return engine


def main() -> None:
    """Función principal del CLI."""
    
    # Parsear argumentos
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    try:
        # Inicializar el motor
        engine = initialize_engine(args)
        
        # Cargar archivo si se especificó
        if args.file:
            file_path = Path(args.file)
            if not file_path.exists():
                print(f"Error: El archivo '{args.file}' no existe.")
                sys.exit(1)
            
            print(f"Cargando {args.file}...")
            try:
                consult(str(file_path), engine)
                print(f"Archivo {args.file} cargado exitosamente.")
            except LoadError as e:
                print(f"Error al cargar {args.file}: {e.message}")
                sys.exit(1)
            except PrologError as e:
                print(f"Error de Prolog al cargar {args.file}: {e}")
                sys.exit(1)
        
        # Mensaje de bienvenida
        print(f"Prolog-Python {DEFAULT_CONFIG.version}")
        print("Escriba \\help para obtener ayuda.")
        if args.occurs_check:
            print("[Occurs-check habilitado]")
        if args.trace:
            print("[Modo trace habilitado]")
        print()
        
        # Iniciar REPL
        start(engine)
        
    except KeyboardInterrupt:
        print("\n\nInterrumpido por el usuario.")
        sys.exit(0)
    except Exception as e:
        print(f"Error fatal: {e}")
        if args.trace:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()