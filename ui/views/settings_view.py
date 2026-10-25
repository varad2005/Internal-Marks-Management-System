"""
Database Configuration & Setup View
K.K. Wagh Institute of Engineering Education and Research, Nashik
Department of Computer Engineering | Academic Year 2026-27
"""

import tkinter as tk
from tkinter import ttk, messagebox
from config import load_config, save_config
from db import db
from ui.theme import COLORS, FONTS

class SettingsView(tk.Frame):
    def __init__(self, parent, on_config_changed=None):
        super().__init__(parent, bg=COLORS["bg_main"])
        self.on_config_changed = on_config_changed
        self.config = load_config()

        self._build_header()
        self._build_form()

    def _build_header(self):
        hdr = tk.Frame(self, bg=COLORS["bg_main"], pady=10)
        hdr.pack(fill="x", padx=20)
        tk.Label(hdr, text="Database Settings & Initialization", font=FONTS["header_title"], bg=COLORS["bg_main"], fg=COLORS["text_dark"]).pack(anchor="w")
        tk.Label(hdr, text="Configure MySQL Server credentials, test connectivity, or initialize tables from database.sql and sample_data.sql", font=FONTS["caption"], bg=COLORS["bg_main"], fg=COLORS["text_muted"]).pack(anchor="w")

    def _build_form(self):
        container = tk.Frame(self, bg=COLORS["bg_main"])
        container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Card 1: Engine Selection
        card_engine = tk.Frame(container, bg=COLORS["bg_card"], bd=1, relief="solid", padx=20, pady=16)
        card_engine.pack(fill="x", pady=(0, 15))

        tk.Label(card_engine, text="1. Database Engine Selection", font=FONTS["section_title"], bg=COLORS["bg_card"], fg=COLORS["text_dark"]).pack(anchor="w", pady=(0, 8))

        self.engine_var = tk.StringVar(value=db.active_engine)

        r_mysql = ttk.Radiobutton(
            card_engine,
            text="MySQL Server (Mandatory Syllabus Requirement - mysql-connector-python)",
            variable=self.engine_var,
            value="mysql",
            command=self._on_engine_toggle
        )
        r_mysql.pack(anchor="w", pady=2)

        r_sqlite = ttk.Radiobutton(
            card_engine,
            text="SQLite Standalone Engine (Self-contained Offline / Testing fallback)",
            variable=self.engine_var,
            value="sqlite",
            command=self._on_engine_toggle
        )
        r_sqlite.pack(anchor="w", pady=2)

        # Card 2: MySQL Connection Parameters
        self.card_mysql = tk.Frame(container, bg=COLORS["bg_card"], bd=1, relief="solid", padx=20, pady=16)
        self.card_mysql.pack(fill="x", pady=(0, 15))

        tk.Label(self.card_mysql, text="2. MySQL Server Connection Parameters", font=FONTS["section_title"], bg=COLORS["bg_card"], fg=COLORS["text_dark"]).pack(anchor="w", pady=(0, 12))

        m_cfg = self.config.get("mysql", {})

        grid = tk.Frame(self.card_mysql, bg=COLORS["bg_card"])
        grid.pack(fill="x")

        # Host & Port
        tk.Label(grid, text="Server Host:", bg=COLORS["bg_card"], font=FONTS["body_bold"]).grid(row=0, column=0, sticky="w", pady=6)
        self.host_var = tk.StringVar(value=m_cfg.get("host", "localhost"))
        ttk.Entry(grid, textvariable=self.host_var, width=28).grid(row=0, column=1, sticky="w", padx=(10, 30), pady=6)

        tk.Label(grid, text="Port:", bg=COLORS["bg_card"], font=FONTS["body_bold"]).grid(row=0, column=2, sticky="w", pady=6)
        self.port_var = tk.StringVar(value=str(m_cfg.get("port", 3306)))
        ttk.Entry(grid, textvariable=self.port_var, width=12).grid(row=0, column=3, sticky="w", padx=10, pady=6)

        # User & Password
        tk.Label(grid, text="Username:", bg=COLORS["bg_card"], font=FONTS["body_bold"]).grid(row=1, column=0, sticky="w", pady=6)
        self.user_var = tk.StringVar(value=m_cfg.get("user", "root"))
        ttk.Entry(grid, textvariable=self.user_var, width=28).grid(row=1, column=1, sticky="w", padx=(10, 30), pady=6)

        tk.Label(grid, text="Password:", bg=COLORS["bg_card"], font=FONTS["body_bold"]).grid(row=1, column=2, sticky="w", pady=6)
        self.pass_var = tk.StringVar(value=m_cfg.get("password", ""))
        ttk.Entry(grid, textvariable=self.pass_var, show="•", width=20).grid(row=1, column=3, sticky="w", padx=10, pady=6)

        # Database Name
        tk.Label(grid, text="Database Name:", bg=COLORS["bg_card"], font=FONTS["body_bold"]).grid(row=2, column=0, sticky="w", pady=6)
        self.db_var = tk.StringVar(value=m_cfg.get("database", "internal_marks_db"))
        ttk.Entry(grid, textvariable=self.db_var, width=28).grid(row=2, column=1, sticky="w", padx=(10, 30), pady=6)

        # Connection Buttons
        btn_row = tk.Frame(self.card_mysql, bg=COLORS["bg_card"], pady=10)
        btn_row.pack(fill="x")

        ttk.Button(btn_row, text="🔌 Test MySQL Connection", style="Secondary.TButton", command=self._test_connection).pack(side="left", padx=(0, 10))
        ttk.Button(btn_row, text="💾 Save Configuration", style="Primary.TButton", command=self._save_config).pack(side="left")

        # Card 3: Database Initialization
        card_init = tk.Frame(container, bg=COLORS["bg_card"], bd=1, relief="solid", padx=20, pady=16)
        card_init.pack(fill="x")

        tk.Label(card_init, text="3. Initialize / Reset Database Schema & Sample Data", font=FONTS["section_title"], bg=COLORS["bg_card"], fg=COLORS["text_dark"]).pack(anchor="w", pady=(0, 6))
        tk.Label(
            card_init,
            text="Executes 'database.sql' (all 7 tables, constraints, views, and triggers) and populates 'sample_data.sql' with realistic Computer Engineering department records.",
            bg=COLORS["bg_card"],
            fg=COLORS["text_muted"],
            font=FONTS["body"]
        ).pack(anchor="w", pady=(0, 12))

        ttk.Button(card_init, text="🚀 Run Schema & Sample Data Initialization", style="Success.TButton", command=self._run_initialization).pack(anchor="w")

        self._on_engine_toggle()

    def _on_engine_toggle(self):
        engine = self.engine_var.get()
        db.active_engine = engine

    def _test_connection(self):
        host = self.host_var.get().strip()
        port = self.port_var.get().strip()
        user = self.user_var.get().strip()
        pwd = self.pass_var.get()

        ok, msg = db.test_mysql_connection(host, port, user, pwd)
        if ok:
            messagebox.showinfo("Connection Successful", f"Successfully reached MySQL Server at {host}:{port} as user '{user}'!")
        else:
            messagebox.showerror(
                "Connection Failed",
                f"Could not connect to MySQL Server:\n\n{msg}\n\nTroubleshooting:\n"
                "1. Ensure MySQL Server service is running (or start via Windows Services or 'mysqld').\n"
                "2. Verify root username and password.\n"
                "3. Alternatively, select SQLite mode to run offline immediately."
            )

    def _save_config(self):
        cfg = {
            "db_engine": self.engine_var.get(),
            "mysql": {
                "host": self.host_var.get().strip(),
                "port": int(self.port_var.get().strip() or 3306),
                "user": self.user_var.get().strip(),
                "password": self.pass_var.get(),
                "database": self.db_var.get().strip()
            },
            "sqlite": {
                "database": "internal_marks.db"
            }
        }
        save_config(cfg)
        db.config = cfg
        db.active_engine = cfg["db_engine"]
        messagebox.showinfo("Saved", "Configuration successfully saved!")
        if self.on_config_changed:
            self.on_config_changed()

    def _run_initialization(self):
        self._save_config()
        confirm = messagebox.askyesno(
            "Confirm Database Initialization",
            "This will create/reset database tables and load sample records from database.sql and sample_data.sql.\n\nDo you want to proceed?"
        )
        if not confirm:
            return

        try:
            ok, msg = db.init_database_from_sql_files("database.sql", "sample_data.sql")
            messagebox.showinfo("Initialization Finished", msg)
            if self.on_config_changed:
                self.on_config_changed()
        except Exception as e:
            messagebox.showerror("Initialization Error", f"Failed to initialize database:\n\n{str(e)}")
