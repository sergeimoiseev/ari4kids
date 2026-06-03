#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from platform import system, uname
import json


DEFAULT_TEST_LEN = 10
TEST_LEN_OPTIONS = [10, 20, 30]
USER_FILE = "users.txt"
LOG_PREFIX = "ari4kids_test"
SETTINGS_FILE = "settings.json"
MENU_SEPARATOR = None

TRAINING_MODES = [
    ("сложение", "addition"),
    ("сложное сложение", "hard_addition"),
    ("умножение", "multiplication"),
    ("сложное умножение", "hard_multiplication"),
    ("скобки", "brackets"),
    ("дроби", "fractions"),
    ("дроби со скобками", "fraction_brackets"),
]
MENU = [title for title, _ in TRAINING_MODES] + [
    MENU_SEPARATOR,
    "настройки",
    "посмотреть журнал",
    "выйти",
]


def in_wsl() -> bool:
    """
    WSL is thought to be the only common Linux kernel with Microsoft in the name, per Microsoft:
    https://github.com/microsoft/WSL/issues/4071#issuecomment-496715404
    """
    return "WSL" in uname().release


# TODO: при первом запуске запрашивать путь до папки, затем хранить его в неверсионируемом файле
if system() == "Linux":
    print("This code is running on a Linux system.")
    fpath = os.path.expanduser(os.path.join("~", "Dropbox", "ari4kids"))
else:
    print(f"This code is running on a {system()} system, not Linux.")
    if in_wsl():
        # не работает - в wsl возвращате False
        fpath = os.path.join("mnt", "c", "Users", "User", "Dropbox", "ari4kids")
    else:
        fpath = os.path.join("c:", os.sep, "Users", "User", "Dropbox", "ari4kids")


def ensure_storage():
    os.makedirs(fpath, exist_ok=True)


def storage_path(filename):
    return os.path.join(fpath, filename)


def load_settings():
    ensure_storage()
    try:
        with open(storage_path(SETTINGS_FILE), "r", encoding="utf-8") as settings_file:
            settings = json.load(settings_file)
    except (FileNotFoundError, json.JSONDecodeError):
        settings = {}
    test_len = settings.get("test_len", DEFAULT_TEST_LEN)
    if test_len not in TEST_LEN_OPTIONS:
        test_len = DEFAULT_TEST_LEN
    return {"test_len": test_len}


def save_settings(settings):
    ensure_storage()
    with open(storage_path(SETTINGS_FILE), "w", encoding="utf-8") as settings_file:
        json.dump(settings, settings_file, ensure_ascii=False, indent=2)


def get_test_len():
    return load_settings()["test_len"]


def set_test_len(test_len):
    if test_len not in TEST_LEN_OPTIONS:
        raise ValueError("Unsupported test length")
    save_settings({"test_len": test_len})
