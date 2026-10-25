"""
Student Management View
K.K. Wagh Institute of Engineering Education and Research, Nashik
Department of Computer Engineering | Academic Year 2026-27
"""

import tkinter as tk
from tkinter import ttk, messagebox
from db import db
from ui.theme import COLORS, FONTS
from ui.components import DataTable, SearchBar, FormModal

class StudentView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg_main"])
        self._build_header()
        self._build_toolbar()
        self._build_table()
        self.load_students()

    def _build_header(self):
        hdr = tk.Frame(self, bg=COLORS["bg_main"], pady=10)
        hdr.pack(fill="x", padx=20)
        tk.Label(hdr, text="Student Management", font=FONTS["header_title"], bg=COLORS["bg_main"], fg=COLORS["text_dark"]).pack(anchor="w")
        tk.Label(hdr, text="Maintain student profiles, PRN identity, class division, and roll numbers", font=FONTS["caption"], bg=COLORS["bg_main"], fg=COLORS["text_muted"]).pack(anchor="w")

    def _build_toolbar(self):
        toolbar = tk.Frame(self, bg=COLORS["bg_main"])
        toolbar.pack(fill="x", padx=20, pady=(0, 10))

        filters = [
            ("class_year", "Class", ["FE", "SE", "TE", "BE"]),
            ("division", "Division", ["A", "B", "C", "D"])
        ]

        self.search_bar = SearchBar(
            toolbar,
            placeholder="Search PRN, roll no, name...",
            filters=filters,
            on_search=self._handle_search,
            on_reset=self.load_students
        )
        self.search_bar.pack(side="left")

        # Action Buttons
        btn_box = tk.Frame(toolbar, bg=COLORS["bg_main"])
        btn_box.pack(side="right")

        ttk.Button(btn_box, text="➕ Add Student", style="Primary.TButton", command=self._open_add_modal).pack(side="left", padx=4)
        ttk.Button(btn_box, text="✏️ Edit", style="Secondary.TButton", command=self._open_edit_modal).pack(side="left", padx=4)
        ttk.Button(btn_box, text="🗑️ Delete", style="Danger.TButton", command=self._handle_delete).pack(side="left", padx=4)

    def _build_table(self):
        tbl_frame = tk.Frame(self, bg=COLORS["bg_main"])
        tbl_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        columns = [
            ("student_id", "ID", 45, "center"),
            ("prn", "PRN", 110, "center"),
            ("roll_no", "Roll No", 110, "center"),
            ("full_name", "Student Name", 180, "w"),
            ("class_year", "Class", 60, "center"),
            ("division", "Div", 50, "center"),
            ("dept_name", "Department", 180, "w"),
            ("email", "Email Address", 200, "w"),
            ("phone", "Phone", 110, "center")
        ]
        self.table = DataTable(tbl_frame, columns)
        self.table.pack(fill="both", expand=True)
        self.table.on_double_click(lambda item: self._open_edit_modal())

    def load_students(self):
        """Fetch all students with department name."""
        sql = """
        SELECT 
            s.student_id, s.prn, s.roll_no,
            CONCAT(s.first_name, ' ', s.last_name) AS full_name,
            s.first_name, s.last_name,
            s.class_year, s.division, d.dept_name, s.department_id,
            s.email, s.phone, s.admission_year
        FROM students s
        JOIN departments d ON s.department_id = d.department_id
        ORDER BY s.class_year DESC, s.division ASC, s.roll_no ASC
        """
        if db.active_engine == "sqlite":
            sql = sql.replace("CONCAT(s.first_name, ' ', s.last_name)", "(s.first_name || ' ' || s.last_name)")
        rows = db.fetch_all(sql)
        self.table.set_data(rows)

    def _handle_search(self, keyword, filters):
        conditions = ["1=1"]
        params = []

        if keyword:
            conditions.append("(s.prn LIKE %s OR s.roll_no LIKE %s OR s.first_name LIKE %s OR s.last_name LIKE %s OR s.email LIKE %s)")
            p = f"%{keyword}%"
            params.extend([p, p, p, p, p])

        if filters.get("class_year") and filters["class_year"] != "All":
            conditions.append("s.class_year = %s")
            params.append(filters["class_year"])

        if filters.get("division") and filters["division"] != "All":
            conditions.append("s.division = %s")
            params.append(filters["division"])

        where_clause = " AND ".join(conditions)
        sql = f"""
        SELECT 
            s.student_id, s.prn, s.roll_no,
            CONCAT(s.first_name, ' ', s.last_name) AS full_name,
            s.first_name, s.last_name,
            s.class_year, s.division, d.dept_name, s.department_id,
            s.email, s.phone, s.admission_year
        FROM students s
        JOIN departments d ON s.department_id = d.department_id
        WHERE {where_clause}
        ORDER BY s.class_year DESC, s.division ASC, s.roll_no ASC
        """
        if db.active_engine == "sqlite":
            sql = sql.replace("CONCAT(s.first_name, ' ', s.last_name)", "(s.first_name || ' ' || s.last_name)")

        rows = db.fetch_all(sql, tuple(params))
        self.table.set_data(rows)

    def _get_form_fields(self):
        dept_rows = db.fetch_all("SELECT department_id, dept_code, dept_name FROM departments ORDER BY dept_code")
        self.dept_map = {f"{r['dept_code']} - {r['dept_name']}": r["department_id"] for r in dept_rows}
        dept_options = list(self.dept_map.keys())

        adm_options = ["2027", "2026", "2025", "2024", "2023", "2022", "2021"]

        return [
            {"name": "prn", "label": "PRN (e.g. 72210019I)", "type": "text", "hint": "Permanent Registration Number (University PRN)", "required": True},
            {"name": "roll_no", "label": "Roll Number (e.g. TE-COMP-09)", "type": "text", "hint": "Format: [Year]-[Dept]-[RollNo] or Class Roll No", "required": True},
            {"name": "first_name", "label": "First Name", "type": "text", "required": True},
            {"name": "last_name", "label": "Last Name", "type": "text", "required": True},
            {"name": "class_year", "label": "Class Year", "type": "combobox", "options": ["FE", "SE", "TE", "BE"], "default": "TE", "required": True},
            {"name": "division", "label": "Division", "type": "combobox", "options": ["A", "B", "C", "D"], "default": "A", "required": True},
            {"name": "dept_label", "label": "Department", "type": "combobox", "options": dept_options, "required": True},
            {"name": "email", "label": "College Email Address", "type": "text", "hint": "Institutional email (e.g. name@kkwagh.edu.in)", "required": True},
            {"name": "phone", "label": "Contact Phone Number", "type": "text", "hint": "10-digit mobile number (optional)", "required": False},
            {"name": "admission_year", "label": "Admission Year", "type": "combobox", "options": adm_options, "default": "2024", "editable": True, "required": True}
        ]

    def _open_add_modal(self):
        fields = self._get_form_fields()

        def save(data):
            prn = data.get("prn", "").strip().upper()
            roll_no = data.get("roll_no", "").strip().upper()
            first_name = data.get("first_name", "").strip().title()
            last_name = data.get("last_name", "").strip().title()
            class_year = data.get("class_year", "").strip()
            division = data.get("division", "").strip()
            dept_label = data.get("dept_label", "").strip()
            email = data.get("email", "").strip().lower()
            phone = data.get("phone", "").strip()
            adm_year_str = str(data.get("admission_year", "")).strip()

            if not prn:
                raise ValueError("PRN (Permanent Registration Number) is required.")
            if not roll_no:
                raise ValueError("Roll Number is required.")
            if not first_name:
                raise ValueError("First Name is required.")
            if not last_name:
                raise ValueError("Last Name is required.")
            if not email:
                raise ValueError("College Email Address is required.")
            if "@" not in email or "." not in email.split("@")[-1]:
                raise ValueError("Please provide a valid College Email address (e.g. student@kkwagh.edu.in).")
            if phone and (not phone.isdigit() or len(phone) < 7 or len(phone) > 15):
                raise ValueError("Contact phone must contain between 7 and 15 digits.")
            try:
                adm_year = int(adm_year_str)
                if adm_year < 1980 or adm_year > 2050:
                    raise ValueError()
            except Exception:
                raise ValueError("Admission Year must be a valid 4-digit number (e.g. 2024).")

            dept_id = self.dept_map.get(dept_label)
            if not dept_id:
                raise ValueError("Please select a valid Department from the dropdown.")

            sql = """
            INSERT INTO students (prn, roll_no, first_name, last_name, class_year, division, department_id, email, phone, admission_year)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            db.execute_query(sql, (
                prn,
                roll_no,
                first_name,
                last_name,
                class_year,
                division,
                dept_id,
                email,
                phone or None,
                adm_year
            ))
            messagebox.showinfo("Success", f"Student '{first_name} {last_name}' registered successfully!")
            self.load_students()

        FormModal(self, title="Register Student", fields=fields, on_save=save, width=520, submit_text="Register Student")

    def _open_edit_modal(self):
        selected = self.table.get_selected_item()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a student to edit.")
            return

        fields = self._get_form_fields()
        current_dept_label = ""
        for k, v in self.dept_map.items():
            if v == int(selected.get("department_id", 0)) or selected.get("dept_name") in k:
                current_dept_label = k
                break

        init_data = selected.copy()
        init_data["dept_label"] = current_dept_label

        def save(data):
            prn = data.get("prn", "").strip().upper()
            roll_no = data.get("roll_no", "").strip().upper()
            first_name = data.get("first_name", "").strip().title()
            last_name = data.get("last_name", "").strip().title()
            class_year = data.get("class_year", "").strip()
            division = data.get("division", "").strip()
            dept_label = data.get("dept_label", "").strip()
            email = data.get("email", "").strip().lower()
            phone = data.get("phone", "").strip()
            adm_year_str = str(data.get("admission_year", "")).strip()

            if not prn:
                raise ValueError("PRN is required.")
            if not roll_no:
                raise ValueError("Roll Number is required.")
            if not first_name:
                raise ValueError("First Name is required.")
            if not last_name:
                raise ValueError("Last Name is required.")
            if not email:
                raise ValueError("College Email Address is required.")
            if "@" not in email or "." not in email.split("@")[-1]:
                raise ValueError("Please provide a valid College Email address (e.g. student@kkwagh.edu.in).")
            if phone and (not phone.isdigit() or len(phone) < 7 or len(phone) > 15):
                raise ValueError("Contact phone must contain between 7 and 15 digits.")
            try:
                adm_year = int(adm_year_str)
                if adm_year < 1980 or adm_year > 2050:
                    raise ValueError()
            except Exception:
                raise ValueError("Admission Year must be a valid 4-digit number (e.g. 2024).")

            dept_id = self.dept_map.get(dept_label)
            if not dept_id:
                raise ValueError("Please select a valid Department from the dropdown.")

            sql = """
            UPDATE students
            SET prn = %s, roll_no = %s, first_name = %s, last_name = %s, class_year = %s, division = %s,
                department_id = %s, email = %s, phone = %s, admission_year = %s
            WHERE student_id = %s
            """
            db.execute_query(sql, (
                prn,
                roll_no,
                first_name,
                last_name,
                class_year,
                division,
                dept_id,
                email,
                phone or None,
                adm_year,
                selected["student_id"]
            ))
            messagebox.showinfo("Success", f"Student record for '{first_name} {last_name}' updated successfully!")
            self.load_students()

        FormModal(self, title="Edit Student Profile", fields=fields, initial_data=init_data, on_save=save, width=520, submit_text="Save Changes")

    def _handle_delete(self):
        selected = self.table.get_selected_item()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a student to delete.")
            return

        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete student '{selected['full_name']}' ({selected['prn']})?\n\nWARNING: Deleting a student will also remove their course enrollments and recorded marks."
        )
        if confirm:
            try:
                db.execute_query("DELETE FROM students WHERE student_id = %s", (selected["student_id"],))
                messagebox.showinfo("Success", "Student and associated records deleted.")
                self.load_students()
            except Exception as e:
                messagebox.showerror("Cannot Delete", str(e))
