# Internal Marks Management System — Presentation Outline & Viva Guide

**Institution:** K.K. Wagh Institute of Engineering Education and Research, Nashik  
**Department:** Department of Computer Engineering  
**Academic Year:** 2026–2027  
**Course:** Database Management Systems (DBMS Mini Project)  

---

## 📽️ PART 1: SLIDE-BY-SLIDE PRESENTATION OUTLINE

### **Slide 1: Title Slide**
- **Title:** Internal Marks Management System
- **Subtitle:** A Python & MySQL Relational Database Application for Academic Evaluation
- **Department:** Department of Computer Engineering
- **Institute:** K.K. Wagh Institute of Engineering Education and Research, Nashik
- **Presenter(s):** [Your Name(s) & Roll Number(s)]
- **Guide / Faculty In-Charge:** [Faculty Name]
- **Speaking Notes:**
  > "Respected examiners and teachers, good morning. Today we present our DBMS mini-project: the Internal Marks Management System. It is an end-to-end desktop database application built to streamline student assessment grading for our department."

---

### **Slide 2: Problem Statement & Motivation**
- **Manual Spreadsheet Drawbacks:**
  - Redundant data entry and absence of referential integrity.
  - Vulnerability to duplicate enrollments and duplicate marks entries.
  - Risk of human error: entering marks higher than the evaluation limit.
  - Time-consuming aggregation for marksheet printing and division-wide analysis.
- **Proposed Solution:**
  - A secure, transactional desktop DBMS with automated validations, normalized relational design, and instant multi-level reports.

---

### **Slide 3: Technology Stack & Architectural Highlights**
- **Language:** Python 3.10+
- **Desktop GUI:** Tkinter with `ttk` themed widgets (Clean, modern desktop application without web dependencies)
- **Database Server:** MySQL Server 8.0+
- **Driver:** `mysql-connector-python`
- **Administration:** MySQL Command-Line Client (`mysql.exe`)
- **Key Architecture:**
  - 3-tier desktop architecture: Presentation Layer (Tkinter) $\rightarrow$ Data Access Layer (`db.py`) $\rightarrow$ Relational Database (MySQL InnoDB).
  - Parameterized queries to eliminate SQL injection vulnerabilities.
  - Transaction atomicity (`COMMIT` and `ROLLBACK`).

---

### **Slide 4: Entity-Relationship (ER) Modeling**
- **7 Core Entities:**
  1. `departments`
  2. `teachers`
  3. `students`
  4. `subjects`
  5. `enrollments` (Resolves M:N relationship between Students and Subjects)
  6. `assessments`
  7. `marks` (Relates an Enrollment to a specific Assessment)
- **Cardinality Ratios:**
  - Department $\rightarrow$ Students: $1:N$
  - Department $\rightarrow$ Subjects: $1:N$
  - Teacher $\rightarrow$ Subjects: $1:N$
  - Student $\rightarrow$ Enrollments $\rightarrow$ Subject: $M:N$
  - Subject $\rightarrow$ Assessments: $1:N$
  - Enrollment $\times$ Assessment $\rightarrow$ Marks: $1:1$ (Unique pair)

---

### **Slide 5: Relational Schema & Normalization**
- **1NF:** Atomic attributes, scalar domains, no multi-valued attributes.
- **2NF:** Surrogate integer primary keys; zero partial functional dependencies.
- **3NF & BCNF:** All transitive dependencies eliminated; every determinant is a candidate key.
- **Foreign Key Integrity Rules:**
  - `departments` $\rightarrow$ `students`: `ON DELETE RESTRICT` (prevents deleting active academic departments).
  - `subjects` $\rightarrow$ `enrollments`: `ON DELETE RESTRICT`.
  - `students` $\rightarrow$ `enrollments`: `ON DELETE CASCADE` (student removal cleans associated enrollments).
  - `enrollments` $\rightarrow$ `marks`: `ON DELETE CASCADE`.

---

### **Slide 6: Crucial Database Constraints & Business Logic**
- **Requirement #9 (Prevent Duplicate Enrollments):**
  ```sql
  CONSTRAINT uq_student_enrollment UNIQUE (student_id, subject_id, academic_year, semester);
  ```
- **Requirement #9 (Prevent Duplicate Marks Entry):**
  ```sql
  CONSTRAINT uq_enrollment_assessment UNIQUE (enrollment_id, assessment_id);
  ```
- **Requirement #10 (Marks Range Validation $0 \le \text{marks} \le \text{max\_marks}$):**
  - **Check Constraint:** `CHECK (marks_obtained >= 0.00)`
  - **Database Triggers:** `BEFORE INSERT` and `BEFORE UPDATE` trigger `trg_validate_marks` dynamically cross-checks `assessments.max_marks` and raises SQLSTATE 45000 if violated.
  - **GUI Validation:** Real-time form inspection prevents invalid submissions before touching the network.

---

### **Slide 7: GUI Demonstration (Core Management Modules)**
- **Dashboard:** Live KPI tiles (Total Students, Teachers, Courses, Marks Recorded) + Real-time feed of recent submissions.
- **Department & Faculty Management:** Form modals, designation filters, and contact directories.
- **Student Roster:** Multi-criteria filtering by Class Year (`FE`, `SE`, `TE`, `BE`) and Division (`A`, `B`, `C`, `D`).
- **Subject Management:** Mapping SPPU subject codes, credits, and faculty in-charge.
- **Course Enrollment:** Individual enrollment + **Batch Enroll Class** utility.

---

### **Slide 8: Marks Entry & Evaluation Screen**
- **Workflow:**
  1. Select Course (e.g., `310241 - Database Management Systems`).
  2. Select Assessment (e.g., `In-Semester Exam (Max: 30.00)`).
  3. System automatically queries and populates the class roster.
  4. Real-time indicators: Evaluated count, Pass/Fail count, Absent count, and Average score.
  5. Action buttons: Record Marks, Mark Absent, Clear Record.

---

### **Slide 9: Academic Reports & Analytics (Requirement #6 & #7)**
- **Report 1: Student-wise Marksheet:**
  - Detailed course breakdown (Code, Title, Assessment, Scored, Max, Percentage, Pass/Fail).
  - Cumulative total, aggregate percentage, and SPPU grade classification.
  - Text file export feature for student distribution.
- **Report 2: Subject-wise Performance Report:**
  - Aggregates: Appeared count, Pass percentage, Average, Max, and Min score.
- **Report 3: Class Performance & Analytics:**
  - Division-wide grade distribution (Distinction, First Class, Second Class, Fail).
  - Class Merit Leaderboard ranked by cumulative percentage.

---

### **Slide 10: Advanced SQL Query Highlights**
- **5-Table JOIN with Conditional CASE:**
  - Queries `marks`, `enrollments`, `students`, `assessments`, and `subjects` simultaneously.
- **Aggregations & Grouping:**
  - `COUNT(m.mark_id)`, `SUM(m.marks_obtained)`, `AVG(m.marks_obtained)`.
  - `GROUP BY sub.subject_code, a.assessment_name`.
  - `NULLIF()` handling to prevent division-by-zero errors.

---

### **Slide 11: Testing & Verification**
- **Automated Unit & Integration Test Suite:**
  - 12 comprehensive unit and integration tests written with Python's `unittest`.
  - Verified constraints: Duplicate enrollments rejected, duplicate marks blocked, out-of-range marks rejected.
  - 100% test pass rate in under 1.5 seconds.

---

### **Slide 12: Summary & Viva Conclusion**
- **Achievements:**
  - Fully functional, beginner-friendly yet enterprise-grade DBMS mini project.
  - Zero web framework overhead; runs cleanly on any Windows 11 machine.
  - Robust database schema adhering to SPPU standards.
- **Thank you! We welcome questions from the panel.**

---

## 🎓 PART 2: VIVA VOCE QUESTIONS & MODEL ANSWERS

### **Q1: Why did you design 7 tables instead of fewer tables?**
**Answer:**  
"A single or two-table design introduces severe data redundancy and update anomalies. By decomposing into seven entities—`departments`, `teachers`, `students`, `subjects`, `enrollments`, `assessments`, and `marks`—we achieve Boyce-Codd Normal Form (BCNF). For example, a student enrolls in many subjects, and each subject has distinct assessment schemes (In-Sem, End-Sem, TW, Oral). The `enrollments` table cleanly handles the M:N relationship between Students and Subjects, while `marks` links each enrollment to an assessment."

---

### **Q2: How do you prevent duplicate enrollments and duplicate marks?**
**Answer:**  
"We enforced composite unique constraints in the MySQL schema:
1. In `enrollments`: `CONSTRAINT uq_student_enrollment UNIQUE (student_id, subject_id, academic_year, semester)`. If a student attempts to enroll in the same course in the same semester, the database rejects it with an error.
2. In `marks`: `CONSTRAINT uq_enrollment_assessment UNIQUE (enrollment_id, assessment_id)`. This ensures only one mark entry can exist per student per assessment head."

---

### **Q3: How do you validate that marks obtained do not exceed maximum marks?**
**Answer:**  
"We implement a three-tier validation strategy:
1. **Database Triggers:** A `BEFORE INSERT` and `BEFORE UPDATE` trigger checks `NEW.marks_obtained > (SELECT max_marks FROM assessments WHERE assessment_id = NEW.assessment_id)`. If violated, it executes `SIGNAL SQLSTATE '45000'` with a custom validation message.
2. **Database Check Constraint:** `CHECK (marks_obtained >= 0.00)` ensures marks cannot be negative.
3. **Application Layer:** In Python `marks_entry_view.py`, user input is cast to a float and verified against the assessment's `max_marks` before the query is dispatched."

---

### **Q4: Why did you use `ON DELETE RESTRICT` for Departments and Subjects, but `ON DELETE CASCADE` for Enrollments?**
**Answer:**  
"`ON DELETE RESTRICT` protects critical master data. If someone tries to delete a department that still has registered students or teachers, MySQL stops the operation to prevent orphan records. Conversely, if a student profile is legitimately deleted, `ON DELETE CASCADE` automatically removes that student's enrollments and marks, maintaining referential integrity without leaving dangling foreign keys."

---

### **Q5: Why are parameterized queries used instead of string formatting (f-strings)?**
**Answer:**  
"Using f-strings or string concatenation like `f'SELECT * FROM users WHERE name = \"{name}\"'` is vulnerable to **SQL Injection**, where malicious inputs can alter query semantics or drop tables. Parameterized queries (`cursor.execute(sql, params)`) pass SQL code and user data separately. The database engine compiles the query structure first and treats parameters strictly as literal data values, completely eliminating SQL injection risks."

---

### **Q6: How does the application handle database transactions?**
**Answer:**  
"In our Database Access Layer (`db.py`), all data modification queries (`INSERT`, `UPDATE`, `DELETE`) operate inside transactional blocks. If an operation succeeds, `conn.commit()` commits the changes permanently. If an error occurs (such as a constraint failure or disconnection), `conn.rollback()` is invoked inside the `except` block to roll back uncommitted changes, preserving the ACID properties of the database."

---

### **Q7: What is the purpose of the Database Views you created in `database.sql`?**
**Answer:**  
"Database views encapsulate complex multi-table joins and aggregation logic into reusable virtual tables:
1. `vw_student_marks_detailed`: Pre-joins five tables (`marks`, `enrollments`, `students`, `assessments`, `subjects`) to output unified columns like student name, course title, percentage, and pass/fail status.
2. `vw_subject_performance_summary`: Automatically groups marks by subject and calculates total appeared, pass count, average marks, and highest/lowest scores.
This improves query performance, reduces code duplication in the GUI, and adds a layer of abstraction."

---

### **Q8: Can this application run without MySQL Workbench?**
**Answer:**  
"Yes, absolutely. MySQL Workbench is merely a graphical client tool. Our application connects directly to the core **MySQL Server daemon** using the official driver `mysql-connector-python`. Schema setup is performed using standard SQL scripts (`database.sql` and `sample_data.sql`) via the command-line client or through our in-app initialization wizard."
