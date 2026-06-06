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
    ("закон Ома", "ohms_law"),
]
MENU_BOTTOM_ITEMS = [
    "настройки",
    "выбор пути к папке с логами",
    "посмотреть журнал",
    "выйти",
]
MODE_TITLES_BY_KEY = {mode_key: title for title, mode_key in TRAINING_MODES}
MODE_KEYS_BY_TITLE = {title: mode_key for title, mode_key in TRAINING_MODES}


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
    if system() == "Windows":
        return os.path.join(os.path.expanduser("~"), "Dropbox", "ari4kids")
    if system() == "Linux":
        return os.path.expanduser(os.path.join("~", "Dropbox", "ari4kids"))
    if in_wsl():
        # не работает - в wsl возвращате False
        return os.path.join("mnt", "c", "Users", "User", "Dropbox", "ari4kids")
    return os.path.join(os.path.expanduser("~"), "Dropbox", "ari4kids")


DEFAULT_LOG_DIR = detect_default_log_dir()


def migrate_windows_user_path(log_dir):
    if system() != "Windows" or not log_dir:
        return log_dir

    current_home = os.path.abspath(os.path.expanduser("~"))
    configured = os.path.abspath(os.path.expanduser(log_dir))
    configured_drive, configured_tail = os.path.splitdrive(configured)
    home_drive, _ = os.path.splitdrive(current_home)
    parts = configured_tail.strip(os.sep).split(os.sep)
    configured_under_current_home = (
        os.path.commonpath([os.path.normcase(configured), os.path.normcase(current_home)])
        == os.path.normcase(current_home)
    )

    if (
        configured_drive.lower() == home_drive.lower()
        and len(parts) >= 2
        and parts[0].lower() == "users"
        and not configured_under_current_home
    ):
        return os.path.join(current_home, *parts[2:])

    return log_dir


def normalize_settings(settings):
    test_len = settings.get("test_len", DEFAULT_TEST_LEN)
    if test_len not in TEST_LEN_OPTIONS:
        test_len = DEFAULT_TEST_LEN
    log_dir = settings.get("log_dir") or DEFAULT_LOG_DIR
    log_dir = migrate_windows_user_path(log_dir)
    log_dir = os.path.abspath(os.path.expanduser(log_dir))
    last_modes = settings.get("last_modes", {})
    if not isinstance(last_modes, dict):
        last_modes = {}
    last_modes = {
        str(user): mode_key
        for user, mode_key in last_modes.items()
        if mode_key in MODE_TITLES_BY_KEY
    }
    return {"test_len": test_len, "log_dir": log_dir, "last_modes": last_modes}


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


def get_last_training_mode(user):
    return load_settings()["last_modes"].get(user)


def set_last_training_mode(user, mode_key):
    if mode_key not in MODE_TITLES_BY_KEY:
        raise ValueError("Unsupported training mode")
    settings = load_settings()
    settings["last_modes"][user] = mode_key
    save_settings(settings)


def build_main_menu(user):
    last_mode_key = get_last_training_mode(user)
    menu = []
    if last_mode_key:
        menu.append(f"повторить ({MODE_TITLES_BY_KEY[last_mode_key]})")
        menu.append(MENU_SEPARATOR)
    menu.extend(title for title, _ in TRAINING_MODES)
    menu.append(MENU_SEPARATOR)
    menu.extend(MENU_BOTTOM_ITEMS)
    return menu
