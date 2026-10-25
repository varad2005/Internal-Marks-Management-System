"""
Subject / Course Management View
K.K. Wagh Institute of Engineering Education and Research, Nashik
Department of Computer Engineering | Academic Year 2026-27
"""

import tkinter as tk
from tkinter import ttk, messagebox
from db import db
from ui.theme import COLORS, FONTS
from ui.components import DataTable, SearchBar, FormModal

class SubjectView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg_main"])
        self._build_header()
        self._build_toolbar()
        self._build_table()
        self.load_subjects()

    def _build_header(self):
        hdr = tk.Frame(self, bg=COLORS["bg_main"], pady=10)
        hdr.pack(fill="x", padx=20)
        tk.Label(hdr, text="Subject / Course Management", font=FONTS["header_title"], bg=COLORS["bg_main"], fg=COLORS["text_dark"]).pack(anchor="w")
        tk.Label(hdr, text="Configure curriculum subjects, credits, semester mappings, and assigned faculty", font=FONTS["caption"], bg=COLORS["bg_main"], fg=COLORS["text_muted"]).pack(anchor="w")

    def _build_toolbar(self):
        toolbar = tk.Frame(self, bg=COLORS["bg_main"])
        toolbar.pack(fill="x", padx=20, pady=(0, 10))

        filters = [
            ("class_year", "Class", ["FE", "SE", "TE", "BE"]),
            ("semester", "Semester", [str(i) for i in range(1, 9)])
        ]

        self.search_bar = SearchBar(
            toolbar,
            placeholder="Search code or subject title...",
            filters=filters,
            on_search=self._handle_search,
            on_reset=self.load_subjects
        )
        self.search_bar.pack(side="left")

        # Action Buttons
        btn_box = tk.Frame(toolbar, bg=COLORS["bg_main"])
        btn_box.pack(side="right")

        ttk.Button(btn_box, text="➕ Add Subject", style="Primary.TButton", command=self._open_add_modal).pack(side="left", padx=4)
        ttk.Button(btn_box, text="✏️ Edit", style="Secondary.TButton", command=self._open_edit_modal).pack(side="left", padx=4)
        ttk.Button(btn_box, text="🗑️ Delete", style="Danger.TButton", command=self._handle_delete).pack(side="left", padx=4)

    def _build_table(self):
        tbl_frame = tk.Frame(self, bg=COLORS["bg_main"])
        tbl_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        columns = [
            ("subject_id", "ID", 45, "center"),
            ("subject_code", "Code", 90, "center"),
            ("subject_name", "Subject Name", 250, "w"),
            ("class_year", "Class", 60, "center"),
            ("semester", "Sem", 50, "center"),
            ("credits", "Credits", 65, "center"),
            ("dept_name", "Department", 180, "w"),
            ("teacher_name", "Faculty In-Charge", 180, "w")
        ]
        self.table = DataTable(tbl_frame, columns)
        self.table.pack(fill="both", expand=True)
        self.table.on_double_click(lambda item: self._open_edit_modal())

    def load_subjects(self):
        sql = """
        SELECT 
            s.subject_id, s.subject_code, s.subject_name,
            s.class_year, s.semester, s.credits,
            d.dept_name, s.department_id, s.teacher_id,
            COALESCE(CONCAT(t.first_name, ' ', t.last_name), 'Unassigned') AS teacher_name
        FROM subjects s
        JOIN departments d ON s.department_id = d.department_id
        LEFT JOIN teachers t ON s.teacher_id = t.teacher_id
        ORDER BY s.semester ASC, s.subject_code ASC
        """
        if db.active_engine == "sqlite":
            sql = sql.replace("CONCAT(t.first_name, ' ', t.last_name)", "(t.first_name || ' ' || t.last_name)")
        rows = db.fetch_all(sql)
        self.table.set_data(rows)

    def _handle_search(self, keyword, filters):
        conditions = ["1=1"]
        params = []

        if keyword:
            conditions.append("(s.subject_code LIKE %s OR s.subject_name LIKE %s)")
            p = f"%{keyword}%"
            params.extend([p, p])

        if filters.get("class_year") and filters["class_year"] != "All":
            conditions.append("s.class_year = %s")
            params.append(filters["class_year"])

        if filters.get("semester") and filters["semester"] != "All":
            conditions.append("s.semester = %s")
            params.append(int(filters["semester"]))

        where_clause = " AND ".join(conditions)
        sql = f"""
        SELECT 
            s.subject_id, s.subject_code, s.subject_name,
            s.class_year, s.semester, s.credits,
            d.dept_name, s.department_id, s.teacher_id,
            COALESCE(CONCAT(t.first_name, ' ', t.last_name), 'Unassigned') AS teacher_name
        FROM subjects s
        JOIN departments d ON s.department_id = d.department_id
        LEFT JOIN teachers t ON s.teacher_id = t.teacher_id
        WHERE {where_clause}
        ORDER BY s.semester ASC, s.subject_code ASC
        """
        if db.active_engine == "sqlite":
            sql = sql.replace("CONCAT(t.first_name, ' ', t.last_name)", "(t.first_name || ' ' || t.last_name)")

        rows = db.fetch_all(sql, tuple(params))
        self.table.set_data(rows)

    def _get_form_fields(self):
        dept_rows = db.fetch_all("SELECT department_id, dept_code, dept_name FROM departments ORDER BY dept_code")
        self.dept_map = {f"{r['dept_code']} - {r['dept_name']}": r["department_id"] for r in dept_rows}
        dept_options = list(self.dept_map.keys())

        t_sql = "SELECT teacher_id, emp_code, first_name, last_name FROM teachers ORDER BY first_name"
        teacher_rows = db.fetch_all(t_sql)
        self.teacher_map = {"Unassigned": None}
        for r in teacher_rows:
            label = f"{r['first_name']} {r['last_name']} ({r['emp_code']})"
            self.teacher_map[label] = r["teacher_id"]
        teacher_options = list(self.teacher_map.keys())

        return [
            {"name": "subject_code", "label": "Subject Code (e.g. 310245)", "type": "text", "required": True},
            {"name": "subject_name", "label": "Subject Title", "type": "text", "required": True},
            {"name": "class_year", "label": "Class Year", "type": "combobox", "options": ["FE", "SE", "TE", "BE"], "default": "TE", "required": True},
            {"name": "semester", "label": "Semester (1-8)", "type": "combobox", "options": [str(i) for i in range(1, 9)], "default": "5", "required": True},
            {"name": "credits", "label": "Course Credits", "type": "text", "default": "3", "required": True},
            {"name": "dept_label", "label": "Department", "type": "combobox", "options": dept_options, "required": True},
            {"name": "teacher_label", "label": "Assigned Faculty", "type": "combobox", "options": teacher_options, "default": "Unassigned", "required": False}
        ]

    def _open_add_modal(self):
        fields = self._get_form_fields()

        def save(data):
            code = data.get("subject_code", "").strip().upper()
            name = data.get("subject_name", "").strip()
            class_year = data.get("class_year", "").strip()
            dept_label = data.get("dept_label", "").strip()

            if not code or not name:
                raise ValueError("Subject Code and Title are required.")
            dept_id = self.dept_map.get(dept_label)
            if not dept_id:
                raise ValueError("Please select a Department.")
            t_id = self.teacher_map.get(data.get("teacher_label"))

            try:
                credits = int(data.get("credits", 3))
                if credits <= 0 or credits > 10:
                    raise ValueError()
            except Exception:
                raise ValueError("Credits must be a positive integer between 1 and 10.")

            try:
                sem = int(data.get("semester", 5))
                if sem < 1 or sem > 8:
                    raise ValueError()
            except Exception:
                raise ValueError("Semester must be between 1 and 8.")

            sql = """
            INSERT INTO subjects (subject_code, subject_name, class_year, semester, credits, department_id, teacher_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            db.execute_query(sql, (
                code,
                name,
                class_year,
                sem,
                credits,
                dept_id,
                t_id
            ))
            messagebox.showinfo("Success", f"Subject '{name}' added successfully!")
            self.load_subjects()

        FormModal(self, title="Add Subject / Course", fields=fields, on_save=save, width=500, submit_text="Add Subject")

    def _open_edit_modal(self):
        selected = self.table.get_selected_item()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a subject from the table to edit.")
            return

        fields = self._get_form_fields()
        current_dept_label = ""
        for k, v in self.dept_map.items():
            if v == int(selected.get("department_id", 0)) or selected.get("dept_name") in k:
                current_dept_label = k
                break

        current_t_label = "Unassigned"
        for k, v in self.teacher_map.items():
            if selected.get("teacher_id") and v == int(selected.get("teacher_id")):
                current_t_label = k
                break

        init_data = selected.copy()
        init_data["dept_label"] = current_dept_label
        init_data["teacher_label"] = current_t_label

        def save(data):
            code = data.get("subject_code", "").strip().upper()
            name = data.get("subject_name", "").strip()
            class_year = data.get("class_year", "").strip()
            dept_label = data.get("dept_label", "").strip()

            if not code or not name:
                raise ValueError("Subject Code and Title are required.")
            dept_id = self.dept_map.get(dept_label)
            if not dept_id:
                raise ValueError("Please select a Department.")
            t_id = self.teacher_map.get(data.get("teacher_label"))

            try:
                credits = int(data.get("credits", 3))
                if credits <= 0 or credits > 10:
                    raise ValueError()
            except Exception:
                raise ValueError("Credits must be a positive integer between 1 and 10.")

            try:
                sem = int(data.get("semester", 5))
                if sem < 1 or sem > 8:
                    raise ValueError()
            except Exception:
                raise ValueError("Semester must be between 1 and 8.")

            sql = """
            UPDATE subjects
            SET subject_code = %s, subject_name = %s, class_year = %s, semester = %s, credits = %s, department_id = %s, teacher_id = %s
            WHERE subject_id = %s
            """
            db.execute_query(sql, (
                code,
                name,
                class_year,
                sem,
                credits,
                dept_id,
                t_id,
                selected["subject_id"]
            ))
            messagebox.showinfo("Success", f"Subject '{name}' updated successfully!")
            self.load_subjects()

        FormModal(self, title="Edit Subject", fields=fields, initial_data=init_data, on_save=save, width=500, submit_text="Save Changes")

    def _handle_delete(self):
        selected = self.table.get_selected_item()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a subject to delete.")
            return

        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete subject '{selected['subject_name']}' ({selected['subject_code']})?\n\nNote: Deletion will be rejected if enrollments or assessments exist."
        )
        if confirm:
            try:
                db.execute_query("DELETE FROM subjects WHERE subject_id = %s", (selected["subject_id"],))
                messagebox.showinfo("Success", "Subject deleted successfully.")
                self.load_subjects()
            except Exception as e:
                messagebox.showerror("Cannot Delete", str(e))
