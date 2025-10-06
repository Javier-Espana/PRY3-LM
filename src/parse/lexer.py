"""
Tokenizador (lexer) para un subconjunto de Prolog.

Soporta: átomos, variables, números, paréntesis, coma, punto, listas
([, ], |) y el operador ':-' para reglas. Comentarios: '%' de línea.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, Optional, Tuple

from core.errors import SyntaxErrorProlog


@dataclass(frozen=True)
class Token:
    kind: str
    lexeme: str
    line: int
    col: int


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.i = 0
        self.line = 1
        self.col = 1

    def _peek_char(self) -> str:
        return "" if self.i >= len(self.source) else self.source[self.i]

    def _advance(self) -> str:
        ch = self._peek_char()
        if not ch:
            return ""
        self.i += 1
        if ch == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def _match(self, expected: str) -> bool:
        if self._peek_char() == expected:
            self._advance()
            return True
        return False

    def tokens(self) -> Iterator[Token]:
        while True:
            tok = self._next_token()
            yield tok
            if tok.kind == "EOF":
                break

    def _skip_ws_and_comments(self) -> None:
        while True:
            ch = self._peek_char()
            if ch in " \t\r\n":
                self._advance()
                continue
            # comentario de línea: % ... \n
            if ch == "%":
                self._advance()  # consumir el %
                while True:
                    ch = self._peek_char()
                    if not ch or ch == "\n":
                        break
                    self._advance()
                continue
            break

    def _next_token(self) -> Token:
        self._skip_ws_and_comments()
        start_line, start_col = self.line, self.col
        ch = self._peek_char()
        if not ch:
            return Token("EOF", "", start_line, start_col)

        # puntación simple
        if ch in "(),[].|":
            self._advance()
            return Token(ch, ch, start_line, start_col)

        # ':-'
        if ch == ":":
            self._advance()
            if self._match("-"):
                return Token(":-", ":-", start_line, start_col)
            raise SyntaxErrorProlog("se esperaba '-' tras ':'", start_line, start_col)

        # '.' final de cláusula
        if ch == ".":
            self._advance()
            return Token(".", ".", start_line, start_col)

        # variable (Mayúscula o _)
        if ch == "_" or ch.isalpha() and ch.isupper():
            ident = self._consume_ident()
            return Token("VAR", ident, start_line, start_col)

        # átomo (minúscula inicial) o nombre de functor
        if ch.isalpha() and ch.islower():
            ident = self._consume_ident()
            return Token("ATOM", ident, start_line, start_col)

        # número
        if ch.isdigit():
            num = self._consume_number()
            return Token("NUMBER", num, start_line, start_col)

        raise SyntaxErrorProlog(f"carácter inesperado: '{ch}'", start_line, start_col)

    def _consume_ident(self) -> str:
        start = self.i
        while True:
            ch = self._peek_char()
            if ch.isalnum() or ch == "_":
                self._advance()
            else:
                break
        return self.source[start:self.i]

    def _consume_number(self) -> str:
        start = self.i
        while self._peek_char().isdigit():
            self._advance()
        if self._peek_char() == "." and self._peek_next().isdigit():
            self._advance()
            while self._peek_char().isdigit():
                self._advance()
        return self.source[start:self.i]

    def _peek_next(self) -> str:
        return "" if self.i + 1 >= len(self.source) else self.source[self.i + 1]

