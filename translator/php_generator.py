#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List
from lexer.scanner import Scanner


class PHPGenerator:

    def __init__(self, scanner: Scanner, rpn: List[str]):
        self.scanner = scanner
        self.rpn = rpn
        self.id_to_name = scanner.id_to_name
        self.num_to_value = scanner.num_to_value

        self.name_to_code = {name: code for code, name in self.id_to_name.items()}
        self.stack: List[str] = []
        self.php_code: List[str] = []

    def restore_value(self, token: str) -> str:
        if token.startswith('I'):
            try:
                code = int(token[1:])
                return f"${self.id_to_name.get(code, token)}"
            except:
                return token
        elif token.startswith('N'):
            try:
                code = int(token[1:])
                return self.num_to_value.get(code, token)
            except:
                return token
        elif token.isalpha() and token in self.name_to_code:
            return f"${token}"
        elif token.startswith('M') and token[1:].isdigit():
            return token
        return token

    def generate(self) -> str:
        self.stack = []
        self.php_code = ['<?php', '']

        print("\n" + "=" * 70)
        print("ГЕНЕРАЦИЯ PHP КОДА")
        print("=" * 70)

        i = 0
        while i < len(self.rpn):
            token = self.rpn[i]

            # Метки
            if token.endswith(':'):
                self.php_code.append(f"{token}")
                i += 1
                continue

            # Операнды в стек
            if (token.startswith(('I', 'N')) or
                    token.isdigit() or
                    (token.isalpha() and token not in ['УПЛ', 'БП', ':=', '+', '-', '*', '/', '&&', '||', '!', '<', '>',
                                                       '<=', '>=', '==', '!='])):
                val = self.restore_value(token)
                self.stack.append(val)
                i += 1
                continue

            # Присваивание
            if token == ':=':
                if len(self.stack) >= 2:
                    right = self.stack.pop()
                    left = self.stack.pop()
                    self.php_code.append(f"{left} = {right};")
                    i += 1
                continue

            # Бинарные операции
            if token in ['+', '-', '*', '/', '&&', '||', '<', '>', '<=', '>=', '==', '!=']:
                if len(self.stack) >= 2:
                    right = self.stack.pop()
                    left = self.stack.pop()
                    result = f"({left} {token} {right})"
                    self.stack.append(result)
                i += 1
                continue

            # Унарное НЕ
            if token == '!':
                if len(self.stack) >= 1:
                    operand = self.stack.pop()
                    result = f"!{operand}"
                    self.stack.append(result)
                i += 1
                continue

            # Условный переход
            if token == 'УПЛ':
                if len(self.stack) >= 2:
                    label = self.stack.pop()
                    condition = self.stack.pop()
                    self.php_code.append(f"if (!({condition})) goto {label};")
                i += 1
                continue

            # Безусловный переход
            if token == 'БП':
                if len(self.stack) >= 1:
                    label = self.stack.pop()
                    self.php_code.append(f"goto {label};")
                i += 1
                continue

            i += 1

        self.php_code.append("")
        self.php_code.append("?>")
        return "\n".join(self.php_code)