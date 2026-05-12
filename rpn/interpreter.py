#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Вычислитель обратной польской записи
Согласно стр. 1 методички: ОПЗ может быть вычислена за один просмотр цепочки слева направо
"""

from typing import List, Any
from lexer.scanner import Scanner


class RPNInterpreter:
    """
    Вычислитель обратной польской записи

    Основное преимущество ОПЗ: может быть вычислена за один просмотр
    цепочки слева направо, который часто называют проходом (стр. 1)
    """

    def __init__(self, scanner: Scanner):
        self.scanner = scanner
        self.id_to_name = scanner.id_to_name
        self.num_to_value = scanner.num_to_value
        self.str_to_value = scanner.str_to_value
        self.stack: List[str] = []

    def restore_value(self, token: str) -> str:
        """Восстановление значения по коду"""
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
        elif token.startswith('C'):
            try:
                code = int(token[1:])
                return f'"{self.str_to_value.get(code, token)}"'
            except:
                return token
        return token

    def is_operand(self, token: str) -> bool:
        """Проверка, является ли токен операндом"""
        if token.startswith(('I', 'N', 'C')):
            return True
        if token.isdigit() or (token.startswith('.') and len(token) > 1 and token[1:].isdigit()):
            return True
        if token.startswith('"') and token.endswith('"'):
            return True
        if token.startswith('$') or token.isalpha():
            return True
        return False

    def evaluate(self, rpn: List[str]) -> str:
        """
        Вычисление ОПЗ за один просмотр слева направо (стр. 1)

        Принцип вычисления:
        - Операнды помещаются в стек
        - При встрече с операцией из стека извлекаются операнды,
          операция выполняется, результат помещается в стек
        """
        self.stack = []

        print("\n" + "=" * 70)
        print("ВЫЧИСЛЕНИЕ ОБРАТНОЙ ПОЛЬСКОЙ ЗАПИСИ")
        print("(один просмотр слева направо)")
        print("=" * 70)
        print("\n{:<20} {:<30} {:<30}".format("Токен", "Стек", "Действие"))
        print("-" * 80)

        for token in rpn:
            # Обработка меток (заканчиваются на ":")
            if token.endswith(':'):
                self.stack.append(token)
                print("{:<20} {:<30} {:<30}".format(
                    token,
                    str(self.stack)[:30],
                    f"метка {token}"
                ))
                continue

            # Условный переход по лжи (УПЛ) - стр. 9
            if token == 'УПЛ':
                if len(self.stack) >= 2:
                    label = self.stack.pop()
                    condition = self.stack.pop()
                    result = f"if (!({condition})) goto {label}"
                    self.stack.append(result)
                    print("{:<20} {:<30} {:<30}".format(
                        token,
                        str(self.stack)[:30],
                        f"условный переход по лжи"
                    ))
                continue

            # Безусловный переход (БП) - стр. 9
            if token == 'БП':
                if len(self.stack) >= 1:
                    label = self.stack.pop()
                    result = f"goto {label}"
                    self.stack.append(result)
                    print("{:<20} {:<30} {:<30}".format(
                        token,
                        str(self.stack)[:30],
                        f"безусловный переход"
                    ))
                continue

            # Бинарные операции
            if token in ['+', '-', '*', '/', '%', '==', '!=', '<', '>', '<=', '>=', '&&', '||']:
                if len(self.stack) >= 2:
                    right = self.stack.pop()
                    left = self.stack.pop()
                    # Восстанавливаем значения, если это коды
                    left_val = self.restore_value(left) if left.startswith(('I', 'N', 'C')) else left
                    right_val = self.restore_value(right) if right.startswith(('I', 'N', 'C')) else right
                    result = f"({left_val} {token} {right_val})"
                    self.stack.append(result)
                    print("{:<20} {:<30} {:<30}".format(
                        token,
                        str(self.stack)[:30],
                        f"{left_val} {token} {right_val}"
                    ))
                continue

            # Унарная операция НЕ
            if token == '!':
                if len(self.stack) >= 1:
                    operand = self.stack.pop()
                    operand_val = self.restore_value(operand) if operand.startswith(('I', 'N', 'C')) else operand
                    result = f"!{operand_val}"
                    self.stack.append(result)
                    print("{:<20} {:<30} {:<30}".format(
                        token,
                        str(self.stack)[:30],
                        f"!{operand_val}"
                    ))
                continue

            # Оператор присваивания
            if token == ':=':
                if len(self.stack) >= 2:
                    right = self.stack.pop()
                    left = self.stack.pop()
                    left_val = self.restore_value(left) if left.startswith(('I', 'N', 'C')) else left
                    right_val = self.restore_value(right) if right.startswith(('I', 'N', 'C')) else right
                    result = f"{left_val} = {right_val}"
                    self.stack.append(result)
                    print("{:<20} {:<30} {:<30}".format(
                        token,
                        str(self.stack)[:30],
                        f"присваивание"
                    ))
                continue

            # GOTO (безусловный переход)
            if token == 'GOTO':
                if len(self.stack) >= 1:
                    label = self.stack.pop()
                    result = f"goto {label}"
                    self.stack.append(result)
                    print("{:<20} {:<30} {:<30}".format(
                        token,
                        str(self.stack)[:30],
                        f"goto {label}"
                    ))
                continue

            # Операнды помещаются в стек
            if self.is_operand(token):
                value = self.restore_value(token)
                self.stack.append(value)
                print("{:<20} {:<30} {:<30}".format(
                    token,
                    str(self.stack)[:30],
                    f"операнд: {value}"
                ))
                continue

            # Служебные токены (пропускаем)
            if token in ['IF', 'THEN', 'ELSE']:
                print("{:<20} {:<30} {:<30}".format(
                    token,
                    str(self.stack)[:30],
                    f"служебный токен (пропуск)"
                ))
                continue

            # Неизвестный токен
            print("{:<20} {:<30} {:<30}".format(
                token,
                str(self.stack)[:30],
                f"неизвестный токен"
            ))

        # Результат - последний элемент стека
        result = self.stack[-1] if self.stack else ""

        print("\n" + "-" * 80)
        print(f"РЕЗУЛЬТАТ ВЫЧИСЛЕНИЯ: {result}")

        return result