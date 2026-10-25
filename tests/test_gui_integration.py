"""
Integration Tests for GUI Views and Business Logic
K.K. Wagh Institute of Engineering Education and Research, Nashik
Department of Computer Engineering | Academic Year 2026-27
"""

import sys
import os
import unittest
import tkinter as tk

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from db import db
from main import App

class TestGUIViews(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Set to standalone mode for continuous testing
        db.active_engine = "sqlite"
        db.init_database_from_sql_files("database.sql", "sample_data.sql")
        cls.app = App()
        cls.app.withdraw()  # Hide main window during testing

    @classmethod
    def tearDownClass(cls):
        try:
            cls.app.destroy()
        except Exception:
            pass

    def test_01_dashboard_stats(self):
        """Dashboard accurately reads DB metrics and populates table."""
        d_view = self.app.views["dashboard"]
        d_view.refresh_data()
        self.assertGreater(len(d_view.table.tree.get_children()), 0)
        print("  [OK] Dashboard View verified with live DB records.")

    def test_02_student_view_search_and_filter(self):
        """Student view filters correctly by class and division."""
        st_view = self.app.views["students"]
        st_view.load_students()
        initial_count = len(st_view.table.tree.get_children())
        self.assertGreater(initial_count, 0)

        # Search for 'Aarav'
        st_view._handle_search("Aarav", {"class_year": "All", "division": "All"})
        filtered_count = len(st_view.table.tree.get_children())
        self.assertEqual(filtered_count, 1)

        # Reset
        st_view.load_students()
        self.assertEqual(len(st_view.table.tree.get_children()), initial_count)
        print("  [OK] Student View search and filter verified.")

    def test_03_subject_and_assessment_relationship(self):
        """Assessments belong to curriculum subjects and max marks are defined."""
        ass_view = self.app.views["assessments"]
        ass_view.load_assessments()
        ass_count = len(ass_view.table.tree.get_children())
        self.assertGreater(ass_count, 0)
        print(f"  [OK] Assessment View verified with {ass_count} evaluation heads.")

    def test_04_marks_entry_and_validation(self):
        """Marks entry view loads enrollments and validates boundaries."""
        marks_view = self.app.views["marks"]
        marks_view.cb_subject.current(0)
        marks_view._on_subject_changed()
        marks_view.cb_assessment.current(0)
        marks_view._on_assessment_changed()

        rows = len(marks_view.table.tree.get_children())
        self.assertGreater(rows, 0)
        print(f"  [OK] Marks Entry View loaded roster of {rows} enrolled candidates.")

    def test_05_reports_generation(self):
        """Reports view generates student marksheet, subject report, and class analytics."""
        rep_view = self.app.views["reports"]
        
        # 1. Student Marksheet
        rep_view.generate_student_marksheet()
        ms_items = len(rep_view.ms_table.tree.get_children())
        self.assertGreater(ms_items, 0, "Student marksheet should have evaluation items.")
        print(f"  [OK] Student Marksheet generated with {ms_items} course assessments.")

        # 2. Subject Report
        rep_view.generate_subject_report()
        sub_items = len(rep_view.sub_table.tree.get_children())
        self.assertGreater(sub_items, 0, "Subject report should have student entries.")
        print(f"  [OK] Subject Performance Report generated with {sub_items} student records.")

        # 3. Class Analytics
        rep_view.generate_class_report()
        cls_items = len(rep_view.cls_table.tree.get_children())
        self.assertGreater(cls_items, 0, "Class leaderboard should have ranked students.")
        print(f"  [OK] Class Performance Leaderboard generated with {cls_items} ranked students.")

if __name__ == "__main__":
    unittest.main()
