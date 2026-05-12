#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List, Optional
from lexer.token_types import Token, TokenType
from lexer.scanner import Scanner
from rpn.priorities import OperatorPriority


class RPNConverter:

    def __init__(self, scanner: Scanner):
        self.scanner = scanner
        self.tokens = scanner.tokens
        self.id_to_name = scanner.id_to_name
        self.num_to_value = scanner.num_to_value

        self.output: List[str] = []
        self.stack: List[str] = []
        self.context_stack = []
        self.rpn: List[str] = []
        self.label_counter = 1

        self.proc_counter = 1
        self.current_proc_num = 1  # Текущий номер процедуры для КО
        self.proc_level = 0
        self.in_declaration = False
        self.decl_vars: List[str] = []

    def new_label(self) -> str:
        label = f"M{self.label_counter}"
        self.label_counter += 1
        return label

    def get_token_str(self, token: Token) -> Optional[str]:
        if token.type == TokenType.I:
            return self.id_to_name.get(token.code, f"I{token.code}")

        if token.type == TokenType.N:
            return self.num_to_value.get(token.code, f"N{token.code}")

        if token.type == TokenType.W:
            codes = {2: 'DCL', 3: 'END', 4: 'FUNCTION', 5: 'GOTO',
                     6: 'IF', 7: 'PROC', 8: 'THEN', 9: 'MAIN', 10: 'ELSE', 11: 'WHILE', 12: 'DO'} #-------------------------------
            return codes.get(token.code, None)

        if token.type == TokenType.O:
            op_map = {1: '+', 2: '*', 3: '<', 4: '>', 5: ':=',
                      6: ':', 7: '<>', 8: '-', 9: '/', 10: '<=',
                      11: '>=', 12: '==', 13: '!=', 14: '&&', 15: '||', 16: '!'}
            return op_map.get(token.code, token.value)

        if token.type == TokenType.R and token.value != '\n':
            return token.value

        return None

    def convert(self) -> List[str]:
        self.output = []
        self.stack = []
        self.context_stack = []
        self.label_counter = 1
        self.proc_counter = 1
        self.current_proc_num = 1
        self.proc_level = 0
        self.in_declaration = False
        self.decl_vars = []

        print("\n" + "=" * 70)
        print("ПРОЦЕСС ПЕРЕВОДА В ОБРАТНУЮ ПОЛЬСКУЮ ЗАПИСЬ")
        print("=" * 70)
        print("\n{:<30} {:<50} {:<30}".format("Входной символ", "Выходная строка", "Стек"))
        print("-" * 110)

        i = 0
        while i < len(self.tokens):
            token = self.tokens[i]
            token_str = self.get_token_str(token)

            if token_str is None:
                i += 1
                continue

            output_str = " ".join(self.output)[:50]
            stack_str = " ".join(str(s) for s in self.stack)[:30]
            print("{:<30} {:<50} {:<30}".format(token_str, output_str, stack_str))

            # ========== MAIN ==========
            if token_str == 'MAIN':
                self.proc_level = 1
                self.current_proc_num = self.proc_counter
                self.output.append(f'MAIN {self.proc_counter} {self.proc_level} НП')
                self.proc_counter += 1
                if self.stack and self.stack[-1] == 'PROC':
                    self.stack.pop()
                i += 1
                continue

            # ========== PROC ==========
            if token_str == 'PROC':
                self.stack.append('PROC')
                i += 1
                continue

            # ========== CALC ==========
            if token_str == 'CALC' and self.stack and self.stack[-1] == 'PROC':
                self.proc_level += 1
                self.current_proc_num = self.proc_counter
                self.output.append(f'CALC {self.proc_counter} {self.proc_level} НП')
                self.proc_counter += 1
                self.stack.pop()
                i += 1
                continue


            #============ FUNCTION ===============
            if token_str == 'FUNCTION':
                # пропускаем само слово FUNCTION
                i += 1
                # следующее – имя функции
                if i >= len(self.tokens):
                    raise SyntaxError("Неожиданный конец после FUNCTION")
                func_name_token = self.tokens[i]
                if func_name_token.type != TokenType.I:
                    raise SyntaxError("Ожидалось имя функции после FUNCTION")
                func_name = self.get_token_str(func_name_token)
                i += 1
                # пропускаем '('
                if i >= len(self.tokens) or self.get_token_str(self.tokens[i]) != '(':
                    raise SyntaxError("Ожидалась '(' после имени функции")
                i += 1
                # пропускаем ')'
                if i >= len(self.tokens) or self.get_token_str(self.tokens[i]) != ')':
                    raise SyntaxError("Ожидалась ')' после '('")
                i += 1
                # должна быть '{'
                if i >= len(self.tokens) or self.get_token_str(self.tokens[i]) != '{':
                    raise SyntaxError("Ожидался '{' для тела функции")
                # выводим имя функции и НП
                self.output.append(func_name)
                self.output.append('НП')
                # помечаем в стеке, что началось тело функции (для закрытия КП)



                #self.stack.append(['FUNC_DEF', func_name])

                self.context_stack.append(['FUNC_DEF', func_name])

                # пропускаем '{'
                i += 1
                continue

            # ========== DCL ==========
            if token_str == 'DCL':
                self.in_declaration = True
                self.decl_vars = []
                i += 1
                continue

            # ========== DEC - пропускаем ==========
            if token_str == 'DEC':
                i += 1
                continue

            # ========== FIXED ==========
            if token_str == 'FIXED':
                # Добавляем накопленные переменные
                for var in self.decl_vars:
                    self.output.append(var)

                # Количество переменных
                var_count = len(self.decl_vars)
                self.output.append(str(var_count))

                # Тип DFD
                self.output.append('DFD')

                # КО (конец описания) - используем current_proc_num
                self.output.append(f'{self.current_proc_num} {self.proc_level} КО')

                self.in_declaration = False
                self.decl_vars = []
                i += 1
                continue

            # ========== END ==========
            if token_str == 'END':
                while self.stack:
                    op = self.stack.pop()
                    if op not in ['PROC', 'IF', 'WHILE'] and not str(op).startswith('M'):
                        if op not in ['GOTO']:
                            self.output.append(op)
                self.output.append('КП')
                i += 1
                continue

            # ========== ( ==========
            if token_str == '(':
                self.stack.append('(')
                i += 1
                continue

            # ========== ) ==========
            # if token_str == ')':
            #     while self.stack and self.stack[-1] != '(':
            #         self.output.append(self.stack.pop())
            #     if self.stack and self.stack[-1] == '(':
            #         self.stack.pop()
            #     i += 1
            #     continue
            if token_str == ')':
                # Если это конец вызова функции


                # if self.stack and isinstance(self.stack[-1], list) and self.stack[-1][0] == 'FUNC':
                #     marker = self.stack.pop()
                #     arg_count = marker[2]
                #     self.output.append(str(arg_count + 1))  # n+1
                #     self.output.append('Ф')
                #     i += 1
                #     continue

                if self.context_stack and isinstance(self.context_stack[-1], list) and self.context_stack[-1][0] == 'FUNC':
                    marker = self.context_stack.pop()
                    arg_count = marker[2]
                    self.output.append(str(arg_count + 1))  # n+1
                    self.output.append('Ф')
                    i += 1
                    continue



                # Обычная скобка
                while self.stack and self.stack[-1] != '(':
                    self.output.append(self.stack.pop())
                if self.stack and self.stack[-1] == '(':
                    self.stack.pop()
                i += 1
                continue



            #========== [ ===========
            if token_str == ']':
                # if self.stack and isinstance(self.stack[-1], list) and self.stack[-1][0] == 'ARR':
                #     marker = self.stack.pop()
                #     index_count = marker[2]
                #     self.output.append(str(index_count + 1))  # n+1
                #     self.output.append('АЭС')
                #     i += 1
                #     continue
                if self.context_stack and isinstance(self.context_stack[-1], list) and self.context_stack[-1][
                    0] == 'ARR':
                    marker = self.context_stack.pop()
                    index_count = marker[2]
                    self.output.append(str(index_count + 1))  # n+1
                    self.output.append('АЭС')
                    i += 1
                    continue
                else:
                    # неожиданная ']' – пропускаем или генерируем ошибку
                    i += 1
                    continue

            # ========== , ==========
            # if token_str == ',':
            #     i += 1
            #     continue
            if token_str == ',':
                # Если внутри вызова функции или массива – увеличиваем счётчик

                # if self.stack and isinstance(self.stack[-1], list) and self.stack[-1][0] in ('FUNC', 'ARR'):
                #     self.stack[-1][2] += 1

                if self.context_stack and isinstance(self.context_stack[-1], list) and self.context_stack[-1][0] in (
                'FUNC', 'ARR'):
                    self.context_stack[-1][2] += 1


                i += 1
                continue

            # ========== ; ==========
            if token_str == ';':
                #--------------------------------------------------------------------------------------------------------------
                # while self.stack and self.stack[-1] not in ['(', 'IF', 'PROC']:
                #     top = self.stack[-1]
                #     if str(top).startswith('M'):
                #         break
                #     self.output.append(self.stack.pop())
                # i += 1
                # continue

                while self.stack and self.stack[-1] not in ['(', 'IF', 'PROC', 'WHILE']:
                    top = self.stack[-1]
                    if str(top).startswith('M'):
                        break
                    self.output.append(self.stack.pop())
                i += 1
                continue

            # ========== { ==========
            if token_str == '{':
                # Начало блока - генерируем метку и условный переход -----------------------------------------------------------------
                # if self.stack and self.stack[-1] == 'IF':
                #     self.stack.pop()  # Убираем IF
                #     label = self.new_label()
                #     self.output.append(label)
                #     self.output.append('УПЛ')
                #     self.stack.append(label)
                # i += 1
                # continue
                if self.stack and (self.stack[-1] == 'IF' or self.stack[-1] == 'WHILE'):
                    self.stack.pop()  # Убираем IF или WHILE
                    label = self.new_label()
                    self.output.append(label)
                    self.output.append('УПЛ')
                    self.stack.append(label)
                i += 1
                continue

            # ========== } ==========
            # if token_str == '}':
            #     # Конец блока - добавляем метку
            #     if self.stack and str(self.stack[-1]).startswith('M'):
            #         label = self.stack.pop()
            #         self.output.append(f'{label}:')
            #     i += 1
            #     continue

            if token_str == '}':
                # Если это конец тела функции
                # if self.stack and isinstance(self.stack[-1], list) and self.stack[-1][0] == 'FUNC_DEF':
                #     self.stack.pop()
                #     self.output.append('КП')
                #     i += 1
                #     continue

                if self.context_stack and isinstance(self.context_stack[-1], list) and self.context_stack[-1][0] == 'FUNC_DEF':
                    # self.stack.pop()
                    self.context_stack.pop()
                    self.output.append('КП')
                    i += 1
                    continue

                # Конец обычного блока – добавляем метку (существующая логика)
                if self.stack and str(self.stack[-1]).startswith('M'):
                    label = self.stack.pop()
                    self.output.append(f'{label}:')
                i += 1
                continue

            # ========== : ==========
            if token_str == ':':
                if self.output and self.output[-1] not in [':', ';']:
                    label = self.output.pop()
                    self.output.append(f'{label}:')
                i += 1
                continue

            # ========== IF ==========
            if token_str == 'IF':
                self.stack.append('IF')
                i += 1
                continue

            # ========== THEN ==========
            if token_str == 'THEN':
                while self.stack and self.stack[-1] != 'IF':
                    self.output.append(self.stack.pop())
                if self.stack and self.stack[-1] == 'IF':
                    self.stack.pop()
                    label = self.new_label()
                    self.output.append(label)
                    self.output.append('УПЛ')
                    self.stack.append(label)
                i += 1
                continue

            # ========== ELSE ==========
            if token_str == 'ELSE':
                if self.stack and str(self.stack[-1]).startswith('M'):
                    label = self.stack.pop()
                    else_label = self.new_label()
                    self.output.append(else_label)
                    self.output.append('БП')
                    self.output.append(f'{label}:')
                    self.stack.append(else_label)
                i += 1
                continue

            # ========== GOTO ==========
            if token_str == 'GOTO':
                self.stack.append('GOTO')
                i += 1
                continue

            # ========== WHILE ==========
            if token_str == 'WHILE': #----------------------------------------------------------------------------------------
                self.stack.append('WHILE')
                i += 1
                continue

            # ========== DO ==========
            if token_str == 'DO': #-------------------------------------------------------------------------------------------
                while self.stack and self.stack[-1] != 'WHILE':
                    self.output.append(self.stack.pop())
                if self.stack and self.stack[-1] == 'WHILE':
                    self.stack.pop()
                    label = self.new_label()
                    self.output.append(label)
                    self.output.append('УПЛ')
                    self.stack.append(label)
                i += 1
                continue

            # ========== ИДЕНТИФИКАТОРЫ (переменные) ==========
            # if token.type == TokenType.I and token_str != 'DEC':
            #     if self.in_declaration:
            #         self.decl_vars.append(token_str)
            #     else:
            #         self.output.append(token_str)
            #     i += 1
            #     continue
            if token.type == TokenType.I and token_str != 'DEC':
                if self.in_declaration:
                    self.decl_vars.append(token_str)
                    i += 1
                    continue
                else:
                    # Проверка на вызов функции или доступ к массиву
                    if i + 1 < len(self.tokens):
                        next_token = self.tokens[i + 1]
                        next_str = self.get_token_str(next_token)
                        if next_str == '(':
                            # Вызов функции
                            self.output.append(token_str)


                            #self.stack.append(['FUNC', token_str, 1])  # счётчик аргументов = 1
                            self.context_stack.append(['FUNC', token_str, 1])



                            i += 2  # пропускаем идентификатор и '('
                            continue
                        elif next_str == '[':
                            # Доступ к массиву
                            self.output.append(token_str)


                            # self.stack.append(['ARR', token_str, 1])  # счётчик индексов = 1
                            self.context_stack.append(['ARR', token_str, 1])


                            i += 2  # пропускаем идентификатор и '['
                            continue
                    # Обычный идентификатор
                    self.output.append(token_str)
                    i += 1
                    continue


            # ========== Строки =============
            if token.type == TokenType.C:
                self.output.append(token_str)
                i += 1
                continue

            # ========== ЧИСЛА ==========
            if token.type == TokenType.N:
                self.output.append(token_str)
                i += 1
                continue

            # ========== := ==========
            if token_str == ':=':
                priority = OperatorPriority.get(token_str)
                while (self.stack and
                       self.stack[-1] != '(' and
                       self.stack[-1] != 'IF' and
                       self.stack[-1] != 'WHILE' and
                       not str(self.stack[-1]).startswith('M') and
                       self.stack[-1] != 'PROC' and
                       self.stack[-1] != 'GOTO' and
                       OperatorPriority.get(self.stack[-1]) >= priority):
                    self.output.append(self.stack.pop())
                self.stack.append(token_str)
                i += 1
                continue

            # ========== БИНАРНЫЕ ОПЕРАЦИИ ==========
            priority = OperatorPriority.get(token_str)
            # while (self.stack and-----------------------------------------------------------------------------------------
            #        self.stack[-1] != '(' and
            #        self.stack[-1] != 'IF' and
            #        not str(self.stack[-1]).startswith('M') and
            #        self.stack[-1] != 'PROC' and
            #        self.stack[-1] != 'GOTO' and
            #        OperatorPriority.get(self.stack[-1]) >= priority):
            #     self.output.append(self.stack.pop())
            # self.stack.append(token_str)
            # i += 1
            while (self.stack and
                   self.stack[-1] != '(' and
                   self.stack[-1] != 'IF' and
                   self.stack[-1] != 'WHILE' and
                   not str(self.stack[-1]).startswith('M') and
                   self.stack[-1] != 'PROC' and
                   self.stack[-1] != 'GOTO' and
                   OperatorPriority.get(self.stack[-1]) >= priority):
                self.output.append(self.stack.pop())
            self.stack.append(token_str)
            i += 1

        # Выталкиваем оставшиеся операции----------------------------------------------------------------------------------------
        # while self.stack:
        #     op = self.stack.pop()
        #     if str(op).startswith('M') and len(str(op)) > 1:
        #         self.output.append(f'{op}:')
        #     elif op not in ['IF', 'PROC']:
        #         self.output.append(op)
        #
        # self.rpn = self.output
        # return self.rpn

        while self.stack:
            op = self.stack.pop()
            if str(op).startswith('M') and len(str(op)) > 1:
                self.output.append(f'{op}:')
            elif op not in ['IF', 'PROC', 'WHILE']:
                self.output.append(op)

        self.rpn = self.output
        return self.rpn

    def print_result(self) -> None:
        # rpn = self.convert()

        print("\n" + "=" * 70)
        print("РЕЗУЛЬТАТ ПЕРЕВОДА В ОБРАТНУЮ ПОЛЬСКУЮ ЗАПИСЬ")
        print("=" * 70)

        print("\nОПЗ программы (читаемый вид):")
        print("-" * 70)
        cleaned = [t for t in self.rpn if t and t.strip()]
        print(" ".join(cleaned))

        # print("\nОПЗ в кодированном виде:")
        # print("-" * 70)
        # coded = []
        # for token in cleaned:
        #     if token in self.id_to_name.values() and token != 'DEC':
        #         for code, name in self.id_to_name.items():
        #             if name == token:
        #                 coded.append(f"I{code}")
        #                 break
        #         else:
        #             coded.append(token)
        #     elif token in self.num_to_value.values():
        #         for code, val in self.num_to_value.items():
        #             if val == token:
        #                 coded.append(f"N{code}")
        #                 break
        #         else:
        #             coded.append(token)
        #     else:
        #         coded.append(token)
        # print(" ".join(coded))


    def get_result(self) -> None:
        rpn = self.convert()

        res_string = "\n" + "=" * 70 + "\nРЕЗУЛЬТАТ ПЕРЕВОДА В ОБРАТНУЮ ПОЛЬСКУЮ ЗАПИСЬ\n" + "=" * 70 + "\n"
        cleaned = [t for t in rpn if t and t.strip()]
        res_string += "\nОПЗ программы (читаемый вид):\n" + "-" * 70 + "\n" + " ".join(cleaned)

        return res_string

        # print("\n" + "=" * 70)
        # print("РЕЗУЛЬТАТ ПЕРЕВОДА В ОБРАТНУЮ ПОЛЬСКУЮ ЗАПИСЬ")
        # print("=" * 70)

        # print("\nОПЗ программы (читаемый вид):")
        # print("-" * 70)
        # cleaned = [t for t in rpn if t and t.strip()]
        # print(" ".join(cleaned))


# if __name__ == "__main__":
#     from lexer.scanner import Scanner
#
#     test_program = """PROC MAIN;
# DCL (A1, A2) DEC FIXED;
# A1 = 378;
# A2 = .73;
# PROC CALC;
# DCL (SUM, MULT) DEC FIXED;
# IF A1 + A2 <> 3.2 THEN GOTO P;
# SUM = (A1 + A2) * A2;
# P: MULT = A1 * A2;
# END;
# END;"""
#
#     scanner = Scanner(test_program)
#     scanner.scan()
#     converter = RPNConverter(scanner)
#     converter.print_result()