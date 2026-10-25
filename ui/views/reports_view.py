"""
Reports Generation Module (Student Marksheet, Subject Performance, Class Analytics)
K.K. Wagh Institute of Engineering Education and Research, Nashik
Department of Computer Engineering | Academic Year 2026-27
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from db import db
from ui.theme import COLORS, FONTS
from ui.components import DataTable, StatCard

class ReportsView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg_main"])
        self._build_header()
        self._build_notebook()

    def _build_header(self):
        hdr = tk.Frame(self, bg=COLORS["bg_main"], pady=10)
        hdr.pack(fill="x", padx=20)
        tk.Label(hdr, text="Academic Performance Reports & Marksheets", font=FONTS["header_title"], bg=COLORS["bg_main"], fg=COLORS["text_dark"]).pack(anchor="w")
        tk.Label(hdr, text="Analytical DBMS reports demonstrating complex multi-table JOINs, GROUP BY aggregations, and performance rankings", font=FONTS["caption"], bg=COLORS["bg_main"], fg=COLORS["text_muted"]).pack(anchor="w")

    def _build_notebook(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Tab 1: Student Marksheet
        self.tab_marksheet = tk.Frame(self.notebook, bg=COLORS["bg_main"])
        self.notebook.add(self.tab_marksheet, text=" 📜 Student-wise Marksheet ")
        self._setup_marksheet_tab()

        # Tab 2: Subject-wise Performance Report
        self.tab_subject = tk.Frame(self.notebook, bg=COLORS["bg_main"])
        self.notebook.add(self.tab_subject, text=" 📊 Subject-wise Report ")
        self._setup_subject_tab()

        # Tab 3: Class Performance Report
        self.tab_class = tk.Frame(self.notebook, bg=COLORS["bg_main"])
        self.notebook.add(self.tab_class, text=" 🏛️ Class Performance & Analytics ")
        self._setup_class_tab()

    # =========================================================================
    # TAB 1: Student-wise Marksheet
    # =========================================================================
    def _setup_marksheet_tab(self):
        bar = tk.Frame(self.tab_marksheet, bg=COLORS["bg_card"], bd=1, relief="solid", padx=16, pady=10)
        bar.pack(fill="x", padx=10, pady=10)

        tk.Label(bar, text="Select Student:", bg=COLORS["bg_card"], font=FONTS["body_bold"]).pack(side="left", padx=(0, 10))
        self.ms_student_var = tk.StringVar()
        self.cb_ms_student = ttk.Combobox(bar, textvariable=self.ms_student_var, state="readonly", width=45)
        self.cb_ms_student.pack(side="left", padx=(0, 15))
        self.cb_ms_student.bind("<<ComboboxSelected>>", lambda e: self.generate_student_marksheet())

        ttk.Button(bar, text="Generate Marksheet", style="Primary.TButton", command=self.generate_student_marksheet).pack(side="left", padx=4)
        ttk.Button(bar, text="💾 Export Marksheet", style="Secondary.TButton", command=self._export_marksheet).pack(side="right")

        # Student Profile Card
        self.ms_profile_frame = tk.Frame(self.tab_marksheet, bg=COLORS["bg_card"], bd=1, relief="solid", padx=16, pady=10)
        self.ms_profile_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.lbl_ms_name = tk.Label(self.ms_profile_frame, text="Student: —", font=FONTS["section_title"], bg=COLORS["bg_card"], fg=COLORS["text_dark"])
        self.lbl_ms_name.pack(anchor="w")

        self.lbl_ms_meta = tk.Label(self.ms_profile_frame, text="PRN: — | Roll No: — | Class: — | Dept: —", font=FONTS["body"], bg=COLORS["bg_card"], fg=COLORS["text_muted"])
        self.lbl_ms_meta.pack(anchor="w", pady=(2, 0))

        # Marksheet Table
        columns = [
            ("subject_code", "Code", 85, "center"),
            ("subject_name", "Course Name", 240, "w"),
            ("assessment_name", "Evaluation Head", 170, "w"),
            ("assessment_type", "Type", 110, "center"),
            ("marks_obtained", "Scored", 80, "center"),
            ("max_marks", "Max", 75, "center"),
            ("percentage", "Pct", 80, "center"),
            ("result_status", "Status", 80, "center")
        ]
        self.ms_table = DataTable(self.tab_marksheet, columns)
        self.ms_table.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Summary KPIs footer
        self.ms_footer = tk.Frame(self.tab_marksheet, bg=COLORS["bg_card"], bd=1, relief="solid", padx=16, pady=12)
        self.ms_footer.pack(fill="x", padx=10, pady=(0, 10))

        self.lbl_ms_summary = tk.Label(
            self.ms_footer,
            text="Aggregate Score: — / — | Percentage: —% | Class Classification: —",
            font=FONTS["body_bold"],
            bg=COLORS["bg_card"],
            fg=COLORS["primary"]
        )
        self.lbl_ms_summary.pack(side="left")

        self.load_marksheet_students()

    def load_marksheet_students(self):
        sql = "SELECT student_id, prn, roll_no, first_name, last_name, class_year, division FROM students ORDER BY class_year DESC, roll_no ASC"
        rows = db.fetch_all(sql)
        self.ms_students_map = {
            f"{r['roll_no']} - {r['first_name']} {r['last_name']} ({r['prn']})": r
            for r in rows
        }
        self.cb_ms_student["values"] = list(self.ms_students_map.keys())
        if rows:
            self.cb_ms_student.current(0)
            self.generate_student_marksheet()

    def generate_student_marksheet(self):
        st_data = self.ms_students_map.get(self.ms_student_var.get())
        if not st_data:
            return

        st_id = st_data["student_id"]
        # Query using view vw_student_marks_detailed (or JOINs)
        sql = """
        SELECT 
            m.mark_id, s.prn, s.roll_no,
            CONCAT(s.first_name, ' ', s.last_name) AS student_name,
            s.class_year, s.division, d.dept_name,
            sub.subject_code, sub.subject_name,
            a.assessment_name, a.assessment_type, a.max_marks,
            m.marks_obtained, m.is_absent,
            ROUND((m.marks_obtained / a.max_marks) * 100, 2) AS percentage,
            CASE 
                WHEN m.is_absent = 1 OR m.is_absent = TRUE THEN 'Absent'
                WHEN (m.marks_obtained / a.max_marks) >= 0.40 THEN 'Pass'
                ELSE 'Fail'
            END AS result_status
        FROM marks m
        JOIN enrollments e ON m.enrollment_id = e.enrollment_id
        JOIN students s ON e.student_id = s.student_id
        JOIN departments d ON s.department_id = d.department_id
        JOIN assessments a ON m.assessment_id = a.assessment_id
        JOIN subjects sub ON a.subject_id = sub.subject_id
        WHERE s.student_id = %s
        ORDER BY sub.subject_code ASC, a.assessment_id ASC;
        """
        if db.active_engine == "sqlite":
            sql = sql.replace("CONCAT(s.first_name, ' ', s.last_name)", "(s.first_name || ' ' || s.last_name)")

        rows = db.fetch_all(sql, (st_id,))
        self.current_marksheet_rows = rows
        self.current_marksheet_student = st_data

        # Update profile header
        dept_name = rows[0]["dept_name"] if rows else "Computer Engineering"
        self.lbl_ms_name.config(text=f"Student Marksheet: {st_data['first_name']} {st_data['last_name']}")
        self.lbl_ms_meta.config(text=f"PRN: {st_data['prn']} | Roll No: {st_data['roll_no']} | Class: {st_data['class_year']} Div {st_data['division']} | Department: {dept_name}")

        self.ms_table.set_data(rows)

        if rows:
            total_obtained = sum(float(r["marks_obtained"]) for r in rows)
            total_max = sum(float(r["max_marks"]) for r in rows)
            overall_pct = round((total_obtained / total_max) * 100, 2) if total_max > 0 else 0.0

            has_fail = any(r["result_status"] in ("Fail", "Absent") for r in rows)
            if has_fail:
                res_class = "FAILED / BACKLOG SUBJECTS"
                color = COLORS["danger"]
            elif overall_pct >= 75.0:
                res_class = "FIRST CLASS WITH DISTINCTION ⭐"
                color = COLORS["success"]
            elif overall_pct >= 60.0:
                res_class = "FIRST CLASS"
                color = COLORS["primary"]
            elif overall_pct >= 55.0:
                res_class = "HIGHER SECOND CLASS"
                color = COLORS["primary"]
            elif overall_pct >= 50.0:
                res_class = "SECOND CLASS"
                color = COLORS["text_dark"]
            else:
                res_class = "PASS CLASS"
                color = COLORS["text_dark"]

            self.lbl_ms_summary.config(
                text=f"Aggregate Score: {total_obtained:.2f} / {total_max:.2f}  |  Percentage: {overall_pct:.2f}%  |  Classification: {res_class}",
                fg=color
            )
        else:
            self.lbl_ms_summary.config(text="No marks records evaluated yet for this student.", fg=COLORS["text_muted"])

    def _export_marksheet(self):
        if not getattr(self, "current_marksheet_rows", None):
            messagebox.showinfo("Export", "No marksheet data to export.")
            return

        st = self.current_marksheet_student
        filename = f"Marksheet_{st['roll_no']}_{st['prn']}.txt"
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile=filename,
            filetypes=[("Text File", "*.txt")]
        )
        if not filepath:
            return

        total_obtained = sum(float(r["marks_obtained"]) for r in self.current_marksheet_rows)
        total_max = sum(float(r["max_marks"]) for r in self.current_marksheet_rows)
        overall_pct = round((total_obtained / total_max) * 100, 2) if total_max > 0 else 0.0

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write("    K.K. WAGH INSTITUTE OF ENGINEERING EDUCATION AND RESEARCH, NASHIK\n")
            f.write("               DEPARTMENT OF COMPUTER ENGINEERING\n")
            f.write("             STUDENT INTERNAL MARKSHEET (AY 2026-27)\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Student Name : {st['first_name']} {st['last_name']}\n")
            f.write(f"PRN          : {st['prn']}\n")
            f.write(f"Roll Number  : {st['roll_no']}\n")
            f.write(f"Class & Div  : {st['class_year']} - Division {st['division']}\n")
            f.write(f"Generated On : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("-" * 80 + "\n")
            f.write(f"{'Code':<10} {'Subject Name':<30} {'Assessment':<18} {'Scored':<8} {'Max':<8} {'Pct %':<8} {'Status'}\n")
            f.write("-" * 80 + "\n")

            for r in self.current_marksheet_rows:
                f.write(f"{r['subject_code']:<10} {r['subject_name'][:28]:<30} {r['assessment_name'][:16]:<18} {float(r['marks_obtained']):<8.2f} {float(r['max_marks']):<8.2f} {float(r['percentage']):<8.2f} {r['result_status']}\n")

            f.write("-" * 80 + "\n")
            f.write(f"TOTAL MARKS  : {total_obtained:.2f} / {total_max:.2f}\n")
            f.write(f"PERCENTAGE   : {overall_pct:.2f}%\n")
            f.write("=" * 80 + "\n")
            f.write("                  Verified By: Faculty In-Charge / HOD Computer\n")

        messagebox.showinfo("Export Successful", f"Marksheet saved successfully to:\n{filepath}")

    # =========================================================================
    # TAB 2: Subject-wise Performance Report
    # =========================================================================
    def _setup_subject_tab(self):
        bar = tk.Frame(self.tab_subject, bg=COLORS["bg_card"], bd=1, relief="solid", padx=16, pady=10)
        bar.pack(fill="x", padx=10, pady=10)

        # Subject Select
        tk.Label(bar, text="Subject:", bg=COLORS["bg_card"], font=FONTS["body_bold"]).pack(side="left", padx=(0, 6))
        self.sub_rep_var = tk.StringVar()
        self.cb_sub_rep = ttk.Combobox(bar, textvariable=self.sub_rep_var, state="readonly", width=36)
        self.cb_sub_rep.pack(side="left", padx=(0, 15))
        self.cb_sub_rep.bind("<<ComboboxSelected>>", self._on_sub_report_changed)

        # Assessment Select
        tk.Label(bar, text="Assessment:", bg=COLORS["bg_card"], font=FONTS["body_bold"]).pack(side="left", padx=(0, 6))
        self.ass_rep_var = tk.StringVar()
        self.cb_ass_rep = ttk.Combobox(bar, textvariable=self.ass_rep_var, state="readonly", width=28)
        self.cb_ass_rep.pack(side="left", padx=(0, 15))
        self.cb_ass_rep.bind("<<ComboboxSelected>>", lambda e: self.generate_subject_report())

        ttk.Button(bar, text="Generate Report", style="Primary.TButton", command=self.generate_subject_report).pack(side="left", padx=4)
        ttk.Button(bar, text="💾 Export Report", style="Secondary.TButton", command=self._export_subject_report).pack(side="right")

        # KPI Stats row
        self.sub_kpi_frame = tk.Frame(self.tab_subject, bg=COLORS["bg_main"])
        self.sub_kpi_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.kpi_appeared = StatCard(self.sub_kpi_frame, "Appeared", "0", "Students evaluated", accent_color="#2563EB")
        self.kpi_appeared.pack(side="left", fill="both", expand=True, padx=(0, 8))

        self.kpi_pass_pct = StatCard(self.sub_kpi_frame, "Pass Rate", "0%", "Passed assessment", accent_color="#16A34A")
        self.kpi_pass_pct.pack(side="left", fill="both", expand=True, padx=(0, 8))

        self.kpi_avg = StatCard(self.sub_kpi_frame, "Average Marks", "0.0", "Class mean", accent_color="#0D9488")
        self.kpi_avg.pack(side="left", fill="both", expand=True, padx=(0, 8))

        self.kpi_high = StatCard(self.sub_kpi_frame, "Highest / Lowest", "0 / 0", "Score extremes", accent_color="#D97706")
        self.kpi_high.pack(side="left", fill="both", expand=True)

        # Table
        cols = [
            ("roll_no", "Roll No", 100, "center"),
            ("prn", "PRN", 110, "center"),
            ("student_name", "Student Name", 200, "w"),
            ("class_div", "Class & Div", 90, "center"),
            ("marks_obtained", "Marks Scored", 90, "center"),
            ("max_marks", "Max Marks", 80, "center"),
            ("percentage", "Percentage", 85, "center"),
            ("status", "Status", 80, "center"),
            ("remarks", "Remarks", 200, "w")
        ]
        self.sub_table = DataTable(self.tab_subject, cols)
        self.sub_table.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.load_subject_report_filters()

    def load_subject_report_filters(self):
        sub_sql = "SELECT subject_id, subject_code, subject_name FROM subjects ORDER BY subject_code"
        rows = db.fetch_all(sub_sql)
        self.sub_rep_map = {f"{r['subject_code']} - {r['subject_name']}": r["subject_id"] for r in rows}
        self.cb_sub_rep["values"] = list(self.sub_rep_map.keys())
        if rows:
            self.cb_sub_rep.current(0)
            self._on_sub_report_changed()

    def _on_sub_report_changed(self, event=None):
        sub_id = self.sub_rep_map.get(self.sub_rep_var.get())
        if not sub_id:
            return

        ass_sql = "SELECT assessment_id, assessment_name, max_marks FROM assessments WHERE subject_id = %s ORDER BY assessment_id"
        ass_rows = db.fetch_all(ass_sql, (sub_id,))
        self.ass_rep_map = {f"{r['assessment_name']} (Max: {r['max_marks']})": r for r in ass_rows}
        self.cb_ass_rep["values"] = list(self.ass_rep_map.keys())
        if ass_rows:
            self.cb_ass_rep.current(0)
            self.generate_subject_report()
        else:
            self.ass_rep_var.set("")
            self.sub_table.clear()

    def generate_subject_report(self):
        ass_data = self.ass_rep_map.get(self.ass_rep_var.get())
        if not ass_data:
            return

        ass_id = ass_data["assessment_id"]
        max_m = float(ass_data["max_marks"])

        # Complex SQL Query demonstrating GROUP BY and Aggregates
        agg_sql = """
        SELECT 
            COUNT(m.mark_id) AS total_appeared,
            SUM(CASE WHEN m.is_absent = 0 AND (m.marks_obtained / %s) >= 0.40 THEN 1 ELSE 0 END) AS passed_count,
            SUM(CASE WHEN m.is_absent = 0 AND (m.marks_obtained / %s) < 0.40 THEN 1 ELSE 0 END) AS failed_count,
            SUM(CASE WHEN m.is_absent = 1 THEN 1 ELSE 0 END) AS absent_count,
            ROUND(AVG(CASE WHEN m.is_absent = 0 THEN m.marks_obtained ELSE NULL END), 2) AS avg_marks,
            MAX(CASE WHEN m.is_absent = 0 THEN m.marks_obtained ELSE NULL END) AS max_marks_val,
            MIN(CASE WHEN m.is_absent = 0 THEN m.marks_obtained ELSE NULL END) AS min_marks_val
        FROM marks m
        WHERE m.assessment_id = %s;
        """
        agg = db.fetch_one(agg_sql, (max_m, max_m, ass_id))

        if agg and agg["total_appeared"]:
            appeared = agg["total_appeared"]
            passed = agg["passed_count"] or 0
            failed = agg["failed_count"] or 0
            absent = agg["absent_count"] or 0
            avg_val = agg["avg_marks"] or 0.0
            max_val = agg["max_marks_val"] or 0.0
            min_val = agg["min_marks_val"] or 0.0
            pass_rate = round((passed / (appeared - absent)) * 100, 2) if (appeared - absent) > 0 else 0.0

            self.kpi_appeared.update_value(appeared, f"Passed: {passed} | Failed: {failed} | Absent: {absent}")
            self.kpi_pass_pct.update_value(f"{pass_rate}%", f"{passed} of {appeared - absent} candidates")
            self.kpi_avg.update_value(f"{avg_val:.2f}", f"Out of {max_m:.2f}")
            self.kpi_high.update_value(f"{max_val:.2f} / {min_val:.2f}", "Top / Min scored")
        else:
            self.kpi_appeared.update_value("0", "No marks recorded")
            self.kpi_pass_pct.update_value("0%", "—")
            self.kpi_avg.update_value("0.0", "—")
            self.kpi_high.update_value("— / —", "—")

        # Fetch detailed student rows
        det_sql = """
        SELECT 
            s.roll_no, s.prn,
            CONCAT(s.first_name, ' ', s.last_name) AS student_name,
            CONCAT(s.class_year, ' - ', s.division) AS class_div,
            m.marks_obtained,
            a.max_marks,
            ROUND((m.marks_obtained / a.max_marks) * 100, 2) AS percentage,
            CASE 
                WHEN m.is_absent = 1 THEN 'Absent'
                WHEN (m.marks_obtained / a.max_marks) >= 0.40 THEN 'Pass'
                ELSE 'Fail'
            END AS status,
            m.remarks
        FROM marks m
        JOIN enrollments e ON m.enrollment_id = e.enrollment_id
        JOIN students s ON e.student_id = s.student_id
        JOIN assessments a ON m.assessment_id = a.assessment_id
        WHERE m.assessment_id = %s
        ORDER BY m.marks_obtained DESC, s.roll_no ASC;
        """
        if db.active_engine == "sqlite":
            det_sql = det_sql.replace("CONCAT(s.first_name, ' ', s.last_name)", "(s.first_name || ' ' || s.last_name)")
            det_sql = det_sql.replace("CONCAT(s.class_year, ' - ', s.division)", "(s.class_year || ' - ' || s.division)")

        self.current_subject_rows = db.fetch_all(det_sql, (ass_id,))
        self.sub_table.set_data(self.current_subject_rows)

    def _export_subject_report(self):
        if not getattr(self, "current_subject_rows", None):
            messagebox.showinfo("Export", "No report data to export.")
            return

        ass_name = self.ass_rep_var.get().split()[0]
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile=f"Subject_Report_{ass_name}.txt",
            filetypes=[("Text File", "*.txt")]
        )
        if not filepath:
            return

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write("    K.K. WAGH INSTITUTE OF ENGINEERING EDUCATION AND RESEARCH, NASHIK\n")
            f.write("               DEPARTMENT OF COMPUTER ENGINEERING\n")
            f.write("             SUBJECT PERFORMANCE REPORT (AY 2026-27)\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Subject    : {self.sub_rep_var.get()}\n")
            f.write(f"Assessment : {self.ass_rep_var.get()}\n")
            f.write(f"Generated  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("-" * 80 + "\n")
            f.write(f"{'Roll No':<12} {'PRN':<12} {'Student Name':<25} {'Scored':<8} {'Max':<8} {'Pct %':<8} {'Status'}\n")
            f.write("-" * 80 + "\n")
            for r in self.current_subject_rows:
                f.write(f"{r['roll_no']:<12} {r['prn']:<12} {r['student_name'][:23]:<25} {float(r['marks_obtained']):<8.2f} {float(r['max_marks']):<8.2f} {float(r['percentage']):<8.2f} {r['status']}\n")
            f.write("=" * 80 + "\n")

        messagebox.showinfo("Export Successful", f"Subject report saved to:\n{filepath}")

    # =========================================================================
    # TAB 3: Class Performance Report & Analytics
    # =========================================================================
    def _setup_class_tab(self):
        bar = tk.Frame(self.tab_class, bg=COLORS["bg_card"], bd=1, relief="solid", padx=16, pady=10)
        bar.pack(fill="x", padx=10, pady=10)

        tk.Label(bar, text="Class Year:", bg=COLORS["bg_card"], font=FONTS["body_bold"]).pack(side="left", padx=(0, 6))
        self.cls_year_var = tk.StringVar(value="TE")
        cb_yr = ttk.Combobox(bar, textvariable=self.cls_year_var, values=["FE", "SE", "TE", "BE"], state="readonly", width=8)
        cb_yr.pack(side="left", padx=(0, 15))
        cb_yr.bind("<<ComboboxSelected>>", lambda e: self.generate_class_report())

        tk.Label(bar, text="Division:", bg=COLORS["bg_card"], font=FONTS["body_bold"]).pack(side="left", padx=(0, 6))
        self.cls_div_var = tk.StringVar(value="A")
        cb_div = ttk.Combobox(bar, textvariable=self.cls_div_var, values=["All", "A", "B", "C", "D"], state="readonly", width=8)
        cb_div.pack(side="left", padx=(0, 15))
        cb_div.bind("<<ComboboxSelected>>", lambda e: self.generate_class_report())

        ttk.Button(bar, text="Generate Analytics", style="Primary.TButton", command=self.generate_class_report).pack(side="left", padx=4)
        ttk.Button(bar, text="💾 Export Class Summary", style="Secondary.TButton", command=self._export_class_report).pack(side="right")

        # Stats banner
        self.cls_stats_frame = tk.Frame(self.tab_class, bg=COLORS["bg_card"], bd=1, relief="solid", padx=16, pady=12)
        self.cls_stats_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.lbl_class_kpi = tk.Label(
            self.cls_stats_frame,
            text="Class Analytics Loading...",
            font=FONTS["body_bold"],
            bg=COLORS["bg_card"],
            fg=COLORS["text_dark"]
        )
        self.lbl_class_kpi.pack(anchor="w")

        # Leaderboard Table
        tk.Label(self.tab_class, text="Class Merit Leaderboard (Aggregate Score Ranking):", font=FONTS["section_title"], bg=COLORS["bg_main"], fg=COLORS["text_dark"]).pack(anchor="w", padx=10, pady=(5, 5))

        cols = [
            ("rank", "Rank", 50, "center"),
            ("roll_no", "Roll No", 100, "center"),
            ("prn", "PRN", 110, "center"),
            ("student_name", "Student Name", 220, "w"),
            ("class_div", "Class & Div", 90, "center"),
            ("total_scored", "Total Scored", 100, "center"),
            ("total_max", "Total Max", 90, "center"),
            ("overall_percentage", "Aggregate %", 100, "center"),
            ("result_category", "Performance Grade", 180, "w")
        ]
        self.cls_table = DataTable(self.tab_class, cols)
        self.cls_table.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.generate_class_report()

    def generate_class_report(self):
        c_year = self.cls_year_var.get()
        c_div = self.cls_div_var.get()

        conditions = ["s.class_year = %s"]
        params = [c_year]
        if c_div != "All":
            conditions.append("s.division = %s")
            params.append(c_div)

        where_clause = " AND ".join(conditions)

        # SQL JOINs, Aggregates, and GROUP BY to compute student totals and overall class performance
        sql = f"""
        SELECT 
            s.student_id, s.roll_no, s.prn,
            CONCAT(s.first_name, ' ', s.last_name) AS student_name,
            CONCAT(s.class_year, ' - ', s.division) AS class_div,
            SUM(m.marks_obtained) AS total_scored,
            SUM(a.max_marks) AS total_max,
            ROUND((SUM(m.marks_obtained) / NULLIF(SUM(a.max_marks), 0)) * 100, 2) AS overall_percentage
        FROM students s
        JOIN enrollments e ON s.student_id = e.student_id
        JOIN marks m ON e.enrollment_id = m.enrollment_id
        JOIN assessments a ON m.assessment_id = a.assessment_id
        WHERE {where_clause}
        GROUP BY s.student_id, s.roll_no, s.prn, s.first_name, s.last_name, s.class_year, s.division
        ORDER BY overall_percentage DESC;
        """
        if db.active_engine == "sqlite":
            sql = sql.replace("CONCAT(s.first_name, ' ', s.last_name)", "(s.first_name || ' ' || s.last_name)")
            sql = sql.replace("CONCAT(s.class_year, ' - ', s.division)", "(s.class_year || ' - ' || s.division)")

        rows = db.fetch_all(sql, tuple(params))
        self.current_class_rows = []

        distinction_cnt = 0
        first_class_cnt = 0
        second_class_cnt = 0
        fail_cnt = 0
        total_pct_sum = 0.0

        for rank_idx, r in enumerate(rows, start=1):
            row = dict(r)
            row["rank"] = f"#{rank_idx}"
            pct = float(row["overall_percentage"] or 0)
            total_pct_sum += pct

            if pct >= 75.0:
                row["result_category"] = "Distinction (>=75%)"
                distinction_cnt += 1
            elif pct >= 60.0:
                row["result_category"] = "First Class (60-74%)"
                first_class_cnt += 1
            elif pct >= 40.0:
                row["result_category"] = "Second Class (40-59%)"
                second_class_cnt += 1
            else:
                row["result_category"] = "Fail (<40%)"
                fail_cnt += 1

            self.current_class_rows.append(row)

        self.cls_table.set_data(self.current_class_rows)

        total_students = len(rows)
        avg_class_pct = round(total_pct_sum / total_students, 2) if total_students > 0 else 0.0

        self.lbl_class_kpi.config(
            text=f"Class {c_year} Division {c_div} Analytics:\n"
                 f"• Total Evaluated Students: {total_students}   |   Class Mean Aggregate: {avg_class_pct}%\n"
                 f"• Distinction: {distinction_cnt}   |   First Class: {first_class_cnt}   |   Second Class: {second_class_cnt}   |   Fail: {fail_cnt}"
        )

    def _export_class_report(self):
        if not getattr(self, "current_class_rows", None):
            messagebox.showinfo("Export", "No class analytics to export.")
            return

        c_year = self.cls_year_var.get()
        c_div = self.cls_div_var.get()
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile=f"Class_Performance_{c_year}_{c_div}.txt",
            filetypes=[("Text File", "*.txt")]
        )
        if not filepath:
            return

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write("    K.K. WAGH INSTITUTE OF ENGINEERING EDUCATION AND RESEARCH, NASHIK\n")
            f.write("               DEPARTMENT OF COMPUTER ENGINEERING\n")
            f.write(f"          CLASS PERFORMANCE ANALYTICS ({c_year} - {c_div}) AY 2026-27\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Class Year : {c_year}\n")
            f.write(f"Division   : {c_div}\n")
            f.write(f"Generated  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("-" * 80 + "\n")
            f.write(f"{'Rank':<6} {'Roll No':<12} {'PRN':<12} {'Student Name':<25} {'Total':<14} {'Pct %':<8} {'Classification'}\n")
            f.write("-" * 80 + "\n")
            for r in self.current_class_rows:
                tot_str = f"{float(r['total_scored']):.1f}/{float(r['total_max']):.1f}"
                f.write(f"{r['rank']:<6} {r['roll_no']:<12} {r['prn']:<12} {r['student_name'][:23]:<25} {tot_str:<14} {float(r['overall_percentage']):<8.2f} {r['result_category']}\n")
            f.write("=" * 80 + "\n")

        messagebox.showinfo("Export Successful", f"Class report saved to:\n{filepath}")
