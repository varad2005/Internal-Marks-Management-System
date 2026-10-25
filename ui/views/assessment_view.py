"""
Assessment Scheme Management View
K.K. Wagh Institute of Engineering Education and Research, Nashik
Department of Computer Engineering | Academic Year 2026-27
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from db import db
from ui.theme import COLORS, FONTS
from ui.components import DataTable, SearchBar, FormModal

class AssessmentView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg_main"])
        self._build_header()
        self._build_toolbar()
        self._build_table()
        self.load_assessments()

    def _build_header(self):
        hdr = tk.Frame(self, bg=COLORS["bg_main"], pady=10)
        hdr.pack(fill="x", padx=20)
        tk.Label(hdr, text="Assessment Scheme Management", font=FONTS["header_title"], bg=COLORS["bg_main"], fg=COLORS["text_dark"]).pack(anchor="w")
        tk.Label(hdr, text="Configure evaluation heads (In-Sem, End-Sem, Unit Tests, Term Work, Practical/Oral) and maximum marks", font=FONTS["caption"], bg=COLORS["bg_main"], fg=COLORS["text_muted"]).pack(anchor="w")

    def _build_toolbar(self):
        toolbar = tk.Frame(self, bg=COLORS["bg_main"])
        toolbar.pack(fill="x", padx=20, pady=(0, 10))

        filters = [
            ("assessment_type", "Type", ["In-Semester", "End-Semester", "Unit Test", "Term Work", "Practical / Oral", "Assignment"])
        ]

        self.search_bar = SearchBar(
            toolbar,
            placeholder="Search assessment name or subject...",
            filters=filters,
            on_search=self._handle_search,
            on_reset=self.load_assessments
        )
        self.search_bar.pack(side="left")

        # Action Buttons
        btn_box = tk.Frame(toolbar, bg=COLORS["bg_main"])
        btn_box.pack(side="right")

        ttk.Button(btn_box, text="➕ Add Assessment", style="Primary.TButton", command=self._open_add_modal).pack(side="left", padx=4)
        ttk.Button(btn_box, text="✏️ Edit", style="Secondary.TButton", command=self._open_edit_modal).pack(side="left", padx=4)
        ttk.Button(btn_box, text="🗑️ Delete", style="Danger.TButton", command=self._handle_delete).pack(side="left", padx=4)

    def _build_table(self):
        tbl_frame = tk.Frame(self, bg=COLORS["bg_main"])
        tbl_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        columns = [
            ("assessment_id", "ID", 45, "center"),
            ("subject_code", "Code", 85, "center"),
            ("subject_name", "Subject", 220, "w"),
            ("assessment_name", "Assessment Name", 170, "w"),
            ("assessment_type", "Evaluation Type", 140, "w"),
            ("max_marks", "Max Marks", 85, "center"),
            ("weightage_percent", "Weight %", 80, "center"),
            ("conducted_date", "Date", 100, "center"),
            ("academic_year", "Academic Year", 110, "center")
        ]
        self.table = DataTable(tbl_frame, columns)
        self.table.pack(fill="both", expand=True)
        self.table.on_double_click(lambda item: self._open_edit_modal())

    def load_assessments(self):
        sql = """
        SELECT 
            a.assessment_id, a.subject_id, sub.subject_code, sub.subject_name,
            a.assessment_name, a.assessment_type, a.max_marks, a.weightage_percent,
            a.conducted_date, a.academic_year
        FROM assessments a
        JOIN subjects sub ON a.subject_id = sub.subject_id
        ORDER BY sub.subject_code ASC, a.assessment_id ASC
        """
        rows = db.fetch_all(sql)
        self.table.set_data(rows)

    def _handle_search(self, keyword, filters):
        conditions = ["1=1"]
        params = []

        if keyword:
            conditions.append("(a.assessment_name LIKE %s OR sub.subject_code LIKE %s OR sub.subject_name LIKE %s)")
            p = f"%{keyword}%"
            params.extend([p, p, p])

        if filters.get("assessment_type") and filters["assessment_type"] != "All":
            conditions.append("a.assessment_type = %s")
            params.append(filters["assessment_type"])

        where_clause = " AND ".join(conditions)
        sql = f"""
        SELECT 
            a.assessment_id, a.subject_id, sub.subject_code, sub.subject_name,
            a.assessment_name, a.assessment_type, a.max_marks, a.weightage_percent,
            a.conducted_date, a.academic_year
        FROM assessments a
        JOIN subjects sub ON a.subject_id = sub.subject_id
        WHERE {where_clause}
        ORDER BY sub.subject_code ASC, a.assessment_id ASC
        """
        rows = db.fetch_all(sql, tuple(params))
        self.table.set_data(rows)

    def _get_form_fields(self):
        sub_rows = db.fetch_all("SELECT subject_id, subject_code, subject_name FROM subjects ORDER BY subject_code")
        self.sub_map = {f"{r['subject_code']} - {r['subject_name']}": r["subject_id"] for r in sub_rows}
        sub_options = list(self.sub_map.keys())

        return [
            {"name": "subject_label", "label": "Subject", "type": "combobox", "options": sub_options, "required": True},
            {"name": "assessment_name", "label": "Assessment Name (e.g., In-Semester Exam)", "type": "text", "required": True},
            {"name": "assessment_type", "label": "Assessment Category", "type": "combobox",
             "options": ["In-Semester", "End-Semester", "Unit Test", "Term Work", "Practical / Oral", "Assignment"],
             "default": "In-Semester", "required": True},
            {"name": "max_marks", "label": "Maximum Marks", "type": "text", "default": "30.00", "required": True},
            {"name": "weightage_percent", "label": "Weightage %", "type": "text", "default": "100.00", "required": True},
            {"name": "conducted_date", "label": "Conducted Date (YYYY-MM-DD)", "type": "text", "default": str(date.today()), "required": False},
            {"name": "academic_year", "label": "Academic Year", "type": "text", "default": "2026-2027", "required": True}
        ]

    def _open_add_modal(self):
        fields = self._get_form_fields()

        def save(data):
            sub_id = self.sub_map.get(data["subject_label"])
            if not sub_id:
                raise ValueError("Please select a valid subject.")
            try:
                max_m = float(data["max_marks"])
                if max_m <= 0:
                    raise ValueError()
            except Exception:
                raise ValueError("Maximum marks must be a positive number greater than zero.")

            try:
                weight = float(data["weightage_percent"])
                if weight <= 0 or weight > 100:
                    raise ValueError()
            except Exception:
                raise ValueError("Weightage percentage must be between 1 and 100.")

            sql = """
            INSERT INTO assessments (subject_id, assessment_name, assessment_type, max_marks, weightage_percent, conducted_date, academic_year)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            db.execute_query(sql, (
                sub_id,
                data["assessment_name"].strip(),
                data["assessment_type"],
                max_m,
                weight,
                data["conducted_date"].strip() or None,
                data["academic_year"].strip()
            ))
            messagebox.showinfo("Success", "Assessment created successfully!")
            self.load_assessments()

        FormModal(self, title="Add Assessment", fields=fields, on_save=save, width=500, submit_text="Add Assessment")

    def _open_edit_modal(self):
        selected = self.table.get_selected_item()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select an assessment to edit.")
            return

        fields = self._get_form_fields()
        current_sub_label = ""
        for k, v in self.sub_map.items():
            if v == int(selected.get("subject_id", 0)) or selected.get("subject_code") in k:
                current_sub_label = k
                break

        init_data = selected.copy()
        init_data["subject_label"] = current_sub_label

        def save(data):
            sub_id = self.sub_map.get(data["subject_label"])
            if not sub_id:
                raise ValueError("Please select a valid subject.")
            try:
                max_m = float(data["max_marks"])
                if max_m <= 0:
                    raise ValueError()
            except Exception:
                raise ValueError("Maximum marks must be a positive number greater than zero.")

            try:
                weight = float(data["weightage_percent"])
                if weight <= 0 or weight > 100:
                    raise ValueError()
            except Exception:
                raise ValueError("Weightage percentage must be between 1 and 100.")

            sql = """
            UPDATE assessments
            SET subject_id = %s, assessment_name = %s, assessment_type = %s, max_marks = %s,
                weightage_percent = %s, conducted_date = %s, academic_year = %s
            WHERE assessment_id = %s
            """
            db.execute_query(sql, (
                sub_id,
                data["assessment_name"].strip(),
                data["assessment_type"],
                max_m,
                weight,
                data["conducted_date"].strip() or None,
                data["academic_year"].strip(),
                selected["assessment_id"]
            ))
            messagebox.showinfo("Success", "Assessment updated successfully!")
            self.load_assessments()

        FormModal(self, title="Edit Assessment", fields=fields, initial_data=init_data, on_save=save, width=500, submit_text="Save Changes")

    def _handle_delete(self):
        selected = self.table.get_selected_item()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select an assessment to delete.")
            return

        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete assessment '{selected['assessment_name']}' for '{selected['subject_name']}'?\n\nWARNING: All student marks recorded for this assessment will be deleted."
        )
        if confirm:
            try:
                db.execute_query("DELETE FROM assessments WHERE assessment_id = %s", (selected["assessment_id"],))
                messagebox.showinfo("Success", "Assessment deleted.")
                self.load_assessments()
            except Exception as e:
                messagebox.showerror("Error", str(e))
