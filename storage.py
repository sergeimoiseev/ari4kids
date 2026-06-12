#!/usr/bin/env python
# -*- coding: utf-8 -*-
from glob import glob
import os
import re

import pandas as pd

from config import (
    LOG_PREFIX,
    MODE_KEYS_BY_TITLE,
    MODE_TITLES_BY_KEY,
    ensure_storage,
    storage_path,
)


LEGACY_MODE_TITLES = {
    "сложение",
    "сложное сложение",
}


def known_mode_filename_suffixes():
    suffixes = set(MODE_TITLES_BY_KEY)
    suffixes.update(MODE_KEYS_BY_TITLE)
    suffixes.update(LEGACY_MODE_TITLES)
    return sorted(suffixes, key=len, reverse=True)


def extract_user_from_log_filename(path):
    basename = os.path.basename(path)
    stem, ext = os.path.splitext(basename)
    if ext.lower() != ".xlsx" or not stem.startswith(LOG_PREFIX + " "):
        return None

    stem_without_prefix = stem[len(LOG_PREFIX) + 1 :]
    date_match = re.search(r" \d{2}_\d{2}_\d{4} \d{2}_\d{2}_\d{2}$", stem_without_prefix)
    if not date_match:
        return None

    before_date = stem_without_prefix[: date_match.start()].strip()
    for mode_suffix in known_mode_filename_suffixes():
        suffix = " " + mode_suffix
        if before_date.endswith(suffix):
            user = before_date[: -len(suffix)].strip()
            return user or None
    return before_date or None


def is_valid_user_name(user):
    return bool(user and user.strip() and user.strip().lower() != "nan")


def load_users():
    ensure_storage()
    users = set()
    for path in glob(storage_path(f"{LOG_PREFIX}*.xlsx")):
        user = extract_user_from_log_filename(path)
        if is_valid_user_name(user):
            users.add(user)
    return sorted(users, key=str.casefold)


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
