"""
Department Management View
K.K. Wagh Institute of Engineering Education and Research, Nashik
Department of Computer Engineering | Academic Year 2026-27
"""

import tkinter as tk
from tkinter import ttk, messagebox
from db import db
from ui.theme import COLORS, FONTS
from ui.components import DataTable, SearchBar, FormModal

class DepartmentView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg_main"])
        self._build_header()
        self._build_toolbar()
        self._build_table()
        self.load_departments()

    def _build_header(self):
        hdr = tk.Frame(self, bg=COLORS["bg_main"], pady=10)
        hdr.pack(fill="x", padx=20)
        tk.Label(hdr, text="Department Management", font=FONTS["header_title"], bg=COLORS["bg_main"], fg=COLORS["text_dark"]).pack(anchor="w")
        tk.Label(hdr, text="Manage academic departments, intake capacity, and heads of department", font=FONTS["caption"], bg=COLORS["bg_main"], fg=COLORS["text_muted"]).pack(anchor="w")

    def _build_toolbar(self):
        toolbar = tk.Frame(self, bg=COLORS["bg_main"])
        toolbar.pack(fill="x", padx=20, pady=(0, 10))

        # Search bar
        self.search_bar = SearchBar(
            toolbar,
            placeholder="Search code, name, HOD...",
            on_search=self._handle_search,
            on_reset=self.load_departments
        )
        self.search_bar.pack(side="left")

        # Action Buttons
        btn_box = tk.Frame(toolbar, bg=COLORS["bg_main"])
        btn_box.pack(side="right")

        ttk.Button(btn_box, text="➕ Add Department", style="Primary.TButton", command=self._open_add_modal).pack(side="left", padx=4)
        ttk.Button(btn_box, text="✏️ Edit", style="Secondary.TButton", command=self._open_edit_modal).pack(side="left", padx=4)
        ttk.Button(btn_box, text="🗑️ Delete", style="Danger.TButton", command=self._handle_delete).pack(side="left", padx=4)

    def _build_table(self):
        tbl_frame = tk.Frame(self, bg=COLORS["bg_main"])
        tbl_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        columns = [
            ("department_id", "ID", 60, "center"),
            ("dept_code", "Code", 100, "center"),
            ("dept_name", "Department Name", 250, "w"),
            ("intake_capacity", "Intake Capacity", 120, "center"),
            ("hod_name", "Head of Department (HOD)", 220, "w"),
            ("established_year", "Est. Year", 100, "center")
        ]
        self.table = DataTable(tbl_frame, columns)
        self.table.pack(fill="both", expand=True)
        self.table.on_double_click(lambda item: self._open_edit_modal())

    def load_departments(self):
        """Fetch all departments ordered by ID."""
        sql = "SELECT department_id, dept_code, dept_name, intake_capacity, hod_name, established_year FROM departments ORDER BY department_id ASC"
        rows = db.fetch_all(sql)
        self.table.set_data(rows)

    def _handle_search(self, keyword, filters):
        """Search departments by code, name, or HOD."""
        sql = """
        SELECT department_id, dept_code, dept_name, intake_capacity, hod_name, established_year 
        FROM departments 
        WHERE dept_code LIKE %s OR dept_name LIKE %s OR hod_name LIKE %s
        ORDER BY department_id ASC
        """
        param = f"%{keyword}%"
        rows = db.fetch_all(sql, (param, param, param))
        self.table.set_data(rows)

    def _get_form_fields(self):
        return [
            {"name": "dept_code", "label": "Department Code (e.g., COMP)", "type": "text", "required": True},
            {"name": "dept_name", "label": "Department Name", "type": "text", "required": True},
            {"name": "intake_capacity", "label": "Intake Capacity", "type": "text", "default": "180", "required": True},
            {"name": "hod_name", "label": "HOD Name", "type": "text", "required": True},
            {"name": "established_year", "label": "Established Year", "type": "text", "default": "1984", "required": True}
        ]

    def _open_add_modal(self):
        def save(data):
            code = data.get("dept_code", "").strip().upper()
            name = data.get("dept_name", "").strip()
            hod = data.get("hod_name", "").strip()

            if not code or not name:
                raise ValueError("Department Code and Name are required.")
            if not hod:
                raise ValueError("Head of Department (HOD) Name is required.")

            try:
                intake = int(data.get("intake_capacity", 0))
                if intake <= 0:
                    raise ValueError()
            except Exception:
                raise ValueError("Intake capacity must be a positive integer greater than zero.")

            try:
                est_year = int(data.get("established_year", 1984))
                if est_year < 1950 or est_year > 2030:
                    raise ValueError()
            except Exception:
                raise ValueError("Established year must be a valid 4-digit year (e.g. 1984).")

            sql = """
            INSERT INTO departments (dept_code, dept_name, intake_capacity, hod_name, established_year)
            VALUES (%s, %s, %s, %s, %s)
            """
            db.execute_query(sql, (code, name, intake, hod, est_year))
            messagebox.showinfo("Success", f"Department '{name}' added successfully!")
            self.load_departments()

        FormModal(self, title="Add Department", fields=self._get_form_fields(), on_save=save, width=500, submit_text="Add Department")

    def _open_edit_modal(self):
        selected = self.table.get_selected_item()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a department from the table to edit.")
            return

        def save(data):
            code = data.get("dept_code", "").strip().upper()
            name = data.get("dept_name", "").strip()
            hod = data.get("hod_name", "").strip()

            if not code or not name:
                raise ValueError("Department Code and Name are required.")
            if not hod:
                raise ValueError("Head of Department (HOD) Name is required.")

            try:
                intake = int(data.get("intake_capacity", 0))
                if intake <= 0:
                    raise ValueError()
            except Exception:
                raise ValueError("Intake capacity must be a positive integer greater than zero.")

            try:
                est_year = int(data.get("established_year", 1984))
                if est_year < 1950 or est_year > 2030:
                    raise ValueError()
            except Exception:
                raise ValueError("Established year must be a valid 4-digit year (e.g. 1984).")

            sql = """
            UPDATE departments 
            SET dept_code = %s, dept_name = %s, intake_capacity = %s, hod_name = %s, established_year = %s
            WHERE department_id = %s
            """
            db.execute_query(sql, (
                code,
                name,
                intake,
                hod,
                est_year,
                selected["department_id"]
            ))
            messagebox.showinfo("Success", f"Department '{name}' updated successfully!")
            self.load_departments()

        FormModal(self, title="Edit Department", fields=self._get_form_fields(), initial_data=selected, on_save=save, width=500, submit_text="Save Changes")

    def _handle_delete(self):
        selected = self.table.get_selected_item()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a department to delete.")
            return

        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete department '{selected['dept_name']}' ({selected['dept_code']})?\n\nNote: If students or teachers are associated, the database will block deletion."
        )
        if confirm:
            try:
                db.execute_query("DELETE FROM departments WHERE department_id = %s", (selected["department_id"],))
                messagebox.showinfo("Success", "Department deleted successfully.")
                self.load_departments()
            except Exception as e:
                messagebox.showerror("Cannot Delete", str(e))
