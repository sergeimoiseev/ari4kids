#!/usr/bin/env python
# -*- coding: utf-8 -*-
from fractions import Fraction
from random import choice, randint
import re


def fraction_text(value):
    return f"{value.numerator}/{value.denominator}"


def simple_fraction(min_value=1, max_value=9):
    while True:
        denominator = randint(2, max_value)
        numerator = randint(min_value, max_value)
        value = Fraction(numerator, denominator)
        if value.denominator != 1:
            return value


def format_fraction(value):
    return fraction_text(value)


def generate_addition():
    operation = choice(["+", "-"])
    if operation == "+":
        a = randint(1, 10)
        b = randint(1, 10)
        answer = a + b
    else:
        a = randint(1, 10)
        b = randint(1, a)
        answer = a - b
    return {
        "expression": f"{a} {operation} {b}",
        "answer": answer,
        "answer_text": str(answer),
        "answer_type": "int",
    }


def generate_hard_addition():
    a = randint(10, 99)
    b = randint(10, 99)
    operation = choice(["+", "-"])
    answer = a + b if operation == "+" else a - b
    return {
        "expression": f"{a} {operation} {b}",
        "answer": answer,
        "answer_text": str(answer),
        "answer_type": "int",
    }


def generate_multiplication():
    a = randint(2, 6)
    b = randint(1, 6)
    return {
        "expression": f"{a} * {b}",
        "answer": a * b,
        "answer_text": str(a * b),
        "answer_type": "int",
    }


def generate_hard_multiplication():
    a = randint(3, 10)
    b = randint(9, 20)
    return {
        "expression": f"{a} * {b}",
        "answer": a * b,
        "answer_text": str(a * b),
        "answer_type": "int",
    }


def generate_brackets():
    generators = [
        lambda: (lambda a, b, c: (f"({a} + {b}) * {c}", (a + b) * c))(
            randint(1, 12), randint(1, 12), randint(2, 6)
        ),
        lambda: (lambda a, b, c: (f"{a} * ({b} + {c})", a * (b + c)))(
            randint(2, 8), randint(1, 9), randint(1, 9)
        ),
        lambda: (lambda a, b, c: (f"({a} - {b}) * {c}", (a - b) * c))(
            randint(8, 18), randint(1, 7), randint(2, 6)
        ),
        lambda: (lambda a, b, c: (f"{a} + ({b} * {c})", a + b * c))(
            randint(1, 20), randint(2, 9), randint(2, 9)
        ),
    ]
    expression, answer = choice(generators)()
    return {
        "expression": expression,
        "answer": answer,
        "answer_text": str(answer),
        "answer_type": "int",
    }


def generate_fractions():
    while True:
        left = simple_fraction()
        right = simple_fraction()
        operation = choice(["+", "-"])
        answer = left + right if operation == "+" else left - right
        if answer.denominator != 1 and answer != 0:
            return {
                "expression": f"{format_fraction(left)} {operation} {format_fraction(right)}",
                "answer": answer,
                "answer_text": fraction_text(answer),
                "answer_type": "fraction",
            }


def generate_fraction_brackets():
    while True:
        left = simple_fraction()
        right = simple_fraction()
        multiplier = simple_fraction()
        operation = choice(["+", "-"])
        middle = left + right if operation == "+" else left - right
        answer = middle * multiplier
        if answer.denominator != 1 and answer != 0:
            return {
                "expression": (
                    f"({format_fraction(left)} {operation} {format_fraction(right)})"
                    f" * {format_fraction(multiplier)}"
                ),
                "answer": answer,
                "answer_text": fraction_text(answer),
                "answer_type": "fraction",
            }


SERIES_RESISTORS_SCHEME = [
    "     +------------+    +------------+     ",
    "o----|     R1     |----|     R2     |----o",
    "     +------------+    +------------+     ",
]

PARALLEL_RESISTORS_SCHEME = [
    "          +------------+          ",
    "     +----|     R1     |----+     ",
    "     |    +------------+    |     ",
    "o----|                      |----o",
    "     |    +------------+    |     ",
    "     +----|     R2     |----+     ",
    "          +------------+          ",
]


def format_current(current):
    if current.denominator == 1:
        return str(current.numerator)
    return f"{current.numerator / current.denominator:.1f}"


def generate_series_ohms_law():
    current_tenths = randint(1, 10)
    current = Fraction(current_tenths, 10)
    resistance_step = current.denominator
    max_total_resistance = 1000 // current_tenths
    total_resistance = resistance_step * randint(2, max_total_resistance // resistance_step)
    r1 = randint(1, total_resistance - 1)
    r2 = total_resistance - r1
    voltage = int(current * total_resistance)
    lines = [
        "Закон Ома. Последовательное соединение.",
        "",
        *SERIES_RESISTORS_SCHEME,
        "",
        f"U = {voltage} В, I = {format_current(current)} А, R1 = {r1} Ом",
        "Найди R2. Ответ введи числом в омах.",
    ]
    return {
        "expression": " | ".join(line for line in lines if line),
        "text_lines": lines,
        "answer": r2,
        "answer_text": str(r2),
        "answer_type": "int",
    }


def generate_parallel_ohms_law():
    while True:
        current_tenths = randint(1, 10)
        current = Fraction(current_tenths, 10)
        r1 = randint(2, 200)
        r2 = randint(2, 200)
        equivalent_resistance = Fraction(r1 * r2, r1 + r2)
        voltage = current * equivalent_resistance
        if voltage.denominator == 1 and 1 <= voltage <= 100:
            lines = [
                "Закон Ома. Параллельное соединение.",
                "",
                *PARALLEL_RESISTORS_SCHEME,
                "",
                f"U = {int(voltage)} В, I = {format_current(current)} А, R1 = {r1} Ом",
                "Найди R2. Ответ введи числом в омах.",
            ]
            return {
                "expression": " | ".join(line for line in lines if line),
                "text_lines": lines,
                "answer": r2,
                "answer_text": str(r2),
                "answer_type": "int",
            }


def generate_ohms_law():
    return choice([generate_series_ohms_law, generate_parallel_ohms_law])()


GENERATORS = {
    "addition": generate_addition,
    "hard_addition": generate_hard_addition,
    "multiplication": generate_multiplication,
    "hard_multiplication": generate_hard_multiplication,
    "brackets": generate_brackets,
    "fractions": generate_fractions,
    "fraction_brackets": generate_fraction_brackets,
    "ohms_law": generate_ohms_law,
}


def parse_answer(message, answer_type):
    text = message.strip().split()[0] if message.strip() else ""
    if answer_type == "int":
        if not re.fullmatch(r"-?\d+", text):
            return text, None
        return text, int(text)
    if not re.fullmatch(r"-?\d+/\d+", text):
        return text, None
    try:
        return text, Fraction(text)
    except ZeroDivisionError:
        return text, None


def is_correct(task, entered_text, parsed_value):
    if parsed_value != task["answer"]:
        return False
    if task["answer_type"] == "fraction":
        return entered_text == task["answer_text"]
    return True
