#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List, Dict, Optional
from lexer.token_types import Token, TokenType, IdentifierInfo
from lexer.tables import KEYWORDS, OPERATORS, DELIMITERS


class Scanner:
    """Лексический анализатор"""

    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.length = len(source)
        self.line = 1
        self.column = 1

        self.identifiers: Dict[str, int] = {}
        self.numbers: Dict[str, int] = {}
        self.strings: Dict[str, int] = {}

        self.identifier_counter = 1
        self.number_counter = 1
        self.string_counter = 1

        self.id_to_name: Dict[int, str] = {}
        self.num_to_value: Dict[int, str] = {}
        self.str_to_value: Dict[int, str] = {}

        self.identifiers_info: Dict[int, IdentifierInfo] = {}
        self.tokens: List[Token] = []

    def current_char(self) -> str:
        if self.pos < self.length:
            return self.source[self.pos]
        return '\0'

    def peek_char(self) -> str:
        if self.pos + 1 < self.length:
            return self.source[self.pos + 1]
        return '\0'

    def next_char(self) -> None:
        if self.current_char() == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        self.pos += 1

    def skip_whitespace(self) -> None:
        while self.pos < self.length and self.current_char() in ' \t\r':
            self.next_char()

    def skip_comment(self) -> bool:
        if self.current_char() == '/' and self.peek_char() == '/':
            self.next_char()
            self.next_char()
            while self.pos < self.length and self.current_char() != '\n':
                self.next_char()
            return True
        return False

    def read_number(self) -> Token:
        start = self.pos
        start_line, start_col = self.line, self.column

        while self.pos < self.length and self.current_char().isdigit():
            self.next_char()

        if self.pos < self.length and self.current_char() == '.' and self.peek_char().isdigit():
            self.next_char()
            while self.pos < self.length and self.current_char().isdigit():
                self.next_char()

        num_str = self.source[start:self.pos]

        if num_str not in self.numbers:
            self.numbers[num_str] = self.number_counter
            self.num_to_value[self.number_counter] = num_str
            self.number_counter += 1

        code = self.numbers[num_str]
        return Token(TokenType.N, code, num_str, start_line, start_col)

    def read_identifier_or_keyword(self) -> Optional[Token]:
        start = self.pos
        start_line, start_col = self.line, self.column

        while self.pos < self.length and (self.current_char().isalnum() or self.current_char() == '_'):
            self.next_char()

        word = self.source[start:self.pos]

        # Пропускаем 'let' - возвращаем None, но не прерываем сканирование
        if word == 'let':
            return None

        # Проверяем служебные слова PL/1 (для совместимости)
        if word.upper() in KEYWORDS:
            code = KEYWORDS[word.upper()]
            return Token(TokenType.W, code, word, start_line, start_col)
        else:
            # Идентификатор
            if word not in self.identifiers:
                self.identifiers[word] = self.identifier_counter
                self.id_to_name[self.identifier_counter] = word
                self.identifiers_info[self.identifier_counter] = IdentifierInfo(
                    code=self.identifier_counter,
                    name=word
                )
                self.identifier_counter += 1
            code = self.identifiers[word]
            return Token(TokenType.I, code, word, start_line, start_col)

    def read_operator(self) -> Token:
        start_line, start_col = self.line, self.column

        # Проверка на двулитерные операторы
        two_char = self.source[self.pos:self.pos + 2] if self.pos + 1 < self.length else ""

        if two_char in OPERATORS:
            self.pos += 2
            code = OPERATORS[two_char]
            return Token(TokenType.O, code, two_char, start_line, start_col)

        ch = self.current_char()
        if ch in OPERATORS:
            self.next_char()
            code = OPERATORS[ch]
            return Token(TokenType.O, code, ch, start_line, start_col)

        raise SyntaxError(f"Ошибка: неизвестный символ '{ch}'")

    def read_delimiter(self) -> Token:
        start_line, start_col = self.line, self.column
        ch = self.current_char()
        self.next_char()

        if ch in DELIMITERS:
            code = DELIMITERS[ch]
            return Token(TokenType.R, code, ch, start_line, start_col)
        else:
            raise SyntaxError(f"Ошибка: неизвестный разделитель '{ch}'")

    def get_next_token(self) -> Optional[Token]:
        self.skip_whitespace()

        if self.pos >= self.length:
            return None

        if self.skip_comment():
            return self.get_next_token()

        ch = self.current_char()

        # Строковые константы

        if ch in ('"', "'"):
            return self.read_string()

        # Числа
        if ch.isdigit() or (ch == '.' and self.peek_char().isdigit()):
            return self.read_number()

        # Идентификаторы и ключевые слова
        if ch.isalpha() or ch == '_':
            return self.read_identifier_or_keyword()

        # Операторы
        if ch in OPERATORS or (self.pos + 1 < self.length and self.source[self.pos:self.pos + 2] in OPERATORS):
            return self.read_operator()

        # Разделители
        if ch in DELIMITERS:
            return self.read_delimiter()

        # Конец строки
        if ch == '\n':
            self.next_char()
            return self.get_next_token()

        raise SyntaxError(f"Ошибка: неизвестный символ '{ch}' на строке {self.line}")

    def scan(self) -> List[Token]:
        self.tokens = []
        while True:
            token = self.get_next_token()
            if token is None:
                # Если достигли конца файла, выходим
                if self.pos >= self.length:
                    break
                # Иначе продолжаем сканирование
                continue
            self.tokens.append(token)
        return self.tokens

    def read_string(self) -> Token:
        start = self.pos
        start_line, start_col = self.line, self.column
        quote = self.current_char()
        self.next_char()
        while self.pos < self.length and self.current_char() != quote:
            self.next_char()
        if self.pos < self.length:
            self.next_char()
        str_value = self.source[start + 1:self.pos - 1]  # содержимое без кавычек
        if str_value not in self.strings:
            self.strings[str_value] = self.string_counter
            self.str_to_value[self.string_counter] = str_value
            self.string_counter += 1
        code = self.strings[str_value]
        return Token(TokenType.C, code, str_value, start_line, start_col)


    @staticmethod
    def preprocess(text):
        import re
        pattern = r'(\b[a-zA-Z_][a-zA-Z0-9_]*)\s*<-\s*function\s*(\([^)]*\)\s*\{)'
        replacement = r'function \1 \2'
        new_text = re.sub(pattern, replacement, text).replace("<-", "=")

        return new_text


    def print_tables(self) -> None:
        print("\n" + "=" * 70)
        print("ТАБЛИЦЫ ЛЕКСИЧЕСКОГО АНАЛИЗАТОРА")
        print("=" * 70)

        if self.id_to_name:
            print("\n┌" + "─" * 68 + "┐")
            print("│{:^68}│".format("ИДЕНТИФИКАТОРЫ (Таблица 1.6)"))
            print("├" + "─" * 68 + "┤")
            for code, name in sorted(self.id_to_name.items(), key=lambda x: x[0]):
                print(f"│  {code:3d}  →  {name:<30} │")
            print("└" + "─" * 68 + "┘")

        if self.num_to_value:
            print("\n┌" + "─" * 68 + "┐")
            print("│{:^68}│".format("ЧИСЛОВЫЕ КОНСТАНТЫ (Таблица 1.5)"))
            print("├" + "─" * 68 + "┤")
            for code, value in sorted(self.num_to_value.items(), key=lambda x: x[0]):
                print(f"│  {code:3d}  →  {value:<30} │")
            print("└" + "─" * 68 + "┘")
