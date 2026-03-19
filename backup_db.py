#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backup CRM SQLite database before migrations.
Usage: python backup_db.py
"""
import os
import shutil
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'crm.db')
BACKUP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backups')


def backup():
    if not os.path.exists(DB_PATH):
        print(f"[BACKUP] Database not found at {DB_PATH}")
        return None

    os.makedirs(BACKUP_DIR, exist_ok=True)
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    dest = os.path.join(BACKUP_DIR, f'crm_{stamp}.db')
    shutil.copy2(DB_PATH, dest)
    size_kb = os.path.getsize(dest) / 1024
    print(f"[BACKUP] ✓ Backed up to {dest} ({size_kb:.1f} KB)")
    return dest


if __name__ == '__main__':
    backup()
