"""
Database Access Layer (DAL) for Internal Marks Management System
K.K. Wagh Institute of Engineering Education and Research, Nashik
Department of Computer Engineering | Academic Year 2026-27

Supports:
1. MySQL Server via mysql-connector-python (Primary Requirement)
2. Embedded SQLite Engine (Fallback/Standalone testing mode)
3. Schema & Sample Data initialization from SQL scripts
4. Safe Parameterized Queries and Transaction Management
"""

import os
import re
import sqlite3
from config import load_config, save_config

try:
    import mysql.connector
    from mysql.connector import Error as MySQLError
    HAS_MYSQL = True
except ImportError:
    HAS_MYSQL = False
    MySQLError = Exception

class DatabaseManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance.config = load_config()
            cls._instance.active_engine = cls._instance.config.get("db_engine", "mysql")
        return cls._instance

    def get_connection(self):
        """Create and return an active database connection based on configured engine."""
        if self.active_engine == "mysql":
            if not HAS_MYSQL:
                raise RuntimeError("mysql-connector-python is not installed. Please install via pip.")
            m_cfg = self.config["mysql"]
            conn = mysql.connector.connect(
                host=m_cfg.get("host", "localhost"),
                port=int(m_cfg.get("port", 3306)),
                user=m_cfg.get("user", "root"),
                password=m_cfg.get("password", ""),
                database=m_cfg.get("database", "internal_marks_db")
            )
            return conn
        else:
            s_cfg = self.config.get("sqlite", {})
            db_path = s_cfg.get("database", "internal_marks.db")
            conn = sqlite3.connect(db_path)
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.row_factory = sqlite3.Row
            return conn

    def test_mysql_connection(self, host, port, user, password, database=None):
        """Test connection parameters for MySQL server."""
        if not HAS_MYSQL:
            return False, "mysql-connector-python is not installed in the current environment."
        try:
            kwargs = {
                "host": host,
                "port": int(port),
                "user": user,
                "password": password,
                "connection_timeout": 5
            }
            if database:
                kwargs["database"] = database
            conn = mysql.connector.connect(**kwargs)
            conn.close()
            return True, "Connection successful!"
        except Exception as e:
            return False, str(e)

    def _convert_query_for_sqlite(self, sql):
        """Convert MySQL syntax / placeholders to SQLite syntax when in SQLite mode."""
        # Replace %s with ? for SQLite
        # But be careful not to replace % inside string literals
        pattern = re.compile(r'%s')
        sqlite_sql = pattern.sub('?', sql)
        # Replace AUTO_INCREMENT with AUTOINCREMENT
        sqlite_sql = sqlite_sql.replace("AUTO_INCREMENT", "AUTOINCREMENT")
        sqlite_sql = sqlite_sql.replace("INT AUTOINCREMENT", "INTEGER PRIMARY KEY AUTOINCREMENT")
        sqlite_sql = sqlite_sql.replace("INT AUTO_INCREMENT", "INTEGER PRIMARY KEY AUTOINCREMENT")
        sqlite_sql = sqlite_sql.replace("ENGINE=InnoDB", "")
        sqlite_sql = sqlite_sql.replace("COLLATE utf8mb4_unicode_ci", "")
        sqlite_sql = sqlite_sql.replace("CHARACTER SET utf8mb4", "")
        # Remove CREATE OR REPLACE VIEW -> CREATE VIEW IF NOT EXISTS
        sqlite_sql = sqlite_sql.replace("CREATE OR REPLACE VIEW", "CREATE VIEW IF NOT EXISTS")
        return sqlite_sql

    def execute_query(self, sql, params=None, commit=True):
        """
        Execute an INSERT, UPDATE, or DELETE query using parameterized inputs.
        Returns lastrowid for INSERTs, or affected rowcount for UPDATE/DELETEs.
        """
        conn = None
        try:
            conn = self.get_connection()
            if self.active_engine == "mysql":
                cursor = conn.cursor(dictionary=True)
                cursor.execute(sql, params or ())
                result = cursor.lastrowid or cursor.rowcount
            else:
                sql_converted = self._convert_query_for_sqlite(sql)
                cursor = conn.cursor()
                cursor.execute(sql_converted, params or ())
                result = cursor.lastrowid or cursor.rowcount
            
            if commit:
                conn.commit()
            cursor.close()
            return result
        except Exception as e:
            if conn:
                conn.rollback()
            raise self._format_error(e)
        finally:
            if conn:
                conn.close()

    def fetch_all(self, sql, params=None):
        """Execute a SELECT query and return list of row dictionaries."""
        conn = None
        try:
            conn = self.get_connection()
            if self.active_engine == "mysql":
                cursor = conn.cursor(dictionary=True)
                cursor.execute(sql, params or ())
                rows = cursor.fetchall()
                cursor.close()
                return rows
            else:
                sql_converted = self._convert_query_for_sqlite(sql)
                cursor = conn.cursor()
                cursor.execute(sql_converted, params or ())
                rows = [dict(row) for row in cursor.fetchall()]
                cursor.close()
                return rows
        except Exception as e:
            raise self._format_error(e)
        finally:
            if conn:
                conn.close()

    def fetch_one(self, sql, params=None):
        """Execute a SELECT query and return a single row dictionary or None."""
        conn = None
        try:
            conn = self.get_connection()
            if self.active_engine == "mysql":
                cursor = conn.cursor(dictionary=True)
                cursor.execute(sql, params or ())
                row = cursor.fetchone()
                cursor.close()
                return row
            else:
                sql_converted = self._convert_query_for_sqlite(sql)
                cursor = conn.cursor()
                cursor.execute(sql_converted, params or ())
                row = cursor.fetchone()
                cursor.close()
                return dict(row) if row else None
        except Exception as e:
            raise self._format_error(e)
        finally:
            if conn:
                conn.close()

    def _format_error(self, err):
        """Return a user-friendly error message from database exception."""
        msg = str(err)
        # Duplicate key violations
        if "Duplicate entry" in msg or "UNIQUE constraint failed" in msg:
            if "uq_student_enrollment" in msg or "enrollments.student_id" in msg:
                return Exception("Duplicate Error: The student is already enrolled in this subject for the specified academic year and semester.")
            if "uq_enrollment_assessment" in msg or "marks.enrollment_id" in msg:
                return Exception("Duplicate Error: Marks have already been recorded for this student in this assessment.")
            if "prn" in msg or "students.prn" in msg:
                return Exception("Duplicate Error: A student with this PRN already exists in the system.")
            if "email" in msg or "students.email" in msg:
                return Exception("Duplicate Error: A student or faculty with this Email Address already exists.")
            if "uq_student_roll" in msg or "students.roll_no" in msg:
                return Exception("Duplicate Error: A student with this Roll Number already exists in the selected Department, Class, and Division.")
            if "emp_code" in msg or "teachers.emp_code" in msg:
                return Exception("Duplicate Error: A teacher with this Employee Code already exists.")
            if "subject_code" in msg or "subjects.subject_code" in msg:
                return Exception("Duplicate Error: A subject with this Subject Code already exists.")
            if "dept_code" in msg or "departments.dept_code" in msg:
                return Exception("Duplicate Error: A department with this Department Code already exists.")
            return Exception(f"Duplicate Record Error: {msg}")

        # Foreign Key violations
        if "foreign key constraint fails" in msg.lower() or "FOREIGN KEY constraint failed" in msg:
            return Exception("Integrity Error: Cannot delete or update this record as it is referenced by other records (e.g., enrollments or marks).")

        # Check constraint violations
        if "chk_marks_non_negative" in msg:
            return Exception("Validation Error: Marks obtained cannot be negative.")
        if "Validation Error: Marks obtained cannot exceed" in msg:
            return Exception("Validation Error: Marks obtained cannot exceed assessment maximum marks.")

        return Exception(msg)

    def init_database_from_sql_files(self, db_schema_file="database.sql", sample_data_file="sample_data.sql"):
        """Initialize database tables, views, triggers, and sample data."""
        if not os.path.exists(db_schema_file):
            raise FileNotFoundError(f"Schema file '{db_schema_file}' not found.")

        if self.active_engine == "mysql":
            # For MySQL, first connect to server without database to create the database if needed
            m_cfg = self.config["mysql"]
            root_conn = mysql.connector.connect(
                host=m_cfg.get("host", "localhost"),
                port=int(m_cfg.get("port", 3306)),
                user=m_cfg.get("user", "root"),
                password=m_cfg.get("password", "")
            )
            root_cursor = root_conn.cursor()
            db_name = m_cfg.get("database", "internal_marks_db")
            root_cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            root_cursor.close()
            root_conn.close()

            # Now connect to target database and execute statements
            conn = self.get_connection()
            cursor = conn.cursor()

            # Execute schema
            with open(db_schema_file, "r", encoding="utf-8") as f:
                schema_content = f.read()

            # Strip comments and execute multi-statements
            # Split commands by delimiter or execute with multi=True
            for result in cursor.execute(schema_content, multi=True):
                pass
            conn.commit()

            # Execute sample data if present
            if sample_data_file and os.path.exists(sample_data_file):
                with open(sample_data_file, "r", encoding="utf-8") as f:
                    data_content = f.read()
                for result in cursor.execute(data_content, multi=True):
                    pass
                conn.commit()

            cursor.close()
            conn.close()
            return True, "MySQL database initialized successfully with schema and sample data!"
        else:
            # SQLite initialization
            s_cfg = self.config.get("sqlite", {})
            db_path = s_cfg.get("database", "internal_marks.db")
            if os.path.exists(db_path):
                try:
                    os.remove(db_path)
                except Exception:
                    pass

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")

            # Execute schema commands
            sqlite_ddl = """
            CREATE TABLE IF NOT EXISTS departments (
                department_id INTEGER PRIMARY KEY AUTOINCREMENT,
                dept_code TEXT NOT NULL UNIQUE,
                dept_name TEXT NOT NULL,
                intake_capacity INTEGER NOT NULL DEFAULT 180 CHECK (intake_capacity > 0),
                hod_name TEXT NOT NULL,
                established_year INTEGER NOT NULL DEFAULT 1984 CHECK (established_year >= 1984)
            );

            CREATE TABLE IF NOT EXISTS teachers (
                teacher_id INTEGER PRIMARY KEY AUTOINCREMENT,
                emp_code TEXT NOT NULL UNIQUE,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                phone TEXT,
                designation TEXT NOT NULL CHECK (designation IN ('Professor', 'Associate Professor', 'Assistant Professor', 'Adjunct Faculty')),
                department_id INTEGER NOT NULL REFERENCES departments(department_id) ON DELETE RESTRICT
            );

            CREATE TABLE IF NOT EXISTS students (
                student_id INTEGER PRIMARY KEY AUTOINCREMENT,
                prn TEXT NOT NULL UNIQUE,
                roll_no TEXT NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                phone TEXT,
                class_year TEXT NOT NULL CHECK (class_year IN ('FE', 'SE', 'TE', 'BE')),
                division TEXT NOT NULL CHECK (division IN ('A', 'B', 'C', 'D')),
                admission_year INTEGER NOT NULL DEFAULT 2026,
                department_id INTEGER NOT NULL REFERENCES departments(department_id) ON DELETE RESTRICT,
                CONSTRAINT uq_student_roll UNIQUE (department_id, class_year, division, roll_no)
            );

            CREATE TABLE IF NOT EXISTS subjects (
                subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_code TEXT NOT NULL UNIQUE,
                subject_name TEXT NOT NULL,
                semester INTEGER NOT NULL CHECK (semester BETWEEN 1 AND 8),
                class_year TEXT NOT NULL CHECK (class_year IN ('FE', 'SE', 'TE', 'BE')),
                credits INTEGER NOT NULL DEFAULT 3 CHECK (credits > 0),
                department_id INTEGER NOT NULL REFERENCES departments(department_id) ON DELETE RESTRICT,
                teacher_id INTEGER REFERENCES teachers(teacher_id) ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS enrollments (
                enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
                subject_id INTEGER NOT NULL REFERENCES subjects(subject_id) ON DELETE RESTRICT,
                academic_year TEXT NOT NULL DEFAULT '2026-2027',
                semester INTEGER NOT NULL CHECK (semester BETWEEN 1 AND 8),
                enrollment_date TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Active' CHECK (status IN ('Active', 'Completed', 'Dropped')),
                CONSTRAINT uq_student_enrollment UNIQUE (student_id, subject_id, academic_year, semester)
            );

            CREATE TABLE IF NOT EXISTS assessments (
                assessment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_id INTEGER NOT NULL REFERENCES subjects(subject_id) ON DELETE CASCADE,
                assessment_name TEXT NOT NULL,
                assessment_type TEXT NOT NULL CHECK (assessment_type IN ('In-Semester', 'End-Semester', 'Unit Test', 'Term Work', 'Practical / Oral', 'Assignment')),
                max_marks REAL NOT NULL CHECK (max_marks > 0),
                weightage_percent REAL NOT NULL DEFAULT 100.00 CHECK (weightage_percent > 0 AND weightage_percent <= 100),
                conducted_date TEXT,
                academic_year TEXT NOT NULL DEFAULT '2026-2027',
                CONSTRAINT uq_subject_assessment UNIQUE (subject_id, assessment_name, academic_year)
            );

            CREATE TABLE IF NOT EXISTS marks (
                mark_id INTEGER PRIMARY KEY AUTOINCREMENT,
                enrollment_id INTEGER NOT NULL REFERENCES enrollments(enrollment_id) ON DELETE CASCADE,
                assessment_id INTEGER NOT NULL REFERENCES assessments(assessment_id) ON DELETE CASCADE,
                marks_obtained REAL NOT NULL DEFAULT 0.00 CHECK (marks_obtained >= 0.00),
                is_absent INTEGER NOT NULL DEFAULT 0,
                remarks TEXT,
                entered_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT uq_enrollment_assessment UNIQUE (enrollment_id, assessment_id)
            );

            -- Trigger for max_marks validation on insert
            CREATE TRIGGER IF NOT EXISTS trg_validate_marks_insert
            BEFORE INSERT ON marks
            FOR EACH ROW
            WHEN NEW.is_absent = 0 AND NEW.marks_obtained > (SELECT max_marks FROM assessments WHERE assessment_id = NEW.assessment_id)
            BEGIN
                SELECT RAISE(ABORT, 'Validation Error: Marks obtained cannot exceed assessment maximum marks');
            END;

            -- Trigger for max_marks validation on update
            CREATE TRIGGER IF NOT EXISTS trg_validate_marks_update
            BEFORE UPDATE ON marks
            FOR EACH ROW
            WHEN NEW.is_absent = 0 AND NEW.marks_obtained > (SELECT max_marks FROM assessments WHERE assessment_id = NEW.assessment_id)
            BEGIN
                SELECT RAISE(ABORT, 'Validation Error: Marks obtained cannot exceed assessment maximum marks');
            END;

            -- Views
            CREATE VIEW IF NOT EXISTS vw_student_marks_detailed AS
            SELECT 
                m.mark_id,
                s.student_id,
                s.prn,
                s.roll_no,
                (s.first_name || ' ' || s.last_name) AS student_name,
                s.class_year,
                s.division,
                d.dept_code,
                d.dept_name,
                sub.subject_code,
                sub.subject_name,
                a.assessment_id,
                a.assessment_name,
                a.assessment_type,
                a.max_marks,
                m.marks_obtained,
                m.is_absent,
                ROUND((m.marks_obtained / a.max_marks) * 100, 2) AS percentage,
                CASE 
                    WHEN m.is_absent = 1 THEN 'Absent'
                    WHEN (m.marks_obtained / a.max_marks) >= 0.40 THEN 'Pass'
                    ELSE 'Fail'
                END AS result_status,
                e.academic_year,
                e.semester
            FROM marks m
            JOIN enrollments e ON m.enrollment_id = e.enrollment_id
            JOIN students s ON e.student_id = s.student_id
            JOIN departments d ON s.department_id = d.department_id
            JOIN assessments a ON m.assessment_id = a.assessment_id
            JOIN subjects sub ON a.subject_id = sub.subject_id;

            CREATE VIEW IF NOT EXISTS vw_subject_performance_summary AS
            SELECT 
                sub.subject_id,
                sub.subject_code,
                sub.subject_name,
                sub.class_year,
                sub.semester,
                a.assessment_id,
                a.assessment_name,
                a.max_marks,
                COUNT(m.mark_id) AS total_students_appeared,
                SUM(CASE WHEN m.is_absent = 0 AND (m.marks_obtained / a.max_marks) >= 0.40 THEN 1 ELSE 0 END) AS students_passed,
                SUM(CASE WHEN m.is_absent = 0 AND (m.marks_obtained / a.max_marks) < 0.40 THEN 1 ELSE 0 END) AS students_failed,
                SUM(CASE WHEN m.is_absent = 1 THEN 1 ELSE 0 END) AS students_absent,
                ROUND(AVG(CASE WHEN m.is_absent = 0 THEN m.marks_obtained ELSE NULL END), 2) AS average_marks,
                MAX(CASE WHEN m.is_absent = 0 THEN m.marks_obtained ELSE NULL END) AS highest_marks,
                MIN(CASE WHEN m.is_absent = 0 THEN m.marks_obtained ELSE NULL END) AS lowest_marks,
                ROUND((CAST(SUM(CASE WHEN m.is_absent = 0 AND (m.marks_obtained / a.max_marks) >= 0.40 THEN 1 ELSE 0 END) AS REAL) / 
                       NULLIF(COUNT(m.mark_id), 0)) * 100, 2) AS pass_percentage
            FROM subjects sub
            JOIN assessments a ON sub.subject_id = a.subject_id
            LEFT JOIN marks m ON a.assessment_id = m.assessment_id
            GROUP BY sub.subject_id, sub.subject_code, sub.subject_name, sub.class_year, sub.semester, a.assessment_id, a.assessment_name, a.max_marks;
            """
            cursor.executescript(sqlite_ddl)
            conn.commit()

            # Execute sample data converted for SQLite
            if sample_data_file and os.path.exists(sample_data_file):
                with open(sample_data_file, "r", encoding="utf-8") as f:
                    raw_lines = f.readlines()
                insert_lines = [
                    line.replace("FALSE", "0").replace("TRUE", "1")
                    for line in raw_lines
                    if not line.strip().upper().startswith("USE ") and not line.strip().startswith("--")
                ]
                cleaned_sql = "".join(insert_lines)
                cursor.executescript(cleaned_sql)
                conn.commit()

            cursor.close()
            conn.close()
            return True, "SQLite database initialized successfully with schema and sample data!"

# Singleton instance accessor
db = DatabaseManager()
