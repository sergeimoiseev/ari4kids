#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re

import pandas as pd

from config import LOG_PREFIX, USER_FILE, ensure_storage, storage_path


def load_users():
    ensure_storage()
    path = storage_path(USER_FILE)
    try:
        with open(path, "r", encoding="utf-8") as users_file:
            return [line.strip() for line in users_file if line.strip()]
    except FileNotFoundError:
        return []


def save_user(name):
    users = load_users()
    if name and name not in users:
        with open(storage_path(USER_FILE), "a", encoding="utf-8") as users_file:
            users_file.write(name + "\n")


def safe_filename_part(value):
    return re.sub(r'[\\/:*?"<>|]+', "_", value).strip() or "user"


def save_results(user, mode_key, started_at, results):
    ensure_storage()
    df = pd.DataFrame(results)
    filename = "{} {} {} {}.xlsx".format(
        LOG_PREFIX,
        safe_filename_part(user),
        mode_key,
        started_at.strftime("%m_%d_%Y %H_%M_%S"),
    )
    df.to_excel(storage_path(filename), index=False)
