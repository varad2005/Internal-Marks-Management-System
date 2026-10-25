"""
Configuration Module for Internal Marks Management System
K.K. Wagh Institute of Engineering Education and Research, Nashik
Department of Computer Engineering | Academic Year 2026-27
"""

import os
import json

CONFIG_FILE = "db_config.json"

DEFAULT_CONFIG = {
    "db_engine": "mysql",  # 'mysql' or 'sqlite'
    "mysql": {
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": "",
        "database": "internal_marks_db"
    },
    "sqlite": {
        "database": "internal_marks.db"
    },
    "institution": {
        "name": "K.K. Wagh Institute of Engineering Education and Research, Nashik",
        "department": "Department of Computer Engineering",
        "academic_year": "2026-2027"
    }
}

def load_config():
    """Load configuration from JSON file or return defaults."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                config = DEFAULT_CONFIG.copy()
                config.update(saved)
                return config
        except Exception:
            return DEFAULT_CONFIG
    return DEFAULT_CONFIG

def save_config(config):
    """Save configuration to JSON file."""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)
