#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Optional


class TokenType(Enum):
    """Классы лексем (Таблица 1.1)"""
    W = 'W'  # Служебные слова
    I = 'I'  # Идентификаторы
    O = 'O'  # Операции
    R = 'R'  # Разделители
    N = 'N'  # Числовые константы
    C = 'C'  # Строковые константы


@dataclass
class Token:
    """Лексема во внутреннем представлении (вид: <буква><код>)"""
    type: TokenType
    code: int
    value: str
    line: int
    column: int

    def __repr__(self) -> str:
        return f"{self.type.value}{self.code}"

    def to_internal(self) -> str:
        """Внутреннее представление лексемы"""
        return f"{self.type.value}{self.code}"


@dataclass
class IdentifierInfo:
    """Информация об идентификаторе (Таблица 1.6)"""
    code: int
    name: str
    proc_number: int = 0
    proc_level: int = 0
    proc_index: int = 0
    var_type: str = ""
    memory_size: int = 0