"""
Enrollment Management View
K.K. Wagh Institute of Engineering Education and Research, Nashik
Department of Computer Engineering | Academic Year 2026-27
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from db import db
from ui.theme import COLORS, FONTS
from ui.components import DataTable, SearchBar, FormModal

class EnrollmentView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg_main"])
        self._build_header()
        self._build_toolbar()
        self._build_table()
        self.load_enrollments()

    def _build_header(self):
        hdr = tk.Frame(self, bg=COLORS["bg_main"], pady=10)
        hdr.pack(fill="x", padx=20)
        tk.Label(hdr, text="Course Enrollment Management", font=FONTS["header_title"], bg=COLORS["bg_main"], fg=COLORS["text_dark"]).pack(anchor="w")
        tk.Label(hdr, text="Manage student course registrations per academic semester with duplicate-prevention enforcement", font=FONTS["caption"], bg=COLORS["bg_main"], fg=COLORS["text_muted"]).pack(anchor="w")

    def _build_toolbar(self):
        toolbar = tk.Frame(self, bg=COLORS["bg_main"])
        toolbar.pack(fill="x", padx=20, pady=(0, 10))

        filters = [
            ("academic_year", "Academic Year", ["2026-2027", "2025-2026"]),
            ("semester", "Semester", [str(i) for i in range(1, 9)]),
            ("status", "Status", ["Active", "Completed", "Dropped"])
        ]

        self.search_bar = SearchBar(
            toolbar,
            placeholder="Search PRN, roll no, subject...",
            filters=filters,
            on_search=self._handle_search,
            on_reset=self.load_enrollments
        )
        self.search_bar.pack(side="left")

        # Action Buttons
        btn_box = tk.Frame(toolbar, bg=COLORS["bg_main"])
        btn_box.pack(side="right")

        ttk.Button(btn_box, text="⚡ Batch Enroll Class", style="Secondary.TButton", command=self._open_batch_modal).pack(side="left", padx=4)
        ttk.Button(btn_box, text="➕ Enroll Student", style="Primary.TButton", command=self._open_enroll_modal).pack(side="left", padx=4)
        ttk.Button(btn_box, text="✏️ Edit Status", style="Secondary.TButton", command=self._open_edit_modal).pack(side="left", padx=4)
        ttk.Button(btn_box, text="🗑️ Drop / Delete", style="Danger.TButton", command=self._handle_delete).pack(side="left", padx=4)

    def _build_table(self):
        tbl_frame = tk.Frame(self, bg=COLORS["bg_main"])
        tbl_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        columns = [
            ("enrollment_id", "ID", 50, "center"),
            ("prn", "PRN", 110, "center"),
            ("roll_no", "Roll No", 110, "center"),
            ("student_name", "Student Name", 180, "w"),
            ("subject_code", "Code", 90, "center"),
            ("subject_name", "Subject Title", 220, "w"),
            ("academic_year", "Academic Year", 110, "center"),
            ("semester", "Sem", 50, "center"),
            ("status", "Status", 90, "center"),
            ("enrollment_date", "Enrolled Date", 100, "center")
        ]
        self.table = DataTable(tbl_frame, columns)
        self.table.pack(fill="both", expand=True)

    def load_enrollments(self):
        sql = """
        SELECT 
            e.enrollment_id, s.prn, s.roll_no,
            CONCAT(s.first_name, ' ', s.last_name) AS student_name,
            sub.subject_code, sub.subject_name,
            e.academic_year, e.semester, e.status, e.enrollment_date
        FROM enrollments e
        JOIN students s ON e.student_id = s.student_id
        JOIN subjects sub ON e.subject_id = sub.subject_id
        ORDER BY e.enrollment_id DESC
        """
        if db.active_engine == "sqlite":
            sql = sql.replace("CONCAT(s.first_name, ' ', s.last_name)", "(s.first_name || ' ' || s.last_name)")
        rows = db.fetch_all(sql)
        self.table.set_data(rows)

    def _handle_search(self, keyword, filters):
        conditions = ["1=1"]
        params = []

        if keyword:
            conditions.append("(s.prn LIKE %s OR s.roll_no LIKE %s OR s.first_name LIKE %s OR sub.subject_code LIKE %s OR sub.subject_name LIKE %s)")
            p = f"%{keyword}%"
            params.extend([p, p, p, p, p])

        if filters.get("academic_year") and filters["academic_year"] != "All":
            conditions.append("e.academic_year = %s")
            params.append(filters["academic_year"])

        if filters.get("semester") and filters["semester"] != "All":
            conditions.append("e.semester = %s")
            params.append(int(filters["semester"]))

        if filters.get("status") and filters["status"] != "All":
            conditions.append("e.status = %s")
            params.append(filters["status"])

        where_clause = " AND ".join(conditions)
        sql = f"""
        SELECT 
            e.enrollment_id, s.prn, s.roll_no,
            CONCAT(s.first_name, ' ', s.last_name) AS student_name,
            sub.subject_code, sub.subject_name,
            e.academic_year, e.semester, e.status, e.enrollment_date
        FROM enrollments e
        JOIN students s ON e.student_id = s.student_id
        JOIN subjects sub ON e.subject_id = sub.subject_id
        WHERE {where_clause}
        ORDER BY e.enrollment_id DESC
        """
        if db.active_engine == "sqlite":
            sql = sql.replace("CONCAT(s.first_name, ' ', s.last_name)", "(s.first_name || ' ' || s.last_name)")

        rows = db.fetch_all(sql, tuple(params))
        self.table.set_data(rows)

    def _open_enroll_modal(self):
        # Fetch active students
        st_sql = "SELECT student_id, prn, roll_no, first_name, last_name, class_year FROM students ORDER BY roll_no"
        st_rows = db.fetch_all(st_sql)
        student_map = {f"{r['roll_no']} - {r['first_name']} {r['last_name']} ({r['prn']})": r["student_id"] for r in st_rows}
        student_opts = list(student_map.keys())

        # Fetch subjects
        sub_sql = "SELECT subject_id, subject_code, subject_name, semester FROM subjects ORDER BY semester, subject_name"
        sub_rows = db.fetch_all(sub_sql)
        subject_map = {f"{r['subject_code']} - {r['subject_name']} (Sem {r['semester']})": (r["subject_id"], r["semester"]) for r in sub_rows}
        subject_opts = list(subject_map.keys())

        fields = [
            {"name": "student_label", "label": "Select Student", "type": "combobox", "options": student_opts, "required": True},
            {"name": "subject_label", "label": "Select Subject", "type": "combobox", "options": subject_opts, "required": True},
            {"name": "academic_year", "label": "Academic Year", "type": "text", "default": "2026-2027", "required": True},
            {"name": "enrollment_date", "label": "Enrollment Date (YYYY-MM-DD)", "type": "text", "default": str(date.today()), "required": True},
            {"name": "status", "label": "Status", "type": "combobox", "options": ["Active", "Completed", "Dropped"], "default": "Active", "required": True}
        ]

        def save(data):
            st_id = student_map.get(data["student_label"])
            sub_info = subject_map.get(data["subject_label"])
            if not st_id or not sub_info:
                raise ValueError("Valid student and subject selections are required.")

            sub_id, sem = sub_info
            sql = """
            INSERT INTO enrollments (student_id, subject_id, academic_year, semester, enrollment_date, status)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            db.execute_query(sql, (
                st_id,
                sub_id,
                data["academic_year"].strip(),
                sem,
                data["enrollment_date"].strip(),
                data["status"]
            ))
            messagebox.showinfo("Success", "Student successfully enrolled in course!")
            self.load_enrollments()

        FormModal(self, title="Enroll Student in Subject", fields=fields, on_save=save, width=500, submit_text="Enroll Student")

    def _open_batch_modal(self):
        """Allows enrolling all students of a given class year into a subject."""
        # Subjects
        sub_sql = "SELECT subject_id, subject_code, subject_name, semester, class_year FROM subjects ORDER BY semester, subject_name"
        sub_rows = db.fetch_all(sub_sql)
        subject_map = {f"{r['subject_code']} - {r['subject_name']} ({r['class_year']}, Sem {r['semester']})": r for r in sub_rows}

        batch_win = tk.Toplevel(self)
        batch_win.title("Batch Class Enrollment")
        batch_win.geometry("450x380")
        batch_win.configure(bg=COLORS["bg_main"])
        batch_win.transient(self)
        batch_win.grab_set()

        header = tk.Frame(batch_win, bg=COLORS["header_bg"], padx=16, pady=12)
        header.pack(fill="x")
        tk.Label(header, text="Batch Enroll Entire Class", bg=COLORS["header_bg"], fg=COLORS["text_light"], font=FONTS["brand_title"]).pack(anchor="w")

        body = tk.Frame(batch_win, bg=COLORS["bg_main"], padx=20, pady=16)
        body.pack(fill="both", expand=True)

        tk.Label(body, text="Select Subject to Enroll Students Into:", bg=COLORS["bg_main"], font=FONTS["body_bold"]).pack(anchor="w", pady=(0, 4))
        sub_var = tk.StringVar(value=list(subject_map.keys())[0] if subject_map else "")
        cb_sub = ttk.Combobox(body, textvariable=sub_var, values=list(subject_map.keys()), state="readonly")
        cb_sub.pack(fill="x", pady=(0, 10))

        tk.Label(body, text="Target Class Year:", bg=COLORS["bg_main"], font=FONTS["body_bold"]).pack(anchor="w", pady=(0, 4))
        year_var = tk.StringVar(value="TE")
        cb_year = ttk.Combobox(body, textvariable=year_var, values=["FE", "SE", "TE", "BE"], state="readonly")
        cb_year.pack(fill="x", pady=(0, 10))

        tk.Label(body, text="Academic Year:", bg=COLORS["bg_main"], font=FONTS["body_bold"]).pack(anchor="w", pady=(0, 4))
        ay_var = tk.StringVar(value="2026-2027")
        ent_ay = ttk.Entry(body, textvariable=ay_var)
        ent_ay.pack(fill="x", pady=(0, 15))

        def run_batch():
            sub_data = subject_map.get(sub_var.get())
            if not sub_data:
                messagebox.showerror("Error", "Please select a valid subject.")
                return

            sub_id = sub_data["subject_id"]
            sem = sub_data["semester"]
            target_year = year_var.get()
            ay = ay_var.get().strip()

            # Find all students matching class year
            students = db.fetch_all("SELECT student_id, roll_no FROM students WHERE class_year = %s", (target_year,))
            if not students:
                messagebox.showwarning("No Students", f"No students found in class {target_year}.")
                return

            enrolled_count = 0
            skipped_count = 0
            for st in students:
                try:
                    sql = """
                    INSERT INTO enrollments (student_id, subject_id, academic_year, semester, enrollment_date, status)
                    VALUES (%s, %s, %s, %s, %s, 'Active')
                    """
                    db.execute_query(sql, (st["student_id"], sub_id, ay, sem, str(date.today())))
                    enrolled_count += 1
                except Exception:
                    # Duplicate enrollment caught by UNIQUE constraint
                    skipped_count += 1

            batch_win.destroy()
            messagebox.showinfo(
                "Batch Enrollment Complete",
                f"Batch Operation Finished:\n• Successfully enrolled: {enrolled_count} students\n• Already enrolled (skipped): {skipped_count} students"
            )
            self.load_enrollments()

        ttk.Button(body, text="⚡ Run Batch Enrollment", style="Primary.TButton", command=run_batch).pack(fill="x", pady=10)

    def _open_edit_modal(self):
        selected = self.table.get_selected_item()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select an enrollment record to edit.")
            return

        fields = [
            {"name": "status", "label": "Enrollment Status", "type": "combobox", "options": ["Active", "Completed", "Dropped"], "default": selected["status"], "required": True}
        ]

        def save(data):
            db.execute_query(
                "UPDATE enrollments SET status = %s WHERE enrollment_id = %s",
                (data["status"], selected["enrollment_id"])
            )
            messagebox.showinfo("Success", "Enrollment status updated!")
            self.load_enrollments()

        FormModal(self, title="Update Enrollment Status", fields=fields, initial_data=selected, on_save=save, width=420, submit_text="Update Status")

    def _handle_delete(self):
        selected = self.table.get_selected_item()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select an enrollment to delete.")
            return

        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to drop enrollment for '{selected['student_name']}' in '{selected['subject_name']}'?\n\nWARNING: Any recorded marks for this student in this course will also be deleted."
        )
        if confirm:
            try:
                db.execute_query("DELETE FROM enrollments WHERE enrollment_id = %s", (selected["enrollment_id"],))
                messagebox.showinfo("Success", "Enrollment record deleted.")
                self.load_enrollments()
            except Exception as e:
                messagebox.showerror("Error", str(e))
