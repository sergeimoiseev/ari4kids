#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import json
from platform import system, uname
import sys


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
    "выбор пути к папке с логами",
    "посмотреть журнал",
    "выйти",
]


def in_wsl() -> bool:
    """
    WSL is thought to be the only common Linux kernel with Microsoft in the name, per Microsoft:
    https://github.com/microsoft/WSL/issues/4071#issuecomment-496715404
    """
    return "WSL" in uname().release


def app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def settings_path():
    return os.path.join(app_dir(), SETTINGS_FILE)


def detect_default_log_dir():
    # TODO: при первом запуске запрашивать путь до папки, затем хранить его в неверсионируемом файле
    if system() == "Linux":
        print("This code is running on a Linux system.")
        return os.path.expanduser(os.path.join("~", "Dropbox", "ari4kids"))
    print(f"This code is running on a {system()} system, not Linux.")
    if in_wsl():
        # не работает - в wsl возвращате False
        return os.path.join("mnt", "c", "Users", "User", "Dropbox", "ari4kids")
    return os.path.join("c:", os.sep, "Users", "User", "Dropbox", "ari4kids")


DEFAULT_LOG_DIR = detect_default_log_dir()


def normalize_settings(settings):
    test_len = settings.get("test_len", DEFAULT_TEST_LEN)
    if test_len not in TEST_LEN_OPTIONS:
        test_len = DEFAULT_TEST_LEN
    log_dir = settings.get("log_dir") or DEFAULT_LOG_DIR
    log_dir = os.path.abspath(os.path.expanduser(log_dir))
    return {"test_len": test_len, "log_dir": log_dir}


def load_settings():
    try:
        with open(settings_path(), "r", encoding="utf-8") as settings_file:
            settings = json.load(settings_file)
    except (FileNotFoundError, json.JSONDecodeError):
        settings = {}
    return normalize_settings(settings)


def save_settings(settings):
    with open(settings_path(), "w", encoding="utf-8") as settings_file:
        json.dump(normalize_settings(settings), settings_file, ensure_ascii=False, indent=2)


def get_log_dir():
    return load_settings()["log_dir"]


def set_log_dir(log_dir):
    new_log_dir = os.path.abspath(os.path.expanduser(log_dir))
    os.makedirs(new_log_dir, exist_ok=True)
    settings = load_settings()
    settings["log_dir"] = new_log_dir
    save_settings(settings)


def ensure_storage():
    os.makedirs(get_log_dir(), exist_ok=True)


def storage_path(filename):
    return os.path.join(get_log_dir(), filename)


def get_test_len():
    return load_settings()["test_len"]


def set_test_len(test_len):
    if test_len not in TEST_LEN_OPTIONS:
        raise ValueError("Unsupported test length")
    settings = load_settings()
    settings["test_len"] = test_len
    save_settings(settings)
