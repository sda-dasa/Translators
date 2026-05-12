#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lexer.scanner import Scanner
from rpn.converter import RPNConverter
from translator import PHPGenerator


def main():


    with open("C:/Users/Даша/PycharmProjects/RPN_TRans_/INPUT_NEW.txt", 'r', encoding='utf-8') as f:
        r_code = f.read()

    scanner = Scanner(Scanner.preprocess(r_code))
    tokens = scanner.scan()
    print (tokens)

    converter = RPNConverter(scanner)
    converter.print_result()
    php_gen = PHPGenerator(scanner, converter.convert())
    print (php_gen.generate())




    # print("=" * 70)
    # print("     ЛАБОРАТОРНАЯ РАБОТА №2")
    # print("     ПЕРЕВОД ПРОГРАММЫ В ОБРАТНУЮ ПОЛЬСКУЮ ЗАПИСЬ")
    # print("=" * 70)
    # res_string = "=" * 70 + "\n     ЛАБОРАТОРНАЯ РАБОТА №2" + "\n     ПЕРЕВОД ПРОГРАММЫ В ОБРАТНУЮ ПОЛЬСКУЮ ЗАПИСЬ\n"+ "=" * 70 + "\n"
    #
    # with open("C:/Users/Даша/PycharmProjects/RPN_TRans_/INPUT.txt", 'r', encoding='utf-8') as f:
    #     r_code = f.read()
    #
    # res_string += "\n" + "─" * 70 + "ВХОДНАЯ ПРОГРАММА (R):\n" + "─" * 70 + "\n"
    #
    # res_string += r_code + '\n'
    #
    # res_string += "\n" + "─" * 70 +"\nЭТАП 1: ЛЕКСИЧЕСКИЙ АНАЛИЗ\n" + "─" * 70 + "\n"
    #
    #
    # scanner = Scanner(Scanner.preprocess(r_code))
    # tokens = scanner.scan()
    # print (tokens)
    #
    # res_string += " ".join([token.__repr__() for token in tokens]) + "\n"
    #
    #
    # if tokens:
    #
    #     res_string += "\n" + "\n" + "─" * 70
    #
    #     converter = RPNConverter(scanner)
    #     res_string += converter.get_result()
    #     converter.print_result()
    #
    # else:
    #     print("\nОШИБКА: Не найдено лексем для обработки!")
    #
    # res_string += "\n" + "=" * 70 + "\nРАБОТА ЗАВЕРШЕНА\n" + "=" * 70
    #
    # with open("C:/Users/Даша/PycharmProjects/RPN_TRans_/RESULTS.txt", 'w', encoding='utf-8') as f:
    #     f.write(res_string)
    #
    # print("\n" + "=" * 70)
    # print("РАБОТА ЗАВЕРШЕНА")
    # print("=" * 70)












if __name__ == "__main__":
    main()


