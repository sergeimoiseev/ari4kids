#!/usr/bin/env python
# -*- coding: utf-8 -*-
import curses
from curses.textpad import Textbox, rectangle
from datetime import datetime
import time

from config import MENU, TEST_LEN, TRAINING_MODES, in_wsl
from journal import format_duration, load_journal_rows
from storage import load_users, save_results, save_user
from tasks import GENERATORS, is_correct, parse_answer


def print_center(stdscr, text, row_offset=0):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    y = max(0, h // 2 + row_offset)
    x = max(0, w // 2 - len(text) // 2)
    stdscr.addstr(y, x, text[: max(0, w - x - 1)])
    stdscr.refresh()


def draw_menu(stdscr, items, selected_row_idx, title=None, footer=None):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    if title:
        stdscr.addstr(1, max(0, w // 2 - len(title) // 2), title[: w - 1])
    start_y = max(3, h // 2 - len(items) // 2)
    for idx, row in enumerate(items):
        x = max(0, w // 2 - len(row) // 2)
        y = start_y + idx
        if idx == selected_row_idx:
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(y, x, row[: w - x - 1])
            stdscr.attroff(curses.color_pair(1))
        else:
            stdscr.addstr(y, x, row[: w - x - 1])
    if in_wsl():
        stdscr.addstr(0, 0, "Сейчас я работаю в WSL!"[: w - 1])
    if footer:
        stdscr.addstr(h - 2, 1, footer[: w - 2])
    stdscr.refresh()


def select_from_menu(stdscr, items, title=None, footer=None):
    current_row = 0
    draw_menu(stdscr, items, current_row, title, footer)
    while True:
        key = stdscr.getch()
        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(items) - 1:
            current_row += 1
        elif key in [curses.KEY_ENTER, 10, 13]:
            return current_row
        draw_menu(stdscr, items, current_row, title, footer)


def read_textbox(stdscr, prompt, width=30):
    stdscr.clear()
    stdscr.addstr(0, 0, prompt)
    editwin = curses.newwin(1, width, 2, 1)
    rectangle(stdscr, 1, 0, 3, width + 1)
    stdscr.refresh()
    box = Textbox(editwin)
    box.edit()
    return box.gather().strip()


def choose_user(stdscr):
    users = load_users()
    if users:
        items = users + ["новое имя"]
        idx = select_from_menu(
            stdscr,
            items,
            "Я - Арифметик! Выбери имя или добавь новое.",
        )
        if idx < len(users):
            return users[idx]
    while True:
        name = read_textbox(stdscr, "Я - Арифметик! А как тебя зовут?")
        if name:
            save_user(name)
            return name
        print_center(stdscr, "Имя не должно быть пустым. Нажми любую клавишу.")
        stdscr.getch()


def show_task(stdscr, task):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    prompt = f"{task['expression']} = "
    stdscr.addstr(0, 0, prompt[: w - 1])
    if task["answer_type"] == "fraction":
        hint = 'Ответ вводи простой дробью, например "1/3".'
        stdscr.addstr(4, 0, hint[: w - 1])
    editwin = curses.newwin(1, 20, 2, 1)
    rectangle(stdscr, 1, 0, 3, 21)
    stdscr.refresh()
    return editwin


def run_training(stdscr, user, mode_title, mode_key):
    results = []
    test_score = 0
    started_at = datetime.now()
    for i in range(TEST_LEN):
        task = GENERATORS[mode_key]()
        editwin = show_task(stdscr, task)
        box = Textbox(editwin)
        start = time.time()
        box.edit()
        elapsed_time = time.time() - start
        entered_text, parsed_value = parse_answer(box.gather(), task["answer_type"])
        correct = is_correct(task, entered_text, parsed_value)
        if correct:
            test_score += 1
        results.append(
            {
                "user": user,
                "date": started_at.strftime("%Y-%m-%d %H:%M:%S"),
                "mode": mode_title,
                "expression": task["expression"],
                "answer": task["answer_text"],
                "user_input": entered_text,
                "elapsed_time": elapsed_time,
                "correct": correct,
                "test_score": test_score,
                "test_len": TEST_LEN,
            }
        )
    save_results(user, mode_key, started_at, results)
    show_journal(stdscr, user)


def fit_cell(value, width, align="left"):
    text = str(value)
    if len(text) > width:
        text = text[: max(0, width - 1)] + "~"
    if align == "right":
        return text.rjust(width)
    return text.ljust(width)


def format_journal_line(values):
    columns = [
        (values["user"], 12, "left"),
        (values["date"], 16, "left"),
        (values["mode"], 20, "left"),
        (values["correct"], 5, "right"),
        (values["incorrect"], 6, "right"),
        (values["elapsed"], 5, "right"),
        (values["speed"], 8, "right"),
    ]
    return " | ".join(fit_cell(value, width, align) for value, width, align in columns)


def draw_journal(stdscr, rows, user_filter, top):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    title = "Журнал"
    if user_filter:
        title += f" | пользователь: {user_filter}"
    stdscr.addstr(0, 0, title[: w - 1])
    stdscr.addstr(1, 0, "F - фильтр, A - все, Esc/Enter - назад"[: w - 1])
    header = format_journal_line(
        {
            "user": "Пользователь",
            "date": "Дата",
            "mode": "Режим",
            "correct": "Верно",
            "incorrect": "Ошибки",
            "elapsed": "Время",
            "speed": "Скорость",
        }
    )
    stdscr.addstr(3, 0, header[: w - 1])
    visible_rows = [row for row in rows if not user_filter or row["user"] == user_filter]
    for screen_idx, row in enumerate(visible_rows[top : top + max(0, h - 5)]):
        line = format_journal_line(
            {
                "user": row["user"],
                "date": row["date"].strftime("%Y-%m-%d %H:%M"),
                "mode": row["mode"],
                "correct": row["correct"],
                "incorrect": row["incorrect"],
                "elapsed": format_duration(row["elapsed"]),
                "speed": f"{row['speed']:.1f}",
            }
        )
        stdscr.addstr(4 + screen_idx, 0, line[: w - 1])
    if not visible_rows:
        stdscr.addstr(5, 0, "Записей нет."[: w - 1])
    stdscr.refresh()
    return len(visible_rows)


def show_journal(stdscr, initial_user_filter=None):
    rows = load_journal_rows()
    users = sorted({row["user"] for row in rows if row["user"]})
    user_filter = initial_user_filter
    top = 0
    while True:
        visible_count = draw_journal(stdscr, rows, user_filter, top)
        key = stdscr.getch()
        if key in [27, curses.KEY_ENTER, 10, 13]:
            return
        if key == curses.KEY_UP and top > 0:
            top -= 1
        elif key == curses.KEY_DOWN and top < max(0, visible_count - 1):
            top += 1
        elif key in [ord("a"), ord("A"), ord("ф"), ord("Ф")]:
            user_filter = None
            top = 0
        elif key in [ord("f"), ord("F"), ord("а"), ord("А")] and users:
            idx = select_from_menu(stdscr, users + ["все пользователи"], "Фильтр журнала")
            user_filter = users[idx] if idx < len(users) else None
            top = 0


def main(stdscr):
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

    user = choose_user(stdscr)
    print_center(stdscr, f"Привет, {user}! Нажми любую клавишу, чтобы продолжить.")
    stdscr.getch()

    while True:
        current_row = select_from_menu(stdscr, MENU)
        selected = MENU[current_row]
        if selected == "выйти":
            break
        if selected == "посмотреть журнал":
            show_journal(stdscr)
            continue
        mode_title, mode_key = TRAINING_MODES[current_row]
        run_training(stdscr, user, mode_title, mode_key)
