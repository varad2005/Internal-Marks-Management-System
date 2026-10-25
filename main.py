"""
Main Application Entry Point
Internal Marks Management System
K.K. Wagh Institute of Engineering Education and Research, Nashik
Department of Computer Engineering | Academic Year 2026-27
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox

# Ensure current directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from config import load_config
from db import db
from ui.theme import COLORS, FONTS, apply_theme

# Views
from ui.views.dashboard_view import DashboardView
from ui.views.department_view import DepartmentView
from ui.views.teacher_view import TeacherView
from ui.views.student_view import StudentView
from ui.views.subject_view import SubjectView
from ui.views.enrollment_view import EnrollmentView
from ui.views.assessment_view import AssessmentView
from ui.views.marks_entry_view import MarksEntryView
from ui.views.reports_view import ReportsView
from ui.views.settings_view import SettingsView

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Internal Marks Management System — K.K. Wagh Institute of Engineering Education and Research")
        self.geometry("1240x780")
        self.minsize(1050, 680)

        # Apply global ttk theme
        apply_theme(self)

        # Check DB connection / Auto-fallback
        self._verify_database_connection()

        # Layout containers
        self._build_top_header()
        self._build_main_layout()

        # Show initial dashboard view
        self.show_view("dashboard")

    def _verify_database_connection(self):
        """Verify DB connection. If default MySQL server is offline, switch to standalone SQLite for demo."""
        try:
            # Try getting a connection
            conn = db.get_connection()
            conn.close()
        except Exception as e:
            # If MySQL connection failed, fallback to SQLite
            if db.active_engine == "mysql":
                print(f"[Notice] MySQL Server not reachable ({e}). Falling back to SQLite mode for local session.")
                db.active_engine = "sqlite"
                try:
                    # Initialize SQLite if file doesn't exist
                    s_cfg = db.config.get("sqlite", {})
                    db_file = s_cfg.get("database", "internal_marks.db")
                    if not os.path.exists(db_file):
                        db.init_database_from_sql_files("database.sql", "sample_data.sql")
                except Exception as ex:
                    print("Error during fallback DB init:", ex)

    def _build_top_header(self):
        self.header_frame = tk.Frame(self, bg=COLORS["header_bg"], height=64)
        self.header_frame.pack(fill="x", side="top")

        # Left branding
        brand_box = tk.Frame(self.header_frame, bg=COLORS["header_bg"], padx=20, pady=10)
        brand_box.pack(side="left")

        tk.Label(
            brand_box,
            text="🎓 K.K. Wagh Institute of Engineering Education and Research, Nashik",
            font=FONTS["header_title"],
            bg=COLORS["header_bg"],
            fg=COLORS["text_light"]
        ).pack(anchor="w")

        tk.Label(
            brand_box,
            text="Department of Computer Engineering | Academic Year 2026–27 | Internal Marks Management System",
            font=FONTS["brand_sub"],
            bg=COLORS["header_bg"],
            fg="#94A3B8"
        ).pack(anchor="w")

        # Right status indicator
        status_box = tk.Frame(self.header_frame, bg=COLORS["header_bg"], padx=20)
        status_box.pack(side="right")

        self.lbl_db_badge = tk.Label(
            status_box,
            text=self._get_db_status_text(),
            font=("Segoe UI", 9, "bold"),
            bg="#064E3B" if db.active_engine == "mysql" else "#1E3A8A",
            fg="#6EE7B7" if db.active_engine == "mysql" else "#93C5FD",
            padx=12,
            pady=4,
            relief="flat"
        )
        self.lbl_db_badge.pack(side="left", padx=(0, 10))

        btn_settings = ttk.Button(
            status_box,
            text="⚙️ DB Config",
            style="Secondary.TButton",
            command=lambda: self.show_view("settings")
        )
        btn_settings.pack(side="left")

    def _get_db_status_text(self):
        if db.active_engine == "mysql":
            m_cfg = db.config.get("mysql", {})
            return f"🟢 MySQL Server ({m_cfg.get('host', 'localhost')}:{m_cfg.get('port', 3306)})"
        else:
            return "🔵 Engine: Standalone SQLite (Demo / Offline)"

    def _build_main_layout(self):
        body = tk.Frame(self, bg=COLORS["bg_main"])
        body.pack(fill="both", expand=True)

        # Sidebar navigation
        self.sidebar = tk.Frame(body, bg=COLORS["bg_sidebar"], width=230)
        self.sidebar.pack(fill="y", side="left")
        self.sidebar.pack_propagate(False)

        # Nav items
        nav_items = [
            ("📊 Institutional Dashboard", "dashboard"),
            ("🏢 Departments", "departments"),
            ("👨‍🏫 Faculty / Teachers", "teachers"),
            ("🎓 Students Roster", "students"),
            ("📚 Subjects & Courses", "subjects"),
            ("📝 Course Enrollments", "enrollments"),
            ("📑 Assessment Schemes", "assessments"),
            ("✍️ Marks Entry & Grading", "marks"),
            ("📈 Reports & Marksheets", "reports"),
            ("⚙️ Database Settings", "settings")
        ]

        tk.Label(self.sidebar, text="NAVIGATION MENU", bg=COLORS["bg_sidebar"], fg="#64748B", font=("Segoe UI", 8, "bold"), padx=18, pady=12).pack(anchor="w")

        self.nav_buttons = {}
        for label, view_key in nav_items:
            btn = tk.Button(
                self.sidebar,
                text=f"  {label}",
                anchor="w",
                bg=COLORS["bg_sidebar"],
                fg=COLORS["text_sidebar"],
                activebackground=COLORS["bg_sidebar_hover"],
                activeforeground=COLORS["text_light"],
                bd=0,
                padx=16,
                pady=10,
                font=FONTS["body"],
                cursor="hand2",
                command=lambda k=view_key: self.show_view(k)
            )
            btn.pack(fill="x")
            self.nav_buttons[view_key] = btn

        # Sidebar footer
        side_footer = tk.Frame(self.sidebar, bg="#0B1120", padx=16, pady=14)
        side_footer.pack(side="bottom", fill="x")
        tk.Label(side_footer, text="DBMS Mini Project", font=FONTS["caption"], bg="#0B1120", fg="#94A3B8").pack(anchor="w")
        tk.Label(side_footer, text="Computer Engg | AY 2026-27", font=("Segoe UI", 8), bg="#0B1120", fg="#64748B").pack(anchor="w")

        # View container
        self.content_area = tk.Frame(body, bg=COLORS["bg_main"])
        self.content_area.pack(fill="both", expand=True, side="right")

        # Instantiate views
        self.views = {
            "dashboard": DashboardView(self.content_area, nav_callback=self.show_view),
            "departments": DepartmentView(self.content_area),
            "teachers": TeacherView(self.content_area),
            "students": StudentView(self.content_area),
            "subjects": SubjectView(self.content_area),
            "enrollments": EnrollmentView(self.content_area),
            "assessments": AssessmentView(self.content_area),
            "marks": MarksEntryView(self.content_area),
            "reports": ReportsView(self.content_area),
            "settings": SettingsView(self.content_area, on_config_changed=self._on_config_updated)
        }

    def show_view(self, view_key):
        """Switch active view in content container."""
        for k, v in self.views.items():
            v.pack_forget()

        # Update sidebar button highlight
        for k, btn in self.nav_buttons.items():
            if k == view_key:
                btn.configure(bg=COLORS["bg_sidebar_active"], fg=COLORS["text_light"], font=FONTS["body_bold"])
            else:
                btn.configure(bg=COLORS["bg_sidebar"], fg=COLORS["text_sidebar"], font=FONTS["body"])

        # Display selected view
        active = self.views.get(view_key)
        if active:
            active.pack(fill="both", expand=True)
            # Call refresh if available
            if hasattr(active, "refresh_data"):
                active.refresh_data()
            elif hasattr(active, "load_departments"):
                active.load_departments()
            elif hasattr(active, "load_students"):
                active.load_students()
            elif hasattr(active, "load_teachers"):
                active.load_teachers()
            elif hasattr(active, "load_subjects"):
                active.load_subjects()
            elif hasattr(active, "load_enrollments"):
                active.load_enrollments()
            elif hasattr(active, "load_assessments"):
                active.load_assessments()

    def _on_config_updated(self):
        """Update top status badge and refresh views."""
        self.lbl_db_badge.config(
            text=self._get_db_status_text(),
            bg="#064E3B" if db.active_engine == "mysql" else "#1E3A8A",
            fg="#6EE7B7" if db.active_engine == "mysql" else "#93C5FD"
        )
        if "dashboard" in self.views:
            self.views["dashboard"].refresh_data()

def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
