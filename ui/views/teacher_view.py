"""
Teacher Management View
K.K. Wagh Institute of Engineering Education and Research, Nashik
Department of Computer Engineering | Academic Year 2026-27
"""

import tkinter as tk
from tkinter import ttk, messagebox
from db import db
from ui.theme import COLORS, FONTS
from ui.components import DataTable, SearchBar, FormModal

class TeacherView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg_main"])
        self._build_header()
        self._build_toolbar()
        self._build_table()
        self.load_teachers()

    def _build_header(self):
        hdr = tk.Frame(self, bg=COLORS["bg_main"], pady=10)
        hdr.pack(fill="x", padx=20)
        tk.Label(hdr, text="Teacher / Faculty Management", font=FONTS["header_title"], bg=COLORS["bg_main"], fg=COLORS["text_dark"]).pack(anchor="w")
        tk.Label(hdr, text="Manage faculty profiles, designations, and departmental appointments", font=FONTS["caption"], bg=COLORS["bg_main"], fg=COLORS["text_muted"]).pack(anchor="w")

    def _build_toolbar(self):
        toolbar = tk.Frame(self, bg=COLORS["bg_main"])
        toolbar.pack(fill="x", padx=20, pady=(0, 10))

        # Filters: Designation
        filters = [
            ("designation", "Designation", ["Professor", "Associate Professor", "Assistant Professor", "Adjunct Faculty"])
        ]

        self.search_bar = SearchBar(
            toolbar,
            placeholder="Search code, name, email...",
            filters=filters,
            on_search=self._handle_search,
            on_reset=self.load_teachers
        )
        self.search_bar.pack(side="left")

        # Action Buttons
        btn_box = tk.Frame(toolbar, bg=COLORS["bg_main"])
        btn_box.pack(side="right")

        ttk.Button(btn_box, text="➕ Add Teacher", style="Primary.TButton", command=self._open_add_modal).pack(side="left", padx=4)
        ttk.Button(btn_box, text="✏️ Edit", style="Secondary.TButton", command=self._open_edit_modal).pack(side="left", padx=4)
        ttk.Button(btn_box, text="🗑️ Delete", style="Danger.TButton", command=self._handle_delete).pack(side="left", padx=4)

    def _build_table(self):
        tbl_frame = tk.Frame(self, bg=COLORS["bg_main"])
        tbl_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        columns = [
            ("teacher_id", "ID", 50, "center"),
            ("emp_code", "Emp Code", 110, "center"),
            ("full_name", "Full Name", 180, "w"),
            ("designation", "Designation", 170, "w"),
            ("dept_name", "Department", 200, "w"),
            ("email", "Email Address", 210, "w"),
            ("phone", "Contact Phone", 120, "center")
        ]
        self.table = DataTable(tbl_frame, columns)
        self.table.pack(fill="both", expand=True)
        self.table.on_double_click(lambda item: self._open_edit_modal())

    def load_teachers(self):
        """Fetch all teachers with department JOIN."""
        sql = """
        SELECT 
            t.teacher_id, t.emp_code, 
            CONCAT(t.first_name, ' ', t.last_name) AS full_name,
            t.first_name, t.last_name,
            t.designation, d.dept_name, t.department_id,
            t.email, t.phone
        FROM teachers t
        JOIN departments d ON t.department_id = d.department_id
        ORDER BY t.teacher_id ASC
        """
        # SQLite compatibility helper for CONCAT
        if db.active_engine == "sqlite":
            sql = sql.replace("CONCAT(t.first_name, ' ', t.last_name)", "(t.first_name || ' ' || t.last_name)")
        rows = db.fetch_all(sql)
        self.table.set_data(rows)

    def _handle_search(self, keyword, filters):
        """Search and filter teachers using parameterized SQL."""
        conditions = ["1=1"]
        params = []

        if keyword:
            conditions.append("(t.emp_code LIKE %s OR t.first_name LIKE %s OR t.last_name LIKE %s OR t.email LIKE %s)")
            p = f"%{keyword}%"
            params.extend([p, p, p, p])

        if filters.get("designation") and filters["designation"] != "All":
            conditions.append("t.designation = %s")
            params.append(filters["designation"])

        where_clause = " AND ".join(conditions)
        sql = f"""
        SELECT 
            t.teacher_id, t.emp_code, 
            CONCAT(t.first_name, ' ', t.last_name) AS full_name,
            t.first_name, t.last_name,
            t.designation, d.dept_name, t.department_id,
            t.email, t.phone
        FROM teachers t
        JOIN departments d ON t.department_id = d.department_id
        WHERE {where_clause}
        ORDER BY t.teacher_id ASC
        """
        if db.active_engine == "sqlite":
            sql = sql.replace("CONCAT(t.first_name, ' ', t.last_name)", "(t.first_name || ' ' || t.last_name)")

        rows = db.fetch_all(sql, tuple(params))
        self.table.set_data(rows)

    def _get_form_fields(self):
        # Fetch available departments
        dept_rows = db.fetch_all("SELECT department_id, dept_code, dept_name FROM departments ORDER BY dept_code")
        self.dept_map = {f"{r['dept_code']} - {r['dept_name']}": r["department_id"] for r in dept_rows}
        dept_options = list(self.dept_map.keys())

        return [
            {"name": "emp_code", "label": "Employee Code (e.g. T-COMP-105)", "type": "text", "required": True},
            {"name": "first_name", "label": "First Name", "type": "text", "required": True},
            {"name": "last_name", "label": "Last Name", "type": "text", "required": True},
            {"name": "designation", "label": "Designation", "type": "combobox", 
             "options": ["Professor", "Associate Professor", "Assistant Professor", "Adjunct Faculty"], "required": True},
            {"name": "dept_label", "label": "Department", "type": "combobox", "options": dept_options, "required": True},
            {"name": "email", "label": "Email Address", "type": "text", "required": True},
            {"name": "phone", "label": "Phone Number", "type": "text", "required": False}
        ]

    def _open_add_modal(self):
        fields = self._get_form_fields()

        def save(data):
            emp_code = data.get("emp_code", "").strip().upper()
            first_name = data.get("first_name", "").strip().title()
            last_name = data.get("last_name", "").strip().title()
            designation = data.get("designation", "").strip()
            dept_label = data.get("dept_label", "").strip()
            email = data.get("email", "").strip().lower()
            phone = data.get("phone", "").strip()

            if not emp_code:
                raise ValueError("Employee Code is required.")
            if not first_name or not last_name:
                raise ValueError("First Name and Last Name are required.")
            if not designation:
                raise ValueError("Please select a Designation.")
            if not email:
                raise ValueError("Email Address is required.")
            if "@" not in email or "." not in email.split("@")[-1]:
                raise ValueError("Please provide a valid Email Address (e.g. faculty@kkwagh.edu.in).")
            if phone and (not phone.isdigit() or len(phone) < 7 or len(phone) > 15):
                raise ValueError("Phone number must contain between 7 and 15 digits.")

            dept_id = self.dept_map.get(dept_label)
            if not dept_id:
                raise ValueError("Please select a valid Department from the dropdown.")

            sql = """
            INSERT INTO teachers (emp_code, first_name, last_name, designation, department_id, email, phone)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            db.execute_query(sql, (
                emp_code,
                first_name,
                last_name,
                designation,
                dept_id,
                email,
                phone or None
            ))
            messagebox.showinfo("Success", f"Teacher '{first_name} {last_name}' registered successfully!")
            self.load_teachers()

        FormModal(self, title="Add Faculty Member", fields=fields, on_save=save, width=500, submit_text="Add Faculty Member")

    def _open_edit_modal(self):
        selected = self.table.get_selected_item()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a teacher from the table to edit.")
            return

        fields = self._get_form_fields()
        # Find matching dept label
        current_dept_label = ""
        for k, v in self.dept_map.items():
            if v == int(selected.get("department_id", 0)) or selected.get("dept_name") in k:
                current_dept_label = k
                break

        init_data = selected.copy()
        init_data["dept_label"] = current_dept_label

        def save(data):
            emp_code = data.get("emp_code", "").strip().upper()
            first_name = data.get("first_name", "").strip().title()
            last_name = data.get("last_name", "").strip().title()
            designation = data.get("designation", "").strip()
            dept_label = data.get("dept_label", "").strip()
            email = data.get("email", "").strip().lower()
            phone = data.get("phone", "").strip()

            if not emp_code:
                raise ValueError("Employee Code is required.")
            if not first_name or not last_name:
                raise ValueError("First Name and Last Name are required.")
            if not designation:
                raise ValueError("Please select a Designation.")
            if not email:
                raise ValueError("Email Address is required.")
            if "@" not in email or "." not in email.split("@")[-1]:
                raise ValueError("Please provide a valid Email Address (e.g. faculty@kkwagh.edu.in).")
            if phone and (not phone.isdigit() or len(phone) < 7 or len(phone) > 15):
                raise ValueError("Phone number must contain between 7 and 15 digits.")

            dept_id = self.dept_map.get(dept_label)
            if not dept_id:
                raise ValueError("Please select a valid Department from the dropdown.")

            sql = """
            UPDATE teachers
            SET emp_code = %s, first_name = %s, last_name = %s, designation = %s, department_id = %s, email = %s, phone = %s
            WHERE teacher_id = %s
            """
            db.execute_query(sql, (
                emp_code,
                first_name,
                last_name,
                designation,
                dept_id,
                email,
                phone or None,
                selected["teacher_id"]
            ))
            messagebox.showinfo("Success", f"Teacher record for '{first_name} {last_name}' updated successfully!")
            self.load_teachers()

        FormModal(self, title="Edit Faculty Member", fields=fields, initial_data=init_data, on_save=save, width=500, submit_text="Save Changes")

    def _handle_delete(self):
        selected = self.table.get_selected_item()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a teacher to delete.")
            return

        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete teacher '{selected['full_name']}' ({selected['emp_code']})?"
        )
        if confirm:
            try:
                db.execute_query("DELETE FROM teachers WHERE teacher_id = %s", (selected["teacher_id"],))
                messagebox.showinfo("Success", "Teacher deleted successfully.")
                self.load_teachers()
            except Exception as e:
                messagebox.showerror("Cannot Delete", str(e))
