"""
Dashboard View - Metrics, KPIs, and Recent Activity
K.K. Wagh Institute of Engineering Education and Research, Nashik
Department of Computer Engineering | Academic Year 2026-27
"""

import tkinter as tk
from tkinter import ttk
from db import db
from ui.theme import COLORS, FONTS
from ui.components import StatCard, DataTable

class DashboardView(tk.Frame):
    def __init__(self, parent, nav_callback=None):
        super().__init__(parent, bg=COLORS["bg_main"])
        self.nav_callback = nav_callback

        self._build_header()
        self._build_stat_cards()
        self._build_quick_actions()
        self._build_recent_activity()

    def _build_header(self):
        header_frame = tk.Frame(self, bg=COLORS["bg_main"], pady=10)
        header_frame.pack(fill="x", padx=20)

        tk.Label(header_frame, text="Institutional Dashboard", font=FONTS["header_title"], bg=COLORS["bg_main"], fg=COLORS["text_dark"]).pack(anchor="w")
        tk.Label(header_frame, text="Academic Year 2026–27 | Real-time Department Statistics & Assessment Highlights", font=FONTS["caption"], bg=COLORS["bg_main"], fg=COLORS["text_muted"]).pack(anchor="w")

    def _build_stat_cards(self):
        self.cards_frame = tk.Frame(self, bg=COLORS["bg_main"])
        self.cards_frame.pack(fill="x", padx=20, pady=(5, 15))

        self.card_students = StatCard(self.cards_frame, "Total Students", "0", "Enrolled in department", accent_color="#2563EB")
        self.card_students.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.card_teachers = StatCard(self.cards_frame, "Faculty Members", "0", "Computer Engineering", accent_color="#0D9488")
        self.card_teachers.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.card_subjects = StatCard(self.cards_frame, "Curriculum Courses", "0", "Theory & Labs active", accent_color="#D97706")
        self.card_subjects.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.card_marks = StatCard(self.cards_frame, "Marks Recorded", "0", "Assessments evaluated", accent_color="#16A34A")
        self.card_marks.pack(side="left", fill="both", expand=True)

    def _build_quick_actions(self):
        act_frame = tk.Frame(self, bg=COLORS["bg_card"], bd=1, relief="solid", padx=16, pady=12)
        act_frame.pack(fill="x", padx=20, pady=(0, 15))

        tk.Label(act_frame, text="Quick Management Actions", font=FONTS["body_bold"], bg=COLORS["bg_card"], fg=COLORS["text_dark"]).pack(side="left", padx=(0, 20))

        actions = [
            ("➕ Add Student", "students"),
            ("📝 Enter Marks", "marks"),
            ("📊 Student Marksheet", "reports"),
            ("📚 Manage Courses", "subjects")
        ]

        for label, view_key in actions:
            btn = ttk.Button(
                act_frame,
                text=label,
                style="Secondary.TButton",
                command=lambda k=view_key: self.nav_callback(k) if self.nav_callback else None
            )
            btn.pack(side="left", padx=4)

        btn_refresh = ttk.Button(act_frame, text="🔄 Refresh Stats", style="Primary.TButton", command=self.refresh_data)
        btn_refresh.pack(side="right")

    def _build_recent_activity(self):
        act_cont = tk.Frame(self, bg=COLORS["bg_main"])
        act_cont.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        tk.Label(act_cont, text="Recent Assessment Marks Entries", font=FONTS["section_title"], bg=COLORS["bg_main"], fg=COLORS["text_dark"]).pack(anchor="w", pady=(0, 8))

        columns = [
            ("mark_id", "ID", 50, "center"),
            ("student_name", "Student Name", 180, "w"),
            ("prn", "PRN", 110, "center"),
            ("subject_name", "Subject", 200, "w"),
            ("assessment_name", "Assessment", 150, "w"),
            ("marks_obtained", "Marks Scored", 90, "center"),
            ("max_marks", "Max Marks", 80, "center"),
            ("percentage", "Percentage", 90, "center"),
            ("result_status", "Status", 80, "center")
        ]
        self.table = DataTable(act_cont, columns)
        self.table.pack(fill="both", expand=True)

    def refresh_data(self):
        """Fetch latest database stats and recent marks."""
        try:
            # Stats counts
            st_count = db.fetch_one("SELECT COUNT(*) AS c FROM students")["c"]
            tc_count = db.fetch_one("SELECT COUNT(*) AS c FROM teachers")["c"]
            sub_count = db.fetch_one("SELECT COUNT(*) AS c FROM subjects")["c"]
            mrk_count = db.fetch_one("SELECT COUNT(*) AS c FROM marks")["c"]

            self.card_students.update_value(st_count)
            self.card_teachers.update_value(tc_count)
            self.card_subjects.update_value(sub_count)
            self.card_marks.update_value(mrk_count)

            # Recent Marks Entries (Using view vw_student_marks_detailed with JOINs)
            recent_sql = """
            SELECT 
                mark_id, student_name, prn, subject_name, assessment_name,
                marks_obtained, max_marks, percentage, result_status
            FROM vw_student_marks_detailed
            ORDER BY mark_id DESC
            LIMIT 15;
            """
            rows = db.fetch_all(recent_sql)
            self.table.set_data(rows)
        except Exception as e:
            print("Error refreshing dashboard:", e)
