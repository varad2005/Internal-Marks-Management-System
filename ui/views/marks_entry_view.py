"""
Marks Entry & Updating Management View
K.K. Wagh Institute of Engineering Education and Research, Nashik
Department of Computer Engineering | Academic Year 2026-27
"""

import tkinter as tk
from tkinter import ttk, messagebox
from db import db
from ui.theme import COLORS, FONTS
from ui.components import DataTable, FormModal

class MarksEntryView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg_main"])
        self.current_assessment_info = None
        self._build_header()
        self._build_selection_bar()
        self._build_summary_banner()
        self._build_table()
        self.load_subjects()

    def _build_header(self):
        hdr = tk.Frame(self, bg=COLORS["bg_main"], pady=10)
        hdr.pack(fill="x", padx=20)
        tk.Label(hdr, text="Marks Entry & Evaluation", font=FONTS["header_title"], bg=COLORS["bg_main"], fg=COLORS["text_dark"]).pack(anchor="w")
        tk.Label(hdr, text="Record, update, and validate internal assessment marks with boundary checks (0 to Max Marks)", font=FONTS["caption"], bg=COLORS["bg_main"], fg=COLORS["text_muted"]).pack(anchor="w")

    def _build_selection_bar(self):
        bar = tk.Frame(self, bg=COLORS["bg_card"], bd=1, relief="solid", padx=16, pady=12)
        bar.pack(fill="x", padx=20, pady=(0, 10))

        # Subject Selection
        s_box = tk.Frame(bar, bg=COLORS["bg_card"])
        s_box.pack(side="left", padx=(0, 15))
        tk.Label(s_box, text="1. Select Subject:", bg=COLORS["bg_card"], fg=COLORS["text_dark"], font=FONTS["body_bold"]).pack(anchor="w", pady=(0, 2))
        self.sub_var = tk.StringVar()
        self.cb_subject = ttk.Combobox(s_box, textvariable=self.sub_var, state="readonly", width=36)
        self.cb_subject.pack()
        self.cb_subject.bind("<<ComboboxSelected>>", self._on_subject_changed)

        # Assessment Selection
        a_box = tk.Frame(bar, bg=COLORS["bg_card"])
        a_box.pack(side="left", padx=(0, 15))
        tk.Label(a_box, text="2. Select Assessment:", bg=COLORS["bg_card"], fg=COLORS["text_dark"], font=FONTS["body_bold"]).pack(anchor="w", pady=(0, 2))
        self.ass_var = tk.StringVar()
        self.cb_assessment = ttk.Combobox(a_box, textvariable=self.ass_var, state="readonly", width=32)
        self.cb_assessment.pack()
        self.cb_assessment.bind("<<ComboboxSelected>>", self._on_assessment_changed)

        # Filter Student search
        f_box = tk.Frame(bar, bg=COLORS["bg_card"])
        f_box.pack(side="left", padx=(0, 10))
        tk.Label(f_box, text="Filter Student:", bg=COLORS["bg_card"], fg=COLORS["text_dark"], font=FONTS["body_bold"]).pack(anchor="w", pady=(0, 2))
        self.filter_var = tk.StringVar()
        ent_filter = ttk.Entry(f_box, textvariable=self.filter_var, width=18)
        ent_filter.pack()
        ent_filter.bind("<KeyRelease>", lambda e: self._filter_displayed_students())

        # Buttons
        b_box = tk.Frame(bar, bg=COLORS["bg_card"])
        b_box.pack(side="right")
        ttk.Button(b_box, text="📝 Record / Edit Marks", style="Primary.TButton", command=self._open_marks_modal).pack(side="left", padx=4)
        ttk.Button(b_box, text="⚡ Mark Absent", style="Secondary.TButton", command=self._mark_student_absent).pack(side="left", padx=4)
        ttk.Button(b_box, text="🗑️ Clear Marks", style="Danger.TButton", command=self._delete_marks).pack(side="left", padx=4)

    def _build_summary_banner(self):
        self.banner = tk.Frame(self, bg="#EFF6FF", bd=1, relief="solid", padx=16, pady=8)
        self.banner.pack(fill="x", padx=20, pady=(0, 10))

        self.lbl_stats = tk.Label(
            self.banner,
            text="Please select a Subject and Assessment above to load student enrollment roster.",
            bg="#EFF6FF",
            fg="#1E40AF",
            font=FONTS["body_bold"]
        )
        self.lbl_stats.pack(anchor="w")

    def _build_table(self):
        tbl_frame = tk.Frame(self, bg=COLORS["bg_main"])
        tbl_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        columns = [
            ("enrollment_id", "Enr ID", 60, "center"),
            ("roll_no", "Roll No", 100, "center"),
            ("prn", "PRN", 110, "center"),
            ("student_name", "Student Name", 180, "w"),
            ("marks_obtained", "Marks Scored", 95, "center"),
            ("max_marks", "Max Marks", 85, "center"),
            ("percentage", "Percentage", 85, "center"),
            ("is_absent", "Absent", 70, "center"),
            ("status", "Status", 80, "center"),
            ("remarks", "Remarks / Comments", 220, "w")
        ]
        self.table = DataTable(tbl_frame, columns)
        self.table.pack(fill="both", expand=True)
        self.table.on_double_click(lambda item: self._open_marks_modal())

    def load_subjects(self):
        sub_sql = "SELECT subject_id, subject_code, subject_name FROM subjects ORDER BY subject_code"
        rows = db.fetch_all(sub_sql)
        self.subject_map = {f"{r['subject_code']} - {r['subject_name']}": r["subject_id"] for r in rows}
        self.cb_subject["values"] = list(self.subject_map.keys())
        if rows:
            self.cb_subject.current(0)
            self._on_subject_changed()

    def _on_subject_changed(self, event=None):
        sub_name = self.sub_var.get()
        sub_id = self.subject_map.get(sub_name)
        if not sub_id:
            return

        # Fetch assessments for this subject
        ass_sql = "SELECT assessment_id, subject_id, assessment_name, assessment_type, max_marks FROM assessments WHERE subject_id = %s ORDER BY assessment_id"
        rows = db.fetch_all(ass_sql, (sub_id,))
        self.assessment_map = {f"{r['assessment_name']} ({r['assessment_type']}, Max: {r['max_marks']})": r for r in rows}
        self.cb_assessment["values"] = list(self.assessment_map.keys())
        if rows:
            self.cb_assessment.current(0)
            self._on_assessment_changed()
        else:
            self.ass_var.set("")
            self.table.clear()
            self.lbl_stats.config(text="No assessments configured for this subject. Please add assessments in 'Assessment Management'.")

    def _on_assessment_changed(self, event=None):
        ass_item = self.assessment_map.get(self.ass_var.get())
        if not ass_item:
            return
        self.current_assessment_info = ass_item
        self.load_students_for_assessment()

    def load_students_for_assessment(self):
        if not self.current_assessment_info:
            return

        ass_id = self.current_assessment_info["assessment_id"]
        sub_id = self.current_assessment_info["subject_id"]
        max_m = float(self.current_assessment_info["max_marks"])

        # Fetch all enrolled students and their marks for this assessment using LEFT JOIN
        sql = """
        SELECT 
            e.enrollment_id, s.roll_no, s.prn,
            CONCAT(s.first_name, ' ', s.last_name) AS student_name,
            m.mark_id,
            m.marks_obtained,
            m.is_absent,
            m.remarks
        FROM enrollments e
        JOIN students s ON e.student_id = s.student_id
        LEFT JOIN marks m ON (e.enrollment_id = m.enrollment_id AND m.assessment_id = %s)
        WHERE e.subject_id = %s AND e.status = 'Active'
        ORDER BY s.roll_no ASC
        """
        if db.active_engine == "sqlite":
            sql = sql.replace("CONCAT(s.first_name, ' ', s.last_name)", "(s.first_name || ' ' || s.last_name)")

        raw_rows = db.fetch_all(sql, (ass_id, sub_id))
        self.all_current_rows = []

        total_enrolled = len(raw_rows)
        entered_count = 0
        pass_count = 0
        fail_count = 0
        absent_count = 0
        total_score = 0.0

        for r in raw_rows:
            row = dict(r)
            row["max_marks"] = f"{max_m:.2f}"
            if row["mark_id"] is not None:
                entered_count += 1
                is_abs = bool(row["is_absent"])
                row["is_absent"] = "Yes" if is_abs else "No"
                if is_abs:
                    absent_count += 1
                    row["marks_obtained"] = "0.00"
                    row["percentage"] = "0.00%"
                    row["status"] = "Absent"
                else:
                    marks = float(row["marks_obtained"])
                    row["marks_obtained"] = f"{marks:.2f}"
                    pct = round((marks / max_m) * 100, 2)
                    row["percentage"] = f"{pct:.2f}%"
                    total_score += marks
                    if pct >= 40.0:
                        pass_count += 1
                        row["status"] = "Pass"
                    else:
                        fail_count += 1
                        row["status"] = "Fail"
            else:
                row["marks_obtained"] = "—"
                row["percentage"] = "—"
                row["is_absent"] = "No"
                row["status"] = "Pending"
                row["remarks"] = ""

            self.all_current_rows.append(row)

        self.table.set_data(self.all_current_rows)

        avg_str = f"{(total_score / (entered_count - absent_count)):.2f}" if (entered_count - absent_count) > 0 else "0.00"
        self.lbl_stats.config(
            text=f"Assessment: {self.current_assessment_info['assessment_name']} (Max Marks: {max_m}) | "
                 f"Enrolled: {total_enrolled} | Evaluated: {entered_count}/{total_enrolled} | "
                 f"Passed: {pass_count} | Failed: {fail_count} | Absent: {absent_count} | Class Avg: {avg_str}/{max_m}"
        )

    def _filter_displayed_students(self):
        query = self.filter_var.get().strip().lower()
        if not query:
            self.table.set_data(self.all_current_rows)
            return

        filtered = [
            r for r in self.all_current_rows
            if query in r["roll_no"].lower() or query in r["prn"].lower() or query in r["student_name"].lower()
        ]
        self.table.set_data(filtered)

    def _open_marks_modal(self):
        selected = self.table.get_selected_item()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a student from the table.")
            return

        max_m = float(self.current_assessment_info["max_marks"])
        ass_id = self.current_assessment_info["assessment_id"]
        enr_id = int(selected["enrollment_id"])

        # Check existing mark
        existing_mark = selected["marks_obtained"]
        is_abs = selected["is_absent"] == "Yes"
        existing_val = "" if existing_mark == "—" else existing_mark

        fields = [
            {"name": "student_name", "label": "Student Name", "type": "text", "default": selected["student_name"], "readonly": True, "required": False},
            {"name": "marks_obtained", "label": f"Marks Obtained (Max: {max_m})", "type": "text", "default": existing_val, "required": True},
            {"name": "is_absent", "label": "Mark as Absent", "type": "checkbox", "default": is_abs, "required": False},
            {"name": "remarks", "label": "Teacher Remarks / Notes", "type": "text", "default": selected.get("remarks", ""), "required": False}
        ]

        def save(data):
            is_absent_flag = data["is_absent"]
            if is_absent_flag:
                marks_val = 0.00
            else:
                try:
                    marks_val = float(data["marks_obtained"])
                except ValueError:
                    raise ValueError("Marks obtained must be a valid number.")

                # Validation Rule: 0 <= marks_obtained <= max_marks
                if marks_val < 0:
                    raise ValueError("Validation Error: Marks cannot be negative.")
                if marks_val > max_m:
                    raise ValueError(f"Validation Error: Marks obtained ({marks_val}) cannot exceed maximum marks ({max_m}).")

            # Check if record exists
            check_sql = "SELECT mark_id FROM marks WHERE enrollment_id = %s AND assessment_id = %s"
            existing = db.fetch_one(check_sql, (enr_id, ass_id))

            if existing:
                upd_sql = """
                UPDATE marks
                SET marks_obtained = %s, is_absent = %s, remarks = %s
                WHERE mark_id = %s
                """
                db.execute_query(upd_sql, (marks_val, 1 if is_absent_flag else 0, data["remarks"].strip(), existing["mark_id"]))
                messagebox.showinfo("Success", "Marks updated successfully!")
            else:
                ins_sql = """
                INSERT INTO marks (enrollment_id, assessment_id, marks_obtained, is_absent, remarks)
                VALUES (%s, %s, %s, %s, %s)
                """
                db.execute_query(ins_sql, (enr_id, ass_id, marks_val, 1 if is_absent_flag else 0, data["remarks"].strip()))
                messagebox.showinfo("Success", "Marks recorded successfully!")

            self.load_students_for_assessment()

        FormModal(self, title=f"Enter Marks - {selected['student_name']}", fields=fields, on_save=save, width=480, submit_text="Save Marks")

    def _mark_student_absent(self):
        selected = self.table.get_selected_item()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a student to mark as absent.")
            return

        ass_id = self.current_assessment_info["assessment_id"]
        enr_id = int(selected["enrollment_id"])

        confirm = messagebox.askyesno(
            "Confirm Absence",
            f"Are you sure you want to mark '{selected['student_name']}' as Absent for this assessment?\nMarks will be recorded as 0.00 with status 'Absent'."
        )
        if confirm:
            check_sql = "SELECT mark_id FROM marks WHERE enrollment_id = %s AND assessment_id = %s"
            existing = db.fetch_one(check_sql, (enr_id, ass_id))
            if existing:
                db.execute_query(
                    "UPDATE marks SET marks_obtained = 0.00, is_absent = 1, remarks = 'Marked Absent' WHERE mark_id = %s",
                    (existing["mark_id"],)
                )
            else:
                db.execute_query(
                    "INSERT INTO marks (enrollment_id, assessment_id, marks_obtained, is_absent, remarks) VALUES (%s, %s, 0.00, 1, 'Marked Absent')",
                    (enr_id, ass_id)
                )
            messagebox.showinfo("Success", "Student marked as Absent.")
            self.load_students_for_assessment()

    def _delete_marks(self):
        selected = self.table.get_selected_item()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a record.")
            return

        if selected["marks_obtained"] == "—":
            messagebox.showinfo("Info", "No marks have been recorded for this student yet.")
            return

        confirm = messagebox.askyesno(
            "Clear Marks",
            f"Are you sure you want to delete the recorded marks for '{selected['student_name']}'?"
        )
        if confirm:
            ass_id = self.current_assessment_info["assessment_id"]
            enr_id = int(selected["enrollment_id"])
            db.execute_query(
                "DELETE FROM marks WHERE enrollment_id = %s AND assessment_id = %s",
                (enr_id, ass_id)
            )
            messagebox.showinfo("Success", "Marks record deleted.")
            self.load_students_for_assessment()
