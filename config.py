#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from platform import system, uname


TEST_LEN = 20
USER_FILE = "users.txt"
LOG_PREFIX = "ari4kids_test"

TRAINING_MODES = [
    ("сложение", "addition"),
    ("сложное сложение", "hard_addition"),
    ("умножение", "multiplication"),
    ("сложное умножение", "hard_multiplication"),
    ("скобки", "brackets"),
    ("дроби", "fractions"),
    ("дроби со скобками", "fraction_brackets"),
]
MENU = [title for title, _ in TRAINING_MODES] + ["посмотреть журнал", "выйти"]


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
