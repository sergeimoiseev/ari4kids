#!/usr/bin/env python
# -*- coding: utf-8 -*-
import curses
from curses.textpad import Textbox, rectangle
from datetime import datetime
import time

from config import (
    MENU_SEPARATOR,
    MODE_KEYS_BY_TITLE,
    MODE_TITLES_BY_KEY,
    TEST_LEN_OPTIONS,
    build_main_menu,
    get_log_dir,
    get_last_training_mode,
    get_test_len,
    in_wsl,
    set_log_dir,
    set_last_training_mode,
    set_test_len,
)
from journal import format_duration, load_journal_rows
from storage import load_users, save_results
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
        if row is MENU_SEPARATOR:
            line_width = min(28, max(0, w - 4))
            x = max(0, w // 2 - line_width // 2)
            y = start_y + idx
            stdscr.addstr(y, x, "-" * line_width)
            continue
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


def is_selectable_menu_item(item):
    return item is not MENU_SEPARATOR


def next_selectable_index(items, current_row, direction):
    next_row = current_row
    while True:
        candidate = next_row + direction
        if candidate < 0 or candidate >= len(items):
            return next_row
        next_row = candidate
        if is_selectable_menu_item(items[next_row]):
            return next_row


def select_from_menu(stdscr, items, title=None, footer=None):
    current_row = next(
        (idx for idx, item in enumerate(items) if is_selectable_menu_item(item)),
        0,
    )
    draw_menu(stdscr, items, current_row, title, footer)
    while True:
        key = stdscr.getch()
        if key == curses.KEY_UP:
            current_row = next_selectable_index(items, current_row, -1)
        elif key == curses.KEY_DOWN:
            current_row = next_selectable_index(items, current_row, 1)
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


def read_log_dir_textbox(stdscr):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    current_path = f"Текущий путь: {get_log_dir()}"
    prompt = "Введите новый путь к папке с логами. Пустой ввод - отмена."
    stdscr.addstr(0, 0, current_path[: w - 1])
    stdscr.addstr(2, 0, prompt[: w - 1])
    width = min(80, max(1, w - 4))
    y = min(4, max(0, h - 3))
    editwin = curses.newwin(1, width, y + 1, 1)
    rectangle(stdscr, y, 0, y + 2, width + 1)
    stdscr.refresh()
    box = Textbox(editwin)
    box.edit()
    return box.gather().strip()


def edit_textbox_until_done_or_escape(box):
    cancelled = False

    def validate_key(key):
        nonlocal cancelled
        if key == 27:
            cancelled = True
            return 7
        return key

    box.edit(validate_key)
    return cancelled, box.gather()


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
            return name
        print_center(stdscr, "Имя не должно быть пустым. Нажми любую клавишу.")
        stdscr.getch()


def show_task(stdscr, task):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    task_lines = task.get("text_lines")
    if task_lines:
        prompt_y = max(0, h // 2 - (len(task_lines) + 3) // 2)
        for idx, line in enumerate(task_lines):
            line_x = max(0, w // 2 - len(line) // 2)
            stdscr.addstr(prompt_y + idx, line_x, line[: w - line_x - 1])
        input_y = min(max(0, prompt_y + len(task_lines) + 1), max(0, h - 3))
    else:
        prompt = f"{task['expression']} = "
        prompt_y = max(0, h // 2 - 2)
        prompt_x = max(0, w // 2 - len(prompt) // 2)
        stdscr.addstr(prompt_y, prompt_x, prompt[: w - prompt_x - 1])
        input_y = min(max(0, prompt_y + 2), max(0, h - 3))

    input_width = min(20, max(1, w - 4))
    border_width = input_width + 2
    border_x = max(0, w // 2 - border_width // 2)
    editwin = curses.newwin(1, input_width, input_y + 1, border_x + 1)
    rectangle(stdscr, input_y, border_x, input_y + 2, border_x + border_width - 1)

    if task["answer_type"] == "fraction":
        hint = 'Ответ вводи простой дробью, например "1/3".'
        hint_y = min(h - 1, input_y + 4)
        hint_x = max(0, w // 2 - len(hint) // 2)
        stdscr.addstr(hint_y, hint_x, hint[: w - hint_x - 1])
    stdscr.refresh()
    return editwin


def run_training(stdscr, user, mode_title, mode_key):
    results = []
    test_score = 0
    started_at = datetime.now()
    test_len = get_test_len()
    for i in range(test_len):
        task = GENERATORS[mode_key]()
        editwin = show_task(stdscr, task)
        box = Textbox(editwin)
        start = time.time()
        cancelled, message = edit_textbox_until_done_or_escape(box)
        elapsed_time = time.time() - start
        if cancelled:
            return
        entered_text, parsed_value = parse_answer(message, task["answer_type"])
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
                "test_len": test_len,
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


def draw_journal_loading(stdscr, loaded, total, user_filter=None):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    title = "Журнал"
    if user_filter:
        title += f" | пользователь: {user_filter}"
    stdscr.addstr(0, 0, title[: w - 1])

    message = "Загрузка журнала..."
    stdscr.addstr(max(0, h // 2 - 2), max(0, w // 2 - len(message) // 2), message[: w - 1])

    bar_width = min(40, max(10, w - 10))
    progress = 1 if total == 0 else loaded / total
    filled_width = int(bar_width * progress)
    bar = "[" + "#" * filled_width + "." * (bar_width - filled_width) + "]"
    bar_x = max(0, w // 2 - len(bar) // 2)
    bar_y = max(0, h // 2)
    stdscr.addstr(bar_y, bar_x, bar[: w - bar_x - 1])

    counter = f"{loaded}/{total} файлов"
    stdscr.addstr(
        min(h - 1, bar_y + 2),
        max(0, w // 2 - len(counter) // 2),
        counter[: w - 1],
    )
    stdscr.refresh()


def draw_journal(stdscr, rows, user_filter, top):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    title = "Журнал"
    if user_filter:
        title += f" | пользователь: {user_filter}"
    stdscr.addstr(0, 0, title[: w - 1])
    stdscr.addstr(1, 0, "F - фильтр, A - все, Esc - назад"[: w - 1])
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
    def update_progress(loaded, total):
        draw_journal_loading(stdscr, loaded, total, initial_user_filter)

    rows = load_journal_rows(update_progress)
    users = sorted({row["user"] for row in rows if row["user"]})
    user_filter = initial_user_filter
    top = 0
    while True:
        visible_count = draw_journal(stdscr, rows, user_filter, top)
        key = stdscr.getch()
        if key == 27:
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


def show_settings(stdscr):
    current_test_len = get_test_len()
    items = [
        f"{option} задач" + (" *" if option == current_test_len else "")
        for option in TEST_LEN_OPTIONS
    ]
    idx = select_from_menu(stdscr, items, "Настройки: число задач в прогоне")
    set_test_len(TEST_LEN_OPTIONS[idx])


def show_log_dir_settings(stdscr):
    log_dir = read_log_dir_textbox(stdscr)
    if not log_dir:
        return
    try:
        set_log_dir(log_dir)
        message = "Путь сохранен. Нажми любую клавишу."
    except OSError as error:
        message = f"Не удалось сохранить путь: {error}. Нажми любую клавишу."
    print_center(stdscr, message)
    stdscr.getch()


def resolve_training_mode(user, selected):
    if selected.startswith("повторить ("):
        mode_key = get_last_training_mode(user)
        if mode_key:
            return MODE_TITLES_BY_KEY[mode_key], mode_key
        return None
    if selected in MODE_KEYS_BY_TITLE:
        mode_key = MODE_KEYS_BY_TITLE[selected]
        return selected, mode_key
    return None


def main(stdscr):
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

    user = choose_user(stdscr)
    print_center(stdscr, f"Привет, {user}! Нажми любую клавишу, чтобы продолжить.")
    stdscr.getch()

    while True:
        menu = build_main_menu(user)
        current_row = select_from_menu(stdscr, menu)
        selected = menu[current_row]
        if selected == "выйти":
            break
        if selected == "посмотреть журнал":
            show_journal(stdscr)
            continue
        if selected == "настройки":
            show_settings(stdscr)
            continue
        if selected == "выбор пути к папке с логами":
            show_log_dir_settings(stdscr)
            continue
        training_mode = resolve_training_mode(user, selected)
        if not training_mode:
            continue
        mode_title, mode_key = training_mode
        set_last_training_mode(user, mode_key)
        run_training(stdscr, user, mode_title, mode_key)
