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


def generate_multiplication():
    a = randint(2, 6)
    b = randint(1, 6)
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


GENERATORS = {
    "multiplication": generate_multiplication,
    "brackets": generate_brackets,
    "fractions": generate_fractions,
    "fraction_brackets": generate_fraction_brackets,
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
