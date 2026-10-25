"""
Automated Unit and Integration Tests for Database Schema, Constraints, and Queries
K.K. Wagh Institute of Engineering Education and Research, Nashik
Department of Computer Engineering | Academic Year 2026-27
"""

import sys
import os
import unittest

# Add root directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from db import db
from config import load_config

class TestDatabaseAndQueries(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Force SQLite mode for isolated headless CI/testing environment
        db.active_engine = "sqlite"
        success, msg = db.init_database_from_sql_files("database.sql", "sample_data.sql")
        print(f"\n[SETUP] {msg}")

    def test_01_tables_exist_and_populated(self):
        """Verify all 7 tables exist and have initial records."""
        tables = ["departments", "teachers", "students", "subjects", "enrollments", "assessments", "marks"]
        for tbl in tables:
            rows = db.fetch_all(f"SELECT COUNT(*) as cnt FROM {tbl}")
            count = rows[0]["cnt"]
            self.assertGreater(count, 0, f"Table {tbl} should have records.")
            print(f"  [OK] Table '{tbl}' verified with {count} records.")

    def test_02_prevent_duplicate_enrollment(self):
        """Requirement #9: Prevent duplicate enrollments for the same student, subject, AY, sem."""
        with self.assertRaises(Exception) as ctx:
            # Student 1 is already enrolled in Subject 1 for 2026-2027 Sem 5
            db.execute_query(
                """INSERT INTO enrollments (student_id, subject_id, academic_year, semester, enrollment_date, status)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (1, 1, '2026-2027', 5, '2026-07-20', 'Active')
            )
        self.assertIn("Duplicate", str(ctx.exception))
        print("  [OK] Constraint uq_student_enrollment successfully blocked duplicate enrollment.")

    def test_03_prevent_duplicate_marks(self):
        """Requirement #9: Prevent duplicate marks for the same enrollment and assessment."""
        with self.assertRaises(Exception) as ctx:
            # Enrollment 1 already has marks for Assessment 1
            db.execute_query(
                """INSERT INTO marks (enrollment_id, assessment_id, marks_obtained, is_absent, remarks)
                   VALUES (%s, %s, %s, %s, %s)""",
                (1, 1, 25.0, 0, 'Duplicate test')
            )
        self.assertIn("Duplicate", str(ctx.exception))
        print("  [OK] Constraint uq_enrollment_assessment successfully blocked duplicate marks entry.")

    def test_04_validate_marks_obtained_range(self):
        """Requirement #10: Marks obtained cannot exceed assessment maximum marks."""
        # Assessment 1 (In-Sem Exam) max marks is 30.00
        # Try entering 35.00 marks on Enrollment 2 (Student 1, Subject 2) and Assessment 1
        with self.assertRaises(Exception) as ctx:
            db.execute_query(
                """INSERT INTO marks (enrollment_id, assessment_id, marks_obtained, is_absent, remarks)
                   VALUES (%s, %s, %s, %s, %s)""",
                (2, 1, 35.0, 0, 'Excess marks')
            )
        self.assertIn("Validation Error", str(ctx.exception))
        print("  [OK] Trigger/Check successfully prevented marks > max_marks (35 > 30).")

    def test_05_student_marksheet_query(self):
        """Requirement #6 & #7: Generate student marksheet using SQL JOINs and Aggregates."""
        # Fetch detailed marks for Student 1 (Aarav Sharma)
        query = """
        SELECT 
            s.prn, s.roll_no, (s.first_name || ' ' || s.last_name) AS student_name,
            sub.subject_code, sub.subject_name,
            a.assessment_name, a.max_marks, m.marks_obtained, m.is_absent,
            ROUND((m.marks_obtained / a.max_marks) * 100, 2) AS percentage
        FROM marks m
        JOIN enrollments e ON m.enrollment_id = e.enrollment_id
        JOIN students s ON e.student_id = s.student_id
        JOIN assessments a ON m.assessment_id = a.assessment_id
        JOIN subjects sub ON a.subject_id = sub.subject_id
        WHERE s.student_id = %s
        ORDER BY sub.subject_code, a.assessment_name;
        """
        rows = db.fetch_all(query, (1,))
        self.assertGreater(len(rows), 0, "Student 1 should have marksheet records.")
        total_obtained = sum(r["marks_obtained"] for r in rows)
        total_max = sum(r["max_marks"] for r in rows)
        overall_pct = round((total_obtained / total_max) * 100, 2)
        print(f"  [OK] Student Marksheet Query: Total {total_obtained}/{total_max} ({overall_pct}%)")

    def test_06_subject_performance_aggregate_query(self):
        """Requirement #6 & #7: Subject-wise performance report using GROUP BY and aggregates."""
        query = """
        SELECT 
            sub.subject_code, sub.subject_name, a.assessment_name, a.max_marks,
            COUNT(m.mark_id) AS total_appeared,
            AVG(m.marks_obtained) AS avg_marks,
            MAX(m.marks_obtained) AS max_marks_scored,
            MIN(m.marks_obtained) AS min_marks_scored
        FROM subjects sub
        JOIN assessments a ON sub.subject_id = a.subject_id
        JOIN marks m ON a.assessment_id = m.assessment_id
        WHERE sub.subject_id = 1
        GROUP BY sub.subject_code, sub.subject_name, a.assessment_name, a.max_marks;
        """
        rows = db.fetch_all(query)
        self.assertGreater(len(rows), 0, "Subject 1 (DBMS) should have performance stats.")
        print(f"  [OK] Subject Performance Summary Query returned {len(rows)} assessment aggregates.")

    def test_07_class_performance_query(self):
        """Requirement #6 & #7: Class Performance Analytics by class_year and division."""
        query = """
        SELECT 
            s.class_year, s.division,
            COUNT(DISTINCT s.student_id) AS total_students,
            COUNT(m.mark_id) AS total_assessments_recorded,
            ROUND(AVG((m.marks_obtained / a.max_marks) * 100), 2) AS class_average_percentage
        FROM students s
        JOIN enrollments e ON s.student_id = e.student_id
        JOIN marks m ON e.enrollment_id = m.enrollment_id
        JOIN assessments a ON m.assessment_id = a.assessment_id
        GROUP BY s.class_year, s.division;
        """
        rows = db.fetch_all(query)
        self.assertGreater(len(rows), 0, "Class performance rows should be calculated.")
        for r in rows:
            print(f"  [OK] Class {r['class_year']} Div {r['division']}: {r['total_students']} students, Class Avg: {r['class_average_percentage']}%")

if __name__ == "__main__":
    unittest.main()
