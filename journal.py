#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
from glob import glob
import os
import re

import pandas as pd

from config import LOG_PREFIX, ensure_storage, storage_path
from storage import extract_user_from_log_filename, is_valid_user_name


def parse_date_from_filename(path):
    match = re.search(r"(\d{2}_\d{2}_\d{4} \d{2}_\d{2}_\d{2})", os.path.basename(path))
    if not match:
        return datetime.fromtimestamp(os.path.getmtime(path))
    return datetime.strptime(match.group(1), "%m_%d_%Y %H_%M_%S")


def summarize_log(path):
    user = extract_user_from_log_filename(path)
    if not is_valid_user_name(user):
        return None

    df = pd.read_excel(path)
    if df.empty:
        return None
    date_value = df["date"].iloc[0] if "date" in df.columns else parse_date_from_filename(path)
    date_value = pd.to_datetime(date_value).to_pydatetime()
    mode = str(df["mode"].iloc[0]) if "mode" in df.columns else "умножение"
    correct = int(df["correct"].fillna(False).astype(bool).sum()) if "correct" in df.columns else 0
    total = len(df)
    incorrect = total - correct
    elapsed = float(df["elapsed_time"].fillna(0).sum()) if "elapsed_time" in df.columns else 0.0
    speed = elapsed / total if total else 0.0
    return {
        "user": user,
        "date": date_value,
        "mode": mode,
        "correct": correct,
        "incorrect": incorrect,
        "elapsed": elapsed,
        "speed": speed,
    }


def list_journal_files():
    ensure_storage()
    return sorted(glob(storage_path(f"{LOG_PREFIX}*.xlsx")))


def load_journal_rows(progress_callback=None):
    files = list_journal_files()
    rows = []
    total = len(files)
    if progress_callback:
        progress_callback(0, total)
    for idx, path in enumerate(files, start=1):
        try:
            row = summarize_log(path)
        except Exception:
            row = None
        if row:
            rows.append(row)
        if progress_callback:
            progress_callback(idx, total)
    return sorted(rows, key=lambda row: row["date"], reverse=True)


def format_duration(seconds):
    minutes = int(seconds // 60)
    rest = int(seconds % 60)
    return f"{minutes:02d}:{rest:02d}"
